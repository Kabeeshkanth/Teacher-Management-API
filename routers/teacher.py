from fastapi import APIRouter, Form, Depends, Request
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
    Grade
)
from services import teacher_service
from utils.auth import verify_teacher

router = APIRouter(
    prefix="/teacher",
    tags=["teacher"]
)


@router.post("/materials/upload", response_model=CourseMaterial)
async def upload_lecture_notes(
    request: Request,
    course_id: int = Form(...),
    material_title: str = Form(...),
    file_link: str = Form(...),
    teacher_id: str = Depends(verify_teacher)
):
    """Upload course materials/lecture notes with authentication."""
    return teacher_service.upload_lecture_notes_logic(teacher_id, course_id, material_title, file_link)


@router.post("/assignments/upload", response_model=Assignment)
async def upload_assignment(
    request: Request,
    course_id: int = Form(...),
    assignment_title: str = Form(...),
    description: Optional[str] = Form(None),
    due_date: Optional[datetime] = Form(None),
    file_link: str = Form(...),
    teacher_id: str = Depends(verify_teacher)
):
    """Saves the link/path to an assignment, optional due date allowed."""
    return teacher_service.upload_assignment_logic(
        teacher_id, course_id, assignment_title, description, due_date, file_link
    )



@router.post("/results/upload", response_model=Result)
async def upload_results(
    request: Request,
    course_id: int = Form(...),
    assignment_title: str = Form(...),  # Changed from assignment_id
    student_id: str = Form(...),
    result: Grade = Form(...),
    teacher_id: str = Depends(verify_teacher)
):
    """
    Saves the grade for a student's assignment result.
    Automatically fetches assignment_id from assignment_title and student_name from student_id.
    """
    from uuid import UUID
    return teacher_service.upload_results_logic(
        teacher_id, course_id, assignment_title, UUID(student_id), result
    )


@router.post("/live-classes/schedule", response_model=LiveClass)
async def schedule_live_class(
    request: Request,
    live_class: LiveClassCreate,
    teacher_id: str = Depends(verify_teacher)
):
    """Schedule and share a live class link."""
    return teacher_service.schedule_live_class_logic(teacher_id, live_class)


@router.get("/feedback/{course_id}", response_model=List[Feedback])
async def review_feedback(
    request: Request,
    course_id: int,
    teacher_id: str = Depends(verify_teacher)
):
    """Review feedback given by students for a specific course."""
    return teacher_service.review_feedback_logic(teacher_id, course_id)


@router.post("/attendance/upload", response_model=Attendance)
async def upload_attendance(
    request: Request,
    course_id: int = Form(...),
    class_date: date = Form(...),
    attendance_link: str = Form(...),
    teacher_id: str = Depends(verify_teacher)
):
    """Upload attendance sheet link (Google Drive or Excel sheet link)."""
    return teacher_service.upload_attendance_logic(teacher_id, course_id, class_date, attendance_link)
