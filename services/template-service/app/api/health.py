"""
Health check endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import psutil
import os

from app.database import get_db
from app.config import get_settings
from app.utils.response import success_response, error_response

router = APIRouter(tags=["Health"])

# Store service start time
start_time = time.time()
settings = get_settings()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for monitoring and load balancers
    
    Returns:
        Service health status and dependency checks
    """
    # Check database connection
    db_status = "healthy"
    db_error = None
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
    
    # Calculate uptime
    uptime_seconds = int(time.time() - start_time)
    
    # Get system metrics
    memory_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=0.1)
    disk_usage = psutil.disk_usage('/').percent
    
    health_data = {
        "service": settings.service_name,
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.service_version,
        "environment": settings.environment,
        "uptime_seconds": uptime_seconds,
        "timestamp": time.time(),
        "dependencies": {
            "database": {
                "status": db_status,
                "error": db_error
            }
        },
        "system": {
            "memory_usage_percent": memory_usage,
            "cpu_usage_percent": cpu_usage,
            "disk_usage_percent": disk_usage,
            "process_id": os.getpid()
        }
    }
    
    if db_status == "healthy":
        return success_response(
            message="Service is healthy",
            data=health_data
        )
    else:
        return error_response(
            message="Service is degraded",
            error="DEPENDENCY_UNHEALTHY",
            data=health_data
        )


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe - checks if service is ready to accept traffic
    
    Used by Kubernetes/container orchestrators
    """
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        return {"status": "ready", "service": settings.service_name}
    except Exception as e:
        return {
            "status": "not_ready",
            "service": settings.service_name,
            "error": str(e)
        }


@router.get("/live", status_code=status.HTTP_200_OK)
def liveness_check():
    """
    Liveness probe - checks if service is alive
    
    Used by Kubernetes/container orchestrators
    """
    return {
        "status": "alive",
        "service": settings.service_name,
        "uptime_seconds": int(time.time() - start_time)
    }