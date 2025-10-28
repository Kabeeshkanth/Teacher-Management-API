
from fastapi import FastAPI, Depends # <-- Add Depends
from routers import teacher
from utils.auth import verify_teacher

app = FastAPI(
    title="Teacher Management API",
    description="API for managing teacher-related tasks in the Learning Management System.",
    version="1.0.0"
)

app.include_router(teacher.router, dependencies=[Depends(verify_teacher)])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Teacher Management API"}

