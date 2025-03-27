# app/schemas/user/user_schemas.py
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict

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
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.FACULTY

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    @field_validator('created_at', mode='before')
    @classmethod
    def ensure_utc(cls, v):
        """Ensure created_at is always in UTC"""
        if v is None:
            return None
        
        # If datetime is naive, assume local and convert to UTC
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        
        # If datetime has timezone, convert to UTC
        return v.astimezone(timezone.utc)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None