from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func, or_

from app.database.database import get_db
from app.models.models import User, Question, Option, UserRole
from app.schemas.schemas import QuestionCreate, QuestionResponse, QuestionUpdate, OptionCreate, OptionUpdate
from app.auth.rbac import get_user_with_roles

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
)

# Permissions
get_faculty_or_admin = get_user_with_roles([UserRole.FACULTY, UserRole.ADMIN])
get_student_or_above = get_user_with_roles([UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION, UserRole.ADMIN])

@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    question_data: QuestionCreate,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new question with options (faculty or admin only)"""
    # Create question
    new_question = Question(
        **question_data.model_dump(exclude={"options"}),
        created_by=current_user.id
    )
    db.add(new_question)
    db.flush()  # Get ID without committing
    
    # Create options
    for option_data in question_data.options:
        new_option = Option(
            **option_data.model_dump(),
            question_id=new_question.id
        )
        db.add(new_option)
    
    db.commit()
    db.refresh(new_question)
    return new_question

@router.get("/", response_model=List[QuestionResponse])
def get_questions(
    skip: int = 0, 
    limit: int = 100,
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Get questions with filtering and pagination (faculty or admin only)"""
    # Base query
    query = db.query(Question)
    
    # Handle permissions:
    # - Admin can see all questions
    # - Faculty can see only their own questions AND public questions from other faculty
    if current_user.role == UserRole.FACULTY:
        query = query.filter(
            or_(
                Question.created_by == current_user.id,  # Their own questions (public or private)
                Question.is_public == True  # Public questions from anyone
            )
        )
    
    # Apply filters
    if subject:
        query = query.filter(Question.subject == subject)
    if difficulty:
        query = query.filter(Question.difficulty_level == difficulty)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Question.question_text.ilike(search_term),
                Question.tags.ilike(search_term)
            )
        )
    
    # Get questions with pagination
    questions = query.offset(skip).limit(limit).all()
    return questions

@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Get a specific question by ID (faculty or admin only)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check permissions:
    # - Admin can access any question
    # - Faculty can access their own questions or public questions
    if current_user.role == UserRole.FACULTY and not question.is_public and question.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to view this question")
    
    return question

@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Update a question (faculty owner or admin only)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if user has permission to update
    if current_user.role != UserRole.ADMIN and question.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this question")
    
    # Update question fields
    for key, value in question_data.model_dump(exclude_unset=True).items():
        setattr(question, key, value)
    
    db.commit()
    db.refresh(question)
    return question

@router.delete("/{question_id}", status_code=status.HTTP_200_OK)
def delete_question(
    question_id: int,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Delete a question and its options (faculty owner or admin only)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if user has permission to delete
    if current_user.role != UserRole.ADMIN and question.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this question")
    
    db.delete(question)  # This should cascade to options
    db.commit()
    
    return {"status": "success", "message": "Question deleted successfully"}

@router.post("/{question_id}/options", status_code=status.HTTP_201_CREATED)
def add_option(
    question_id: int,
    option_data: OptionCreate,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Add a new option to a question (faculty owner or admin only)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if user has permission to update
    if current_user.role != UserRole.ADMIN and question.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this question")
    
    # Create option
    new_option = Option(
        **option_data.model_dump(),
        question_id=question_id
    )
    db.add(new_option)
    db.commit()
    
    return {"status": "success", "message": "Option added successfully"}

@router.put("/{question_id}/options/{option_id}")
def update_option(
    question_id: int,
    option_id: int,
    option_data: OptionUpdate,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Update an option (faculty owner or admin only)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if user has permission to update
    if current_user.role != UserRole.ADMIN and question.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this question")
    
    option = db.query(Option).filter(Option.id == option_id, Option.question_id == question_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
    
    # Update option fields
    for key, value in option_data.model_dump(exclude_unset=True).items():
        setattr(option, key, value)
    
    db.commit()
    
    return {"status": "success", "message": "Option updated successfully"}

@router.delete("/{question_id}/options/{option_id}", status_code=status.HTTP_200_OK)
def delete_option(
    question_id: int,
    option_id: int,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Delete an option (faculty owner or admin only)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if user has permission to delete
    if current_user.role != UserRole.ADMIN and question.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this question")
    
    option = db.query(Option).filter(Option.id == option_id, Option.question_id == question_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
    
    # Ensure question has at least 2 options after deletion
    option_count = db.query(func.count(Option.id)).filter(Option.question_id == question_id).scalar()
    if option_count <= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete option: questions must have at least 2 options"
        )
    
    db.delete(option)
    db.commit()
    
    return {"status": "success", "message": "Option deleted successfully"}