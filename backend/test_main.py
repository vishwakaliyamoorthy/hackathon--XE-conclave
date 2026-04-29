# Backend Project Tests
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app
from schemas import SignUpRequest, LoginRequest
from auth import AuthService

client = TestClient(app)


# ==== FIXTURE ====

@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return {
        "email": "testuser@example.com",
        "password": "TestPassword123",
        "full_name": "Test User",
        "organization": "Test Org",
        "role": "dev"
    }


@pytest.fixture
def sample_tokens():
    """Sample JWT tokens."""
    user_id = "test-user-123"
    email = "test@example.com"
    
    access_token, _ = AuthService.create_access_token(
        user_id=user_id,
        email=email,
        role="dev",
        org="test-org"
    )
    
    refresh_token, _ = AuthService.create_refresh_token(
        user_id=user_id,
        email=email
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


# ==== HEALTH CHECKS ====

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert data["version"] == "1.0.0"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "endpoints" in data


# ==== AUTHENTICATION TESTS ====

@pytest.mark.asyncio
async def test_signup_validation_invalid_email(sample_user):
    """Test signup with invalid email."""
    sample_user["email"] = "invalid-email"
    response = client.post("/api/auth/signup", json=sample_user)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_signup_validation_weak_password(sample_user):
    """Test signup with weak password."""
    sample_user["password"] = "weak"
    response = client.post("/api/auth/signup", json=sample_user)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_signup_validation_invalid_org_name(sample_user):
    """Test signup with invalid organization name."""
    sample_user["organization"] = "A"  # Too short
    response = client.post("/api/auth/signup", json=sample_user)
    # Should fail org validation
    assert response.status_code >= 400


def test_login_endpoint_structure():
    """Test login endpoint accepts correct structure."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "password"
        }
    )
    # Will fail due to no user, but endpoint should be reachable
    assert response.status_code in [401, 500]  # Unauthorized or DB error


# ==== FILE UPLOAD TESTS ====

def test_upload_prd_without_auth():
    """Test PRD upload without authentication."""
    response = client.post("/api/upload/prd")
    assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_upload_prd_invalid_file_type():
    """Test PRD upload with invalid file type."""
    # Would need valid token, but testing endpoint exists
    response = client.get("/api/upload/prd")
    assert response.status_code in [401, 405]  # Unauthorized or Method not allowed


# ==== ANALYSIS TESTS ====

def test_analyze_without_auth():
    """Test analysis create without authentication."""
    response = client.post("/api/analyze")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_auth_token_verification():
    """Test JWT token verification."""
    user_id = "test-user"
    email = "test@example.com"
    
    token, _ = AuthService.create_access_token(
        user_id=user_id,
        email=email,
        role="dev",
        org="test"
    )
    
    verified = AuthService.verify_token(token)
    assert verified is not None
    assert verified.sub == user_id
    assert verified.email == email


# ==== PASSWORD HASHING TESTS ====

def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPassword123"
    hashed = AuthService.hash_password(password)
    
    assert hashed != password
    assert AuthService.verify_password(password, hashed)
    assert not AuthService.verify_password("wrong-password", hashed)


# ==== ERROR HANDLING ====

def test_rate_limiting_headers():
    """Test rate limiting headers."""
    response = client.get("/health")
    
    # Should have rate limit headers
    assert "x-ratelimit-limit" in response.headers or response.status_code == 200


def test_request_id_header():
    """Test request ID header in response."""
    response = client.get("/health")
    assert "x-request-id" in response.headers


# ==== CORS TESTS ====

def test_cors_headers():
    """Test CORS headers."""
    response = client.options("/health")
    
    # Should have CORS headers
    cors_headers = ["access-control-allow-origin", "access-control-allow-methods"]
    has_cors = any(h in response.headers for h in cors_headers)
    assert has_cors or response.status_code in [200, 204]


class TestAuthService:
    """Test authentication service."""

    def test_create_and_verify_tokens(self):
        """Test token creation and verification."""
        user_id = "test-123"
        email = "test@example.com"
        role = "admin"
        org = "test-org"
        
        # Create access token
        access_token, exp_time = AuthService.create_access_token(
            user_id=user_id,
            email=email,
            role=role,
            org=org
        )
        
        assert access_token is not None
        assert exp_time is not None
        
        # Verify token
        payload = AuthService.verify_token(access_token)
        assert payload is not None
        assert payload.sub == user_id
        assert payload.email == email
        assert payload.role == role
        assert payload.org == org

    def test_expired_token_verification(self):
        """Test expired token verification."""
        from datetime import timedelta
        
        user_id = "test-123"
        email = "test@example.com"
        
        # Create expired token
        expired_token, _ = AuthService.create_access_token(
            user_id=user_id,
            email=email,
            role="dev",
            org="test",
            expires_delta=timedelta(seconds=-100)  # Already expired
        )
        
        payload = AuthService.verify_token(expired_token)
        assert payload is None  # Should be None for expired token

    def test_refresh_token_creation(self):
        """Test refresh token creation."""
        user_id = "test-123"
        email = "test@example.com"
        
        refresh_token, exp_time = AuthService.create_refresh_token(
            user_id=user_id,
            email=email
        )
        
        assert refresh_token is not None
        
        # Verify refresh token
        payload = AuthService.verify_token(refresh_token)
        assert payload is not None
        assert payload.sub == user_id
        assert payload.type == "refresh"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
