import pytest
from fastapi.testclient import TestClient
from app.main import app

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

@pytest.fixture(scope="session")
def client():
    """Fixture that returns a TestClient instance."""
    return TestClient(app)

def register_user(client, role, index):
    """Helper function to register a user with a specific role and index."""
    payload = USER_PAYLOAD_TEMPLATE.copy()
    payload["email"] = f"{role}{index}@example.com"
    payload["username"] = f"{role}_user_{index}"
    payload["role"] = role
    response = client.post(REGISTER_URL, json=payload)
    assert response.status_code == 201
    return response.json()

def login_user(client, username, password):
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

@pytest.fixture(scope="session")
def setup_users(client):
    """Fixture to set up users with different roles."""
    users = {}
    for role, count in ROLES.items():
        users[role] = [register_user(client, role, i) for i in range(1, count + 1)]
    return users