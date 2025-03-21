from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.models import User, UserRole, Item as ModelItem
from app.schemas.schemas import Item
from app.auth.rbac import get_user_with_roles

# All authenticated users can access viewer endpoints
all_users = get_user_with_roles([UserRole.VIEWER, UserRole.USER, UserRole.MANAGER, UserRole.ADMIN])

router = APIRouter(
    prefix="/viewer",
    tags=["viewer"],
    dependencies=[Depends(all_users)]
)

@router.get("/items", response_model=List[Item])
def view_items(
    skip: int = 0, 
    limit: int = 100, 
    completed: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(all_users)
):
    """View items with optional filtering - Accessible to all authenticated users"""
    query = db.query(ModelItem)
    
    # Apply filter if completed parameter is provided
    if completed is not None:
        query = query.filter(ModelItem.is_completed == completed)
    
    items = query.offset(skip).limit(limit).all()
    return items

@router.get("/items/{item_id}", response_model=Item)
def view_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(all_users)
):
    """View a specific item - Accessible to all authenticated users"""
    item = db.query(ModelItem).filter(ModelItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/items/search", response_model=List[Item])
def search_items(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(all_users)
):
    """Search items by title or description - Accessible to all authenticated users"""
    items = db.query(ModelItem).filter(
        (ModelItem.title.contains(query)) | (ModelItem.description.contains(query))
    ).all()
    return items 