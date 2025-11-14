# Postman Collection for Notification System

## 📥 Quick Import

### Step 1: Import Collection

1. Open Postman
2. Click **Import** (top left)
3. Drag and drop `Notification-System-Production.postman_collection.json`
4. Or click **Upload Files** and select the file
5. Click **Import**

### Step 2: Import Environment

1. Click **Import** again
2. Drag and drop `Production.postman_environment.json`
3. Click **Import**

### Step 3: Select Environment

1. Click the environment dropdown (top right)
2. Select **Production**
3. You're ready to test! ✅

## 📁 Collection Structure

### 1. Health Checks (4 requests)
- API Gateway Health
- Template Service Health
- Push Service Health
- Email Service Health

### 2. Templates (5 requests)
- Get All Templates
- Get Template by ID
- Create Template
- Update Template
- Delete Template

### 3. Notifications (3 requests)
- Send Push Notification
- Send Email Notification
- Bulk Send Notifications

### 4. Direct Service Calls (2 requests)
- Push Service - Send Direct
- Email Service - Send Direct

## 🚀 Quick Start Testing

### Test 1: Check All Services are Healthy

1. Open **Health Checks** folder
2. Click **API Gateway Health**
3. Click **Send**
4. Should return: `{"status": "healthy", ...}`
5. Repeat for all 4 health checks

### Test 2: Get Available Templates

1. Open **Templates** folder
2. Click **Get All Templates**
3. Click **Send**
4. Should return list of templates (welcome, password-reset, etc.)

### Test 3: Send a Push Notification

1. Open **Notifications** folder
2. Click **Send Push Notification**
3. Review the body (already configured with example data)
4. Click **Send**
5. Should return: `{"status": "success", "messageId": "..."}`

### Test 4: Create Your Own Template

1. Open **Templates** folder
2. Click **Create Template**
3. Modify the body JSON:
```json
{
  "name": "my-custom-template",
  "type": "push",
  "subject": "My Custom Notification",
  "body": "Hello {{username}}, welcome to {{app}}!",
  "variables": ["username", "app"]
}
```
4. Click **Send**
5. Template created! ✅

## 🔧 Environment Variables

The collection uses these variables (already configured):

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | http://51.20.141.174:3000 | API Gateway |
| `template_url` | http://51.20.141.174:3004 | Template Service |
| `push_url` | http://51.20.141.174:3003 | Push Service |
| `email_url` | http://51.20.141.174:3005 | Email Service |

To change the IP address:
1. Click **Environments** (left sidebar)
2. Click **Production**
3. Update the values
4. Click **Save**

## 📊 Example Requests

### Send Push Notification
```json
POST {{base_url}}/api/notifications/send

{
  "type": "push",
  "userId": "user123",
  "templateId": "welcome",
  "data": {
    "name": "John Doe",
    "action": "signed up"
  }
}
```

### Send Email Notification
```json
POST {{base_url}}/api/notifications/send

{
  "type": "email",
  "userId": "user456",
  "templateId": "password-reset",
  "data": {
    "name": "Jane Smith",
    "resetLink": "https://example.com/reset/abc123"
  }
}
```

### Create Template
```json
POST {{template_url}}/api/v1/templates

{
  "name": "order-confirmation",
  "type": "email",
  "subject": "Order Confirmed - #{{orderNumber}}",
  "body": "Hi {{customerName}}, your order #{{orderNumber}} has been confirmed!",
  "variables": ["customerName", "orderNumber"]
}
```

## 🎯 Testing Workflow

### Complete Test Flow:

1. **Health Checks** → Verify all services are running
2. **Get All Templates** → See available templates
3. **Send Push Notification** → Test push service
4. **Send Email Notification** → Test email service
5. **Create Template** → Test template creation
6. **Send with New Template** → Test end-to-end

## 🌐 API Documentation

For interactive API docs, open these URLs in your browser:

- **Template Service**: http://51.20.141.174:3004/docs
- **Push Service**: http://51.20.141.174:3003/docs
- **Email Service**: http://51.20.141.174:3005/docs

## 🔍 Troubleshooting

### Issue: Connection Timeout

**Problem**: Can't connect to services

**Solution**: 
1. Check EC2 security group allows ports 3000, 3003, 3004, 3005
2. Verify services are running: `docker ps`
3. Test locally on EC2: `curl http://localhost:3000/health`

### Issue: 404 Not Found

**Problem**: Endpoint not found

**Solution**: Check the URL path is correct
- Health: `/health`
- Templates: `/api/v1/templates`
- Notifications: `/api/notifications/send`

### Issue: Template Not Found

**Problem**: `Template 'xyz' not found`

**Solution**: 
1. Run **Get All Templates** to see available templates
2. Use an existing template ID (e.g., "welcome", "password-reset")
3. Or create the template first

## 📝 Notes

- All requests are pre-configured with example data
- Modify the request bodies as needed
- The system uses mock mode for email/push (no real emails/pushes sent)
- Check service logs on EC2: `docker-compose logs -f`

## 🎉 You're Ready!

Import the collection and start testing your notification system!

**Files to import:**
1. `Notification-System-Production.postman_collection.json`
2. `Production.postman_environment.json`

Happy testing! 🚀
