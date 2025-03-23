from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List, Union, Dict
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

# Option schemas
class OptionBase(BaseModel):
    option_text: str
    is_correct: bool = False

class OptionCreate(OptionBase):
    pass

class OptionUpdate(BaseModel):
    option_text: Optional[str] = None
    is_correct: Optional[bool] = None

class OptionResponse(OptionBase):
    id: int
    
    class Config:
        from_attributes = True

# Question schemas
class QuestionBase(BaseModel):
    question_text: str
    question_type: QuestionType = QuestionType.SINGLE
    subject: Optional[str] = None
    difficulty_level: Optional[str] = None
    tags: Optional[str] = None
    explanation: Optional[str] = None
    is_public: bool = False

class QuestionCreate(QuestionBase):
    options: List[OptionCreate]
    
    @field_validator('options')
    def validate_options(cls, v, values):
        # Ensure there are at least 2 options
        if len(v) < 2:
            raise ValueError("At least 2 options are required")
        
        # For single choice questions, ensure exactly one is correct
        if values.get('question_type') == QuestionType.SINGLE:
            correct_count = sum(1 for option in v if option.is_correct)
            if correct_count != 1:
                raise ValueError("Single choice questions must have exactly one correct answer")
        
        # For multiple choice questions, ensure at least one is correct
        elif values.get('question_type') == QuestionType.MULTIPLE:
            correct_count = sum(1 for option in v if option.is_correct)
            if correct_count < 1:
                raise ValueError("Multiple choice questions must have at least one correct answer")
        
        return v

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    subject: Optional[str] = None
    difficulty_level: Optional[str] = None
    tags: Optional[str] = None
    explanation: Optional[str] = None
    is_public: Optional[bool] = None

class QuestionResponse(QuestionBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    options: List[OptionResponse]
    
    class Config:
        from_attributes = True

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

class TestQuestionAdd(BaseModel):
    question_id: int
    marks: float = 1.0
    question_order: Optional[int] = None

class TestQuestionUpdate(BaseModel):
    marks: Optional[float] = None
    question_order: Optional[int] = None

class TestQuestionResponse(BaseModel):
    question_id: int
    marks: float
    question_order: int
    question: QuestionResponse
    
    class Config:
        from_attributes = True

class TestResponse(TestBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    question_count: Optional[int] = None
    
    class Config:
        from_attributes = True

class TestDetailResponse(TestResponse):
    questions: List[TestQuestionResponse] = []
    
    class Config:
        from_attributes = True

# Test session schemas
class TestSessionBase(BaseModel):
    test_id: int

class TestSessionCreate(TestSessionBase):
    pass

class OptionOrderResponse(BaseModel):
    question_id: int
    option_id: int
    display_order: int
    
    class Config:
        from_attributes = True

class TestSessionWithOptions(TestSessionBase):
    id: int
    user_id: int
    started_at: datetime
    option_orders: List[OptionOrderResponse]
    
    class Config:
        from_attributes = True

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