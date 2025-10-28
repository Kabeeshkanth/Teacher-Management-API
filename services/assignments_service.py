# services/assignments_service.py
from typing import Dict, Any, Optional, List

from datetime import datetime
import logging
from fastapi import HTTPException, status
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access

logger = logging.getLogger(__name__)



def upload_assignment_logic(
        teacher_id: str,
        course_id: int,
        module_id: int,  # Added
        assignment_title: str,
        description: Optional[str],
        due_date: Optional[datetime],
        file_link: str,
) -> Dict[str, Any]:
    """
    Creates assignment matching database schema:
    - assignment_id (auto-generated)
    - course_id
    - module_id  # Added
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
        "module_id": module_id,
        "assignment_title": assignment_title,
        "description": description,
        "file_path": file_link,
    }

    if due_date is not None:
        payload["due_date"] = due_date.isoformat() if isinstance(due_date, datetime) else str(due_date)

    try:
        resp = supabase.table("assignments").insert(payload).execute()

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


def get_assignments_for_module(teacher_id: str, module_id: int) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    module_resp = supabase.table("modules").select("course_id").eq("module_id", module_id).execute()
    if not module_resp.data:
        raise HTTPException(status_code=404, detail="Module not found")
    course_id = module_resp.data[0]["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    resp = supabase.table("assignments").select("*").eq("module_id", module_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="Error fetching assignments")
    return resp.data or []


def update_assignment(teacher_id: str, assignment_id: int, **updates) -> Dict[str, Any]:
    supabase = get_supabase_client()
    assignment_resp = supabase.table("assignments").select("course_id").eq("assignment_id", assignment_id).execute()
    if not assignment_resp.data:
        raise HTTPException(status_code=404, detail="Assignment not found")
    course_id = assignment_resp.data[0]["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    resp = supabase.table("assignments").update(updates).eq("assignment_id", assignment_id).select("*").execute()
    if getattr(resp, "error", None) or not resp.data:
        raise HTTPException(status_code=500, detail="Failed to update assignment")
    return resp.data[0]


def delete_assignment(teacher_id: str, assignment_id: int) -> Dict[str, str]:
    supabase = get_supabase_client()
    assignment_resp = supabase.table("assignments").select("course_id").eq("assignment_id", assignment_id).execute()
    if not assignment_resp.data:
        raise HTTPException(status_code=404, detail="Assignment not found")
    course_id = assignment_resp.data[0]["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    resp = supabase.table("assignments").delete().eq("assignment_id", assignment_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="Failed to delete assignment")
    return {"message": "Assignment deleted"}
