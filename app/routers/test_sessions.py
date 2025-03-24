# app/routers/test_sessions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
import random

from app.database.database import get_db
from app.models.user import User, UserRole
from app.models.test import Test, test_questions
from app.models.question import Question, Option
from app.models.session import TestSession, UserResponse, OptionOrder
from app.schemas.schemas import (
    TestSessionCreate, TestSessionResponse, TestSessionDetailResponse,
    UserResponseCreate, TestSubmission, TestResultsSummary, TestSessionWithOptions
)
from app.auth.rbac import get_user_with_roles

router = APIRouter(
    prefix="/test-sessions",
    tags=["test-sessions"],
)

# Permissions
get_student_or_above = get_user_with_roles([UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION, UserRole.ADMIN])

@router.post("/", response_model=TestSessionWithOptions, status_code=status.HTTP_201_CREATED)
def start_test_session(
    session_data: TestSessionCreate,
    current_user: User = Depends(get_student_or_above),
    db: Session = Depends(get_db)
):
    """Start a new test session for a student"""
    # Verify the test exists and is active
    test = db.query(Test).filter(Test.id == session_data.test_id, Test.is_active == True).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found or not active")
    
    # Check if user already has an active session for this test
    existing_session = db.query(TestSession).filter(
        TestSession.user_id == current_user.id,
        TestSession.test_id == session_data.test_id,
        TestSession.completed_at.is_(None)
    ).first()
    
    if existing_session:
        # Return the existing session
        return existing_session
    
    # Generate a random seed for reproducible shuffling
    shuffle_seed = random.randint(1, 1000000)
    
    # Create a new test session
    new_session = TestSession(
        user_id=current_user.id,
        test_id=session_data.test_id,
        shuffle_seed=shuffle_seed
    )
    db.add(new_session)
    db.flush()
    
    # Get all questions for this test including their order and marks
    questions_query = db.query(
        Question, test_questions.c.question_order, test_questions.c.marks
    ).join(
        test_questions, Question.id == test_questions.c.question_id
    ).filter(
        test_questions.c.test_id == session_data.test_id
    ).order_by(
        test_questions.c.question_order
    ).all()
    
    # Shuffle and store option orders for each question
    random_generator = random.Random(shuffle_seed)  # Use seed for reproducible shuffling
    
    for question_data in questions_query:
        question, _, _ = question_data
        
        # Get all options for this question
        options = db.query(Option).filter(Option.question_id == question.id).all()
        
        # Create a shuffled order of options
        option_ids = [option.id for option in options]
        random_generator.shuffle(option_ids)
        
        # Store the shuffled order
        for display_order, option_id in enumerate(option_ids):
            option_order = OptionOrder(
                test_session_id=new_session.id,
                question_id=question.id,
                option_id=option_id,
                display_order=display_order
            )
            db.add(option_order)
    
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/active", response_model=List[TestSessionResponse])
def get_user_active_sessions(
    current_user: User = Depends(get_student_or_above),
    db: Session = Depends(get_db)
):
    """Get all active (incomplete) test sessions for the current user"""
    sessions = db.query(TestSession).filter(
        TestSession.user_id == current_user.id,
        TestSession.completed_at.is_(None)
    ).all()
    return sessions

@router.get("/{session_id}", response_model=TestSessionWithOptions)
def get_test_session(
    session_id: int,
    current_user: User = Depends(get_student_or_above),
    db: Session = Depends(get_db)
):
    """Get a specific test session with shuffled options"""
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    # Check permissions - only owner or admin can access
    if current_user.id != session.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You don't have permission to view this test session")
    
    # If test is already completed, don't show options
    if session.completed_at:
        raise HTTPException(status_code=400, detail="Test session is already completed")
    
    return session

@router.post("/{session_id}/submit", response_model=TestResultsSummary)
def submit_test(
    session_id: int,
    submission: TestSubmission,
    current_user: User = Depends(get_student_or_above),
    db: Session = Depends(get_db)
):
    """Submit answers for a test session and get results"""
    # Get the test session
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    # Check if this is the user's session
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only submit your own test session")
    
    # Check if session is already completed
    if session.completed_at:
        raise HTTPException(status_code=400, detail="Test already submitted")
    
    # Get the test
    test = db.query(Test).filter(Test.id == session.test_id).first()
    
    # Process responses
    total_score = 0
    correct_count = 0
    
    # Get all test questions
    test_question_data = db.query(
        Question, test_questions.c.marks
    ).join(
        test_questions, Question.id == test_questions.c.question_id
    ).filter(
        test_questions.c.test_id == session.test_id
    ).all()
    
    # Create a dictionary for easy access to question marks
    question_marks = {q.id: marks for q, marks in test_question_data}
    
    # Add user responses and calculate score
    for response in submission.responses:
        # Verify this question belongs to the test
        if response.question_id not in question_marks:
            continue
        
        # Create user response
        user_response = UserResponse(
            test_session_id=session.id,
            question_id=response.question_id,
            selected_option_id=response.selected_option_id
        )
        db.add(user_response)
        
        # Check if answer is correct
        option = db.query(Option).filter(Option.id == response.selected_option_id).first()
        if option and option.is_correct:
            # Add marks for correct answer
            total_score += question_marks[response.question_id]
            correct_count += 1
    
    # Update session as completed
    session.completed_at = datetime.now()
    session.score = total_score
    
    db.commit()
    
    # Create and return result summary
    result_summary = TestResultsSummary(
        test_id=test.id,
        test_title=test.title,
        total_marks=test.total_marks,
        score=total_score,
        percentage=(total_score / test.total_marks) * 100 if test.total_marks > 0 else 0,
        completed_at=session.completed_at,
        duration_minutes=test.duration_minutes,
        question_count=len(test_question_data),
        correct_answers=correct_count
    )
    
    return result_summary

@router.get("/{session_id}/results", response_model=TestResultsSummary)
def get_test_results(
    session_id: int,
    current_user: User = Depends(get_student_or_above),
    db: Session = Depends(get_db)
):
    """Get results for a completed test session"""
    # Get the test session
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    # Check permissions
    if session.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You don't have permission to view these results")
    
    # Check if session is completed
    if not session.completed_at:
        raise HTTPException(status_code=400, detail="Test is not yet completed")
    
    # Get the test
    test = db.query(Test).filter(Test.id == session.test_id).first()
    
    # Get question count
    question_count = db.query(test_questions).filter(test_questions.c.test_id == test.id).count()
    
    # Get correct answers count
    correct_answers = db.query(UserResponse).join(
        Option, UserResponse.selected_option_id == Option.id
    ).filter(
        UserResponse.test_session_id == session.id,
        Option.is_correct == True
    ).count()
    
    # Create result summary
    result_summary = TestResultsSummary(
        test_id=test.id,
        test_title=test.title,
        total_marks=test.total_marks,
        score=session.score,
        percentage=(session.score / test.total_marks) * 100 if test.total_marks > 0 else 0,
        completed_at=session.completed_at,
        duration_minutes=test.duration_minutes,
        question_count=question_count,
        correct_answers=correct_answers
    )
    
    return result_summary