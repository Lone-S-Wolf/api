# app/routers/test_questions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import select, insert, update, delete

from app.database.database import get_db
from app.models.user import User, UserRole
from app.models.test import Test, test_questions
from app.models.question import Question
from app.schemas.test.test_schemas import TestQuestionAdd, TestQuestionUpdate, TestQuestionResponse, QuestionResponse
from app.auth.rbac import get_user_with_roles

router = APIRouter(
    prefix="/tests/{test_id}/questions",
    tags=["test-questions"],
)

# Permissions
get_faculty_or_admin = get_user_with_roles([UserRole.FACULTY, UserRole.ADMIN])

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_question_to_test(
    test_id: int,
    question_data: TestQuestionAdd,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Add a question to a test (faculty owner or admin only)"""
    # Verify the test exists
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if user has permission to update this test
    if current_user.role != UserRole.ADMIN and test.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this test")
    
    # Verify the question exists
    question = db.query(Question).filter(Question.id == question_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if faculty has permission to use this question
    if current_user.role != UserRole.ADMIN and not question.is_public and question.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to use this question")
    
    # Check if question is already in the test
    existing = db.query(test_questions).filter(
        test_questions.c.test_id == test_id,
        test_questions.c.question_id == question_data.question_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Question is already in this test")
    
    # Determine question order if not provided
    if not question_data.question_order:
        # Get the highest current order
        max_order = db.query(test_questions.c.question_order).filter(
            test_questions.c.test_id == test_id
        ).order_by(
            test_questions.c.question_order.desc()
        ).first()
        
        if max_order:
            question_order = max_order[0] + 1
        else:
            question_order = 1
    else:
        question_order = question_data.question_order
    
    # Add question to test
    stmt = insert(test_questions).values(
        test_id=test_id,
        question_id=question_data.question_id,
        question_order=question_order,
        marks=question_data.marks
    )
    db.execute(stmt)
    
    # Update test total marks
    total_marks = db.query(test_questions.c.marks).filter(
        test_questions.c.test_id == test_id
    ).all()
    test.total_marks = sum(mark[0] for mark in total_marks)
    
    db.commit()
    
    return {"status": "success", "message": "Question added to test"}

@router.get("/", response_model=List[TestQuestionResponse])
def get_test_questions(
    test_id: int,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Get all questions in a test (faculty owner or admin only)"""
    # Verify the test exists
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if user has permission to view this test
    if current_user.role != UserRole.ADMIN and test.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to view this test's questions")
    
    # Get questions with their test metadata
    questions = db.query(
        Question, test_questions.c.question_order, test_questions.c.marks
    ).join(
        test_questions, Question.id == test_questions.c.question_id
    ).filter(
        test_questions.c.test_id == test_id
    ).order_by(
        test_questions.c.question_order
    ).all()
    
    # Format response
    result = []
    for question, order, marks in questions:
        result.append({
            "question_id": question.id,
            "marks": marks,
            "question_order": order,
            "question": question
        })
    
    return result

@router.put("/{question_id}", status_code=status.HTTP_200_OK)
def update_test_question(
    test_id: int,
    question_id: int,
    update_data: TestQuestionUpdate,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Update a question in a test (faculty owner or admin only)"""
    # Verify the test exists
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if user has permission to update this test
    if current_user.role != UserRole.ADMIN and test.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this test")
    
    # Check if the question is in the test
    test_question = db.query(test_questions).filter(
        test_questions.c.test_id == test_id,
        test_questions.c.question_id == question_id
    ).first()
    
    if not test_question:
        raise HTTPException(status_code=404, detail="Question not found in this test")
    
    # Update fields
    update_values = {}
    if update_data.marks is not None:
        update_values["marks"] = update_data.marks
    if update_data.question_order is not None:
        update_values["question_order"] = update_data.question_order
    
    if update_values:
        stmt = update(test_questions).where(
            test_questions.c.test_id == test_id,
            test_questions.c.question_id == question_id
        ).values(**update_values)
        db.execute(stmt)
        
        # Update test total marks if marks were changed
        if "marks" in update_values:
            total_marks = db.query(test_questions.c.marks).filter(
                test_questions.c.test_id == test_id
            ).all()
            test.total_marks = sum(mark[0] for mark in total_marks)
        
        db.commit()
    
    return {"status": "success", "message": "Test question updated"}

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_question_from_test(
    test_id: int,
    question_id: int,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Remove a question from a test (faculty owner or admin only)"""
    # Verify the test exists
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if user has permission to update this test
    if current_user.role != UserRole.ADMIN and test.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this test")
    
    # Check if the question is in the test
    test_question = db.query(test_questions).filter(
        test_questions.c.test_id == test_id,
        test_questions.c.question_id == question_id
    ).first()
    
    if not test_question:
        raise HTTPException(status_code=404, detail="Question not found in this test")
    
    # Remove the question from the test
    stmt = delete(test_questions).where(
        test_questions.c.test_id == test_id,
        test_questions.c.question_id == question_id
    )
    db.execute(stmt)
    
    # Update test total marks
    total_marks = db.query(test_questions.c.marks).filter(
        test_questions.c.test_id == test_id
    ).all()
    test.total_marks = sum(mark[0] for mark in total_marks) if total_marks else 0
    
    db.commit()
    
    return None