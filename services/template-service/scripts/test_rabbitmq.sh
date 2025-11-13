#!/bin/bash

# Test RabbitMQ Integration
# This script tests that events are properly published to RabbitMQ

set -e

BASE_URL="http://localhost:3004"
RABBITMQ_API="http://localhost:15672/api"
RABBITMQ_USER="admin"
RABBITMQ_PASS="admin123"

echo "🐰 Testing RabbitMQ Integration"
echo "========================================"

# Check if RabbitMQ is running
echo ""
echo "1️⃣ Checking RabbitMQ status..."
if curl -s -u $RABBITMQ_USER:$RABBITMQ_PASS $RABBITMQ_API/overview > /dev/null; then
    echo "✅ RabbitMQ is running"
else
    echo "❌ RabbitMQ is not accessible"
    exit 1
fi

# Check exchanges
echo ""
echo "2️⃣ Checking RabbitMQ exchanges..."
EXCHANGES=$(curl -s -u $RABBITMQ_USER:$RABBITMQ_PASS $RABBITMQ_API/exchanges/%2F | jq -r '.[].name' | grep template || echo "")
if [[ -n "$EXCHANGES" ]]; then
    echo "✅ Template exchanges found:"
    echo "$EXCHANGES"
else
    echo "⚠️  No template exchanges found yet (will be created on first event)"
fi

# Get initial message count
echo ""
echo "3️⃣ Getting initial message stats..."
INITIAL_PUBLISH=$(curl -s -u $RABBITMQ_USER:$RABBITMQ_PASS "$RABBITMQ_API/exchanges/%2F/template.events" | jq -r '.message_stats.publish // 0')
echo "Initial publish count: $INITIAL_PUBLISH"

# Create a template (should trigger template.created event)
echo ""
echo "4️⃣ Creating a template..."
TEMPLATE_ID="rabbitmq_test_$(date +%s)"
CREATE_RESPONSE=$(curl -s -X POST $BASE_URL/api/v1/templates \
  -H "Content-Type: application/json" \
  -d "{
    \"template_id\": \"$TEMPLATE_ID\",
    \"name\": \"RabbitMQ Test Template\",
    \"type\": \"email\",
    \"body\": \"Test {{name}}\",
    \"language_code\": \"en\"
  }")

if echo "$CREATE_RESPONSE" | jq -e '.success == true' > /dev/null; then
    echo "✅ Template created successfully"
else
    echo "❌ Failed to create template"
    echo "$CREATE_RESPONSE" | jq '.'
    exit 1
fi

# Wait a moment for the event to be published
sleep 2

# Check if message was published
echo ""
echo "5️⃣ Checking if event was published..."
CURRENT_PUBLISH=$(curl -s -u $RABBITMQ_USER:$RABBITMQ_PASS "$RABBITMQ_API/exchanges/%2F/template.events" | jq -r '.message_stats.publish // 0')
echo "Current publish count: $CURRENT_PUBLISH"

if [ "$CURRENT_PUBLISH" -gt "$INITIAL_PUBLISH" ]; then
    echo "✅ Event was published! ($((CURRENT_PUBLISH - INITIAL_PUBLISH)) new message(s))"
else
    echo "⚠️  No new messages published (check application logs)"
fi

# Update the template (should trigger template.updated event)
echo ""
echo "6️⃣ Updating template..."
UPDATE_RESPONSE=$(curl -s -X PUT $BASE_URL/api/v1/templates/$TEMPLATE_ID \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"RabbitMQ Test Template - Updated\"
  }")

if echo "$UPDATE_RESPONSE" | jq -e '.success == true' > /dev/null; then
    echo "✅ Template updated successfully"
else
    echo "❌ Failed to update template"
fi

sleep 1

# Delete the template (should trigger template.deleted event)
echo ""
echo "7️⃣ Deleting template..."
DELETE_RESPONSE=$(curl -s -X DELETE $BASE_URL/api/v1/templates/$TEMPLATE_ID)

if echo "$DELETE_RESPONSE" | jq -e '.success == true' > /dev/null; then
    echo "✅ Template deleted successfully"
else
    echo "❌ Failed to delete template"
fi

sleep 1

# Final message count
echo ""
echo "8️⃣ Final message stats..."
FINAL_PUBLISH=$(curl -s -u $RABBITMQ_USER:$RABBITMQ_PASS "$RABBITMQ_API/exchanges/%2F/template.events" | jq -r '.message_stats.publish // 0')
TOTAL_EVENTS=$((FINAL_PUBLISH - INITIAL_PUBLISH))
echo "Final publish count: $FINAL_PUBLISH"
echo "Total events published: $TOTAL_EVENTS"

if [ "$TOTAL_EVENTS" -ge 3 ]; then
    echo ""
    echo "✅ SUCCESS! All events were published correctly"
    echo "   - template.created"
    echo "   - template.updated"
    echo "   - template.deleted"
else
    echo ""
    echo "⚠️  Expected 3 events, but got $TOTAL_EVENTS"
    echo "   Check application logs for RabbitMQ connection issues"
fi

# Show exchange details
echo ""
echo "9️⃣ Exchange details:"
curl -s -u $RABBITMQ_USER:$RABBITMQ_PASS "$RABBITMQ_API/exchanges/%2F/template.events" | jq '{name, type, durable, message_stats}'

echo ""
echo "🎉 Test complete!"
echo ""
echo "💡 View RabbitMQ Management UI at: http://localhost:15672"
echo "   Username: admin"
echo "   Password: admin123"
