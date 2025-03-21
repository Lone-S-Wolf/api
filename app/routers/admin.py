from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.models import User, UserRole, Item as ModelItem
from app.schemas.schemas import UserResponse, Item
from app.auth.rbac import get_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_admin_user)]
)

@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """List all users - Admin only"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/by-role/{role}", response_model=List[UserResponse])
def list_users_by_role(
    role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """List users by role - Admin only"""
    users = db.query(User).filter(User.role == role).all()
    return users

@router.put("/users/{user_id}/toggle-active", response_model=UserResponse)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Toggle user active status - Admin only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deactivating yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user

@router.put("/users/{user_id}/set-role", response_model=UserResponse)
def set_user_role(
    user_id: int, 
    role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Change user role - Admin only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow changing your own role
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    user.role = role
    db.commit()
    db.refresh(user)
    return user

@router.delete("/items/all", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete all items - Admin only"""
    db.query(ModelItem).delete()
    db.commit()
    return None

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a specific item - Admin only"""
    db_item = db.query(ModelItem).filter(ModelItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return None 