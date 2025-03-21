from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.models import User, UserRole, Item as ModelItem
from app.schemas.schemas import Item, ItemCreate, ItemUpdate
from app.auth.rbac import get_user_with_roles

# Regular users, managers, and admins can access these endpoints
regular_users = get_user_with_roles([UserRole.USER, UserRole.MANAGER, UserRole.ADMIN])

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(regular_users)]
)

@router.post("/items", response_model=Item)
def create_user_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(regular_users)
):
    """Create a new item - Regular user, Manager, Admin"""
    db_item = ModelItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/items/{item_id}", response_model=Item)
def update_user_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(regular_users)
):
    """Update an item - Regular user, Manager, Admin"""
    db_item = db.query(ModelItem).filter(ModelItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update only provided fields
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/items/{item_id}/toggle-completion", response_model=Item)
def toggle_item_completion(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(regular_users)
):
    """Toggle an item's completion status - Regular user, Manager, Admin"""
    db_item = db.query(ModelItem).filter(ModelItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Toggle is_completed
    db_item.is_completed = not db_item.is_completed
    
    db.commit()
    db.refresh(db_item)
    return db_item 