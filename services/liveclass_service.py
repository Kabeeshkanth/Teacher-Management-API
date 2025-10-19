# python
from models.schema import LiveClass, LiveClassCreate
from utils.database import supabase


def schedule_live_class_logic(live_class: LiveClassCreate) -> LiveClass:
    data_to_insert = {
        "course_id": live_class.course_id,
        "title": live_class.title,
        "class_link": live_class.class_link,
        "start_time": live_class.start_time.isoformat(),
        "end_time": live_class.end_time.isoformat()
    }
    response = supabase.table("Live_Classes").insert(data_to_insert).execute()
    if not response.data:
        raise Exception("Failed to schedule live class.")
    return LiveClass(**response.data[0])
