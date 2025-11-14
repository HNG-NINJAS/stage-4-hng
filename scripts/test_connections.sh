#!/bin/bash

# Connection Testing Script
echo "=========================================="
echo "Testing Service Connections"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test function
test_connection() {
    local name=$1
    local command=$2
    
    echo -n "Testing $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Connected${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        return 1
    fi
}

echo "1. Infrastructure Connections"
echo "-----------------------------------"

# Test RabbitMQ
test_connection "RabbitMQ" "docker-compose exec -T rabbitmq rabbitmq-diagnostics -q ping"

# Test Redis
test_connection "Redis" "docker-compose exec -T redis redis-cli -a redis123 ping"

# Test PostgreSQL (Template)
test_connection "PostgreSQL (Template)" "docker-compose exec -T postgres_template pg_isready -U admin -d template_service"

# Test PostgreSQL (User)
test_connection "PostgreSQL (User)" "docker-compose exec -T postgres_user pg_isready -U admin -d user_service"

echo ""
echo "2. Service Health Checks"
echo "-----------------------------------"

# Test API Gateway
test_connection "API Gateway" "curl -sf http://localhost:3000/health"

# Test Template Service
test_connection "Template Service" "curl -sf http://localhost:3004/health"

# Test Push Service
test_connection "Push Service" "curl -sf http://localhost:3003/health"

# Test Email Service
test_connection "Email Service" "curl -sf http://localhost:3005/health"

# Test User Service
test_connection "User Service" "curl -sf http://localhost:3001/health"

echo ""
echo "3. RabbitMQ Queues"
echo "-----------------------------------"
docker-compose exec -T rabbitmq rabbitmqctl list_queues name messages consumers 2>/dev/null | grep -E "push.queue|email.queue" || echo "Queues not yet created (will be created on first use)"

echo ""
echo "4. Inter-Service Communication Test"
echo "-----------------------------------"

# Test API Gateway → Template Service
echo -n "API Gateway → Template Service... "
response=$(docker-compose exec -T api-gateway wget -q -O- http://template-service:3004/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# Test Push Service → Template Service
echo -n "Push Service → Template Service... "
response=$(docker-compose exec -T push-service curl -sf http://template-service:3004/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# Test Email Service → Template Service
echo -n "Email Service → Template Service... "
response=$(docker-compose exec -T email-service curl -sf http://template-service:3004/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

echo ""
echo "5. Database Connections"
echo "-----------------------------------"

# Test Template Service → PostgreSQL
echo -n "Template Service → PostgreSQL... "
docker-compose exec -T template-service python -c "from app.database import check_db_connection; exit(0 if check_db_connection() else 1)" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${YELLOW}⚠ Check logs${NC}"
fi

echo ""
echo "6. Cache Connections"
echo "-----------------------------------"

# Test Redis from Template Service
echo -n "Template Service → Redis... "
docker-compose exec -T template-service python -c "from app.utils.cache import cache_client; cache_client.client.ping() if cache_client.client else exit(1); exit(0)" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${YELLOW}⚠ Check logs${NC}"
fi

echo ""
echo "=========================================="
echo "Connection Test Summary"
echo "=========================================="
echo ""
echo "All critical connections tested."
echo "If any tests failed, check:"
echo "  1. docker-compose ps (all services running?)"
echo "  2. docker-compose logs [service-name]"
echo "  3. Wait 30 seconds and retry"
echo ""
