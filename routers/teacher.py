from models.schema import Module

# Module Management Endpoints
@router.post("/modules/create", response_model=Module)
async def create_module(
    request: Request,
    course_id: int = Form(...),
    module_name: str = Form(...),
    module_description: Optional[str] = Form(None),
    teacher_id: str = Depends(verify_teacher)
):
    """Create a new module for a course."""
    from services.module_service import create_module_logic
    return create_module_logic(teacher_id, course_id, module_name, module_description)


@router.get("/modules/{course_id}", response_model=List[Module])
async def get_modules(
    request: Request,
    course_id: int,
    teacher_id: str = Depends(verify_teacher)
):
    """Get all modules for a specific course."""
    from services.module_service import get_modules_logic
    return get_modules_logic(teacher_id, course_id)


@router.put("/modules/{module_id}", response_model=Module)
async def update_module(
    request: Request,
    module_id: int,
    module_name: Optional[str] = Form(None),
    module_description: Optional[str] = Form(None),
    teacher_id: str = Depends(verify_teacher)
):
    """Update a module."""
    from services.module_service import update_module_logic
    return update_module_logic(teacher_id, module_id, module_name, module_description)


@router.delete("/modules/{module_id}")
async def delete_module(
    request: Request,
    module_id: int,
    teacher_id: str = Depends(verify_teacher)
):
    """Delete a module."""
    from services.module_service import delete_module_logic
    delete_module_logic(teacher_id, module_id)
    return {"message": "Module deleted successfully"}


# Get courses assigned to teacher
@router.get("/courses", response_model=List[dict])
async def get_teacher_courses(
    request: Request,
    teacher_id: str = Depends(verify_teacher)
):
    """Get all courses assigned to the teacher."""
    from services.course_service import get_teacher_courses_logic
    return get_teacher_courses_logic(teacher_id)


# Materials by Module
@router.get("/materials/module/{module_id}", response_model=List[CourseMaterial])
async def get_materials_by_module(
    request: Request,
    module_id: int,
    course_id: int,
    teacher_id: str = Depends(verify_teacher)
):
    """Get all materials for a specific module."""
    from services.materials_service import get_materials_by_module_logic
    return get_materials_by_module_logic(teacher_id, course_id, module_id)


@router.get("/materials/title/{course_id}/{material_title}", response_model=CourseMaterial)
async def get_material_by_title(
    request: Request,
    course_id: int,
    material_title: str,
    teacher_id: str = Depends(verify_teacher)
):
    """Get a specific material by title."""
    from services.materials_service import get_material_by_title_logic
    return get_material_by_title_logic(teacher_id, course_id, material_title)


@router.put("/materials/{material_id}", response_model=CourseMaterial)
async def update_material(
    request: Request,
    material_id: int,
    material_title: Optional[str] = Form(None),
    file_link: Optional[str] = Form(None),
    teacher_id: str = Depends(verify_teacher)
):
    """Update a course material."""
    from services.materials_service import update_material_logic
    return update_material_logic(teacher_id, material_id, material_title, file_link)


@router.delete("/materials/{material_id}")
async def delete_material(
    request: Request,
    material_id: int,
    teacher_id: str = Depends(verify_teacher)
):
    """Delete a course material."""
    from services.materials_service import delete_material_logic
    delete_material_logic(teacher_id, material_id)
    return {"message": "Material deleted successfully"}


# Assignments by Module
@router.get("/assignments/module/{module_id}", response_model=List[Assignment])
async def get_assignments_by_module(
    request: Request,
    module_id: int,
    course_id: int,
    teacher_id: str = Depends(verify_teacher)
):
    """Get all assignments for a specific module."""
    from services.assignments_service import get_assignments_by_module_logic
    return get_assignments_by_module_logic(teacher_id, course_id, module_id)


# Update upload endpoints to support module_id
@router.post("/materials/upload", response_model=CourseMaterial)
async def upload_lecture_notes(
    request: Request,
    course_id: int = Form(...),
    material_title: str = Form(...),
    file_link: str = Form(...),
    module_id: Optional[int] = Form(None),
    teacher_id: str = Depends(verify_teacher)
):
    """Upload course materials/lecture notes with optional module assignment."""
    from services.materials_service import upload_lecture_notes_logic
    return upload_lecture_notes_logic(teacher_id, course_id, material_title, file_link, module_id)


@router.post("/assignments/upload", response_model=Assignment)
async def upload_assignment(
    request: Request,
    course_id: int = Form(...),
    assignment_title: str = Form(...),
    file_link: str = Form(...),
    description: Optional[str] = Form(None),
    due_date: Optional[datetime] = Form(None),
    module_id: Optional[int] = Form(None),
    teacher_id: str = Depends(verify_teacher)
):
    """Upload assignment with optional module assignment."""
    from services.assignments_service import upload_assignment_logic
    return upload_assignment_logic(
        teacher_id, course_id, assignment_title, description, due_date, file_link, module_id
    )
