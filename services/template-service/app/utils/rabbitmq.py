"""
RabbitMQ connection and publishing utilities
"""

import pika
import json
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from pybreaker import CircuitBreaker
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RabbitMQClient:
    """RabbitMQ client with circuit breaker and retry logic"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.circuit_breaker = CircuitBreaker(
            fail_max=5,
            reset_timeout=60,
            name="rabbitmq_breaker"
        )
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            # Parse RabbitMQ URL
            rabbitmq_url = getattr(settings, 'rabbitmq_url', 'amqp://admin:admin123@localhost:5672/')
            
            parameters = pika.URLParameters(rabbitmq_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchanges and queues
            self._setup_exchanges()
            
            logger.info("✅ Connected to RabbitMQ")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {str(e)}")
            return False
    
    def _setup_exchanges(self):
        """Setup RabbitMQ exchanges and queues"""
        # Main exchange for template events
        self.channel.exchange_declare(
            exchange='template.events',
            exchange_type='topic',
            durable=True
        )
        
        # Dead letter exchange
        self.channel.exchange_declare(
            exchange='template.dlx',
            exchange_type='direct',
            durable=True
        )
        
        # Dead letter queue
        self.channel.queue_declare(
            queue='template.events.dlq',
            durable=True
        )
        
        self.channel.queue_bind(
            queue='template.events.dlq',
            exchange='template.dlx',
            routing_key='failed'
        )
        
        logger.info("✅ RabbitMQ exchanges and queues configured")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def publish_event(
        self, 
        routing_key: str, 
        message: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish event to RabbitMQ with circuit breaker and retry
        
        Args:
            routing_key: Routing key (e.g., 'template.created', 'template.updated')
            message: Message payload
            correlation_id: Correlation ID for tracing
            
        Returns:
            True if published successfully
        """
        try:
            # Use circuit breaker
            @self.circuit_breaker
            def _publish():
                if not self.connection or self.connection.is_closed:
                    self.connect()
                
                properties = pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json',
                    correlation_id=correlation_id or 'unknown'
                )
                
                self.channel.basic_publish(
                    exchange='template.events',
                    routing_key=routing_key,
                    body=json.dumps(message),
                    properties=properties
                )
                
                logger.info(f"📤 Published event: {routing_key}", extra={
                    "correlation_id": correlation_id,
                    "routing_key": routing_key
                })
                
                return True
            
            return _publish()
        
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}", extra={
                "routing_key": routing_key,
                "correlation_id": correlation_id
            })
            return False
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {str(e)}")


# Global RabbitMQ client instance
rabbitmq_client = RabbitMQClient()


def get_rabbitmq_client() -> RabbitMQClient:
    """Get or create RabbitMQ client"""
    if not rabbitmq_client.connection or rabbitmq_client.connection.is_closed:
        rabbitmq_client.connect()
    return rabbitmq_client