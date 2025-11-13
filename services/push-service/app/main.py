"""
Push Service - FastAPI app + RabbitMQ worker
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import threading
from datetime import datetime

from app.config import get_settings
from app.services.notification_service import NotificationService
from app.workers.queue_consumer import PushQueueConsumer
from app.utils.response import success_response, error_response

# Configure logging
settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "%(name)s", "message": "%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Global worker thread
worker_thread = None
consumer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global worker_thread, consumer
    
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info("=" * 50)
    
    # Initialize services
    notification_service = NotificationService()
    logger.info("✅ Notification service initialized")
    
    # Start RabbitMQ consumer in background thread
    if settings.worker_enabled:
        consumer = PushQueueConsumer(notification_service)
        worker_thread = threading.Thread(
            target=consumer.start_consuming,
            daemon=True
        )
        worker_thread.start()
        logger.info("✅ RabbitMQ consumer started in background")
    else:
        logger.warning("⚠️ Worker disabled (WORKER_ENABLED=False)")
    
    logger.info(f"🚀 Push Service ready on port {settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Push Service...")
    
    if consumer:
        consumer.stop()
    
    if notification_service.template_client:
        await notification_service.template_client.close()
    
    logger.info("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title="Push Service",
    description="Push notification service for distributed notification system",
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "worker_enabled": settings.worker_enabled
    }


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint
    
    Returns service health and dependency status
    """
    # Check worker status
    worker_status = "running" if worker_thread and worker_thread.is_alive() else "stopped"
    
    # Check FCM (mock mode detection)
    fcm_status = "mock_mode" if settings.fcm_credentials_path is None else "configured"
    
    health_data = {
        "service": settings.service_name,
        "status": "healthy",
        "version": settings.service_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "worker": worker_status,
            "fcm": fcm_status,
            "template_service": settings.template_service_url
        }
    }
    
    return success_response(
        message="Service is healthy",
        data=health_data
    )


@app.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    """Readiness probe for Kubernetes"""
    worker_ready = worker_thread and worker_thread.is_alive()
    
    if worker_ready or not settings.worker_enabled:
        return {"status": "ready"}
    else:
        return {"status": "not_ready"}


@app.get("/live", status_code=status.HTTP_200_OK)
def liveness_check():
    """Liveness probe for Kubernetes"""
    return {"status": "alive"}


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Run with: uvicorn app.main:app --host 0.0.0.0 --port 3003
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )