from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base

# Join table for many-to-many relationship between tests and questions
test_questions = Table(
    "test_questions",
    Base.metadata,
    Column("test_id", Integer, ForeignKey("tests.id"), primary_key=True),
    Column("question_id", Integer, ForeignKey("questions.id"), primary_key=True),
    Column("question_order", Integer),
    Column("marks", Float, default=1.0),
)

class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    total_marks = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_tests")
    questions = relationship("Question", secondary=test_questions, back_populates="tests")
    test_sessions = relationship("TestSession", back_populates="test")
