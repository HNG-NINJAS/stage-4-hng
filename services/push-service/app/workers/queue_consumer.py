import pika
import json
import logging
import asyncio
from typing import Callable
from app.config import get_settings
from app.models import PushNotificationRequest
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)
settings = get_settings()


class PushQueueConsumer:
    """Consumes messages from push.queue"""
    
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
        self.connection = None
        self.channel = None
        self.consuming = False
    
    def connect(self) -> bool:
        """Connect to RabbitMQ"""
        try:
            logger.info("Connecting to RabbitMQ...")
            
            parameters = pika.URLParameters(settings.rabbitmq_url)
            parameters.heartbeat = 600
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue with DLQ
            self.channel.queue_declare(
                queue=settings.push_queue_name,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': 'notifications.dlx',
                    'x-dead-letter-routing-key': 'failed'
                }
            )
            
            logger.info(f"✅ Connected to RabbitMQ")
            logger.info(f"✅ Queue '{settings.push_queue_name}' ready")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {str(e)}")
            return False
    
    def callback(self, ch, method, properties, body):
        """Process incoming messages"""
        try:
            # Parse message
            message = json.loads(body)
            correlation_id = properties.correlation_id or 'unknown'
            
            logger.info(
                f"📥 Received push notification request",
                extra={'correlation_id': correlation_id}
            )
            
            # Convert to model
            request = PushNotificationRequest(**message)
            
            # Process notification (async)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.notification_service.send_notification(request)
            )
            loop.close()
            
            if result.success:
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"✅ Push notification sent to user {request.user_id}")
            else:
                # Retry or send to DLQ
                if request.retry_count < 3:
                    # Requeue for retry
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    logger.warning(f"⚠️ Requeuing message (retry {request.retry_count + 1})")
                else:
                    # Send to DLQ
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    logger.error(f"❌ Message sent to DLQ after 3 retries")
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages"""
        if not self.connect():
            raise Exception("Failed to connect to RabbitMQ")
        
        try:
            self.channel.basic_qos(prefetch_count=settings.worker_prefetch_count)
            self.channel.basic_consume(
                queue=settings.push_queue_name,
                on_message_callback=self.callback
            )
            
            logger.info("🎧 Started consuming push notifications...")
            logger.info("Press Ctrl+C to stop")
            
            self.consuming = True
            self.channel.start_consuming()
        
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.stop()
    
    def stop(self):
        """Stop consuming"""
        logger.info("Stopping queue consumer...")
        
        try:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                self.channel.close()
            
            if self.connection and self.connection.is_open:
                self.connection.close()
            
            logger.info("✅ Consumer stopped gracefully")
        
        except Exception as e:
            logger.error(f"Error stopping consumer: {str(e)}")