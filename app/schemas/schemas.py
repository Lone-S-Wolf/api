from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Union
from enum import Enum

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


# Question type enum for schema validation
class QuestionType(str, Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"

# Test schemas
class TestBase(BaseModel):
    title: str
    description: Optional[str] = None
    total_marks: int = Field(..., gt=0)
    duration_minutes: int = Field(..., gt=0)

class TestCreate(TestBase):
    pass

class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_marks: Optional[int] = Field(None, gt=0)
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

class TestResponse(TestBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    question_count: Optional[int] = None
    
    class Config:
        from_attributes = True

# Question schemas
class OptionBase(BaseModel):
    option_text: str
    is_correct: bool = False

class OptionCreate(OptionBase):
    pass

class OptionResponse(OptionBase):
    id: int
    
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    question_text: str
    question_type: QuestionType = QuestionType.SINGLE
    marks: float = 1.0

class QuestionCreate(QuestionBase):
    options: List[OptionCreate]

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    marks: Optional[float] = None

class QuestionResponse(QuestionBase):
    id: int
    test_id: int
    options: List[OptionResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Test session schemas
class UserResponseCreate(BaseModel):
    question_id: int
    selected_option_id: int

class UserResponseResponse(BaseModel):
    id: int
    question_id: int
    selected_option_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TestSessionBase(BaseModel):
    test_id: int

class TestSessionCreate(TestSessionBase):
    pass

class TestSessionUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    score: Optional[float] = None

class TestSubmission(BaseModel):
    responses: List[UserResponseCreate]

class TestSessionResponse(TestSessionBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    
    class Config:
        from_attributes = True

class TestSessionDetailResponse(TestSessionResponse):
    user_responses: List[UserResponseResponse]
    
    class Config:
        from_attributes = True

class TestResultsSummary(BaseModel):
    test_id: int
    test_title: str
    total_marks: int
    score: float
    percentage: float
    completed_at: datetime
    duration_minutes: int
    question_count: int
    correct_answers: int