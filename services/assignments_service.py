# python
# File: services/assignments_service.py
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from fastapi import HTTPException, status
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access
from services.module_service import verify_module_owner
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def upload_assignment_logic(
        teacher_id: str,
        course_id: int,
        assignment_title: str,
        description: Optional[str],
        due_date: Optional[datetime],
        file_link: str,
        module_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Create assignment and optionally link to a module. If module_id provided,
    verify it belongs to the teacher and the same course.
    """
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()

    if module_id is not None:
        module = verify_module_owner(module_id, teacher_id)
        if module["course_id"] != course_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Module does not belong to specified course")

    payload: Dict[str, Any] = {
        "course_id": course_id,
        "assignment_title": assignment_title,
        "description": description,
        "file_path": file_link,
    }
    if module_id is not None:
        payload["module_id"] = module_id

    if due_date is not None:
        payload["due_date"] = due_date.isoformat() if isinstance(due_date, datetime) else str(due_date)

    try:
        resp = supabase.table("assignments").insert(payload).select("*").execute()

        if getattr(resp, "error", None):
            logger.error("Supabase insert error: %s", resp.error)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create assignment")

        data = getattr(resp, "data", None)
        if not data or len(data) == 0:
            logger.error("No data returned after insert: %s", resp)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No assignment returned from database")

        return data[0]

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error inserting assignment")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


def get_assignments_by_module_logic(teacher_id: str, course_id: int, module_id: int) -> List[Dict[str, Any]]:
    verify_teacher_course_access(teacher_id, course_id)
    # ensure module belongs to teacher and course
    module = verify_module_owner(module_id, teacher_id)
    if module["course_id"] != course_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Module does not belong to course")
    supabase = get_supabase_client()
    resp = supabase.table("assignments").select("*").eq("module_id", module_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch assignments")
    return resp.data or []
