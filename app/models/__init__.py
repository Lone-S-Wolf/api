# Import all models to make them discoverable by SQLAlchemy
from app.database.database import Base  # Import Base directly
from app.models.user import User, UserRole
from app.models.common import Item
from app.models.test import Test, test_questions
from app.models.question import Question, QuestionType, Option
from app.models.session import TestSession, UserResponse, OptionOrder

# Export all models
__all__ = [
    # Base class for SQLAlchemy
    "Base",
    
    # User models
    "User", "UserRole",
    
    # Common models
    "Item",
    
    # Test models
    "Test", "test_questions",
    
    # Question models
    "Question", "QuestionType", "Option",
    
    # Session models
    "TestSession", "UserResponse", "OptionOrder"
]