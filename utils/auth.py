from fastapi import Request, HTTPException, status
from utils.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


def verify_teacher(request: Request) -> str:
    """
    Validates that the current user is a teacher.
    Returns teacher_id (UUID) if valid, raises HTTPException otherwise.
    """
    user_id = request.cookies.get("user_id")
    role = request.cookies.get("role")

    if not user_id:
        logger.warning("Missing user_id cookie in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user ID cookie"
        )

    # Role check
    if role != "teacher":
        logger.warning(f"Access denied: user {user_id} has role '{role}', expected 'teacher'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: teacher role required"
        )

    # Verify against Supabase 'teachers' table
    supabase = get_supabase_client()
    try:
        result = supabase.table("teachers").select("id").eq("id", user_id).execute()

        if not result.data:
            logger.error(f"Teacher verification failed: user_id {user_id} not found in teachers table")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid teacher account"
            )

        logger.info(f"Teacher {user_id} verified successfully")
        return user_id

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Error verifying teacher: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify teacher credentials"
        )


def verify_teacher_course_access(teacher_id: str, course_id: int) -> bool:
    """
    Verify if teacher is assigned to the specific course.
    Matches teacher_id with teacher_ids column in course table.
    """
    supabase = get_supabase_client()

    try:
        response = supabase.table("course").select("teacher_ids").eq("course_id", course_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_id} not found"
            )

        assigned_teacher_id = response.data[0].get("teacher_ids")

        if assigned_teacher_id != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this course"
            )

        return True

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error verifying teacher course access")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
