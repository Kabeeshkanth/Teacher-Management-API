import logging
from datetime import date
from fastapi import HTTPException
from models.schema import Attendance
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access

logger = logging.getLogger(__name__)


def upload_attendance_logic(teacher_id: str, course_id: int, class_date: date, attendance_link: str) -> Attendance:
    """
    Uploads attendance matching database schema:
    - attendance_id (auto-generated)
    - course_id
    - class_date (date)
    - attendance_link (text)
    """
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()

    try:
        logger.info(
            f"Saving attendance: course_id={course_id}, class_date={class_date.isoformat()}, attendance_link={attendance_link}")

        db_response = supabase.table("attendance").insert({
            "course_id": course_id,
            "class_date": class_date.isoformat(),
            "attendance_link": attendance_link
        }).select("*").execute()

        logger.info(f"Database response: {db_response}")

        if not db_response.data:
            raise HTTPException(status_code=500, detail="Failed to save attendance record to database.")

        return Attendance(**db_response.data[0])

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error in upload_attendance_logic: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload attendance: {str(exc)}"
        )
