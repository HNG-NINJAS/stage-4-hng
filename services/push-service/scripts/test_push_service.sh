#!/bin/bash

echo "🧪 Testing Push Service..."
echo ""

BASE_URL="${PUSH_SERVICE_URL:-http://localhost:3003}"

# Test health
echo "1. Testing health check..."
curl -s "$BASE_URL/health" | jq .
echo ""

# Test readiness
echo "2. Testing readiness..."
curl -s "$BASE_URL/ready" | jq .
echo ""

# Test metrics
echo "3. Testing metrics..."
curl -s "$BASE_URL/metrics" | head -n 10
echo ""

echo "✅ Basic tests complete!"
echo ""
echo "To test full flow:"
echo "  1. Ensure Template Service is running"
echo "  2. Seed templates: cd ../template-service && python scripts/seed_templates.py"
echo "  3. Publish test message: python test_publish.py"
echo "  4. Check logs: docker-compose logs -f push-service"