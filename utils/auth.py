# FILE: Teacher-Management-API/utils/auth.py
from fastapi import Request, HTTPException, status, Depends
# Import the specific client instance from database.py
from .database import supabase
from supabase import Client # For type hinting

async def verify_teacher(request: Request):
    """
    Verify the requester is a valid TEACHER.
    Checks headers injected by the API Gateway (X-User-Id, X-User-Role).
    Falls back to cookies/headers for local dev.
    Returns the teacher's user_id on success.
    """
    if supabase is None:
         raise HTTPException(status_code=500, detail="Supabase client not initialized.")

    user_id = request.headers.get("X-User-Id")
    role = request.headers.get("X-User-Role")

    if not user_id: # Fallback
        user_id = request.cookies.get("user_id") or request.headers.get("user_id")
    if not role: # Fallback
        role = request.cookies.get("role") or request.headers.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user_id")

    # --- Role Check: ONLY allow teachers ---
    if role != "teacher":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Access denied: Teacher role required. Received role: {role}")

    # --- Check if user exists in the teachers table ---
    table = "teachers"
    try:
        res = supabase.table(table).select("id").eq("id", user_id).execute()
        if not res.data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Teacher User ID {user_id} not found in {table} table.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error checking user: {str(e)}")

    # Return just the user_id (as expected by original router code)
    return user_id

# --- Helper function used by services ---
# Keep this if your services already use it
def verify_teacher_exists(teacher_id: str) -> None:
    if supabase is None:
         raise HTTPException(status_code=500, detail="Supabase client not initialized.")
    resp = supabase.table("teachers").select("id").eq("id", teacher_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error verifying teacher")
    if not resp.data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher not found")

# --- Helper function used by services ---
# Keep this if your services already use it
def verify_teacher_course_access(teacher_id: str, course_id: int) -> None:
     if supabase is None:
         raise HTTPException(status_code=500, detail="Supabase client not initialized.")
     verify_teacher_exists(teacher_id) # First check teacher exists
     # Then check course exists (ownership check was removed in original code)
     resp = supabase.table("course").select("course_id").eq("course_id", course_id).execute()
     if getattr(resp, "error", None):
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error checking course")
     if not resp.data:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")