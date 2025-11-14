#!/bin/bash

# Start Minimal System (without user-service)
echo "=========================================="
echo "Starting Minimal Notification System"
echo "=========================================="
echo ""
echo "This starts 4 core services:"
echo "  ✅ API Gateway"
echo "  ✅ Template Service"
echo "  ✅ Push Service"
echo "  ✅ Email Service"
echo ""
echo "User Service is skipped (not needed for demo)"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Building services...${NC}"
docker-compose -f docker-compose.minimal.yml build

echo ""
echo -e "${YELLOW}Step 2: Starting services...${NC}"
docker-compose -f docker-compose.minimal.yml up -d

echo ""
echo -e "${YELLOW}Step 3: Waiting for services to be healthy (30 seconds)...${NC}"
sleep 30

echo ""
echo -e "${YELLOW}Step 4: Seeding templates...${NC}"
docker-compose -f docker-compose.minimal.yml exec template-service python scripts/seed_templates.py

echo ""
echo -e "${GREEN}✅ System is ready!${NC}"
echo ""
echo "Service URLs:"
echo "  API Gateway:      http://localhost:3000"
echo "  Template Service: http://localhost:3004/docs"
echo "  Push Service:     http://localhost:3003/docs"
echo "  Email Service:    http://localhost:3005/docs"
echo "  RabbitMQ UI:      http://localhost:15672 (admin/admin123)"
echo ""
echo "Test the system:"
echo "  bash scripts/test_all_services.sh"
echo ""
echo "Send test notification:"
echo "  curl -X POST http://localhost:3000/notify/push \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"user_id\":\"test\",\"template_id\":\"welcome_notification\",\"template_data\":{\"name\":\"Test\",\"app_name\":\"App\"},\"device_token\":\"token\"}'"
echo ""
