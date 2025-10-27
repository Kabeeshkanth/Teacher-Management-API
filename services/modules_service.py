from typing import List, Dict, Any, Optional
from uuid import UUID
import logging
from fastapi import HTTPException, status
from utils.database import get_supabase_client
from utils.auth import verify_teacher_course_access
from models.schema import Module

logger = logging.getLogger(__name__)


def get_modules_for_course(teacher_id: str, course_id: int) -> List[Module]:
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()
    resp = supabase.table("modules").select("*").eq("course_id", course_id).eq("teacher_id", teacher_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="Error fetching modules")
    return [Module(**item) for item in resp.data or []]


def create_module(teacher_id: str, course_id: int, module_name: str, module_description: Optional[str]) -> Module:
    verify_teacher_course_access(teacher_id, course_id)
    supabase = get_supabase_client()
    payload = {"course_id": course_id, "teacher_id": teacher_id, "module_name": module_name, "module_description": module_description}
    resp = supabase.table("modules").insert(payload).select("*").execute()
    if getattr(resp, "error", None) or not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create module")
    return Module(**resp.data[0])


def update_module(teacher_id: str, module_id: int, module_name: Optional[str], module_description: Optional[str]) -> Module:
    # Verify ownership via course
    supabase = get_supabase_client()
    module_resp = supabase.table("modules").select("course_id").eq("module_id", module_id).eq("teacher_id", teacher_id).execute()
    if not module_resp.data:
        raise HTTPException(status_code=404, detail="Module not found or not owned")
    course_id = module_resp.data[0]["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    payload = {}
    if module_name:
        payload["module_name"] = module_name
    if module_description is not None:
        payload["module_description"] = module_description
    resp = supabase.table("modules").update(payload).eq("module_id", module_id).select("*").execute()
    if getattr(resp, "error", None) or not resp.data:
        raise HTTPException(status_code=500, detail="Failed to update module")
    return Module(**resp.data[0])


def delete_module(teacher_id: str, module_id: int) -> Dict[str, str]:
    supabase = get_supabase_client()
    module_resp = supabase.table("modules").select("course_id").eq("module_id", module_id).eq("teacher_id", teacher_id).execute()
    if not module_resp.data:
        raise HTTPException(status_code=404, detail="Module not found or not owned")
    course_id = module_resp.data[0]["course_id"]
    verify_teacher_course_access(teacher_id, course_id)
    resp = supabase.table("modules").delete().eq("module_id", module_id).execute()
    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail="Failed to delete module")
    return {"message": "Module deleted"}
