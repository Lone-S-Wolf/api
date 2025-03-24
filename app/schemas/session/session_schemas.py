from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

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
