from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.question.question_schemas import QuestionResponse

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
