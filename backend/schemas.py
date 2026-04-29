# Data Models and Schemas
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class UserRoleEnum(str, Enum):
    """User role enumeration."""

    ADMIN = "admin"
    PM = "pm"
    DEV = "dev"
    DESIGNER = "designer"


class DocumentTypeEnum(str, Enum):
    """Document type enumeration."""

    PRD = "prd"
    DESIGN = "design"
    CODE = "code"


class AnalysisStatusEnum(str, Enum):
    """Analysis status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Authentication Schemas
class SignUpRequest(BaseModel):
    """User sign-up request."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    organization: str = Field(..., min_length=2)
    role: UserRoleEnum = UserRoleEnum.DEV

    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response data."""

    id: str
    email: str
    full_name: str
    organization: str
    role: UserRoleEnum
    created_at: datetime
    updated_at: datetime


# User Database Schema
class UserDB(BaseModel):
    """User database model."""

    id: str
    email: str
    full_name: str
    organization: str
    role: UserRoleEnum
    password_hash: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# JWT Token Schema
class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # User ID
    email: str
    role: UserRoleEnum
    org: str
    iat: datetime
    exp: datetime


# Document Upload Schemas
class DocumentUploadRequest(BaseModel):
    """Document upload request."""

    doc_type: DocumentTypeEnum
    title: str = Field(..., min_length=3)
    description: Optional[str] = None


class DocumentMetadata(BaseModel):
    """Document metadata."""

    id: str
    doc_type: DocumentTypeEnum
    title: str
    description: Optional[str]
    file_url: str
    file_size: int
    uploaded_by: str
    uploaded_at: datetime
    updated_at: datetime


class DocumentDB(BaseModel):
    """Document database model."""

    id: str
    user_id: str
    org_id: str
    doc_type: DocumentTypeEnum
    title: str
    description: Optional[str]
    file_path: str
    file_url: str
    file_size: int
    raw_text: Optional[str]
    status: str = "processing"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analysis Schemas
class AnalysisRequestSchema(BaseModel):
    """Analysis request."""

    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    analysis_type: str = "consistency"  # For future extensibility


class AnalysisResponseSchema(BaseModel):
    """Analysis response."""

    id: str
    title: str
    description: Optional[str]
    status: AnalysisStatusEnum
    consistency_score: Optional[int]
    total_conflicts: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]


class ConflictSchema(BaseModel):
    """Detected conflict."""

    id: str
    type: str  # MISSING_FEATURE, CONTRADICTING, etc.
    severity: str  # HIGH, MEDIUM, LOW
    title: str
    description: str
    affected_documents: List[str]
    suggested_resolution: Optional[str]


class AnalysisResultSchema(BaseModel):
    """Analysis result."""

    analysis_id: str
    consistency_score: int
    total_conflicts: int
    conflicts: List[ConflictSchema]
    agent_outputs: dict
    processing_time_ms: int
    created_at: datetime


class AnalysisDB(BaseModel):
    """Analysis database model."""

    id: str
    user_id: str
    org_id: str
    title: str
    description: Optional[str]
    status: AnalysisStatusEnum
    consistency_score: Optional[int]
    total_conflicts: Optional[int]
    prd_doc_id: Optional[str]
    design_doc_id: Optional[str]
    code_doc_id: Optional[str]
    results: Optional[dict]
    created_at: datetime
    completed_at: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True


# Health Check
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str
    timestamp: datetime


# Error Response
class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: str
    timestamp: datetime
    request_id: Optional[str] = None
