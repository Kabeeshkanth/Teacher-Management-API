import logging
from typing import List
from fastapi import HTTPException, status
from models.schema import Feedback
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access

logger = logging.getLogger(__name__)



def review_feedback_logic(teacher_id: str, course_id: int) -> List[Feedback]:
    """
    Retrieves feedback matching database schema:
    - feedback_id
    - student_id (UUID)
    - course_id
    - comment (optional)
    - created_at (auto-generated DEFAULT CURRENT_TIMESTAMP)
    """
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()

    try:
        response = supabase.table("feedback").select("*").eq("course_id", course_id).execute()

        if getattr(response, "error", None):
            logger.error("Supabase query error: %s", response.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch feedback"
            )

        return [Feedback(**item) for item in (response.data or [])]

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error fetching feedback")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
