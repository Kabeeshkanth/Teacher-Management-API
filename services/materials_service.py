# python
# File: services/materials_service.py
import logging
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from models.schema import CourseMaterial
from utils.database import get_supabase_client
from services.module_service import verify_module_owner
from utils.auth import verify_teacher_course_access

logger = logging.getLogger(__name__)


def upload_lecture_notes_logic(teacher_id: str, course_id: int, material_title: str, file_link: str, module_id: Optional[int] = None) -> CourseMaterial:
    """
    Insert material. If module_id provided, verify the module belongs to teacher and course.
    """
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()

    if module_id is not None:
        module = verify_module_owner(module_id, teacher_id)
        # ensure module belongs to same course
        if module["course_id"] != course_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Module does not belong to specified course")

    try:
        payload: Dict[str, Any] = {
            "course_id": course_id,
            "material_title": material_title,
            "file_path": file_link
        }
        if module_id is not None:
            payload["module_id"] = module_id

        response = supabase.table("course_materials").insert(payload).select("*").execute()

        if getattr(response, "error", None):
            logger.error("Supabase insert error: %s", response.error)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save course material")

        if not response.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No course material returned from database")

        return CourseMaterial(**response.data[0])
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error uploading course material")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


def get_materials_by_module_logic(teacher_id: str, course_id: int, module_id: int) -> List[CourseMaterial]:
    verify_teacher_course_access(teacher_id, course_id)
    module = verify_module_owner(module_id, teacher_id)
    if module["course_id"] != course_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Module does not belong to specified course")
    supabase = get_supabase_client()

    try:
        resp = supabase.table("course_materials").select("*").eq("module_id", module_id).execute()
        if getattr(resp, "error", None):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch materials")
        return [CourseMaterial(**item) for item in (resp.data or [])]
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error fetching materials")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


def get_material_by_title_logic(teacher_id: str, course_id: int, material_title: str) -> Optional[CourseMaterial]:
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()
    resp = supabase.table("course_materials").select("*").eq("course_id", course_id).eq("material_title", material_title).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error fetching material")
    if not resp.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    return CourseMaterial(**resp.data[0])


def update_material_logic(teacher_id: str, material_id: int, material_title: Optional[str] = None, file_link: Optional[str] = None) -> CourseMaterial:
    supabase = get_supabase_client()
    # fetch material and verify ownership through module (if module exists) or course
    resp = supabase.table("course_materials").select("course_id, module_id").eq("material_id", material_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error fetching material")
    if not resp.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    row = resp.data[0]
    course_id = row["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    module_id = row.get("module_id")
    if module_id:
        # verify module belongs to teacher
        verify_module_owner(module_id, teacher_id)

    updates = {}
    if material_title is not None:
        updates["material_title"] = material_title
    if file_link is not None:
        updates["file_path"] = file_link

    try:
        upd = supabase.table("course_materials").update(updates).eq("material_id", material_id).select("*").execute()
        if getattr(upd, "error", None):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update material")
        return CourseMaterial(**upd.data[0])
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error updating material")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


def delete_material_logic(teacher_id: str, material_id: int) -> None:
    supabase = get_supabase_client()
    resp = supabase.table("course_materials").select("course_id, module_id").eq("material_id", material_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error fetching material")
    if not resp.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    row = resp.data[0]
    course_id = row["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    module_id = row.get("module_id")
    if module_id:
        verify_module_owner(module_id, teacher_id)

    try:
        d = supabase.table("course_materials").delete().eq("material_id", material_id).execute()
        if getattr(d, "error", None):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete material")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error deleting material")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
