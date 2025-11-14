# Email Service (Mock)

Mock email service for testing the notification system. Logs email content instead of sending real emails.

## Features

- ✅ Consumes messages from RabbitMQ `email.queue`
- ✅ Integrates with Template Service for content rendering
- ✅ Mock mode - logs emails instead of sending
- ✅ Health checks and monitoring
- ✅ Ready for production (add real SMTP integration)

## Quick Start

### With Docker

```bash
docker-compose up -d email-service
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn app.main:app --reload --port 3005
```

## Configuration

Environment variables in `.env`:

- `MOCK_MODE=True` - Enable mock mode (logs only)
- `RABBITMQ_URL` - RabbitMQ connection URL
- `TEMPLATE_SERVICE_URL` - Template Service URL
- `WORKER_ENABLED=True` - Enable queue consumer

## Message Format

Consumes messages from `email.queue`:

```json
{
  "message_id": "uuid",
  "correlation_id": "trace-id",
  "user_id": "123",
  "template_id": "welcome_email",
  "template_data": {
    "name": "John Doe"
  },
  "recipient_email": "john@example.com",
  "language_code": "en",
  "priority": "normal",
  "retry_count": 0
}
```

## Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `GET /ready` - Readiness probe
- `GET /live` - Liveness probe

## Production Mode

To send real emails, set `MOCK_MODE=False` and implement SMTP logic in `app/services/email_service.py`.

Example SMTP integration:
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure SMTP
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "your-email@gmail.com"
smtp_password = "your-password"

# Send email
msg = MIMEMultipart()
msg['From'] = smtp_user
msg['To'] = recipient_email
msg['Subject'] = rendered['subject']
msg.attach(MIMEText(rendered['body'], 'html'))

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.send_message(msg)
```
