#!/bin/bash

# Fix Port Conflicts and Start System
echo "=========================================="
echo "Fixing Port Conflicts & Starting System"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Stopping any running containers...${NC}"
docker-compose down 2>/dev/null
docker-compose -f docker-compose.minimal.yml down 2>/dev/null
echo ""

echo -e "${YELLOW}Step 2: Checking port conflicts...${NC}"
if lsof -i :5432 > /dev/null 2>&1; then
    echo -e "${RED}⚠️  Port 5432 is in use (local PostgreSQL running)${NC}"
    echo "   Using minimal setup to avoid conflict..."
else
    echo -e "${GREEN}✓ Port 5432 is available${NC}"
fi
echo ""

echo -e "${YELLOW}Step 3: Starting minimal setup (avoids port conflicts)...${NC}"
docker-compose -f docker-compose.minimal.yml up -d
echo ""

echo -e "${YELLOW}Step 4: Waiting for services (30 seconds)...${NC}"
sleep 30
echo ""

echo -e "${YELLOW}Step 5: Seeding templates...${NC}"
docker-compose -f docker-compose.minimal.yml exec -T template-service python scripts/seed_templates.py
echo ""

echo -e "${YELLOW}Step 6: Checking service status...${NC}"
docker-compose -f docker-compose.minimal.yml ps
echo ""

echo -e "${GREEN}✅ System started successfully!${NC}"
echo ""
echo "Service URLs:"
echo "  API Gateway:      http://localhost:3000"
echo "  Template Service: http://localhost:3004/docs"
echo "  Push Service:     http://localhost:3003/docs"
echo "  Email Service:    http://localhost:3005/docs"
echo "  RabbitMQ UI:      http://localhost:15672 (admin/admin123)"
echo ""
echo "Test the system:"
echo "  bash scripts/test_complete_system.sh"
echo ""
echo "Record video:"
echo "  bash scripts/recording_script.sh"
echo ""
