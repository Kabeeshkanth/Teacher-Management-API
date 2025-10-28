# FILE: Teacher-Management-API/routers/teacher.py

# --- Imports ---
from fastapi import APIRouter, Depends, Form, Request, UploadFile, HTTPException
from typing import List, Optional, Dict, Any
from models.schema import Module, CourseMaterial, Assignment, Grade # Added Grade
from datetime import datetime, date # Added date
from uuid import UUID
from utils.auth import verify_teacher # Use the function from your auth utils

# +++ Import ALL service functions needed by this router HERE +++
from services.module_service import (
    create_module_logic,
    get_modules_logic,
    update_module_logic,
    delete_module_logic
)
from services.course_service import get_teacher_courses_logic
from services.materials_service import (
    get_materials_by_module_logic,
    get_material_by_title_logic,
    update_material_logic,
    delete_material_logic,
    upload_lecture_notes_logic
)
from services.assignments_service import (
    get_assignments_by_module_logic,
    upload_assignment_logic
    # Note: No update/delete assignment logic imported, assuming not needed based on original router
)
# Import services needed for additional routes (add if missing)
# from services.results_service import upload_results_logic # Add if you implement result upload
# from services.attendance_service import upload_attendance_logic # Add if you implement attendance upload
# from services.feedback_service import review_feedback_logic # Add if you implement feedback review
# from services.liveclass_service import schedule_live_class_logic # Add if you implement scheduling

# +++ End service imports +++
# --- End Imports ---

# --- Create the router instance ---
router = APIRouter(
    # No prefix needed here if gateway maps to root
    tags=["Teacher Management"],
    # Apply auth dependency to all routes in this router
    dependencies=[Depends(verify_teacher)]
)
# --- End router creation ---

# --- Define your routes ---

# === Module Management Endpoints ===
@router.post("/modules/create", response_model=Module)
async def create_module(
    course_id: int = Form(...),
    module_name: str = Form(...),
    module_description: Optional[str] = Form(None),
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Create a new module for a course."""
    return create_module_logic(teacher_id, course_id, module_name, module_description)

@router.get("/modules/{course_id}", response_model=List[Module])
async def get_modules(
    course_id: int,
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Get all modules for a specific course taught by the teacher."""
    return get_modules_logic(teacher_id, course_id)

@router.put("/modules/{module_id}", response_model=Module)
async def update_module(
    module_id: int,
    module_name: Optional[str] = Form(None),
    module_description: Optional[str] = Form(None),
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Update a module owned by the teacher."""
    return update_module_logic(teacher_id, module_id, module_name, module_description)

@router.delete("/modules/{module_id}")
async def delete_module(
    module_id: int,
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Delete a module owned by the teacher."""
    delete_module_logic(teacher_id, module_id)
    return {"message": "Module deleted successfully"}

# === Course Listing ===
@router.get("/courses", response_model=List[dict])
async def get_teacher_courses(
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Get all courses assigned to the teacher."""
    return get_teacher_courses_logic(teacher_id)

# === Materials Management ===
@router.post("/materials/upload", response_model=CourseMaterial)
async def upload_lecture_notes(
    course_id: int = Form(...),
    material_title: str = Form(...),
    file_link: str = Form(...), # Assuming file is uploaded elsewhere and link is provided
    module_id: Optional[int] = Form(None),
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Upload course materials/lecture notes, optionally linking to a module."""
    return upload_lecture_notes_logic(teacher_id, course_id, material_title, file_link, module_id)

@router.get("/materials/module/{module_id}", response_model=List[CourseMaterial])
async def get_materials_by_module(
    module_id: int,
    course_id: int, # Needed for verification
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Get all materials for a specific module verified for the teacher and course."""
    return get_materials_by_module_logic(teacher_id, course_id, module_id)

@router.get("/materials/title/{course_id}/{material_title}", response_model=CourseMaterial)
async def get_material_by_title(
    course_id: int,
    material_title: str,
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Get a specific material by title for a course verified for the teacher."""
    return get_material_by_title_logic(teacher_id, course_id, material_title)

@router.put("/materials/{material_id}", response_model=CourseMaterial)
async def update_material(
    material_id: int,
    material_title: Optional[str] = Form(None),
    file_link: Optional[str] = Form(None),
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Update a course material, verifying teacher access."""
    return update_material_logic(teacher_id, material_id, material_title, file_link)

@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int,
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Delete a course material, verifying teacher access."""
    delete_material_logic(teacher_id, material_id)
    return {"message": "Material deleted successfully"}

# === Assignment Management ===
@router.post("/assignments/upload", response_model=Assignment)
async def upload_assignment(
    course_id: int = Form(...),
    assignment_title: str = Form(...),
    file_link: str = Form(...), # Assuming file uploaded elsewhere
    description: Optional[str] = Form(None),
    due_date: Optional[datetime] = Form(None),
    module_id: Optional[int] = Form(None),
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Upload assignment, optionally linking to a module."""
    return upload_assignment_logic(
        teacher_id, course_id, assignment_title, description, due_date, file_link, module_id
    )

@router.get("/assignments/module/{module_id}", response_model=List[Assignment])
async def get_assignments_by_module(
    module_id: int,
    course_id: int, # Needed for verification
    teacher_id: str = Depends(verify_teacher) # Injected teacher_id
):
    """Get all assignments for a specific module verified for the teacher and course."""
    return get_assignments_by_module_logic(teacher_id, course_id, module_id)

# === Add other teacher-specific routes here if needed ===
# e.g., Uploading Results, Scheduling Live Classes, Reviewing Feedback, Uploading Attendance