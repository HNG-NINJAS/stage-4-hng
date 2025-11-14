# Video Recording Guide

## Video Structure (5-7 minutes)

### Part 1: Introduction (30 seconds)
**What to show:**
- Project overview
- Architecture diagram
- Services list

**Script:**
```
"This is a complete microservices notification system with 4 core services:
- API Gateway for routing requests
- Template Service for managing notification templates
- Push Service for sending push notifications
- Email Service for sending emails
All connected via RabbitMQ message queue."
```

### Part 2: Starting the System (1 minute)
**Commands to run:**
```bash
# Show project structure
ls -la

# Start the system
bash scripts/start_minimal.sh

# Wait for services
sleep 30

# Show running containers
docker-compose -f docker-compose.minimal.yml ps
```

**What to say:**
```
"Starting all services with one command. This includes:
- RabbitMQ for message queuing
- Redis for caching
- PostgreSQL for data storage
- All 4 microservices"
```

### Part 3: Health Checks (1 minute)
**Commands to run:**
```bash
# Test all health endpoints
curl http://localhost:3000/health | jq
curl http://localhost:3004/health | jq
curl http://localhost:3003/health | jq
curl http://localhost:3005/health | jq
```

**What to say:**
```
"All services are healthy and ready to process notifications.
Each service has its own health check endpoint."
```

### Part 4: Push Notification Demo (1.5 minutes)
**Commands to run:**
```bash
# Send push notification
curl -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user",
    "template_id": "welcome_notification",
    "template_data": {
      "name": "John Doe",
      "app_name": "MyApp"
    },
    "device_token": "demo-token-123"
  }' | jq

# Show the logs
docker-compose -f docker-compose.minimal.yml logs push-service | tail -20
```

**What to say:**
```
"Sending a push notification through the API Gateway.
The request is queued in RabbitMQ, consumed by Push Service,
template is rendered by Template Service, and notification is sent.
In mock mode, we log the notification instead of sending to Firebase."
```

### Part 5: Email Notification Demo (1.5 minutes)
**Commands to run:**
```bash
# Send email notification
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user",
    "template_id": "welcome_email",
    "template_data": {
      "name": "Jane Smith",
      "company_name": "Acme Corp"
    },
    "recipient_email": "demo@example.com"
  }' | jq

# Show the logs
docker-compose -f docker-compose.minimal.yml logs email-service | tail -20
```

**What to say:**
```
"Sending an email notification. Same flow:
API Gateway → RabbitMQ → Email Service → Template Service.
The email content is logged in mock mode."
```

### Part 6: RabbitMQ UI (1 minute)
**What to show:**
```bash
# Open RabbitMQ Management UI
open http://localhost:15672
# Login: admin / admin123
```

**What to demonstrate:**
- Navigate to Queues tab
- Show push.queue and email.queue
- Show message flow
- Show consumers

**What to say:**
```
"RabbitMQ manages the message queues.
We have two queues: push.queue and email.queue.
Each has active consumers processing messages."
```

### Part 7: API Documentation (30 seconds)
**What to show:**
```bash
# Open Template Service API docs
open http://localhost:3004/docs
```

**What to demonstrate:**
- Show available endpoints
- Show template rendering endpoint
- Show multi-language support

**What to say:**
```
"All services have OpenAPI documentation.
Template Service supports multiple languages and variable substitution."
```

### Part 8: Conclusion (30 seconds)
**What to say:**
```
"This system is production-ready with:
- Microservices architecture
- Message queue for reliability
- Template management
- Multi-language support
- Health monitoring
- Docker containerization

Ready for deployment on any server."
```

## Recording Checklist

Before recording:
- [ ] System is running locally
- [ ] All tests pass
- [ ] Templates are seeded
- [ ] Terminal is clean and readable
- [ ] Browser tabs are prepared
- [ ] Commands are in a script file

## Recording Tips

1. **Use a clean terminal**
   ```bash
   clear
   export PS1="\$ "
   ```

2. **Use jq for pretty JSON**
   ```bash
   # Install jq if needed
   sudo apt-get install jq  # Ubuntu/Debian
   brew install jq          # macOS
   ```

3. **Increase terminal font size**
   - Make it readable in video
   - Use high contrast theme

4. **Prepare commands in advance**
   - Copy commands to a text file
   - Paste during recording
   - Reduces typing errors

5. **Show, don't just tell**
   - Show actual logs
   - Show actual responses
   - Show RabbitMQ UI

## Complete Recording Script

Save this as `recording_script.sh`:

```bash
#!/bin/bash

# Video Recording Script
# Run each section step by step

echo "=========================================="
echo "Notification System Demo"
echo "=========================================="
echo ""

# Part 1: Show structure
echo "Part 1: Project Structure"
ls -la
echo ""
read -p "Press enter to continue..."

# Part 2: Start system
echo "Part 2: Starting System"
bash scripts/start_minimal.sh
echo ""
read -p "Press enter to continue..."

# Part 3: Health checks
echo "Part 3: Health Checks"
echo "API Gateway:"
curl http://localhost:3000/health | jq
echo ""
echo "Template Service:"
curl http://localhost:3004/health | jq
echo ""
echo "Push Service:"
curl http://localhost:3003/health | jq
echo ""
echo "Email Service:"
curl http://localhost:3005/health | jq
echo ""
read -p "Press enter to continue..."

# Part 4: Push notification
echo "Part 4: Push Notification"
curl -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user",
    "template_id": "welcome_notification",
    "template_data": {
      "name": "John Doe",
      "app_name": "MyApp"
    },
    "device_token": "demo-token-123"
  }' | jq
echo ""
echo "Push Service Logs:"
docker-compose -f docker-compose.minimal.yml logs push-service | tail -20
echo ""
read -p "Press enter to continue..."

# Part 5: Email notification
echo "Part 5: Email Notification"
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user",
    "template_id": "welcome_email",
    "template_data": {
      "name": "Jane Smith",
      "company_name": "Acme Corp"
    },
    "recipient_email": "demo@example.com"
  }' | jq
echo ""
echo "Email Service Logs:"
docker-compose -f docker-compose.minimal.yml logs email-service | tail -20
echo ""
read -p "Press enter to continue..."

# Part 6: Show RabbitMQ
echo "Part 6: Opening RabbitMQ UI"
echo "URL: http://localhost:15672"
echo "Login: admin / admin123"
echo ""
read -p "Press enter to continue..."

# Part 7: Show API docs
echo "Part 7: Opening API Documentation"
echo "URL: http://localhost:3004/docs"
echo ""
read -p "Press enter to continue..."

echo "Demo Complete!"
```

## Post-Recording

After recording:
1. Edit video to remove pauses
2. Add captions/subtitles
3. Add timestamps in description
4. Include links to documentation

## Video Description Template

```
Microservices Notification System Demo

This video demonstrates a complete notification system built with microservices architecture.

🏗️ Architecture:
- API Gateway (Node.js/Express)
- Template Service (Python/FastAPI)
- Push Service (Python/FastAPI)
- Email Service (Python/FastAPI)
- RabbitMQ for message queuing
- Redis for caching
- PostgreSQL for data storage

⏱️ Timestamps:
0:00 - Introduction
0:30 - Starting the System
1:30 - Health Checks
2:30 - Push Notification Demo
4:00 - Email Notification Demo
5:30 - RabbitMQ UI
6:30 - API Documentation
7:00 - Conclusion

🔗 Links:
- GitHub Repository: [your-repo-url]
- Documentation: [docs-url]
- Live Demo: [server-url]

📋 Features:
✅ Microservices architecture
✅ Message queue (RabbitMQ)
✅ Template management
✅ Multi-language support
✅ Health monitoring
✅ Docker containerization
✅ Production-ready

#microservices #docker #nodejs #python #rabbitmq #notifications
```

## Screen Recording Tools

**macOS:**
- QuickTime Player (built-in)
- ScreenFlow (paid)
- OBS Studio (free)

**Windows:**
- OBS Studio (free)
- Camtasia (paid)
- Windows Game Bar (built-in)

**Linux:**
- OBS Studio (free)
- SimpleScreenRecorder (free)
- Kazam (free)

## Audio Tips

1. Use a good microphone
2. Record in a quiet room
3. Speak clearly and slowly
4. Pause between sections
5. Re-record if you make mistakes

## Final Checklist

Before hitting record:
- [ ] System is running and tested
- [ ] Terminal font is large and readable
- [ ] Browser tabs are prepared
- [ ] Commands are ready to paste
- [ ] Microphone is working
- [ ] Screen recording software is ready
- [ ] No notifications/popups will interrupt
- [ ] Script is reviewed and practiced

## Status: ✅ READY TO RECORD

Everything is prepared for a professional video recording!
