from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.models import User, UserRole, Item as ModelItem
from app.schemas.schemas import UserResponse, Item, ItemCreate
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

@router.get("/items/stats", response_model=dict)
def get_items_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(institution_users)
):
    """Get statistics about items - Institution only"""
    total_items = db.query(ModelItem).count()
    completed_items = db.query(ModelItem).filter(ModelItem.is_completed == True).count()
    incomplete_items = total_items - completed_items
    
    return {
        "total_items": total_items,
        "completed_items": completed_items,
        "incomplete_items": incomplete_items,
        "completion_rate": completed_items / total_items if total_items > 0 else 0
    }

@router.post("/items/bulk", response_model=List[Item])
def create_bulk_items(
    items: List[ItemCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(institution_users)
):
    """Create multiple items at once - Institution only"""
    db_items = []
    for item in items:
        db_item = ModelItem(**item.model_dump())
        db.add(db_item)
        db_items.append(db_item)
    
    db.commit()
    for item in db_items:
        db.refresh(item)
    
    return db_items