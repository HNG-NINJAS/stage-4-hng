#!/usr/bin/env python3
"""
Test script to verify RabbitMQ is working correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.rabbitmq import get_rabbitmq_client
import time

def test_rabbitmq():
    """Test RabbitMQ connection and event publishing"""
    print("🧪 Testing RabbitMQ Connection...")
    print("-" * 50)
    
    # Get RabbitMQ client
    client = get_rabbitmq_client()
    
    # Test connection
    if client.connection and not client.connection.is_closed:
        print("✅ RabbitMQ connection established")
    else:
        print("❌ RabbitMQ connection failed")
        return False
    
    # Test publishing
    print("\n📤 Testing event publishing...")
    test_message = {
        'test': 'message',
        'timestamp': time.time(),
        'action': 'test_event'
    }
    
    success = client.publish_event(
        routing_key='template.test',
        message=test_message,
        correlation_id='test-123'
    )
    
    if success:
        print("✅ Event published successfully")
    else:
        print("❌ Event publishing failed")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All RabbitMQ tests passed!")
    print("=" * 50)
    print("\n💡 Tips:")
    print("1. Check RabbitMQ Management UI: http://localhost:15672")
    print("2. Username: admin, Password: admin123")
    print("3. Look for 'template.events' exchange")
    print("4. Check message rates and queues")
    
    return True

if __name__ == "__main__":
    try:
        success = test_rabbitmq()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
