
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class CourseMaterial(BaseModel):
    material_id: int
    course_id: int
    material_title: str
    file_path: str
    upload_date: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Assignment(BaseModel):
    assignment_id: int
    course_id: int
    assignment_title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    file_path: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Result(BaseModel):
    result_id: int
    course_id: int
    assignment_id: int
    submission_id: int
    file_path: str
    description: Optional[str] = None

class LiveClassCreate(BaseModel):
    course_id: int
    title: str
    class_link: str
    start_time: datetime
    end_time: datetime

class LiveClass(LiveClassCreate):
    class_id: int

class Feedback(BaseModel):
    feedback_id: int
    student_id: int
    course_id: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# viewing a teacher payment record
class TeacherPayment(BaseModel):
    payment_id: int
    teacher_id: int
    amount: float
    payment_date: date


class PaymentIssueCreate(BaseModel):
    teacher_id: int
    description: str

# Model for the response after creating a payment issue
class PaymentIssue(PaymentIssueCreate):
    issue_id: int
    status: str
    reported_at: datetime
    resolved_at: Optional[datetime] = None

# Model for the response after uploading attendance
class Attendance(BaseModel):
    attendance_id: int
    course_id: int
    class_date: date
    file_path: str