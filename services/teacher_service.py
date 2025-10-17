
from typing import List, Optional
from datetime import date
from fastapi import UploadFile
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


def upload_assignment_logic(course_id: int, assignment_title: str, description: Optional[str],
                            file_link: str) -> Assignment:
    response = supabase.table("Assignments").insert({
        "course_id": course_id,
        "assignment_title": assignment_title,
        "description": description,
        "file_path": file_link
    }).execute()
    if not response.data:
        raise Exception("Failed to save assignment.")
    return Assignment(**response.data[0])


def upload_results_logic(course_id: int, assignment_id: int, description: Optional[str], file_link: str) -> Result:
    response = supabase.table("results").insert({
        "course_id": course_id,
        "assignment_id": assignment_id,
        "submission_id": 1,  # replace if you have a submissions table
        "file_path": file_link,
        "description": description
    }).execute()
    if not response.data:
        raise Exception("Failed to save result.")
    return Result(**response.data[0])


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


def review_feedback_logic(course_id: int) -> List[Feedback]:
    response = supabase.table("Feedback").select("*").eq("course_id", course_id).execute()
    return [Feedback(**item) for item in (response.data or [])]


def get_payments_for_teacher_logic(teacher_id: int) -> List[TeacherPayment]:
    response = supabase.table("Teacher_Payments").select("*").eq("teacher_id", teacher_id).execute()
    return [TeacherPayment(**item) for item in (response.data or [])]


def report_payment_issue_logic(issue_data: PaymentIssueCreate) -> PaymentIssue:
    response = supabase.table("Payment_Issues").insert(issue_data.dict()).execute()
    if not response.data:
        raise Exception("Failed to report payment issue.")
    return PaymentIssue(**response.data[0])


async def upload_attendance_logic(course_id: int, class_date: date, file: UploadFile) -> Attendance:
    contents = await file.read()
    file_path_in_bucket = f"{course_id}/{class_date.isoformat()}_{file.filename}"
    bucket = "attendance_files"

    # Upload with upsert=True to overwrite if exists (supported by many supabase-py versions)
    try:
        supabase.storage.from_(bucket).upload(file_path_in_bucket, contents, file_options={"content-type": file.content_type}, upsert=True)
    except TypeError:
        # older client signature variant - try without upsert argument
        try:
            supabase.storage.from_(bucket).upload(file_path_in_bucket, contents, file_options={"content-type": file.content_type})
        except Exception as e:
            raise e
    except Exception as e:
        raise e

    # Obtain the public URL and extract the string
    public_url_response = supabase.storage.from_(bucket).get_public_url(file_path_in_bucket)
    public_url = None

    if isinstance(public_url_response, dict):
        public_url = public_url_response.get("publicURL") or public_url_response.get("public_url") or public_url_response.get("publicUrl")
    else:
        # some clients return a string or an object with 'publicURL' attr
        try:
            public_url = getattr(public_url_response, "publicURL", None) or getattr(public_url_response, "public_url", None)
        except Exception:
            public_url = str(public_url_response)

    if not public_url:
        raise Exception("Failed to obtain public URL for uploaded attendance file.")

    db_response = supabase.table("Attendance").insert({
        "course_id": course_id,
        "class_date": class_date.isoformat(),
        "file_path": public_url
    }).execute()

    if not db_response.data:
        raise Exception("Failed to save attendance record to the database.")

    return Attendance(**db_response.data[0])
