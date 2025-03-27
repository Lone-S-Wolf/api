# app/models/user/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import timezone

from app.database.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    INSTITUTION = "institution"
    FACULTY = "faculty"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.FACULTY)
    is_active = Column(Boolean, default=True)
    
    # Simplified UTC timestamp creation
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.current_timestamp()
    )
    
    # Relationships
    created_questions = relationship("Question", back_populates="creator")
    created_tests = relationship("Test", back_populates="creator")
    test_sessions = relationship("TestSession", back_populates="user")