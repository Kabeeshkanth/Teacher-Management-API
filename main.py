
from fastapi import FastAPI
from routers import teacher

app = FastAPI(
    title="Teacher Management API",
    description="API for managing teacher-related tasks in the Learning Management System.",
    version="1.0.0"
)

# Include the teacher router with absolute import
app.include_router(teacher.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Teacher Management API"}