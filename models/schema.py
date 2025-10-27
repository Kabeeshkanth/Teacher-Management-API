from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum
from uuid import UUID


class Grade(Enum):
    A = "A"
    B = "B"
    C = "C"
    FAIL = "FAIL"


class CourseMaterial(BaseModel):
    material_id: int
    course_id: int
    module_id: int  # Added
    material_title: str
    file_path: str
    upload_date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Assignment(BaseModel):
    assignment_id: int
    course_id: int
    module_id: int  # Added
    assignment_title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    file_path: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Module(BaseModel):
    module_id: int
    course_id: int
    teacher_id: UUID
    module_name: str
    module_description: Optional[str] = None


class Result(BaseModel):
    result_id: int
    course_id: int
    assignment_id: int
    assignment_title: str
    student_id: UUID
    student_name: str
    result: Grade


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
    student_id: UUID
    course_id: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Attendance(BaseModel):
    attendance_id: int
    course_id: int
    class_date: date
    attendance_link: str


class Course(BaseModel):
    course_id: int
    course_name: str
    course_description: Optional[str] = None
    course_fee: float
    course_details: Optional[str] = None
    start_date: Optional[date] = None
    teacher_ids: UUID
    course_thumbnail_url: Optional[str] = None
    added_by_admin: Optional[UUID] = None
    stripe_price_id: Optional[str] = None
    stripe_product_id: Optional[str] = None
