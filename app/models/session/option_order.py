from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base

class OptionOrder(Base):
    __tablename__ = "option_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("options.id"), nullable=False)
    display_order = Column(Integer, nullable=False)
    
    # Relationships
    test_session = relationship("TestSession", back_populates="option_orders")
