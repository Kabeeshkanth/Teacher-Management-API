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
    print(f"SERVICE: Inserting lecture note link '{file_link}' into Supabase.")
    response = supabase.table("Course_Materials").insert({
        "course_id": course_id,
        "material_title": material_title,
        "file_path": file_link
    }).execute()
    created_record = response.data[0]
    return CourseMaterial(**created_record)


def upload_assignment_logic(course_id: int, assignment_title: str, description: Optional[str],
                            file_link: str) -> Assignment:
    print(f"SERVICE: Inserting assignment link '{file_link}' into Supabase.")
    response = supabase.table("Assignments").insert({
        "course_id": course_id,
        "assignment_title": assignment_title,
        "description": description,
        "file_path": file_link
    }).execute()
    created_record = response.data[0]
    return Assignment(**created_record)
"""."""

def upload_results_logic(course_id: int, assignment_id: int, description: Optional[str], file_link: str) -> Result:
    """Saves results file link to the database."""
    print(f"SERVICE: Inserting results link '{file_link}' into Supabase.")
    response = supabase.table("results").insert({
        "course_id": course_id,
        "assignment_id": assignment_id,
        "submission_id": 1,  # Placeholder
        "file_path": file_link,
        "description": description
    }).execute()
    created_record = response.data[0]
    return Result(**created_record)


def schedule_live_class_logic(live_class: LiveClassCreate) -> LiveClass:
    print(f"SERVICE: Inserting live class '{live_class.title}' into Supabase.")
    data_to_insert = {
        "course_id": live_class.course_id,
        "title": live_class.title,
        "class_link": live_class.class_link,
        "start_time": live_class.start_time.isoformat(),
        "end_time": live_class.end_time.isoformat()
    }
    response = supabase.table("Live_Classes").insert(data_to_insert).execute()
    if not response.data:
        raise Exception("Failed to insert data into Supabase.")
    created_record = response.data[0]
    return LiveClass(**created_record)


def review_feedback_logic(course_id: int) -> List[Feedback]:
    print(f"SERVICE: Fetching feedback for course {course_id} from Supabase.")
    response = supabase.table("Feedback").select("*").eq("course_id", course_id).execute()
    if response.data:
        return [Feedback(**item) for item in response.data]
    return []


def get_payments_for_teacher_logic(teacher_id: int) -> List[TeacherPayment]:
    print(f"SERVICE: Fetching payments for teacher {teacher_id}.")

    # New simplified logic: Query the Teacher_Payments table directly
    response = supabase.table("Teacher_Payments").select("*").eq("teacher_id", teacher_id).execute()

    if response.data:
        return [TeacherPayment(**item) for item in response.data]
    return []


def report_payment_issue_logic(issue_data: PaymentIssueCreate) -> PaymentIssue:
    print(f"SERVICE: Teacher {issue_data.teacher_id} reporting payment issue.")

    response = supabase.table("Payment_Issues").insert(issue_data.dict()).execute()

    if not response.data:
        raise Exception("Failed to report payment issue.")

    created_record = response.data[0]
    return PaymentIssue(**created_record)


async def upload_attendance_logic(course_id: int, class_date: date, file: UploadFile) -> Attendance:
    print(f"SERVICE: Uploading attendance for course {course_id} on {class_date}.")

    contents = await file.read()

    file_path_in_bucket = f"{course_id}/{class_date.isoformat()}_{file.filename}"

    try:
        supabase.storage.from_("attendance_files").upload(
            path=file_path_in_bucket,
            file=contents,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        if "Duplicate" in str(e):
            print(f"File already exists, updating it: {file_path_in_bucket}")
            supabase.storage.from_("attendance_files").update(
                path=file_path_in_bucket,
                file=contents,
                file_options={"content-type": file.content_type}
            )
        else:
            raise e

    public_url_response = supabase.storage.from_("attendance_files").get_public_url(file_path_in_bucket)

    db_response = supabase.table("Attendance").insert({
        "course_id": course_id,
        "class_date": class_date.isoformat(),
        "file_path": public_url_response
    }).execute()

    if not db_response.data:
        raise Exception("Failed to save attendance record to the database.")

    created_record = db_response.data[0]
    return Attendance(**created_record)