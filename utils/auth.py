from fastapi import HTTPException, status, Request
from utils.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


def verify_teacher(request: Request) -> str:
    """
    FastAPI dependency to extract and validate teacher_id from cookies.
    Returns the teacher_id if valid.
    """
    teacher_id = request.cookies.get("teacher_id")
    if not teacher_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Teacher ID not found in cookies"
        )

    verify_teacher_exists(teacher_id)
    return teacher_id


def verify_teacher_exists(teacher_id: str) -> None:
    """
    Verify that the teacher_id exists in the teachers table.
    Raises:
      - 403 if teacher not found
      - 500 on DB error
    """
    supabase = get_supabase_client()
    resp = supabase.table("teachers").select("id").eq("id", teacher_id).execute()

    if getattr(resp, "error", None):
        logger.error("DB error verifying teacher: %s", resp.error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error verifying teacher")

    rows = getattr(resp, "data", None)
    if not rows:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher not found")


def verify_teacher_course_access(teacher_id: str, course_id: int) -> None:
    """
    Verify teacher exists and course exists and is assigned to teacher.
    Raises:
      - 403 if teacher not found or course not assigned
      - 404 if course not found
      - 500 on DB error
    """
    verify_teacher_exists(teacher_id)

    supabase = get_supabase_client()
    resp = supabase.table("course").select("course_id").eq("course_id", course_id).eq("teacher_ids", teacher_id).execute()

    if getattr(resp, "error", None):
        logger.error("DB error checking course: %s", resp.error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error checking course")

    rows = getattr(resp, "data", None)
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or not assigned to teacher")


def verify_teacher_form(teacher_id: str) -> str:
    """
    Verify teacher_id from form input against courses table.
    Raises 403 if no courses assigned.
    """
    supabase = get_supabase_client()
    resp = supabase.table("course").select("course_id").eq("teacher_ids", teacher_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="DB error verifying teacher")
    if not resp.data:
        raise HTTPException(status_code=403, detail="Teacher not assigned to any courses")
    return teacher_id
