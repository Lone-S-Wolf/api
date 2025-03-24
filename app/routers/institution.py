from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User, UserRole
from app.schemas.schemas import UserResponse
from app.auth.rbac import get_user_with_roles

# Only institutions and admins can access these endpoints
institution_users = get_user_with_roles([UserRole.INSTITUTION, UserRole.ADMIN])

router = APIRouter(
    prefix="/institution",
    tags=["institution"],
    dependencies=[Depends(institution_users)]
)

@router.get("/users", response_model=List[UserResponse])
def list_faculty_students(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(institution_users)
):
    """List faculty and student users (no institutions or admins) - Institution only"""
    users = db.query(User).filter(
        User.role.in_([UserRole.FACULTY, UserRole.STUDENT])
    ).offset(skip).limit(limit).all()
    return users

