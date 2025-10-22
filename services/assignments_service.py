from typing import Dict, Any, Optional
from datetime import datetime
import logging
from fastapi import HTTPException, status
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access

logger = logging.getLogger(__name__)


def upload_assignment_logic(
        teacher_id: str,
        course_id: int,
        assignment_title: str,
        description: Optional[str],
        due_date: Optional[datetime],
        file_link: str,
) -> Dict[str, Any]:
    """
    Creates assignment matching database schema:
    - assignment_id (auto-generated)
    - course_id
    - assignment_title
    - description (optional)
    - due_date (optional)
    - file_path
    - created_at (auto-generated DEFAULT CURRENT_TIMESTAMP)
    """
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()

    payload: Dict[str, Any] = {
        "course_id": course_id,
        "assignment_title": assignment_title,
        "description": description,
        "file_path": file_link,
    }

    if due_date is not None:
        payload["due_date"] = due_date.isoformat() if isinstance(due_date, datetime) else str(due_date)

    try:
        resp = supabase.table("assignments").insert(payload).select("*").execute()

        if getattr(resp, "error", None):
            logger.error("Supabase insert error: %s", resp.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create assignment"
            )

        data = getattr(resp, "data", None)
        if not data or len(data) == 0:
            logger.error("No data returned after insert: %s", resp)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No assignment returned from database"
            )

        return data[0]

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error inserting assignment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
