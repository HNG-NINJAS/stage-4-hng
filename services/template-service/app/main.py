"""
FastAPI application entry point
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging
import sys
from typing import Union

from app.config import get_settings
from app.database import init_db, check_db_connection
from app.api import templates, health, metrics
from app.api.metrics import track_request

# Configure logging
settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "%(name)s", "message": "%(message)s", "correlation_id": "%(correlation_id)s"}',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add correlation_id filter
class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = 'none'
        return True

for handler in logging.root.handlers:
    handler.addFilter(CorrelationIdFilter())

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info("=" * 50)
    
    # Skip database initialization if running tests (dependency override is set)
    if not app.dependency_overrides:
        # Initialize database
        try:
            init_db()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {str(e)}")
            raise
        
        # Check database connection
        if check_db_connection():
            logger.info("✅ Database connection verified")
        else:
            logger.warning("⚠️ Database connection check failed")
    else:
        logger.info("⚠️ Running in test mode - skipping database initialization")
    
    logger.info(f"🚀 Service ready on port {settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Template Service...")
    logger.info("👋 Goodbye!")


# Create FastAPI application
app = FastAPI(
    title="Template Service",
    description="Notification template management microservice",
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging and timing middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and add correlation ID"""
    start_time = time.time()
    
    # Get or generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", f"gen-{int(time.time()*1000)}")
    
    # Add to request state for access in routes
    request.state.correlation_id = correlation_id
    
    # Log request
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # Process request
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(
            f"Request failed: {str(e)}",
            extra={"correlation_id": correlation_id},
            exc_info=True
        )
        raise
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Track metrics
    track_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    )
    
    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path} - {response.status_code}",
        extra={
            "correlation_id": correlation_id,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2)
        }
    )
    
    # Add headers
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time"] = f"{duration:.4f}"
    response.headers["X-Service-Version"] = settings.service_version
    
    return response


# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"correlation_id": correlation_id}
    )
    
    return JSONResponse(
        status_code=422,  # HTTP_422_UNPROCESSABLE_CONTENT
        content={
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors(),
            "meta": {
                "total": 0,
                "limit": 10,
                "page": 1,
                "total_pages": 0,
                "has_next": False,
                "has_previous": False
            }
        }
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "error": str(exc)
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "correlation_id": correlation_id,
            "meta": {
                "total": 0,
                "limit": 10,
                "page": 1,
                "total_pages": 0,
                "has_next": False,
                "has_previous": False
            }
        }
    )


# Include routers
app.include_router(health.router)
app.include_router(templates.router)
app.include_router(metrics.router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint - service information"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health"
    }


# Run with: uvicorn app.main:app --reload --port 3004
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )