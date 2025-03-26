from fastapi import FastAPI
from app.routers import auth, admin, institution, faculty, student, test, test_questions, test_sessions, questions
from app.models import Base  # Updated import for Base
from app.database.database import engine
import sqlalchemy.exc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="FastAPI CRUD with Advanced RBAC",
    description="A FastAPI CRUD application with PostgreSQL, authentication, and advanced role-based access control",
    version="0.4.0",
    debug=os.getenv("DEBUG", "False").lower() == "true"
)

# Try to create tables, but handle potential database connection errors
try:
    # Drop all tables and recreate them
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except sqlalchemy.exc.OperationalError:
    print("Could not connect to the database. Please check your connection settings.")
    print("The application will continue to run, but database operations may fail.")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(institution.router)
app.include_router(faculty.router)
app.include_router(student.router)

# Questions
app.include_router(questions.router)
app.include_router(test.router)
app.include_router(test_sessions.router)
app.include_router(test_questions.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI CRUD API with Advanced Role-Based Access Control"}