# app/routers/tests.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database.database import get_db
from app.models.models import User, Test, UserRole
from app.schemas.schemas import (
    TestCreate, TestUpdate, TestResponse
)
from app.auth.rbac import get_user_with_roles

router = APIRouter(
    prefix="/tests",
    tags=["tests"],
)

# Permissions
get_faculty_or_admin = get_user_with_roles([UserRole.FACULTY, UserRole.ADMIN])
get_student_or_above = get_user_with_roles([UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION, UserRole.ADMIN])

# Test management endpoints (for faculty and admins)
@router.post("/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
def create_test(
    test_data: TestCreate,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new test (faculty or admin only)"""
    new_test = Test(
        **test_data.model_dump(),
        created_by=current_user.id
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    
    # Add question_count to response
    setattr(new_test, 'question_count', 0)
    
    return new_test

@router.get("/", response_model=List[TestResponse])
def get_tests(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_student_or_above),
    db: Session = Depends(get_db)
):
    """Get all tests with pagination"""
    # For students, show only active tests
    if current_user.role == UserRole.STUDENT:
        tests = db.query(Test).filter(Test.is_active == True).offset(skip).limit(limit).all()
    # For faculty, show only their own tests and active tests
    elif current_user.role == UserRole.FACULTY:
        tests = db.query(Test).filter(
            (Test.created_by == current_user.id) | (Test.is_active == True)
        ).offset(skip).limit(limit).all()
    # For admin and institution, show all tests
    else:
        tests = db.query(Test).offset(skip).limit(limit).all()
    
    # Add question count to each test using the relationship
    for test in tests:
        setattr(test, 'question_count', len(test.questions))
    
    return tests

@router.get("/{test_id}", response_model=TestResponse)
def get_test(
    test_id: int,
    current_user: User = Depends(get_student_or_above),
    db: Session = Depends(get_db)
):
    """Get a specific test by ID"""
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check permissions
    if current_user.role == UserRole.STUDENT and not test.is_active:
        raise HTTPException(status_code=403, detail="Test is not active")
    
    if current_user.role == UserRole.FACULTY and not test.is_active and test.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to view this test")
    
    # Add question count using the relationship
    setattr(test, 'question_count', len(test.questions))
    
    return test

@router.put("/{test_id}", response_model=TestResponse)
def update_test(
    test_id: int,
    test_data: TestUpdate,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Update a test (faculty owner or admin only)"""
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if user has permission to update
    if current_user.role != UserRole.ADMIN and test.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this test")
    
    # Update test fields
    for key, value in test_data.model_dump(exclude_unset=True).items():
        setattr(test, key, value)
    
    db.commit()
    db.refresh(test)
    
    # Add question count using the relationship
    setattr(test, 'question_count', len(test.questions))
    
    return test

@router.delete("/{test_id}")
def delete_test(
    test_id: int,
    current_user: User = Depends(get_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Delete a test (faculty owner or admin only)"""
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if user has permission to delete
    if current_user.role != UserRole.ADMIN and test.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this test")
    
    db.delete(test)
    db.commit()
    
    return {"detail": "Test deleted successfully"}