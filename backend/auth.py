# Authentication and JWT utilities
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import ValidationError

from config import get_settings, UserRole
from schemas import TokenPayload

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service for JWT tokens and password management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        user_id: str,
        email: str,
        role: str,
        org: str,
        expires_delta: Optional[timedelta] = None
    ) -> Tuple[str, datetime]:
        """Create JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.JWT_EXPIRY_HOURS)

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "org": org,
            "iat": now,
            "exp": expire,
            "type": "access",
        }

        encoded_jwt = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        logger.debug(f"Access token created for user: {email}")
        return encoded_jwt, expire

    @staticmethod
    def create_refresh_token(
        user_id: str,
        email: str,
        expires_delta: Optional[timedelta] = None
    ) -> Tuple[str, datetime]:
        """Create JWT refresh token."""
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.JWT_REFRESH_EXPIRY_HOURS)

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        payload = {
            "sub": user_id,
            "email": email,
            "iat": now,
            "exp": expire,
            "type": "refresh",
        }

        encoded_jwt = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        logger.debug(f"Refresh token created for user: {email}")
        return encoded_jwt, expire

    @staticmethod
    def verify_token(token: str) -> Optional[TokenPayload]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )

            # Convert datetime objects from jwt
            payload["iat"] = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
            payload["exp"] = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

            token_data = TokenPayload(**payload)
            return token_data

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except ValidationError as e:
            logger.warning(f"Token validation error: {e}")
            return None

    @staticmethod
    def verify_token_or_raise(token: str) -> TokenPayload:
        """Verify token and raise exception if invalid."""
        token_data = AuthService.verify_token(token)
        
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return token_data

    @staticmethod
    def generate_random_string(length: int = 32) -> str:
        """Generate random string for tokens/secrets."""
        return secrets.token_urlsafe(length)


class RoleChecker:
    """Check user roles and permissions."""

    def __init__(self, allowed_roles: list):
        """Initialize with allowed roles."""
        self.allowed_roles = allowed_roles

    def __call__(self, token_data: TokenPayload) -> bool:
        """Check if user role is allowed."""
        if token_data.role == UserRole.ADMIN:
            return True  # Admins have all permissions
        
        return token_data.role in self.allowed_roles


def check_permission(token_data: TokenPayload, required_permission: str) -> bool:
    """Check if user has specific permission."""
    from config import ROLE_PERMISSIONS
    
    role_perms = ROLE_PERMISSIONS.get(token_data.role, [])
    
    # Admin has all permissions
    if "*" in role_perms:
        return True
    
    return required_permission in role_perms


def enforce_permission(token_data: TokenPayload, required_permission: str) -> None:
    """Enforce permission or raise exception."""
    if not check_permission(token_data, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {required_permission}"
        )
