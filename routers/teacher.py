from fastapi import APIRouter, Form, HTTPException
from typing import List, Optional
from datetime import date, datetime

from models.schema import (
    CourseMaterial,
    Assignment,
    Result,
    LiveClass,
    Feedback,
    LiveClassCreate,
    Attendance,
    Grade,
    Module,
    Course
)
from services import teacher_service
from utils.auth import verify_teacher_form
from utils.database import get_supabase_client

router = APIRouter(
    prefix="/teacher",
    tags=["teacher"]
)


@router.get("/courses", response_model=List[Course])
async def get_teacher_courses(teacher_id: str = Form(...)):
    verify_teacher_form(teacher_id)
    supabase = get_supabase_client()
    resp = supabase.table("course").select("*").eq("teacher_ids", teacher_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="Error fetching courses")
    return [Course(**item) for item in resp.data or []]


@router.get("/courses/{course_id}/modules", response_model=List[Module])
async def get_modules(course_id: int, teacher_id: str = Form(...)):
    verify_teacher_form(teacher_id)
    return teacher_service.get_modules_for_course(teacher_id, course_id)


@router.post("/modules", response_model=Module)
async def create_module(
    teacher_id: str = Form(...),
    course_id: int = Form(...),
    module_name: str = Form(...),
    module_description: Optional[str] = Form(None),
):
    verify_teacher_form(teacher_id)
    return teacher_service.create_module(teacher_id, course_id, module_name, module_description)


@router.put("/modules/{module_id}", response_model=Module)
async def update_module(
    module_id: int,
    teacher_id: str = Form(...),
    module_name: Optional[str] = Form(None),
    module_description: Optional[str] = Form(None),
):
    verify_teacher_form(teacher_id)
    return teacher_service.update_module(teacher_id, module_id, module_name, module_description)


@router.delete("/modules/{module_id}")
async def delete_module(module_id: int, teacher_id: str = Form(...)):
    verify_teacher_form(teacher_id)
    return teacher_service.delete_module(teacher_id, module_id)


@router.get("/modules/{module_id}/materials", response_model=List[CourseMaterial])
async def get_materials(module_id: int, teacher_id: str = Form(...)):
    verify_teacher_form(teacher_id)
    return teacher_service.get_materials_for_module(teacher_id, module_id)


@router.post("/materials/upload", response_model=CourseMaterial)
async def upload_lecture_notes(
    teacher_id: str = Form(...),
    course_id: int = Form(...),
    module_id: int = Form(...),
    material_title: str = Form(...),
    file_link: str = Form(...),
):
    verify_teacher_form(teacher_id)
    return teacher_service.upload_lecture_notes_logic(teacher_id, course_id, module_id, material_title, file_link)


@router.put("/materials/{material_id}", response_model=CourseMaterial)
async def update_material(
    material_id: int,
    teacher_id: str = Form(...),
    material_title: Optional[str] = Form(None),
    file_link: Optional[str] = Form(None),
):
    verify_teacher_form(teacher_id)
    updates = {}
    if material_title:
        updates["material_title"] = material_title
    if file_link:
        updates["file_path"] = file_link
    return teacher_service.update_material(teacher_id, material_id, **updates)


@router.delete("/materials/{material_id}")
async def delete_material(material_id: int, teacher_id: str = Form(...)):
    verify_teacher_form(teacher_id)
    return teacher_service.delete_material(teacher_id, material_id)


@router.get("/modules/{module_id}/assignments", response_model=List[Assignment])
async def get_assignments(module_id: int, teacher_id: str = Form(...)):
    verify_teacher_form(teacher_id)
    return teacher_service.get_assignments_for_module(teacher_id, module_id)


@router.post("/assignments/upload", response_model=Assignment)
async def upload_assignment(
    teacher_id: str = Form(...),
    course_id: int = Form(...),
    module_id: int = Form(...),
    assignment_title: str = Form(...),
    description: Optional[str] = Form(None),
    due_date: Optional[datetime] = Form(None),
    file_link: str = Form(...),
):
    verify_teacher_form(teacher_id)
    return teacher_service.upload_assignment_logic(
        teacher_id, course_id, module_id, assignment_title, description, due_date, file_link
    )


@router.put("/assignments/{assignment_id}", response_model=Assignment)
async def update_assignment(
    assignment_id: int,
    teacher_id: str = Form(...),
    assignment_title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    due_date: Optional[datetime] = Form(None),
    file_link: Optional[str] = Form(None),
):
    verify_teacher_form(teacher_id)
    updates = {}
    if assignment_title:
        updates["assignment_title"] = assignment_title
    if description is not None:
        updates["description"] = description
    if due_date:
        updates["due_date"] = due_date.isoformat()
    if file_link:
        updates["file_path"] = file_link
    return teacher_service.update_assignment(teacher_id, assignment_id, **updates)


@router.delete("/assignments/{assignment_id}")
async def delete_assignment(assignment_id: int, teacher_id: str = Form(...)):
    verify_teacher_form(teacher_id)
    return teacher_service.delete_assignment(teacher_id, assignment_id)


@router.post("/results/upload", response_model=Result)
async def upload_results(
    teacher_id: str = Form(...),
    course_id: int = Form(...),
    assignment_title: str = Form(...),
    student_id: str = Form(...),
    result: Grade = Form(...),
):
    verify_teacher_form(teacher_id)
    from uuid import UUID
    return teacher_service.upload_results_logic(
        teacher_id, course_id, assignment_title, UUID(student_id), result
    )


@router.post("/live-classes/schedule", response_model=LiveClass)
async def schedule_live_class(
    teacher_id: str = Form(...),
    live_class: LiveClassCreate = Form(...),
):
    verify_teacher_form(teacher_id)
    return teacher_service.schedule_live_class_logic(teacher_id, live_class)



@router.get("/feedback/{course_id}", response_model=List[Feedback])
async def review_feedback(
    course_id: int,
    teacher_id: str = Form(...),
):
    verify_teacher_form(teacher_id)
    return teacher_service.review_feedback_logic(teacher_id, course_id)


@router.post("/attendance/upload", response_model=Attendance)
async def upload_attendance(
    teacher_id: str = Form(...),
    course_id: int = Form(...),
    class_date: date = Form(...),
    attendance_link: str = Form(...),
):
    verify_teacher_form(teacher_id)
    return teacher_service.upload_attendance_logic(teacher_id, course_id, class_date, attendance_link)
