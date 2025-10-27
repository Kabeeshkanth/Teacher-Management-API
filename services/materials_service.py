import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from models.schema import CourseMaterial
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access

logger = logging.getLogger(__name__)


def upload_lecture_notes_logic(teacher_id: str, course_id: int, module_id: int, material_title: str, file_link: str) -> CourseMaterial:
    """
    Uploads course materials matching database schema:
    - material_id (auto-generated)
    - course_id
    - module_id  # Added
    - material_title
    - file_path
    - upload_date (auto-generated DEFAULT CURRENT_TIMESTAMP)
    """
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()
    module_resp = supabase.table("modules").select("module_id").eq("module_id", module_id).eq("course_id", course_id).eq("teacher_id", teacher_id).execute()
    if not module_resp.data:
        raise HTTPException(status_code=404, detail="Module not found for this course and teacher")

    try:
        response = supabase.table("course_materials").insert({
            "course_id": course_id,
            "module_id": module_id,
            "material_title": material_title,
            "file_path": file_link
        }).select("*").execute()

        if getattr(response, "error", None):
            logger.error("Supabase insert error: %s", response.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save course material"
            )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No course material returned from database"
            )

        return CourseMaterial(**response.data[0])

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error uploading course material")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


def get_materials_for_module(teacher_id: str, module_id: int) -> List[CourseMaterial]:
    supabase = get_supabase_client()
    module_resp = supabase.table("modules").select("course_id").eq("module_id", module_id).eq("teacher_id", teacher_id).execute()
    if not module_resp.data:
        raise HTTPException(status_code=404, detail="Module not found or not owned")
    course_id = module_resp.data[0]["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    resp = supabase.table("course_materials").select("*").eq("module_id", module_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="Error fetching materials")
    return [CourseMaterial(**item) for item in resp.data or []]


def update_material(teacher_id: str, material_id: int, **updates) -> CourseMaterial:
    supabase = get_supabase_client()
    material_resp = supabase.table("course_materials").select("course_id").eq("material_id", material_id).execute()
    if not material_resp.data:
        raise HTTPException(status_code=404, detail="Material not found")
    course_id = material_resp.data[0]["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    resp = supabase.table("course_materials").update(updates).eq("material_id", material_id).select("*").execute()
    if getattr(resp, "error", None) or not resp.data:
        raise HTTPException(status_code=500, detail="Failed to update material")
    return CourseMaterial(**resp.data[0])


def delete_material(teacher_id: str, material_id: int) -> Dict[str, str]:
    supabase = get_supabase_client()
    material_resp = supabase.table("course_materials").select("course_id").eq("material_id", material_id).execute()
    if not material_resp.data:
        raise HTTPException(status_code=404, detail="Material not found")
    course_id = material_resp.data[0]["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    resp = supabase.table("course_materials").delete().eq("material_id", material_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="Failed to delete material")
    return {"message": "Material deleted"}
