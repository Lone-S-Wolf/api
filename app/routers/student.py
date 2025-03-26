from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User, UserRole
from app.auth.rbac import get_user_with_roles
from app.models.session.test_session import TestSession
from app.models.session.user_response import UserResponse
from app.models.test import Test
from app.models.question.question import Question
from app.schemas.session.session_schemas import (
    TestSubmission, 
    TestResultsSummary, 
    TestSessionResponse, 
    TestSessionCreate
)

from datetime import datetime, timedelta
import random

# All authenticated users can access student endpoints
all_users = get_user_with_roles([UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION, UserRole.ADMIN])

router = APIRouter(
    prefix="/student",
    tags=["student"],
    dependencies=[Depends(all_users)]
)

@router.get("/available-tests", response_model=List[TestSessionResponse])
def get_available_tests(
    current_user: User = Depends(get_user_with_roles([UserRole.STUDENT])),
    db: Session = Depends(get_db)
):
    """
    Get available tests for the student
    - Exclude tests already taken
    - Check test active status
    """
    # Query tests that:
    # 1. Are active
    # 2. Have not been taken by the current student
    available_tests = (
        db.query(Test)
        .filter(
            Test.is_active == True,
            ~Test.test_sessions.any(TestSession.user_id == current_user.id)
        )
        .all()
    )
    
    return available_tests

@router.post("/start-test/{test_id}", response_model=TestSessionResponse)
def start_test(
    test_id: int,
    current_user: User = Depends(get_user_with_roles([UserRole.STUDENT])),
    db: Session = Depends(get_db)
):
    """
    Start a new test session
    - Validate test availability
    - Create test session with randomized option order
    """
    # Fetch the test
    test = db.query(Test).filter(Test.id == test_id, Test.is_active == True).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found or inactive")
    
    # Check if student has already taken this test
    existing_session = db.query(TestSession).filter(
        TestSession.test_id == test_id, 
        TestSession.user_id == current_user.id
    ).first()
    
    if existing_session:
        raise HTTPException(status_code=400, detail="Test already taken")
    
    # Create test session
    shuffle_seed = random.randint(1, 10000)
    test_session = TestSession(
        user_id=current_user.id,
        test_id=test_id,
        shuffle_seed=shuffle_seed
    )
    db.add(test_session)
    
    # Create shuffled option orders for each question
    random.seed(shuffle_seed)
    for question in test.questions:
        option_ids = [option.id for option in question.options]
        random.shuffle(option_ids)
        
        for order, option_id in enumerate(option_ids, 1):
            option_order = OptionOrder(
                test_session_id=test_session.id,
                question_id=question.id,
                option_id=option_id,
                display_order=order
            )
            db.add(option_order)
    
    db.commit()
    db.refresh(test_session)
    
    return test_session

@router.post("/submit-test/{test_session_id}")
def submit_test(
    test_session_id: int,
    submission: TestSubmission,
    current_user: User = Depends(get_user_with_roles([UserRole.STUDENT])),
    db: Session = Depends(get_db)
):
    """
    Submit test answers and calculate results
    - Validate test session
    - Store user responses
    - Calculate score
    """
    # Fetch the test session
    test_session = db.query(TestSession).filter(
        TestSession.id == test_session_id, 
        TestSession.user_id == current_user.id
    ).first()
    
    if not test_session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    if test_session.completed_at:
        raise HTTPException(status_code=400, detail="Test already submitted")
    
    # Calculate test duration
    test = test_session.test
    max_duration = timedelta(minutes=test.duration_minutes)
    if datetime.utcnow() - test_session.started_at > max_duration:
        raise HTTPException(status_code=400, detail="Test time exceeded")
    
    # Store user responses and calculate score
    correct_answers = 0
    total_questions = len(test.questions)
    
    for response in submission.responses:
        # Find the question
        question = db.query(Question).filter(Question.id == response.question_id).first()
        
        # Create user response
        user_response = UserResponse(
            test_session_id=test_session.id,
            question_id=response.question_id,
            selected_option_id=response.selected_option_id
        )
        db.add(user_response)
        
        # Check if answer is correct
        if question.is_answer_correct(response.selected_option_id):
            correct_answers += 1
    
    # Calculate score
    score = (correct_answers / total_questions) * test.total_marks
    
    # Update test session
    test_session.completed_at = datetime.utcnow()
    test_session.score = score
    
    db.commit()
    
    # Prepare results summary
    results = TestResultsSummary(
        test_id=test.id,
        test_title=test.title,
        total_marks=test.total_marks,
        score=score,
        percentage=(score / test.total_marks) * 100,
        completed_at=test_session.completed_at,
        duration_minutes=test.duration_minutes,
        question_count=total_questions,
        correct_answers=correct_answers
    )
    
    return results

@router.get("/test-results", response_model=List[TestResultsSummary])
def get_test_results(
    current_user: User = Depends(get_user_with_roles([UserRole.STUDENT])),
    db: Session = Depends(get_db)
):
    """
    Retrieve all test results for the student
    """
    # Fetch completed test sessions
    test_sessions = db.query(TestSession).filter(
        TestSession.user_id == current_user.id,
        TestSession.completed_at.isnot(None)
    ).all()
    
    # Convert to results summary
    results = []
    for session in test_sessions:
        test = session.test
        results.append(TestResultsSummary(
            test_id=test.id,
            test_title=test.title,
            total_marks=test.total_marks,
            score=session.score,
            percentage=(session.score / test.total_marks) * 100,
            completed_at=session.completed_at,
            duration_minutes=test.duration_minutes,
            question_count=len(test.questions),
            correct_answers=int((session.score / test.total_marks) * len(test.questions))
        ))
    
    return results