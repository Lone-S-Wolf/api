from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User, UserRole
from app.auth.rbac import get_user_with_roles

# All authenticated users can access student endpoints
all_users = get_user_with_roles([UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION, UserRole.ADMIN])

router = APIRouter(
    prefix="/student",
    tags=["student"],
    dependencies=[Depends(all_users)]
)
