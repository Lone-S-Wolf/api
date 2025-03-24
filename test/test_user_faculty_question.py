import pytest
import random
from test.conftest import login_user

def generate_question(is_public=True):
    """Generate a sample question with random content."""
    subjects = ["Database Management", "Programming", "Data Structures", "Algorithms", 
                "Web Development", "Machine Learning", "Computer Networks", "Operating Systems",
                "Software Engineering", "Artificial Intelligence"]
    
    difficulty_levels = ["easy", "medium", "hard"]
    
    question_types = ["single", "multiple"]
    
    # Generate question text with a unique identifier to avoid duplicates
    random_id = random.randint(1000, 9999)
    
    if random.choice(question_types) == "single":
        # Single choice question
        return {
            "question_text": f"Sample question {random_id} about {random.choice(subjects)}?",
            "question_type": "single",
            "subject": random.choice(subjects),
            "difficulty_level": random.choice(difficulty_levels),
            "tags": f"tag1,tag2,tag{random_id}",
            "explanation": f"This is an explanation for question {random_id}.",
            "is_public": is_public,
            "options": [
                {
                    "option_text": "Correct answer",
                    "is_correct": True
                },
                {
                    "option_text": "Wrong answer 1",
                    "is_correct": False
                },
                {
                    "option_text": "Wrong answer 2",
                    "is_correct": False
                },
                {
                    "option_text": "Wrong answer 3",
                    "is_correct": False
                }
            ]
        }
    else:
        # Multiple choice question
        return {
            "question_text": f"Sample multiple choice question {random_id} about {random.choice(subjects)}?",
            "question_type": "multiple",
            "subject": random.choice(subjects),
            "difficulty_level": random.choice(difficulty_levels),
            "tags": f"tag1,tag2,tag{random_id}",
            "explanation": f"This is an explanation for multiple choice question {random_id}.",
            "is_public": is_public,
            "options": [
                {
                    "option_text": "Correct answer 1",
                    "is_correct": True
                },
                {
                    "option_text": "Correct answer 2",
                    "is_correct": True
                },
                {
                    "option_text": "Wrong answer 1",
                    "is_correct": False
                },
                {
                    "option_text": "Wrong answer 2",
                    "is_correct": False
                }
            ]
        }

def test_faculty_add_questions(client, setup_users):
    """Test to verify that faculty users can add questions."""
    users = setup_users
    
    # Test for each faculty user
    for faculty_user in users["faculty"]:
        # Login as faculty user
        faculty_login_response = login_user(client, faculty_user["username"], "string")
        access_token = faculty_login_response["access_token"]
        
        # Add 10 questions for each faculty (5 public, 5 private)
        created_questions = []
        
        # Add 5 public questions
        for i in range(5):
            question_payload = generate_question(is_public=True)
            response = client.post(
                "/questions/",
                json=question_payload,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 201, f"Failed to create public question {i+1} for {faculty_user['username']}"
            question_data = response.json()
            assert question_data["is_public"] is True
            created_questions.append(question_data)
        
        # Add 5 private questions
        for i in range(5):
            question_payload = generate_question(is_public=False)
            response = client.post(
                "/questions/",
                json=question_payload,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 201, f"Failed to create private question {i+1} for {faculty_user['username']}"
            question_data = response.json()
            assert question_data["is_public"] is False
            created_questions.append(question_data)
        
        # Verify that all 10 questions were created
        assert len(created_questions) == 10
        
        # Verify that each question has the correct attributes
        for question in created_questions:
            assert "id" in question
            assert "created_at" in question
            assert "created_by" in question
            assert question["created_by"] == faculty_user["id"]
            assert len(question["options"]) >= 2
            
            # At least one option should be correct
            correct_options = [option for option in question["options"] if option["is_correct"]]
            assert len(correct_options) >= 1