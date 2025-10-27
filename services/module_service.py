# python
# File: services/module_service.py
from typing import Dict, Any, List, Optional
import logging
from fastapi import HTTPException, status
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access
from models.schema import Module

logger = logging.getLogger(__name__)


def create_module_logic(teacher_id: str, course_id: int, module_name: str, module_description: str = None) -> Module:
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()

    data = {
        "course_id": course_id,
        "teacher_id": teacher_id,
        "module_name": module_name,
        "module_description": module_description
    }

    try:
        resp = supabase.table("modules").insert(data).select("*").execute()
        if getattr(resp, "error", None):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create module")
        return Module(**resp.data[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def get_modules_logic(teacher_id: str, course_id: int) -> List[Module]:
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()

    try:
        resp = supabase.table("modules").select("*").eq("course_id", course_id).eq("teacher_id", teacher_id).execute()
        if getattr(resp, "error", None):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch modules")
        return [Module(**item) for item in resp.data or []]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def get_module_by_id(module_id: int) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    resp = supabase.table("modules").select("*").eq("module_id", module_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB error fetching module")
    return (resp.data or [None])[0]


def verify_module_owner(module_id: int, teacher_id: str) -> Dict[str, Any]:
    """
    Ensure the module exists and belongs to the teacher. Returns module row.
    """
    module = get_module_by_id(module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    if module.get("teacher_id") != teacher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to module")
    return module


def update_module_logic(teacher_id: str, module_id: int, module_name: str = None, module_description: str = None) -> Module:
    supabase = get_supabase_client()
    module = verify_module_owner(module_id, teacher_id)
    course_id = module["course_id"]
    verify_teacher_course_access(teacher_id, course_id)

    updates = {}
    if module_name: updates["module_name"] = module_name
    if module_description is not None: updates["module_description"] = module_description

    try:
        resp = supabase.table("modules").update(updates).eq("module_id", module_id).select("*").execute()
        if getattr(resp, "error", None):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update module")
        return Module(**resp.data[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def delete_module_logic(teacher_id: str, module_id: int) -> None:
    supabase = get_supabase_client()
    module = verify_module_owner(module_id, teacher_id)
    course_id = module["course_id"]
    verify_teacher_course_access(teacher_id, course_id)

    try:
        resp = supabase.table("modules").delete().eq("module_id", module_id).execute()
        if getattr(resp, "error", None):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete module")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
