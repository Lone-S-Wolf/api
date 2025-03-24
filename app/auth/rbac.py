from fastapi import Depends, HTTPException, status
from app.models.user import User, UserRole
from app.auth.utils import get_current_active_user

def check_user_role(required_roles: list[UserRole], user: User):
    """Check if user has at least one of the required roles"""
    if user.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {', '.join([r for r in required_roles])}",
        )
    return True

def get_admin_user(current_user: User = Depends(get_current_active_user)):
    """Dependency to check if user is an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

def get_user_with_roles(roles: list[UserRole]):
    """Factory for creating a dependency that checks for specific roles"""
    
    def _get_user_with_roles(current_user: User = Depends(get_current_active_user)):
        check_user_role(roles, current_user)
        return current_user
        
    return _get_user_with_roles