#!/usr/bin/env python3
"""
Publish a test notification to push.queue

Usage: python scripts/publish_test_notification.py
"""

import pika
import json
import uuid
import sys
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin123@localhost:5672/")
QUEUE_NAME = "push.queue"


def publish_test_notification():
    """Publish test notification to queue"""
    print("📤 Publishing test notification...")
    print(f"   RabbitMQ URL: {RABBITMQ_URL}")
    print()
    
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.URLParameters(RABBITMQ_URL)
        )
        channel = connection.channel()
        
        # Declare queue with same arguments as the worker
        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'notifications.dlx',
                'x-dead-letter-routing-key': 'failed'
            }
        )
        
        # Create test message
        message = {
            "message_id": str(uuid.uuid4()),
            "correlation_id": f"test-{uuid.uuid4()}",
            "user_id": "test-user-123",
            "template_id": "order_shipped",
            "template_data": {
                "name": "John Doe",
                "order_id": "ORD-98765",
                "tracking_url": "https://example.com/track/98765"
            },
            "device_token": "test-fcm-device-token-123456789",
            "language_code": "en",
            "priority": "high",
            "retry_count": 0
        }
        
        # Publish
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                correlation_id=message["correlation_id"],
                content_type='application/json'
            )
        )
        
        print(f"✅ Message published successfully!")
        print(f"   Message ID: {message['message_id']}")
        print(f"   User ID: {message['user_id']}")
        print(f"   Template: {message['template_id']}")
        print()
        print("Check Push Service logs:")
        print("  docker-compose logs -f push-service")
        print()
        
        connection.close()
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print("Make sure RabbitMQ is running and accessible:")
        print(f"  Current URL: {RABBITMQ_URL}")
        print()
        print("If RabbitMQ is in Docker, try:")
        print("  export RABBITMQ_URL='amqp://admin:admin123@localhost:5672/'")
        print("  # Or check your docker-compose port mapping")
        print()
        print("If running locally:")
        print("  docker-compose up -d rabbitmq")
        return False


if __name__ == "__main__":
    success = publish_test_notification()
    sys.exit(0 if success else 1)