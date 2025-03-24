from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr

# Role enum for schema validation
class UserRole(str, Enum):
    ADMIN = "admin"
    INSTITUTION = "institution"
    FACULTY = "faculty"
    STUDENT = "student"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.FACULTY

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
