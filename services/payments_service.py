from typing import List
from models.schema import TeacherPayment
from utils.database import supabase


def get_payments_for_teacher_logic(teacher_id: str) -> List[TeacherPayment]:  # Changed from int to str
    response = supabase.table("Teacher_Payments").select("*").eq("teacher_id", teacher_id).execute()
    return [TeacherPayment(**item) for item in (response.data or [])]
