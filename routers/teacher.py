
from fastapi import APIRouter, Form, File, UploadFile
from typing import List, Optional
from datetime import date

from models.schema import (
    CourseMaterial,
    Assignment,
    Result,
    LiveClass,
    Feedback,
    LiveClassCreate,
    TeacherPayment,
    PaymentIssue,
    PaymentIssueCreate,
    Attendance
)
from services import teacher_service

router = APIRouter(
    prefix="/teacher",
    tags=["teacher"]
)


@router.post("/materials/upload", response_model=CourseMaterial)
async def upload_lecture_notes(
    course_id: int = Form(...),
    material_title: str = Form(...),
    file_link: str = Form(...)
):
    return teacher_service.upload_lecture_notes_logic(course_id, material_title, file_link)

@router.post("/assignments/upload", response_model=Assignment)
async def upload_assignment(
    course_id: int = Form(...),
    assignment_title: str = Form(...),
    description: Optional[str] = Form(None),
    file_link: str = Form(...)
):
    """Saves the link to an assignment."""
    return teacher_service.upload_assignment_logic(course_id, assignment_title, description, file_link)

@router.post("/results/upload", response_model=Result)
async def upload_results(
    course_id: int = Form(...),
    assignment_id: int = Form(...),
    description: Optional[str] = Form(None),
    file_link: str = Form(...)
):
    """Saves the link to a results file."""
    return teacher_service.upload_results_logic(course_id, assignment_id, description, file_link)

@router.post("/live-classes/schedule", response_model=LiveClass)
async def schedule_live_class(live_class: LiveClassCreate):
    """Schedule and share a live class link."""
    return teacher_service.schedule_live_class_logic(live_class)

@router.get("/feedback/{course_id}", response_model=List[Feedback])
async def review_feedback(course_id: int):
    """Review feedback given by students for a specific course."""
    return teacher_service.review_feedback_logic(course_id)


@router.get("/payments/{teacher_id}", response_model=List[TeacherPayment]) # Updated response model
async def view_payments(teacher_id: int):
    """View all payments made directly to a specific teacher."""
    return teacher_service.get_payments_for_teacher_logic(teacher_id)

@router.post("/issues/payment", response_model=PaymentIssue)
async def report_payment_issue(issue_data: PaymentIssueCreate):
    """Allows a teacher to report a payment-related issue."""
    return teacher_service.report_payment_issue_logic(issue_data)

@router.post("/attendance/upload", response_model=Attendance)
async def upload_attendance(
    course_id: int = Form(...),
    class_date: date = Form(...),
    file: UploadFile = File(...)
):

    return await teacher_service.upload_attendance_logic(course_id, class_date, file)