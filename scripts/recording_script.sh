#!/bin/bash

# Video Recording Script
# Run each section step by step for video recording

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear

echo "=========================================="
echo "Notification System Demo"
echo "=========================================="
echo ""
echo "Press ENTER to start each section..."
echo ""

# Part 1: Introduction
echo -e "${BLUE}Part 1: Introduction & Project Structure${NC}"
read -p "Press ENTER to continue..."
clear
echo "Project Structure:"
ls -la
echo ""
echo "Services:"
echo "  - API Gateway (Node.js)"
echo "  - Template Service (Python)"
echo "  - Push Service (Python)"
echo "  - Email Service (Python)"
echo ""
read -p "Press ENTER to continue..."

# Part 2: Start System
clear
echo -e "${BLUE}Part 2: Starting the System${NC}"
read -p "Press ENTER to start services..."
bash scripts/start_minimal.sh
echo ""
read -p "Press ENTER to continue..."

# Part 3: Verify Services
clear
echo -e "${BLUE}Part 3: Verifying Services${NC}"
read -p "Press ENTER to check services..."
echo ""
echo "Container Status:"
docker-compose -f docker-compose.minimal.yml ps
echo ""
read -p "Press ENTER to continue..."

# Part 4: Health Checks
clear
echo -e "${BLUE}Part 4: Health Checks${NC}"
read -p "Press ENTER to check health..."
echo ""
echo "API Gateway Health:"
curl -s http://localhost:3000/health | jq
echo ""
echo "Template Service Health:"
curl -s http://localhost:3004/health | jq
echo ""
echo "Push Service Health:"
curl -s http://localhost:3003/health | jq
echo ""
echo "Email Service Health:"
curl -s http://localhost:3005/health | jq
echo ""
read -p "Press ENTER to continue..."

# Part 5: Push Notification
clear
echo -e "${BLUE}Part 5: Push Notification Demo${NC}"
read -p "Press ENTER to send push notification..."
echo ""
echo "Sending push notification..."
curl -s -X POST http://localhost:3000/notify/push \
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
echo "Waiting for processing..."
sleep 2
echo ""
echo "Push Service Logs:"
docker-compose -f docker-compose.minimal.yml logs --tail=15 push-service | grep -E "Received|Template|notification sent|MOCK"
echo ""
read -p "Press ENTER to continue..."

# Part 6: Email Notification
clear
echo -e "${BLUE}Part 6: Email Notification Demo${NC}"
read -p "Press ENTER to send email notification..."
echo ""
echo "Sending email notification..."
curl -s -X POST http://localhost:3000/notify/email \
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
echo "Waiting for processing..."
sleep 2
echo ""
echo "Email Service Logs:"
docker-compose -f docker-compose.minimal.yml logs --tail=15 email-service | grep -E "Processing|Template|Email sent|MOCK"
echo ""
read -p "Press ENTER to continue..."

# Part 7: RabbitMQ UI
clear
echo -e "${BLUE}Part 7: RabbitMQ Management UI${NC}"
echo ""
echo "Opening RabbitMQ UI..."
echo "URL: http://localhost:15672"
echo "Login: admin / admin123"
echo ""
echo "Navigate to Queues tab to see:"
echo "  - push.queue"
echo "  - email.queue"
echo ""
read -p "Press ENTER to continue..."

# Part 8: API Documentation
clear
echo -e "${BLUE}Part 8: API Documentation${NC}"
echo ""
echo "Opening Template Service API Documentation..."
echo "URL: http://localhost:3004/docs"
echo ""
echo "Features:"
echo "  - Template CRUD operations"
echo "  - Template rendering"
echo "  - Multi-language support"
echo ""
read -p "Press ENTER to continue..."

# Part 9: Conclusion
clear
echo -e "${BLUE}Part 9: Conclusion${NC}"
echo ""
echo "System Features:"
echo "  ✅ Microservices architecture"
echo "  ✅ Message queue (RabbitMQ)"
echo "  ✅ Template management"
echo "  ✅ Multi-language support"
echo "  ✅ Health monitoring"
echo "  ✅ Docker containerization"
echo "  ✅ Production-ready"
echo ""
echo "Services Running:"
docker-compose -f docker-compose.minimal.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo -e "${GREEN}Demo Complete!${NC}"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.minimal.yml down"
echo ""
