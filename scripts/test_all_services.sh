#!/bin/bash

# Test script for all services
echo "=========================================="
echo "Testing Notification System"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
        return 1
    fi
}

# Test all services
echo "1. Testing Service Health Checks"
echo "-----------------------------------"
test_endpoint "API Gateway" "http://localhost:3000/health"
test_endpoint "Template Service" "http://localhost:3004/health"
test_endpoint "Push Service" "http://localhost:3003/health"
test_endpoint "Email Service" "http://localhost:3005/health"
test_endpoint "User Service" "http://localhost:3001/health"
echo ""

# Test RabbitMQ
echo "2. Testing RabbitMQ"
echo "-----------------------------------"
test_endpoint "RabbitMQ Management" "http://localhost:15672"
echo ""

# Test Redis
echo "3. Testing Redis"
echo "-----------------------------------"
if docker-compose exec -T redis redis-cli -a redis123 ping > /dev/null 2>&1; then
    echo -e "Testing Redis... ${GREEN}✓ OK${NC}"
else
    echo -e "Testing Redis... ${RED}✗ FAILED${NC}"
fi
echo ""

# Test databases
echo "4. Testing Databases"
echo "-----------------------------------"
if docker-compose exec -T postgres_template pg_isready -U admin > /dev/null 2>&1; then
    echo -e "Testing Template DB... ${GREEN}✓ OK${NC}"
else
    echo -e "Testing Template DB... ${RED}✗ FAILED${NC}"
fi

if docker-compose exec -T postgres_user pg_isready -U admin > /dev/null 2>&1; then
    echo -e "Testing User DB... ${GREEN}✓ OK${NC}"
else
    echo -e "Testing User DB... ${RED}✗ FAILED${NC}"
fi
echo ""

# Test push notification
echo "5. Testing Push Notification Flow"
echo "-----------------------------------"
response=$(curl -s -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "template_id": "welcome_notification",
    "template_data": {"name": "Test User", "app_name": "MyApp"},
    "device_token": "test-token-123"
  }')

if echo "$response" | grep -q '"success":true'; then
    echo -e "Push notification... ${GREEN}✓ OK${NC}"
    echo "Response: $response"
else
    echo -e "Push notification... ${RED}✗ FAILED${NC}"
    echo "Response: $response"
fi
echo ""

# Test email notification
echo "6. Testing Email Notification Flow"
echo "-----------------------------------"
response=$(curl -s -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-456",
    "template_id": "welcome_email",
    "template_data": {"name": "Test User", "company_name": "Test Co"},
    "recipient_email": "test@example.com"
  }')

if echo "$response" | grep -q '"success":true'; then
    echo -e "Email notification... ${GREEN}✓ OK${NC}"
    echo "Response: $response"
else
    echo -e "Email notification... ${RED}✗ FAILED${NC}"
    echo "Response: $response"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "Check service logs for detailed output:"
echo "  docker-compose logs push-service | tail -20"
echo "  docker-compose logs email-service | tail -20"
echo ""
echo "RabbitMQ Management UI: http://localhost:15672"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
