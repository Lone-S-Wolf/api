from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Item schemas
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class Item(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
