"""
Authentication Middleware
Handles JWT token validation for protected routes
"""

from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.jwt_handler import verify_token

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        User data from token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    payload = verify_token(token, token_type="access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user info from payload
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "USER"),
        "full_name": payload.get("full_name")
    }


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to get current active user (can be extended with user status check)

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Active user data
    """
    # Here you can add additional checks like user.is_active from database
    return current_user


async def require_role(required_role: str):
    """
    Dependency factory to require specific role

    Args:
        required_role: Role required for access (e.g., "ADMIN", "SUPER_ADMIN")

    Returns:
        Dependency function
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "USER")

        # Role hierarchy: SUPER_ADMIN > ADMIN > USER
        role_hierarchy = {
            "USER": 1,
            "ADMIN": 2,
            "SUPER_ADMIN": 3
        }

        required_level = role_hierarchy.get(required_role, 1)
        user_level = role_hierarchy.get(user_role, 1)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )

        return current_user

    return role_checker


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """
    Dependency to get user if token is provided, but don't require it

    Args:
        credentials: Optional HTTP Bearer token credentials

    Returns:
        User data if token is valid, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "USER"),
        "full_name": payload.get("full_name")
    }
