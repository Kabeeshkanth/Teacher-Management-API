# python
from typing import Optional
from models.schema import CourseMaterial
from utils.database import supabase


def upload_lecture_notes_logic(course_id: int, material_title: str, file_link: str) -> CourseMaterial:
    response = supabase.table("Course_Materials").insert({
        "course_id": course_id,
        "material_title": material_title,
        "file_path": file_link
    }).execute()
    if not response.data:
        raise Exception("Failed to save course material.")
    return CourseMaterial(**response.data[0])
