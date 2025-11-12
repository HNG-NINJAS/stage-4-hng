# RabbitMQ Event Integration

Guide for consuming Template Service events via RabbitMQ.

## Overview

Template Service publishes events to RabbitMQ when templates are created, updated, or deleted. Services can listen to these events for:

- Cache invalidation
- Audit logging
- Analytics
- Workflow triggers

## Event Architecture

```
Template Service
       │
       │ publishes
       ▼
  RabbitMQ Exchange
  (template.events)
       │
       ├─── template.created
       ├─── template.updated
       └─── template.deleted
       │
       │ consumed by
       ▼
Other Services
```

## Published Events

| Event | Routing Key | Payload |
|-------|-------------|---------|
| Template Created | `template.created` | `{template_id, name, type, created_at}` |
| Template Updated | `template.updated` | `{template_id, name, updated_at}` |
| Template Deleted | `template.deleted` | `{template_id, deleted_at}` |

**Exchange:** `template.events` (topic, durable)

## Event Payloads

### template.created
```json
{
  "template_id": "welcome_email",
  "name": "Welcome Email",
  "type": "email",
  "created_at": "2025-11-12T10:30:00Z"
}
```

### template.updated
```json
{
  "template_id": "welcome_email",
  "name": "Welcome Email - Updated",
  "updated_at": "2025-11-12T11:45:00Z"
}
```

### template.deleted
```json
{
  "template_id": "old_template",
  "deleted_at": 1699612800.123
}
```

## Python Consumer

### Installation
```bash
pip install pika
```

### Implementation

Create `template_event_consumer.py`:

```python
import pika
import json
import logging
import signal
import sys
from typing import Callable, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateEventConsumer:
    """Consumer for Template Service events"""
    
    def __init__(
        self, 
        service_name: str,
        rabbitmq_url: str = "amqp://admin:admin123@rabbitmq:5672/"
    ):
        self.service_name = service_name
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.queue_name = f"{service_name}_template_events"
        self.event_handlers: Dict[str, Callable] = {}
    
    def on(self, event_type: str, handler: Callable):
        """Register event handler"""
        self.event_handlers[event_type] = handler
        logger.info(f"Registered handler for '{event_type}'")
    
    def connect(self) -> bool:
        """Connect to RabbitMQ"""
        try:
            logger.info("Connecting to RabbitMQ...")
            
            parameters = pika.URLParameters(self.rabbitmq_url)
            parameters.heartbeat = 600
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            # Bind to template events
            self.channel.queue_bind(
                queue=self.queue_name,
                exchange='template.events',
                routing_key='template.*'
            )
            
            logger.info(f"✅ Connected to RabbitMQ")
            logger.info(f"✅ Listening to 'template.*' events")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to connect: {str(e)}")
            return False
    
    def callback(self, ch, method, properties, body):
        """Process incoming events"""
        try:
            event = json.loads(body)
            routing_key = method.routing_key
            correlation_id = properties.correlation_id or 'unknown'
            
            logger.info(f"📥 Received: {routing_key}")
            
            # Handle event
            handler = self.event_handlers.get(routing_key)
            if handler:
                handler(event, correlation_id)
            
            # Acknowledge
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self):
        """Start consuming events"""
        if not self.connect():
            sys.exit(1)
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            self.channel.basic_qos(prefetch_count=10)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback
            )
            
            logger.info("🎧 Started consuming events...")
            self.channel.start_consuming()
        
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop consuming"""
        logger.info("Stopping consumer...")
        
        try:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                self.channel.close()
            
            if self.connection and self.connection.is_open:
                self.connection.close()
            
            logger.info("✅ Stopped gracefully")
        except Exception as e:
            logger.error(f"Error stopping: {str(e)}")
    
    def _signal_handler(self, signum, frame):
        self.stop()
        sys.exit(0)


# Event Handlers
def handle_template_created(event: dict, correlation_id: str):
    """Handle template.created"""
    template_id = event.get('template_id')
    logger.info(f"📝 Template created: {template_id}")
    # Your logic here (e.g., warm up cache)


def handle_template_updated(event: dict, correlation_id: str):
    """Handle template.updated"""
    template_id = event.get('template_id')
    logger.info(f"♻️  Template updated: {template_id}")
    # Your logic here (e.g., invalidate cache)


def handle_template_deleted(event: dict, correlation_id: str):
    """Handle template.deleted"""
    template_id = event.get('template_id')
    logger.info(f"🗑️  Template deleted: {template_id}")
    # Your logic here (e.g., clean up references)


# Usage
if __name__ == "__main__":
    consumer = TemplateEventConsumer(
        service_name="email-service",
        rabbitmq_url="amqp://admin:admin123@rabbitmq:5672/"
    )
    
    consumer.on('template.created', handle_template_created)
    consumer.on('template.updated', handle_template_updated)
    consumer.on('template.deleted', handle_template_deleted)
    
    consumer.start()
```

## TypeScript/Node.js Consumer

### Installation
```bash
npm install amqplib
```

### Implementation

Create `templateEventConsumer.ts`:

```typescript
import * as amqp from 'amqplib';

interface TemplateEvent {
  template_id: string;
  name?: string;
  type?: string;
  created_at?: string;
  updated_at?: string;
  deleted_at?: number;
}

type EventHandler = (event: TemplateEvent, correlationId: string) => void | Promise<void>;

export class TemplateEventConsumer {
  private connection: amqp.Connection | null = null;
  private channel: amqp.Channel | null = null;
  private eventHandlers: Map<string, EventHandler> = new Map();
  private queueName: string;

  constructor(
    private serviceName: string,
    private rabbitmqUrl: string = 'amqp://admin:admin123@rabbitmq:5672/'
  ) {
    this.queueName = `${serviceName}_template_events`;
  }

  on(eventType: string, handler: EventHandler): void {
    this.eventHandlers.set(eventType, handler);
    console.log(`Registered handler for '${eventType}'`);
  }

  async connect(): Promise<boolean> {
    try {
      console.log('Connecting to RabbitMQ...');

      this.connection = await amqp.connect(this.rabbitmqUrl, {
        heartbeat: 600
      });

      this.channel = await this.connection.createChannel();

      await this.channel.assertQueue(this.queueName, {
        durable: true
      });

      await this.channel.bindQueue(
        this.queueName,
        'template.events',
        'template.*'
      );

      console.log('✅ Connected to RabbitMQ');
      console.log(`✅ Listening to 'template.*' events`);

      return true;
    } catch (error) {
      console.error('❌ Failed to connect:', error);
      return false;
    }
  }

  async start(): Promise<void> {
    if (!await this.connect()) {
      process.exit(1);
    }

    if (!this.channel) {
      throw new Error('Channel not initialized');
    }

    process.on('SIGINT', () => this.stop());
    process.on('SIGTERM', () => this.stop());

    await this.channel.prefetch(10);

    await this.channel.consume(this.queueName, async (msg) => {
      if (!msg) return;

      try {
        const event: TemplateEvent = JSON.parse(msg.content.toString());
        const routingKey = msg.fields.routingKey;
        const correlationId = msg.properties.correlationId || 'unknown';

        console.log(`📥 Received: ${routingKey}`);

        const handler = this.eventHandlers.get(routingKey);
        if (handler) {
          await handler(event, correlationId);
        }

        this.channel!.ack(msg);
      } catch (error) {
        console.error('Error processing event:', error);
        this.channel!.nack(msg, false, true);
      }
    });

    console.log('🎧 Started consuming events...');
  }

  async stop(): Promise<void> {
    console.log('Stopping consumer...');

    try {
      if (this.channel) {
        await this.channel.close();
      }

      if (this.connection) {
        await this.connection.close();
      }

      console.log('✅ Stopped gracefully');
      process.exit(0);
    } catch (error) {
      console.error('Error stopping:', error);
      process.exit(1);
    }
  }
}

// Event Handlers
async function handleTemplateCreated(
  event: TemplateEvent,
  correlationId: string
): Promise<void> {
  console.log(`📝 Template created: ${event.template_id}`);
  // Your logic here
}

async function handleTemplateUpdated(
  event: TemplateEvent,
  correlationId: string
): Promise<void> {
  console.log(`♻️  Template updated: ${event.template_id}`);
  // Your logic here
}

async function handleTemplateDeleted(
  event: TemplateEvent,
  correlationId: string
): Promise<void> {
  console.log(`🗑️  Template deleted: ${event.template_id}`);
  // Your logic here
}

// Usage
const consumer = new TemplateEventConsumer(
  'email-service',
  'amqp://admin:admin123@rabbitmq:5672/'
);

consumer.on('template.created', handleTemplateCreated);
consumer.on('template.updated', handleTemplateUpdated);
consumer.on('template.deleted', handleTemplateDeleted);

consumer.start().catch(console.error);
```

## C#/.NET Consumer

### Installation
```bash
dotnet add package RabbitMQ.Client
```

### Implementation

```csharp
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;
using System.Text.Json;

namespace NotificationSystem.Events
{
    public class TemplateEventConsumer
    {
        private readonly string _serviceName;
        private readonly string _rabbitmqUrl;
        private IConnection? _connection;
        private IModel? _channel;
        private readonly Dictionary<string, Action<TemplateEvent, string>> _handlers = new();

        public TemplateEventConsumer(string serviceName, string rabbitmqUrl)
        {
            _serviceName = serviceName;
            _rabbitmqUrl = rabbitmqUrl;
        }

        public void On(string eventType, Action<TemplateEvent, string> handler)
        {
            _handlers[eventType] = handler;
            Console.WriteLine($"Registered handler for '{eventType}'");
        }

        public bool Connect()
        {
            try
            {
                Console.WriteLine("Connecting to RabbitMQ...");

                var factory = new ConnectionFactory
                {
                    Uri = new Uri(_rabbitmqUrl),
                    RequestedHeartbeat = TimeSpan.FromSeconds(600)
                };

                _connection = factory.CreateConnection();
                _channel = _connection.CreateModel();

                var queueName = $"{_serviceName}_template_events";

                _channel.QueueDeclare(
                    queue: queueName,
                    durable: true,
                    exclusive: false,
                    autoDelete: false
                );

                _channel.QueueBind(
                    queue: queueName,
                    exchange: "template.events",
                    routingKey: "template.*"
                );

                Console.WriteLine("✅ Connected to RabbitMQ");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to connect: {ex.Message}");
                return false;
            }
        }

        public void Start()
        {
            if (!Connect())
            {
                Environment.Exit(1);
            }

            var queueName = $"{_serviceName}_template_events";
            var consumer = new EventingBasicConsumer(_channel);

            consumer.Received += (model, ea) =>
            {
                try
                {
                    var body = ea.Body.ToArray();
                    var message = Encoding.UTF8.GetString(body);
                    var @event = JsonSerializer.Deserialize<TemplateEvent>(message);
                    var routingKey = ea.RoutingKey;
                    var correlationId = ea.BasicProperties.CorrelationId ?? "unknown";

                    Console.WriteLine($"📥 Received: {routingKey}");

                    if (_handlers.TryGetValue(routingKey, out var handler) && @event != null)
                    {
                        handler(@event, correlationId);
                    }

                    _channel?.BasicAck(ea.DeliveryTag, false);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error processing event: {ex.Message}");
                    _channel?.BasicNack(ea.DeliveryTag, false, true);
                }
            };

            _channel?.BasicQos(0, 10, false);
            _channel?.BasicConsume(queue: queueName, autoAck: false, consumer: consumer);

            Console.WriteLine("🎧 Started consuming events...");
            Console.WriteLine("Press Enter to exit");
            Console.ReadLine();

            Stop();
        }

        public void Stop()
        {
            Console.WriteLine("Stopping consumer...");
            _channel?.Close();
            _connection?.Close();
            Console.WriteLine("✅ Stopped gracefully");
        }
    }

    public class TemplateEvent
    {
        public string template_id { get; set; } = "";
        public string? name { get; set; }
        public string? type { get; set; }
        public string? created_at { get; set; }
        public string? updated_at { get; set; }
        public double? deleted_at { get; set; }
    }
}
```

## Use Cases

### Cache Invalidation
```python
def handle_template_updated(event: dict, correlation_id: str):
    template_id = event.get('template_id')
    # Invalidate cache
    cache.delete(f"template:{template_id}")
    logger.info(f"Cache invalidated for {template_id}")
```

### Audit Logging
```python
def handle_template_created(event: dict, correlation_id: str):
    # Log to audit system
    audit_log.record({
        "event": "template_created",
        "template_id": event.get('template_id'),
        "timestamp": event.get('created_at'),
        "correlation_id": correlation_id
    })
```

### Analytics
```python
def handle_template_deleted(event: dict, correlation_id: str):
    # Send to analytics
    analytics.track("template_deleted", {
        "template_id": event.get('template_id'),
        "deleted_at": event.get('deleted_at')
    })
```

## Best Practices

1. **Use durable queues** for reliability
2. **Implement idempotency** - events may be delivered multiple times
3. **Handle errors gracefully** - use dead letter queues
4. **Monitor queue depth** - detect processing issues
5. **Use correlation IDs** for distributed tracing
6. **Implement graceful shutdown** - clean up connections
7. **Set appropriate prefetch** - control concurrency
8. **Log all events** - for debugging and audit

## Next Steps

- Review [Integration Overview](./overview.md)
- Set up [Monitoring](../operations/monitoring.md)
- Configure [Deployment](../operations/deployment.md)
