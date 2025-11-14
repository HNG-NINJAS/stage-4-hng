#!/bin/bash

# Complete setup and test script
echo "=========================================="
echo "Notification System - Setup & Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Starting all services...${NC}"
docker-compose up -d
echo ""

echo -e "${YELLOW}Step 2: Waiting for services to be healthy (30 seconds)...${NC}"
sleep 30
echo ""

echo -e "${YELLOW}Step 3: Seeding templates...${NC}"
docker-compose exec -T template-service python scripts/seed_templates.py
echo ""

echo -e "${YELLOW}Step 4: Running tests...${NC}"
bash scripts/test_all_services.sh
echo ""

echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. View logs: docker-compose logs -f"
echo "  2. Test manually: see TEST_SYSTEM.md"
echo "  3. RabbitMQ UI: http://localhost:15672 (admin/admin123)"
echo ""
