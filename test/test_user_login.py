import pytest
from test.conftest import login_user

def test_user_login(client, setup_users):
    """Test to verify that users can log in and retrieve access tokens."""
    users = setup_users

    # Test login for admin user
    admin_user = users["admin"][0]
    admin_login_response = login_user(client, admin_user["username"], "string")
    assert "access_token" in admin_login_response
    assert admin_login_response["token_type"] == "bearer"

    # Test login for faculty users
    for faculty_user in users["faculty"]:
        faculty_login_response = login_user(client, faculty_user["username"], "string")
        assert "access_token" in faculty_login_response
        assert faculty_login_response["token_type"] == "bearer"

    # Test login for student users
    for student_user in users["student"]:
        student_login_response = login_user(client, student_user["username"], "string")
        assert "access_token" in student_login_response
        assert student_login_response["token_type"] == "bearer"

    # Test login for institution users
    for institution_user in users["institution"]:
        institution_login_response = login_user(client, institution_user["username"], "string")
        assert "access_token" in institution_login_response
        assert institution_login_response["token_type"] == "bearer"