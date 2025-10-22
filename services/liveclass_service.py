import logging
from fastapi import HTTPException, status
from models.schema import LiveClass, LiveClassCreate
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access

logger = logging.getLogger(__name__)


def schedule_live_class_logic(teacher_id: str, live_class: LiveClassCreate) -> LiveClass:
    """
    Schedules live class matching database schema:
    - class_id (auto-generated)
    - course_id
    - title
    - class_link
    - start_time (timestamp without time zone)
    - end_time (timestamp without time zone)
    """
    verify_teacher_course_access(teacher_id, live_class.course_id)
    supabase = get_supabase_client()

    data_to_insert = {
        "course_id": live_class.course_id,
        "title": live_class.title,
        "class_link": live_class.class_link,
        "start_time": live_class.start_time.isoformat(),
        "end_time": live_class.end_time.isoformat()
    }

    try:
        response = supabase.table("live_classes").insert(data_to_insert).select("*").execute()

        if getattr(response, "error", None):
            logger.error("Supabase insert error: %s", response.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to schedule live class"
            )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No live class returned from database"
            )

        return LiveClass(**response.data[0])

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error scheduling live class")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
