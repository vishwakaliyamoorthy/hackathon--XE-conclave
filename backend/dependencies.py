# FastAPI dependencies for authentication and authorization
import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

from auth import AuthService
from schemas import TokenPayload
from config import UserRole

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
) -> TokenPayload:
    """
    Get current authenticated user from JWT token.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: TokenPayload = Depends(get_current_user)):
            return {"user": user}
    """
    token = credentials.credentials
    
    try:
        token_data = AuthService.verify_token_or_raise(token)
        return token_data
    except HTTPException:
        raise


async def get_current_admin(
    current_user: TokenPayload = Depends(get_current_user),
) -> TokenPayload:
    """
    Get current user and verify admin role.
    
    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(user: TokenPayload = Depends(get_current_admin)):
            return {"deleted": True}
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_pm(
    current_user: TokenPayload = Depends(get_current_user),
) -> TokenPayload:
    """Get current user and verify PM role."""
    if current_user.role not in [UserRole.ADMIN, UserRole.PM]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PM access required"
        )
    return current_user


async def get_current_dev(
    current_user: TokenPayload = Depends(get_current_user),
) -> TokenPayload:
    """Get current user and verify Dev role."""
    if current_user.role not in [UserRole.ADMIN, UserRole.DEV]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev access required"
        )
    return current_user


async def get_current_designer(
    current_user: TokenPayload = Depends(get_current_user),
) -> TokenPayload:
    """Get current user and verify Designer role."""
    if current_user.role not in [UserRole.ADMIN, UserRole.DESIGNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Designer access required"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthCredentials] = Depends(security),
) -> Optional[TokenPayload]:
    """
    Get optional current user (not required).
    
    Usage:
        @app.get("/public")
        async def public_route(user: Optional[TokenPayload] = Depends(get_optional_user)):
            return {"authenticated": user is not None}
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    token_data = AuthService.verify_token(token)
    
    if token_data is None:
        return None
    
    return token_data
