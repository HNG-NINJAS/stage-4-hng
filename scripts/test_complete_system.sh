#!/bin/bash

# Complete System Testing Script
# Tests all functionality for video recording and deployment verification

echo "=========================================="
echo "Complete Notification System Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL="${API_URL:-http://localhost:3000}"
TEMPLATE_URL="${TEMPLATE_URL:-http://localhost:3004}"
PUSH_URL="${PUSH_URL:-http://localhost:3003}"
EMAIL_URL="${EMAIL_URL:-http://localhost:3005}"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name=$1
    local command=$2
    
    echo -e "${BLUE}Testing: $test_name${NC}"
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test with output
run_test_with_output() {
    local test_name=$1
    local command=$2
    
    echo -e "${BLUE}Testing: $test_name${NC}"
    
    output=$(eval "$command" 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        echo "$output" | head -5
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "$output"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "1. Infrastructure Health Checks"
echo "-----------------------------------"

run_test "RabbitMQ" "docker-compose -f docker-compose.minimal.yml exec -T rabbitmq rabbitmq-diagnostics -q ping"
run_test "Redis" "docker-compose -f docker-compose.minimal.yml exec -T redis redis-cli -a redis123 ping"
run_test "PostgreSQL" "docker-compose -f docker-compose.minimal.yml exec -T postgres_template pg_isready -U admin -d template_service"

echo ""
echo "2. Service Health Endpoints"
echo "-----------------------------------"

run_test "API Gateway Health" "curl -sf $API_URL/health"
run_test "Template Service Health" "curl -sf $TEMPLATE_URL/health"
run_test "Push Service Health" "curl -sf $PUSH_URL/health"
run_test "Email Service Health" "curl -sf $EMAIL_URL/health"

echo ""
echo "3. Template Service Tests"
echo "-----------------------------------"

run_test "List Templates" "curl -sf $TEMPLATE_URL/api/v1/templates"
run_test "Get Specific Template" "curl -sf $TEMPLATE_URL/api/v1/templates/welcome_email"

echo ""
echo "4. Push Notification Tests"
echo "-----------------------------------"

echo -e "${BLUE}Sending Push Notification...${NC}"
response=$(curl -s -X POST $API_URL/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-001",
    "template_id": "welcome_notification",
    "template_data": {
      "name": "Test User",
      "app_name": "TestApp"
    },
    "device_token": "test-token-123"
  }')

if echo "$response" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Push notification sent successfully${NC}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Push notification failed${NC}"
    echo "$response"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${YELLOW}Waiting 2 seconds for processing...${NC}"
sleep 2

echo ""
echo -e "${BLUE}Checking Push Service Logs:${NC}"
docker-compose -f docker-compose.minimal.yml logs --tail=10 push-service | grep -E "Received push|Template rendered|notification sent" || echo "Check full logs for details"

echo ""
echo "5. Email Notification Tests"
echo "-----------------------------------"

echo -e "${BLUE}Sending Email Notification...${NC}"
response=$(curl -s -X POST $API_URL/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-002",
    "template_id": "welcome_email",
    "template_data": {
      "name": "Jane Doe",
      "company_name": "Test Company"
    },
    "recipient_email": "test@example.com"
  }')

if echo "$response" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Email notification sent successfully${NC}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Email notification failed${NC}"
    echo "$response"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${YELLOW}Waiting 2 seconds for processing...${NC}"
sleep 2

echo ""
echo -e "${BLUE}Checking Email Service Logs:${NC}"
docker-compose -f docker-compose.minimal.yml logs --tail=10 email-service | grep -E "Processing email|Template rendered|Email sent" || echo "Check full logs for details"

echo ""
echo "6. Multi-Language Support Test"
echo "-----------------------------------"

echo -e "${BLUE}Sending Spanish Email...${NC}"
response=$(curl -s -X POST $API_URL/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-003",
    "template_id": "welcome_email",
    "template_data": {
      "name": "Carlos García",
      "company_name": "Mi Empresa"
    },
    "recipient_email": "carlos@example.com",
    "language_code": "es"
  }')

if echo "$response" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Spanish email sent successfully${NC}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Spanish email failed${NC}"
    echo "$response"
    ((TESTS_FAILED++))
fi

echo ""
echo "7. Template Rendering Test"
echo "-----------------------------------"

echo -e "${BLUE}Testing Template Rendering...${NC}"
response=$(curl -s -X POST $TEMPLATE_URL/api/v1/templates/welcome_email/render \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "Direct Test",
      "company_name": "Test Corp"
    },
    "language_code": "en"
  }')

if echo "$response" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Template rendered successfully${NC}"
    echo "$response" | jq '.data' 2>/dev/null || echo "$response"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Template rendering failed${NC}"
    echo "$response"
    ((TESTS_FAILED++))
fi

echo ""
echo "8. RabbitMQ Queue Status"
echo "-----------------------------------"

echo -e "${BLUE}Checking RabbitMQ Queues:${NC}"
docker-compose -f docker-compose.minimal.yml exec -T rabbitmq rabbitmqctl list_queues name messages consumers 2>/dev/null | grep -E "push.queue|email.queue" || echo "Queues will be created on first use"

echo ""
echo "9. Service Container Status"
echo "-----------------------------------"

docker-compose -f docker-compose.minimal.yml ps

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo ""
    echo "System is ready for:"
    echo "  ✓ Video recording"
    echo "  ✓ Production deployment"
    echo "  ✓ Live demonstration"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please check:"
    echo "  1. docker-compose -f docker-compose.minimal.yml logs"
    echo "  2. Service health endpoints"
    echo "  3. RabbitMQ connection"
    echo ""
    exit 1
fi
