from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base

class TestSession(Base):
    __tablename__ = "test_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    score = Column(Float)
    shuffle_seed = Column(Integer)  # For reproducible random shuffling
    
    # Relationships
    user = relationship("User", back_populates="test_sessions")
    test = relationship("Test", back_populates="test_sessions")
    user_responses = relationship("UserResponse", back_populates="test_session", cascade="all, delete-orphan")
    option_orders = relationship("OptionOrder", back_populates="test_session", cascade="all, delete-orphan")
