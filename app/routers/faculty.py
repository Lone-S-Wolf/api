from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User, UserRole
from app.auth.rbac import get_user_with_roles

# Faculty, institution, and admins can access these endpoints
faculty_users = get_user_with_roles([UserRole.FACULTY, UserRole.INSTITUTION, UserRole.ADMIN])

router = APIRouter(
    prefix="/faculty",
    tags=["faculty"],
    dependencies=[Depends(faculty_users)]
)

