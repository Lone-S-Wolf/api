import pytest

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