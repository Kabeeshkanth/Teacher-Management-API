from datetime import date
from fastapi import UploadFile, HTTPException
from models.schema import Attendance
from utils.database import supabase
import logging

logger = logging.getLogger(__name__)


async def upload_attendance_logic(course_id: int, class_date: date, file: UploadFile) -> Attendance:
    try:
        contents = await file.read()
        file_path_in_bucket = f"{course_id}/{class_date.isoformat()}_{file.filename}"
        bucket = "attendance_files"

        # Upload file (removed upsert parameter)
        logger.info(f"Uploading file to bucket '{bucket}' at path '{file_path_in_bucket}'")
        upload_response = supabase.storage.from_(bucket).upload(
            file_path_in_bucket,
            contents,
            file_options={"content-type": file.content_type}
        )
        logger.info(f"Upload response: {upload_response}")

        # Get public URL
        public_url_response = supabase.storage.from_(bucket).get_public_url(file_path_in_bucket)
        logger.info(f"Public URL response: {public_url_response}")

        if isinstance(public_url_response, dict):
            public_url = public_url_response.get("publicURL") or public_url_response.get("public_url")
        else:
            public_url = str(public_url_response)

        if not public_url:
            raise HTTPException(status_code=500, detail="Failed to obtain public URL for uploaded file.")

        # Save to database
        logger.info(f"Saving to database: course_id={course_id}, class_date={class_date.isoformat()}, file_path={public_url}")
        db_response = supabase.table("Attendance").insert({
            "course_id": course_id,
            "class_date": class_date.isoformat(),
            "file_path": public_url
        }).execute()

        logger.info(f"Database response: {db_response}")

        if not db_response.data:
            raise HTTPException(status_code=500, detail="Failed to save attendance record to database.")

        return Attendance(**db_response.data[0])

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error in upload_attendance_logic: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload attendance: {str(exc)}"
        )
