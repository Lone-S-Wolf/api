from typing import Optional
from pydantic import BaseModel

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
