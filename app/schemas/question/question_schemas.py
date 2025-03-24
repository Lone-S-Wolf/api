from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, field_validator

from app.schemas.question.option_schemas import OptionCreate, OptionResponse

# Question type enum for schema validation
class QuestionType(str, Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"

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
    def validate_options(cls, v, info):
        # Ensure there are at least 4 options
        if len(v) < 4:
            raise ValueError("At least 4 options are required")
        
        # Access question_type from info.data instead of values.get()
        question_type = info.data.get('question_type')
        
        # For single choice questions, ensure exactly one is correct
        if question_type == QuestionType.SINGLE:
            correct_count = sum(1 for option in v if option.is_correct)
            if correct_count != 1:
                raise ValueError("Single choice questions must have exactly one correct answer")
        
        # For multiple choice questions, ensure at least one is correct
        elif question_type == QuestionType.MULTIPLE:
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
