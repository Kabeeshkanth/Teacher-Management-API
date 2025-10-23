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
