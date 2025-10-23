from typing import Dict, Any
from uuid import UUID
import logging
from fastapi import HTTPException, status
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access
from models.schema import Grade

logger = logging.getLogger(__name__)


def upload_results_logic(
        teacher_id: str,
        course_id: int,
        assignment_id: int,
        student_id: UUID,
        result: Grade
) -> Dict[str, Any]:
    verify_teacher_course_access(teacher_id, course_id)

    supabase = get_supabase_client()
    payload = {
        "course_id": course_id,
        "assignment_id": assignment_id,
        "student_id": str(student_id),
        "result": result.value
    }

    try:
        resp = supabase.table("results").insert(payload).select("*").execute()

        if getattr(resp, "error", None):
            logger.error("Supabase insert error: %s", resp.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save result"
            )

        data = getattr(resp, "data", None)
        if not data or len(data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No result returned from database"
            )

        return data[0]

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error inserting result")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
