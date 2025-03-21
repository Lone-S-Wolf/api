from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

# Role enum for schema validation
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

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

# Question schemas
class QuestionBase(BaseModel):
    title: str
    content: str
    answer: Optional[str] = None
    is_active: bool = True

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    answer: Optional[str] = None
    is_active: Optional[bool] = None

class Question(QuestionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True