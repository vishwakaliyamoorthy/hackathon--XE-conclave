# Configuration and Settings
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    JWT_REFRESH_EXPIRY_HOURS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    UPLOAD_DIRECTORY: str = "/tmp/uploads"
    ALLOWED_EXTENSIONS: str = "pdf,docx,txt"

    # API Keys
    OPENAI_API_KEY: Optional[str] = None

    # Logging
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Convert comma-separated string to list."""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# User Roles
class UserRole:
    """User role definitions."""

    ADMIN = "admin"
    PM = "pm"
    DEV = "dev"
    DESIGNER = "designer"

    ALL_ROLES = [ADMIN, PM, DEV, DESIGNER]

    @classmethod
    def is_valid(cls, role: str) -> bool:
        """Check if role is valid."""
        return role in cls.ALL_ROLES


# Role Permissions
ROLE_PERMISSIONS = {
    UserRole.ADMIN: ["*"],  # All permissions
    UserRole.PM: ["upload:prd", "analyze", "view:results"],
    UserRole.DEV: ["upload:code", "upload:prd", "analyze", "view:results"],
    UserRole.DESIGNER: ["upload:design", "upload:prd", "analyze", "view:results"],
}
