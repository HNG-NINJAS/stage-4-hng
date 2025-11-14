"""RabbitMQ queue consumer for email notifications"""
import pika
import json
import logging
import asyncio
from typing import Optional
from app.config import get_settings
from app.models import EmailNotificationMessage
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailQueueConsumer:
    """RabbitMQ consumer for email.queue"""
    
    def __init__(self, email_service: EmailService):
        self.email_service = email_service
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.queue_name = "email.queue"
        self.running = False
    
    def connect(self) -> bool:
        """Connect to RabbitMQ"""
        try:
            logger.info(f"Connecting to RabbitMQ: {settings.rabbitmq_url}")
            
            parameters = pika.URLParameters(settings.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True,
                arguments={
                    'x-message-ttl': 86400000,  # 24 hours
                    'x-max-length': 10000
                }
            )
            
            # Set QoS
            self.channel.basic_qos(prefetch_count=settings.worker_prefetch_count)
            
            logger.info(f"✅ Connected to RabbitMQ queue: {self.queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {str(e)}")
            return False
    
    def callback(self, ch, method, properties, body):
        """Process message from queue"""
        try:
            # Parse message
            message_data = json.loads(body.decode())
            message = EmailNotificationMessage(**message_data)
            
            logger.info(
                f"📥 Received email notification: {message.message_id}",
                extra={
                    "message_id": message.message_id,
                    "correlation_id": message.correlation_id,
                    "user_id": message.user_id,
                    "template_id": message.template_id
                }
            )
            
            # Process email (async)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(
                self.email_service.send_email(
                    message_id=message.message_id,
                    correlation_id=message.correlation_id,
                    user_id=message.user_id,
                    template_id=message.template_id,
                    template_data=message.template_data,
                    recipient_email=message.recipient_email,
                    language_code=message.language_code
                )
            )
            
            loop.close()
            
            if success:
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"✅ Email notification processed: {message.message_id}")
            else:
                # Reject and requeue (up to retry limit)
                if message.retry_count < 3:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    logger.warning(f"⚠️ Email notification requeued: {message.message_id}")
                else:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    logger.error(f"❌ Email notification failed permanently: {message.message_id}")
                    
        except Exception as e:
            logger.error(f"❌ Error processing message: {str(e)}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Start consuming messages"""
        self.running = True
        
        while self.running:
            try:
                if not self.connection or self.connection.is_closed:
                    if not self.connect():
                        logger.error("Failed to connect, retrying in 5 seconds...")
                        import time
                        time.sleep(5)
                        continue
                
                logger.info(f"👂 Listening for messages on {self.queue_name}...")
                
                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self.callback,
                    auto_ack=False
                )
                
                self.channel.start_consuming()
                
            except KeyboardInterrupt:
                logger.info("Stopping consumer...")
                self.stop()
                break
            except Exception as e:
                logger.error(f"❌ Consumer error: {str(e)}", exc_info=True)
                import time
                time.sleep(5)
    
    def stop(self):
        """Stop consuming"""
        self.running = False
        
        if self.channel and not self.channel.is_closed:
            self.channel.stop_consuming()
        
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        
        logger.info("Consumer stopped")
