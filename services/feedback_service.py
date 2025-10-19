# python
from typing import List
from models.schema import Feedback
from utils.database import supabase


def review_feedback_logic(course_id: int) -> List[Feedback]:
    response = supabase.table("Feedback").select("*").eq("course_id", course_id).execute()
    return [Feedback(**item) for item in (response.data or [])]
