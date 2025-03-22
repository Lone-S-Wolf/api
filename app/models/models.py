from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

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
    role = Column(String, default=UserRole.FACULTY)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    created_questions = relationship("Question", back_populates="creator")
    created_tests = relationship("Test", back_populates="creator")
    test_sessions = relationship("TestSession", back_populates="user")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
    tests = relationship("Test", secondary=test_questions, back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    user_responses = relationship("UserResponse", back_populates="question")

class Option(Base):
    __tablename__ = "options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)
    
    # Relationships
    question = relationship("Question", back_populates="options")
    user_responses = relationship("UserResponse", back_populates="selected_option")

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

class UserResponse(Base):
    __tablename__ = "user_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("options.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    test_session = relationship("TestSession", back_populates="user_responses")
    question = relationship("Question", back_populates="user_responses")
    selected_option = relationship("Option", back_populates="user_responses")

# New model for tracking shuffled option order for each test session
class OptionOrder(Base):
    __tablename__ = "option_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("options.id"), nullable=False)
    display_order = Column(Integer, nullable=False)
    
    # Relationships
    test_session = relationship("TestSession", back_populates="option_orders")