import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Define the registration and login URLs
REGISTER_URL = "http://localhost:8000/auth/register"
LOGIN_URL = "http://localhost:8000/auth/token"

# Define the payload templates for registration
USER_PAYLOAD_TEMPLATE = {
    "email": "user@example.com",
    "username": "string",
    "password": "string",
    "role": "faculty"
}

# Define the roles and the number of users to create for each role
ROLES = {
    "admin": 1,
    "faculty": 4,
    "student": 4,
    "institution": 4
}

# Define login credentials (client_id and client_secret)
CLIENT_ID = "string"
CLIENT_SECRET = "string"

def register_user(role, index):
    """Helper function to register a user with a specific role and index."""
    payload = USER_PAYLOAD_TEMPLATE.copy()
    payload["email"] = f"{role}{index}@example.com"
    payload["username"] = f"{role}_user_{index}"
    payload["role"] = role
    response = client.post(REGISTER_URL, json=payload)
    assert response.status_code == 201
    return response.json()

def login_user(username, password):
    """Helper function to log in a user and retrieve the access token."""
    login_data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = client.post(LOGIN_URL, data=login_data)
    assert response.status_code == 200
    return response.json()

@pytest.fixture(scope="module")
def setup_users():
    """Fixture to set up users with different roles."""
    users = {}
    for role, count in ROLES.items():
        users[role] = [register_user(role, i) for i in range(1, count + 1)]
    return users

def test_user_registration(setup_users):
    """Test to verify that users are registered with the correct roles."""
    users = setup_users
    assert len(users["admin"]) == 1
    assert len(users["faculty"]) == 4
    assert len(users["student"]) == 4
    assert len(users["institution"]) == 4

    # Verify the details of the admin user
    admin_user = users["admin"][0]
    assert admin_user["role"] == "admin"
    assert admin_user["is_active"] is True
    assert "id" in admin_user
    assert "created_at" in admin_user

    # Verify the details of the faculty users
    for faculty_user in users["faculty"]:
        assert faculty_user["role"] == "faculty"
        assert faculty_user["is_active"] is True
        assert "id" in faculty_user
        assert "created_at" in faculty_user

    # Verify the details of the student users
    for student_user in users["student"]:
        assert student_user["role"] == "student"
        assert student_user["is_active"] is True
        assert "id" in student_user
        assert "created_at" in student_user

    # Verify the details of the institution users
    for institution_user in users["institution"]:
        assert institution_user["role"] == "institution"
        assert institution_user["is_active"] is True
        assert "id" in institution_user
        assert "created_at" in institution_user

def test_user_login(setup_users):
    """Test to verify that users can log in and retrieve access tokens."""
    users = setup_users

    # Test login for admin user
    admin_user = users["admin"][0]
    admin_login_response = login_user(admin_user["username"], "string")
    assert "access_token" in admin_login_response
    assert admin_login_response["token_type"] == "bearer"

    # Test login for faculty users
    for faculty_user in users["faculty"]:
        faculty_login_response = login_user(faculty_user["username"], "string")
        assert "access_token" in faculty_login_response
        assert faculty_login_response["token_type"] == "bearer"

    # Test login for student users
    for student_user in users["student"]:
        student_login_response = login_user(student_user["username"], "string")
        assert "access_token" in student_login_response
        assert student_login_response["token_type"] == "bearer"

    # Test login for institution users
    for institution_user in users["institution"]:
        institution_login_response = login_user(institution_user["username"], "string")
        assert "access_token" in institution_login_response
        assert institution_login_response["token_type"] == "bearer"

def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI CRUD API with Advanced Role-Based Access Control"}