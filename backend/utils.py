# Utilities for file handling and common operations
import logging
import os
from typing import Optional
from pathlib import Path

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FileService:
    """Service for file operations."""

    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Validate file extension."""
        allowed_exts = settings.allowed_extensions_list
        file_ext = Path(filename).suffix.lstrip(".").lower()
        return file_ext in allowed_exts

    @staticmethod
    def validate_file_size(file_size_bytes: int) -> bool:
        """Validate file size."""
        return file_size_bytes <= settings.max_file_size_bytes

    @staticmethod
    def get_file_path(user_id: str, doc_type: str, filename: str) -> str:
        """Generate storage path for file."""
        return f"documents/{user_id}/{doc_type}/{filename}"

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension."""
        return Path(filename).suffix.lstrip(".").lower()

    @staticmethod
    async def extract_text_from_file(file_content: bytes, file_type: str) -> Optional[str]:
        """Extract text from various file types."""
        try:
            if file_type.lower() == "txt":
                return file_content.decode("utf-8")
            
            elif file_type.lower() == "pdf":
                # For MVP, we'll note that PDF extraction requires additional dependencies
                logger.info("PDF text extraction would require pypdf library")
                return None
            
            elif file_type.lower() == "docx":
                # For MVP, we'll note that DOCX extraction requires additional dependencies
                logger.info("DOCX text extraction would require python-docx library")
                return None
            
            else:
                logger.warning(f"Unsupported file type: {file_type}")
                return None

        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return None


class ValidationService:
    """Service for data validation."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation."""
        return "@" in email and "." in email

    @staticmethod
    def validate_organization_name(org_name: str) -> bool:
        """Validate organization name."""
        return len(org_name) >= 2 and len(org_name) <= 255

    @staticmethod
    def validate_document_title(title: str) -> bool:
        """Validate document title."""
        return len(title) >= 3 and len(title) <= 255

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for storage."""
        # Remove special characters, keep only alphanumeric, dash, underscore, and dot
        import re
        sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
        return sanitized


class ErrorMessages:
    """Standard error messages."""

    # Authentication
    INVALID_CREDENTIALS = "Invalid email or password"
    USER_NOT_FOUND = "User not found"
    USER_ALREADY_EXISTS = "User with this email already exists"
    TOKEN_EXPIRED = "Token has expired"
    INVALID_TOKEN = "Invalid token"
    UNAUTHORIZED = "Unauthorized"
    FORBIDDEN = "Access denied"

    # File Upload
    INVALID_FILE_TYPE = f"Invalid file type. Allowed types: {', '.join(settings.allowed_extensions_list)}"
    FILE_TOO_LARGE = f"File is too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
    FILE_UPLOAD_FAILED = "File upload failed"
    FILE_NOT_FOUND = "File not found"

    # Validation
    INVALID_EMAIL = "Invalid email format"
    INVALID_PASSWORD = "Password must be at least 8 characters with uppercase and number"
    INVALID_ORG_NAME = "Organization name must be between 2 and 255 characters"
    INVALID_DOC_TITLE = "Document title must be between 3 and 255 characters"

    # Database
    DATABASE_ERROR = "Database error occurred"
    RECORD_NOT_FOUND = "Record not found"

    # Analysis
    ANALYSIS_NOT_FOUND = "Analysis not found"
    INVALID_ANALYSIS_STATUS = "Invalid analysis status"
    MISSING_REQUIRED_DOCUMENTS = "Missing required documents for analysis"


class SuccessMessages:
    """Standard success messages."""

    USER_CREATED = "User created successfully"
    LOGIN_SUCCESS = "Login successful"
    FILE_UPLOADED = "File uploaded successfully"
    ANALYSIS_CREATED = "Analysis created successfully"
    ANALYSIS_STARTED = "Analysis started"
    OPERATION_SUCCESS = "Operation completed successfully"
