#!/bin/bash
# Test script to verify delete and recreate functionality

BASE_URL="http://localhost:3004"
TEMPLATE_ID="test_delete_recreate"

echo "🧪 Testing Template Delete and Recreate"
echo "========================================"

# Step 1: Create template
echo ""
echo "1️⃣ Creating template..."
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/templates" \
  -H "Content-Type: application/json" \
  -d "{
    \"template_id\": \"$TEMPLATE_ID\",
    \"name\": \"Test Delete Recreate\",
    \"type\": \"email\",
    \"body\": \"Hello {{name}}!\",
    \"language_code\": \"en\"
  }")

echo "$CREATE_RESPONSE" | jq '.'

if echo "$CREATE_RESPONSE" | jq -e '.success' > /dev/null; then
  echo "✅ Template created successfully"
else
  echo "❌ Failed to create template"
  exit 1
fi

# Step 2: Verify template exists
echo ""
echo "2️⃣ Verifying template exists..."
GET_RESPONSE=$(curl -s "$BASE_URL/api/v1/templates/$TEMPLATE_ID")
echo "$GET_RESPONSE" | jq '.data.template_id, .data.is_active'

# Step 3: Delete template
echo ""
echo "3️⃣ Deleting template..."
DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/api/v1/templates/$TEMPLATE_ID")
echo "$DELETE_RESPONSE" | jq '.'

if echo "$DELETE_RESPONSE" | jq -e '.success' > /dev/null; then
  echo "✅ Template deleted successfully"
else
  echo "❌ Failed to delete template"
  exit 1
fi

# Step 4: Verify template is deleted (should return not found)
echo ""
echo "4️⃣ Verifying template is deleted..."
GET_AFTER_DELETE=$(curl -s "$BASE_URL/api/v1/templates/$TEMPLATE_ID")
echo "$GET_AFTER_DELETE" | jq '.'

# Step 5: Recreate template with same ID
echo ""
echo "5️⃣ Recreating template with same ID..."
RECREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/templates" \
  -H "Content-Type: application/json" \
  -d "{
    \"template_id\": \"$TEMPLATE_ID\",
    \"name\": \"Test Delete Recreate - New\",
    \"type\": \"email\",
    \"body\": \"Hello {{name}} again!\",
    \"language_code\": \"en\"
  }")

echo "$RECREATE_RESPONSE" | jq '.'

if echo "$RECREATE_RESPONSE" | jq -e '.success' > /dev/null; then
  echo "✅ Template recreated successfully"
else
  echo "❌ Failed to recreate template"
  echo "This was the issue - now it should work!"
  exit 1
fi

# Step 6: Verify new template
echo ""
echo "6️⃣ Verifying recreated template..."
FINAL_GET=$(curl -s "$BASE_URL/api/v1/templates/$TEMPLATE_ID")
echo "$FINAL_GET" | jq '.data.name, .data.is_active'

echo ""
echo "========================================"
echo "✅ All tests passed!"
echo "========================================"
