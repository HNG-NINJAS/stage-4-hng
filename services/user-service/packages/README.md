# User Service

A NestJS-based microservice for managing user authentication, profiles, notification preferences, and device push tokens in the distributed notification system.

## Overview

The User Service is the central authority for user identity and notification configuration within the notification system. It handles user registration, authentication, and maintains all user preferences and device information.

## Key Features

- **User Authentication**: JWT-based authentication with secure password hashing
- **User Management**: Create, read, update, and delete user profiles
- **Notification Preferences**: Granular control over email, push, and SMS notifications with frequency settings
- **Device Management**: Register and manage push notification tokens for mobile and web devices
- **Health Checks**: Built-in health monitoring endpoint

## Service Architecture

### Technology Stack

- **Runtime**: Node.js (v20+)
- **Framework**: NestJS 10
- **Language**: TypeScript 5
- **Database**: MySQL 8 (via Prisma ORM)
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: class-validator & class-transformer
- **Password Hashing**: bcryptjs

### Database Models

```
User
├── id (UUID)
├── name (string)
├── email (string, unique)
├── password (hashed)
├── phone_number (optional)
├── created_at
├── updated_at
└── relations:
    ├── preferences (1:1)
    └── push_tokens (1:many)

PreferencesNotification
├── id (UUID)
├── user_id (FK)
├── email_enabled (boolean)
├── email_frequency (instant|daily|weekly|never)
├── push_enabled (boolean)
├── push_frequency (instant|daily|weekly|never)
├── sms_enabled (boolean)
├── sms_frequency (instant|daily|weekly|never)
├── unsubscribe_all (boolean)
├── created_at
└── updated_at

PushToken
├── id (UUID)
├── user_id (FK)
├── token (string)
├── device_type (ios|android|web|desktop)
├── device_name (optional)
├── is_active (boolean)
├── created_at
└── updated_at
```

## API Endpoints

### Authentication

#### User Registration
```http
POST /users/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": null,
    "created_at": "2025-11-12T14:30:00Z",
    "updated_at": "2025-11-12T14:30:00Z"
  },
  "message": "User registered successfully"
}
```

#### User Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600,
    "token_type": "Bearer"
  },
  "message": "Login successful"
}
```

### User Profile

#### Get Current User Profile
```http
GET /users/me
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+1234567890",
    "created_at": "2025-11-12T14:30:00Z",
    "updated_at": "2025-11-12T14:30:00Z"
  },
  "message": "User profile retrieved successfully"
}
```

#### Get User by ID
```http
GET /users/:id

Response: 200 OK
{
  "success": true,
  "data": { ... user object ... },
  "message": "User retrieved successfully"
}
```

#### Update User Profile
```http
PUT /users/:id
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Jane Doe",
  "phone_number": "+1987654321"
}

Response: 200 OK
{
  "success": true,
  "data": { ... updated user object ... },
  "message": "User updated successfully"
}
```

#### Delete User Account
```http
DELETE /users/:id
Authorization: Bearer {token}

Response: 204 No Content
```

### Notification Preferences

#### Get User Preferences
```http
GET /users/:user_id/preferences

Response: 200 OK
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "email_enabled": true,
    "email_frequency": "daily",
    "push_enabled": true,
    "push_frequency": "instant",
    "sms_enabled": false,
    "sms_frequency": "never",
    "unsubscribe_all": false,
    "created_at": "2025-11-12T14:30:00Z",
    "updated_at": "2025-11-12T14:30:00Z"
  },
  "message": "Preferences retrieved successfully"
}
```

#### Update User Preferences
```http
PUT /users/:user_id/preferences
Content-Type: application/json

{
  "email_enabled": true,
  "email_frequency": "weekly",
  "push_enabled": true,
  "push_frequency": "instant",
  "sms_enabled": false,
  "sms_frequency": "never",
  "unsubscribe_all": false
}

Response: 200 OK
{
  "success": true,
  "data": { ... updated preferences object ... },
  "message": "Preferences updated successfully"
}
```

### Push Token Management

#### Register Push Token
```http
POST /users/:user_id/push-tokens
Content-Type: application/json

{
  "token": "ExponentPushToken[...]",
  "device_type": "ios",
  "device_name": "iPhone 14 Pro"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "token": "ExponentPushToken[...]",
    "device_type": "ios",
    "device_name": "iPhone 14 Pro",
    "is_active": true,
    "created_at": "2025-11-12T14:30:00Z",
    "updated_at": "2025-11-12T14:30:00Z"
  },
  "message": "Push token registered successfully"
}
```

#### Get User Push Tokens
```http
GET /users/:user_id/push-tokens

Response: 200 OK
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "token": "ExponentPushToken[...]",
      "device_type": "ios",
      "device_name": "iPhone 14 Pro",
      "is_active": true,
      "created_at": "2025-11-12T14:30:00Z",
      "updated_at": "2025-11-12T14:30:00Z"
    }
  ],
  "message": "Push tokens retrieved successfully"
}
```

#### Delete Push Token
```http
DELETE /users/:user_id/push-tokens/:token_id

Response: 204 No Content
```

### Health Check

#### Service Health Status
```http
GET /health

Response: 200 OK
{
  "statusCode": 200,
  "message": "Health check passed"
}
```

## Getting Started

### Prerequisites

- Node.js 20 or higher
- npm or yarn
- MySQL 8.0 or higher
- Docker & Docker Compose (for containerized setup)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/HNG-NINJAS/stage-4-hng.git
cd stage-4-hng/packages/user-service
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Update `.env` with your configuration:
```env
PORT=3001
NODE_ENV=development
DATABASE_URL="mysql://root:password@localhost:3306/notification_service"
JWT_SECRET=your-secret-key-here
JWT_EXPIRATION=3600
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=debug
```

4. **Setup database**
```bash
# Generate Prisma client
npm run prisma:generate

# Run migrations
npm run prisma:migrate dev --name init
```

5. **Start the service**
```bash
npm run start:dev
```

The service will be available at `http://localhost:3001`

## Development

### Available Scripts

```bash
# Start development server with auto-reload
npm run start:dev

# Build TypeScript
npm run build

# Start production server
npm run start:prod

# Run tests
npm run test

# Run tests with coverage
npm run test:cov

# Lint code
npm run lint

# Format code
npm run format

# Prisma commands
npm run prisma:generate    # Generate Prisma client
npm run prisma:migrate     # Create migration
npm run prisma:studio      # Open Prisma Studio UI
npm run prisma:seed        # Seed database
```

### Project Structure

```
src/
├── auth/
│   ├── auth.controller.ts      # Authentication endpoints
│   ├── auth.service.ts         # Authentication logic
│   ├── auth.module.ts          # Auth module definition
│   ├── decorators/             # Custom decorators
│   │   └── current-user.decorator.ts
│   ├── guards/                 # JWT guard
│   │   └── jwt.guard.ts
│   └── dto/                    # Data Transfer Objects
│       ├── login.dto.ts
│       └── login.response.ts
├── users/
│   ├── users.controller.ts     # User endpoints
│   ├── users.service.ts        # User business logic
│   ├── users.module.ts         # Users module
│   └── dto/
│       ├── create-user.dto.ts
│       ├── update-user.dto.ts
│       └── user.response.ts
├── preferences/
│   ├── preferences.controller.ts
│   ├── preferences.service.ts
│   ├── preferences.module.ts
│   └── dto/
│       ├── preferences.response.ts
│       └── update-preferences.dto.ts
├── push-tokens/
│   ├── push-tokens.controller.ts
│   ├── push-tokens.service.ts
│   ├── push-tokens.module.ts
│   └── dto/
│       ├── push-token.response.ts
│       └── register-token.dto.ts
├── health/
│   ├── health.controller.ts
│   └── health.module.ts
├── prisma/
│   ├── prisma.service.ts
│   └── prisma.module.ts
├── common/
│   ├── decorators/
│   ├── filters/
│   ├── interceptors/
│   └── pipes/
├── app.module.ts               # Root module
└── main.ts                     # Application entry point

prisma/
├── schema.prisma               # Database schema
└── seed.ts                     # Database seeding
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t user-service:latest .
```

### Run with Docker Compose

From the root directory:

```bash
docker-compose up -d user-service
```

Service will be available at `http://localhost:3001`

### Environment Variables for Docker

All services are configured via the `docker-compose.yml` file with proper networking and dependencies.

## Error Handling

The service uses standard HTTP status codes and structured error responses:

```json
{
  "success": false,
  "error": "INVALID_CREDENTIALS",
  "message": "Email or password is incorrect"
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict (e.g., email already exists) |
| 500 | Internal Server Error |

## Security Features

- ✅ Password hashing with bcryptjs
- ✅ JWT token-based authentication
- ✅ Token expiration (default: 1 hour)
- ✅ Input validation with class-validator
- ✅ CORS protection
- ✅ Rate limiting ready (can be added)

## Performance Considerations

- Database queries are optimized with Prisma
- JWT tokens are stateless (no database lookup needed)
- Caching can be implemented with Redis
- Horizontal scaling supported via stateless design

## Integration with Other Services

### API Gateway
The User Service is queried by the API Gateway for:
- User preference lookups before sending notifications
- Token validation for incoming requests
- User data enrichment

### Email & Push Services
These services query the User Service to:
- Retrieve user preferences
- Get push tokens for device registration
- Validate user IDs

### Example Query
```typescript
// From another service
const userPreferences = await axios.get(
  `http://user-service:3001/users/${userId}/preferences`
);
```

## Monitoring & Logs

The service logs all operations with correlation IDs for tracing:

```
[Nest] 7308  - 11/11/2025, 5:01:01 PM     LOG [NestFactory] Starting Nest application...
[Nest] 7308  - 11/11/2025, 5:01:02 PM     LOG [InstanceLoader] UsersModule dependencies initialized +3ms
[Nest] 7308  - 11/11/2025, 5:01:03 PM     LOG [RouterExplorer] Mapped {/users/register, POST} route +2ms
```

## Testing

```bash
# Unit tests
npm run test

# Integration tests (if configured)
npm run test:e2e

# Coverage report
npm run test:cov
```


## License

MIT License - See LICENSE file for details

## Related Services

- [API Gateway](../api-gateway/README.md)
- [Email Service](../email-service/README.md)
- [Push Service](../push-service/README.md)
- [Template Service](../template-service/README.md)

---