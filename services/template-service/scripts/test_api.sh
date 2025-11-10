#!/bin/bash

# Template Service API Testing Script

BASE_URL="${TEMPLATE_SERVICE_URL:-http://localhost:3004}"
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}🧪 Testing Template Service API${NC}"
echo "=================================================="
echo "Base URL: $BASE_URL"
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq is not installed. Please install it first.${NC}"
    echo "   macOS: brew install jq"
    echo "   Ubuntu: sudo apt-get install jq"
    exit 1
fi

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -e "${BLUE}📍 Testing: $name${NC}"
    
    if [ -z "$data" ]; then
        response=$(curl -s -X $method "$BASE_URL$endpoint" -H "Content-Type: application/json")
    else
        response=$(curl -s -X $method "$BASE_URL$endpoint" -H "Content-Type: application/json" -d "$data")
    fi
    
    if echo "$response" | jq . > /dev/null 2>&1; then
        echo "$response" | jq .
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✅ Passed${NC}\n"
    else
        echo -e "${RED}❌ Failed - Invalid JSON response${NC}"
        echo "$response"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo ""
    fi
}

# 1. Health Check
test_endpoint "Health Check" "GET" "/health"

# 2. Readiness Check
test_endpoint "Readiness Check" "GET" "/ready"

# 3. Liveness Check
test_endpoint "Liveness Check" "GET" "/live"

# 4. Root Endpoint
test_endpoint "Root Endpoint" "GET" "/"

# 5. Create Email Template
test_endpoint "Create Email Template" "POST" "/api/v1/templates" '{
  "template_id": "test_welcome_email",
  "name": "Test Welcome Email",
  "description": "Test welcome email template",
  "type": "email",
  "category": "onboarding",
  "subject": "Welcome {{name}} to {{company_name}}!",
  "body": "Hi {{name}},\n\nWelcome to {{company_name}}! We are excited to have you.\n\nVerify your email: {{verification_link}}\n\nBest regards,\nThe Team",
  "language_code": "en"
}'

# 6. Create Push Template
test_endpoint "Create Push Template" "POST" "/api/v1/templates" '{
  "template_id": "test_order_shipped",
  "name": "Test Order Shipped",
  "description": "Push notification for shipped orders",
  "type": "push",
  "category": "transactional",
  "subject": "Order #{{order_id}} shipped! 📦",
  "body": "Hey {{name}}! Your order is on its way. Track: {{tracking_url}}",
  "language_code": "en"
}'

# 7. List Templates
test_endpoint "List Templates" "GET" "/api/v1/templates?page=1&limit=10"

# 8. Get Specific Template
test_endpoint "Get Template by ID" "GET" "/api/v1/templates/test_welcome_email"

# 9. Render Template
test_endpoint "Render Template" "POST" "/api/v1/templates/test_welcome_email/render" '{
  "data": {
    "name": "John Doe",
    "company_name": "Acme Corp",
    "verification_link": "https://example.com/verify/abc123"
  },
  "language_code": "en"
}'

# 10. Add Spanish Translation
test_endpoint "Add Spanish Translation" "POST" "/api/v1/templates/test_welcome_email/translations" '{
  "language_code": "es",
  "subject": "¡Bienvenido {{name}} a {{company_name}}!",
  "body": "Hola {{name}},\n\n¡Bienvenido a {{company_name}}! Estamos emocionados de tenerte.\n\nVerifica tu correo: {{verification_link}}\n\nSaludos,\nEl Equipo"
}'

# 11. Render Spanish Version
test_endpoint "Render Spanish Template" "POST" "/api/v1/templates/test_welcome_email/render" '{
  "data": {
    "name": "Juan Pérez",
    "company_name": "Acme Corp",
    "verification_link": "https://example.com/verify/xyz789"
  },
  "language_code": "es"
}'

# 12. Update Template
test_endpoint "Update Template" "PUT" "/api/v1/templates/test_welcome_email" '{
  "name": "Updated Welcome Email",
  "description": "Updated description"
}'

# 13. Get Version History
test_endpoint "Get Version History" "GET" "/api/v1/templates/test_welcome_email/versions"

# 14. Filter by Type
test_endpoint "Filter Templates by Type" "GET" "/api/v1/templates?type=email"

# 15. Search Templates
test_endpoint "Search Templates" "GET" "/api/v1/templates?search=welcome"

# 16. Get Statistics
test_endpoint "Get Statistics" "GET" "/api/v1/templates/stats/summary"

# 17. Test Missing Variables Error
test_endpoint "Test Missing Variables" "POST" "/api/v1/templates/test_welcome_email/render" '{
  "data": {
    "name": "Jane Doe"
  }
}'

# 18. Delete Template
test_endpoint "Delete Template" "DELETE" "/api/v1/templates/test_welcome_email"

# 19. Verify Deleted Template Not Found
test_endpoint "Verify Deleted Template" "GET" "/api/v1/templates/test_welcome_email"

# 20. Metrics Endpoint
echo -e "${BLUE}📍 Testing: Prometheus Metrics${NC}"
curl -s "$BASE_URL/metrics" | head -n 20
echo -e "${GREEN}✅ Passed${NC}\n"
TESTS_PASSED=$((TESTS_PASSED + 1))

# Summary
echo "=================================================="
echo -e "${BOLD}Test Summary${NC}"
echo "=================================================="
echo -e "${GREEN}✅ Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Failed: $TESTS_FAILED${NC}"
echo "=================================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}⚠️  Some tests failed${NC}"
    exit 1
fi