# python
from typing import List, Dict, Any
import logging
from fastapi import HTTPException, status
from utils.database import get_supabase_client
from utils.auth import verify_teacher_exists

logger = logging.getLogger(__name__)


def get_teacher_courses_logic(teacher_id: str) -> List[Dict[str, Any]]:
    """
    Return all courses assigned to the teacher.
    The schema stores a `teacher_ids` column referencing a single teacher id.
    """
    verify_teacher_exists(teacher_id)
    supabase = get_supabase_client()

    try:
        resp = supabase.table("course").select("*").eq("teacher_ids", teacher_id).execute()
        if getattr(resp, "error", None):
            logger.error("DB error fetching courses for teacher %s: %s", teacher_id, resp.error)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error fetching courses")
        return resp.data or []
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error fetching teacher courses")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
