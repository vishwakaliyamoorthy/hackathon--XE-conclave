# Main FastAPI Application
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config import get_settings
from middleware import (
    RequestIdMiddleware, ExceptionMiddleware, LoggingMiddleware,
    CORSMiddleware, RateLimitMiddleware
)
from routes_auth import router as auth_router
from routes_upload import router as upload_router
from routes_analyze import router as analyze_router
from services import get_supabase_service
from schemas import HealthResponse

# Configuration
settings = get_settings()

# Logging setup
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if settings.LOG_FORMAT != "json"
    else "%(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# Lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("=== GenAI PCE Backend Starting ===")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    try:
        supabase = get_supabase_service()
        is_healthy = await supabase.health_check()
        if is_healthy:
            logger.info("✓ Supabase connection healthy")
        else:
            logger.warning("⚠ Supabase connection check failed")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Supabase: {e}")

    yield

    # Shutdown
    logger.info("=== GenAI PCE Backend Shutting Down ===")


# Create FastAPI app
app = FastAPI(
    title="GenAI Product Consistency Engine API",
    description="Multi-agent AI system for product consistency analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware (order matters - add in reverse order of execution)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CORSMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ExceptionMiddleware)
app.add_middleware(RequestIdMiddleware)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")


# ==== HEALTH CHECK ====

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check endpoint"
)
async def health_check() -> HealthResponse:
    """
    Check application and Supabase health.
    
    **Returns**:
    - status: Application status ("ok" or "degraded")
    - version: API version
    - environment: Current environment
    - timestamp: Current UTC timestamp
    """
    try:
        supabase = get_supabase_service()
        is_healthy = await supabase.health_check()
        
        status_str = "ok" if is_healthy else "degraded"
    except Exception as e:
        logger.error(f"Health check error: {e}")
        status_str = "degraded"

    return HealthResponse(
        status=status_str,
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.utcnow()
    )


# ==== API DOCUMENTATION ====

@app.get("/", tags=["root"], summary="API root endpoint")
async def root() -> dict:
    """
    Get API information.
    
    **Useful links**:
    - API Docs: /docs
    - ReDoc: /redoc
    - OpenAPI Schema: /openapi.json
    - Health: /health
    """
    return {
        "name": "GenAI Product Consistency Engine API",
        "version": "1.0.0",
        "description": "Multi-agent AI system for analyzing product consistency",
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
        },
        "auth": "/api/auth",
        "upload": "/api/upload",
        "analyze": "/api/analyze",
    }


# ==== ERROR HANDLERS ====

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error" if settings.is_production else str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# ==== STARTUP/SHUTDOWN EVENTS ====

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Application shutdown")


# ==== RUN APPLICATION ====

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
