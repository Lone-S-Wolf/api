from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.models import Question as ModelQuestion, User, UserRole
from app.schemas.schemas import Question, QuestionCreate, QuestionUpdate
from app.auth.rbac import get_user_with_roles, get_admin_user

# Only managers and admins can access these endpoints
manager_users = get_user_with_roles([UserRole.MANAGER, UserRole.ADMIN])

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
    dependencies=[Depends(manager_users)]  # Base authentication for all endpoints
)

@router.post("/", response_model=Question, status_code=status.HTTP_201_CREATED)
def create_question(
    question: QuestionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_users)
):
    """Create a new question - Manager and Admin only"""
    db_question = ModelQuestion(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@router.get("/", response_model=List[Question])
def read_questions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_users)
):
    """Get all questions - Manager and Admin only"""
    questions = db.query(ModelQuestion).offset(skip).limit(limit).all()
    return questions

@router.get("/{question_id}", response_model=Question)
def read_question(
    question_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_users)
):
    """Get a specific question by ID - Manager and Admin only"""
    db_question = db.query(ModelQuestion).filter(ModelQuestion.id == question_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@router.put("/{question_id}", response_model=Question)
def update_question(
    question_id: int, 
    question: QuestionUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_users)
):
    """Update a question - Manager and Admin only"""
    db_question = db.query(ModelQuestion).filter(ModelQuestion.id == question_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Update only provided fields
    update_data = question.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_question, key, value)
    
    db.commit()
    db.refresh(db_question)
    return db_question

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Only admins can delete questions
):
    """Delete a question - Admin only"""
    db_question = db.query(ModelQuestion).filter(ModelQuestion.id == question_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(db_question)
    db.commit()
    return None

@router.put("/{question_id}/toggle-active", response_model=Question)
def toggle_question_active(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_users)
):
    """Toggle the active status of a question - Manager and Admin only"""
    db_question = db.query(ModelQuestion).filter(ModelQuestion.id == question_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db_question.is_active = not db_question.is_active
    db.commit()
    db.refresh(db_question)
    return db_question