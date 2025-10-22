import logging
from fastapi import HTTPException, status
from models.schema import CourseMaterial
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access

logger = logging.getLogger(__name__)


def upload_lecture_notes_logic(teacher_id: str, course_id: int, material_title: str, file_link: str) -> CourseMaterial:
    """
    Uploads course materials matching database schema:
    - material_id (auto-generated)
    - course_id
    - material_title
    - file_path
    - upload_date (auto-generated DEFAULT CURRENT_TIMESTAMP)
    """
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()

    try:
        response = supabase.table("course_materials").insert({
            "course_id": course_id,
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
