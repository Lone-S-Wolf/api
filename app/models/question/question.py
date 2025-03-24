from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.database import Base

class QuestionType(str, enum.Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default=QuestionType.SINGLE)
    is_public = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String)
    difficulty_level = Column(String)
    tags = Column(String)
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_questions")
    tests = relationship("Test", secondary="test_questions", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    user_responses = relationship("UserResponse", back_populates="question")
