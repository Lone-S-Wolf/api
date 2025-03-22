from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.models import Item as ModelItem, User, UserRole
from app.schemas.schemas import Item, ItemCreate, ItemUpdate
from app.auth.utils import get_current_active_user
from app.auth.rbac import get_admin_user, get_user_with_roles

# All users (faculty and admins) can access these endpoints
all_users = get_user_with_roles([UserRole.FACULTY, UserRole.ADMIN])

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_current_active_user)]  # Base authentication for all endpoints
)

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(
    item: ItemCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(all_users)
):
    db_item = ModelItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=List[Item])
def read_items(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(all_users)
):
    items = db.query(ModelItem).offset(skip).limit(limit).all()
    return items

@router.get("/{item_id}", response_model=Item)
def read_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(all_users)
):
    db_item = db.query(ModelItem).filter(ModelItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/{item_id}", response_model=Item)
def update_item(
    item_id: int, 
    item: ItemUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(all_users)
):
    db_item = db.query(ModelItem).filter(ModelItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update only provided fields
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Only admins can delete items
):
    db_item = db.query(ModelItem).filter(ModelItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return None