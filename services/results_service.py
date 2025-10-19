# python
# File: `services/results_service.py`

from typing import Optional, Dict, Any
import logging
from fastapi import HTTPException, status
from utils.database import get_supabase_client

logger = logging.getLogger(__name__)


def upload_results_logic(
        course_id: int,
        assignment_id: int,
        submission_id: str,  # Changed from hardcoded int to UUID string
        description: Optional[str],
        file_link: str
) -> Dict[str, Any]:
    """
    Insert result into `results` table.
    Maps all columns: result_id, course_id, assignment_id, submission_id (UUID), file_path, description
    """
    supabase = get_supabase_client()

    payload = {
        "course_id": course_id,
        "assignment_id": assignment_id,
        "submission_id": submission_id,  # Must be valid UUID string
        "file_path": file_link,
        "description": description
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
