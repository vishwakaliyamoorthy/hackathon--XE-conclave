# Authentication routes
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import EmailStr

from schemas import (
    SignUpRequest, LoginRequest, TokenResponse, UserResponse, TokenPayload
)
from auth import AuthService
from services import get_supabase_service
from dependencies import get_current_user
from utils import ErrorMessages, SuccessMessages, ValidationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

supabase = get_supabase_service()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest) -> TokenResponse:
    """
    Create new user account.
    
    **Request**:
    - email: User email (must be unique)
    - password: At least 8 chars, must include uppercase and digit
    - full_name: User's full name
    - organization: Organization name
    - role: User role (pm, dev, designer)
    
    **Response**:
    - access_token: JWT token for authentication
    - refresh_token: Token to refresh access token
    - expires_in: Token expiration time in seconds
    """
    logger.info(f"Signup attempt: {request.email}")

    # Validate email
    if not ValidationService.validate_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.INVALID_EMAIL
        )

    # Validate organization
    if not ValidationService.validate_organization_name(request.organization):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.INVALID_ORG_NAME
        )

    try:
        # Check if user already exists
        user_exists = await supabase.user_exists(request.email)
        if user_exists:
            logger.warning(f"User already exists: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorMessages.USER_ALREADY_EXISTS
            )

        # Hash password
        password_hash = AuthService.hash_password(request.password)

        # Create user in database
        user = await supabase.create_user(
            email=request.email,
            password_hash=password_hash,
            full_name=request.full_name,
            organization=request.organization,
            role=request.role.value
        )

        logger.info(f"User created successfully: {request.email}")

        # Create tokens
        access_token, _ = AuthService.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            org=user.organization
        )

        refresh_token, _ = AuthService.create_refresh_token(
            user_id=user.id,
            email=user.email
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600  # 1 hour in seconds
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.DATABASE_ERROR
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """
    Authenticate user and receive tokens.
    
    **Request**:
    - email: User email
    - password: User password
    
    **Response**:
    - access_token: JWT token for API access
    - refresh_token: Token to refresh access token
    - expires_in: Token expiration time in seconds
    """
    logger.info(f"Login attempt: {request.email}")

    try:
        # Get user by email
        user = await supabase.get_user_by_email(request.email)
        
        if user is None:
            logger.warning(f"Login failed - user not found: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessages.INVALID_CREDENTIALS,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not AuthService.verify_password(request.password, user.password_hash):
            logger.warning(f"Login failed - invalid password: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessages.INVALID_CREDENTIALS,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login failed - user inactive: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        logger.info(f"Login successful: {request.email}")

        # Create tokens
        access_token, _ = AuthService.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            org=user.organization
        )

        refresh_token, _ = AuthService.create_refresh_token(
            user_id=user.id,
            email=user.email
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.DATABASE_ERROR
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: dict) -> TokenResponse:
    """
    Refresh expired access token.
    
    **Request**:
    - refresh_token: Previously obtained refresh token
    
    **Response**:
    - access_token: New JWT token
    - refresh_token: New refresh token
    - expires_in: Token expiration time in seconds
    """
    refresh_token_str = request.get("refresh_token")
    
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token is required"
        )

    logger.info("Token refresh attempt")

    try:
        # Verify refresh token
        token_data = AuthService.verify_token(refresh_token_str)
        
        if token_data is None or token_data.type != "refresh":
            logger.warning("Token refresh failed - invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessages.INVALID_TOKEN,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user
        user = await supabase.get_user_by_id(token_data.sub)
        
        if user is None or not user.is_active:
            logger.warning("Token refresh failed - user not found or inactive")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessages.INVALID_CREDENTIALS,
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"Token refreshed for user: {user.email}")

        # Create new tokens
        access_token, _ = AuthService.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            org=user.organization
        )

        new_refresh_token, _ = AuthService.create_refresh_token(
            user_id=user.id,
            email=user.email
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=3600
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.DATABASE_ERROR
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenPayload = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information.
    
    **Authorization**: Required (Bearer token)
    
    **Response**: User details
    """
    logger.info(f"Get current user: {current_user.email}")

    try:
        user = await supabase.get_user_by_id(current_user.sub)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.USER_NOT_FOUND
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization=user.organization,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.DATABASE_ERROR
        )


@router.post("/logout")
async def logout(current_user: TokenPayload = Depends(get_current_user)) -> dict:
    """
    Logout user (client-side token invalidation).
    
    **Authorization**: Required
    
    **Note**: JWT tokens are stateless. Logout is typically handled client-side
    by removing the token from storage. For token revocation, implement a token
    blacklist.
    """
    logger.info(f"User logout: {current_user.email}")
    
    return {
        "message": "Logged out successfully",
        "email": current_user.email
    }
