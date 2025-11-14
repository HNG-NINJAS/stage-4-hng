"""
Email Service - Mock implementation for testing
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import threading
from datetime import datetime

from app.config import get_settings
from app.services.email_service import EmailService
from app.workers.queue_consumer import EmailQueueConsumer

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
    logger.info(f"Mock Mode: {settings.mock_mode}")
    logger.info("=" * 50)
    
    # Initialize services
    email_service = EmailService()
    logger.info("✅ Email service initialized")
    
    # Start RabbitMQ consumer in background thread
    if settings.worker_enabled:
        consumer = EmailQueueConsumer(email_service)
        worker_thread = threading.Thread(
            target=consumer.start_consuming,
            daemon=True
        )
        worker_thread.start()
        logger.info("✅ RabbitMQ consumer started in background")
    else:
        logger.warning("⚠️ Worker disabled (WORKER_ENABLED=False)")
    
    logger.info(f"🚀 Email Service ready on port {settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Email Service...")
    
    if consumer:
        consumer.stop()
    
    if email_service.template_client:
        await email_service.template_client.close()
    
    logger.info("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title="Email Service (Mock)",
    description="Mock email service for testing - logs emails instead of sending",
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
        "mock_mode": settings.mock_mode,
        "worker_enabled": settings.worker_enabled
    }


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint"""
    worker_status = "running" if worker_thread and worker_thread.is_alive() else "stopped"
    
    return {
        "success": True,
        "message": "Service is healthy",
        "data": {
            "service": settings.service_name,
            "status": "healthy",
            "version": settings.service_version,
            "environment": settings.environment,
            "mock_mode": settings.mock_mode,
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "worker": worker_status,
                "template_service": settings.template_service_url
            }
        }
    }


@app.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    """Readiness probe"""
    worker_ready = worker_thread and worker_thread.is_alive()
    
    if worker_ready or not settings.worker_enabled:
        return {"status": "ready"}
    else:
        return {"status": "not_ready"}


@app.get("/live", status_code=status.HTTP_200_OK)
def liveness_check():
    """Liveness probe"""
    return {"status": "alive"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
