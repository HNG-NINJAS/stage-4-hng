# Docker Compose Files Explained

## Two Options Available

### 1. docker-compose.minimal.yml (Current Default)
**For**: Quick setup, development, testing

**Credentials**: Hardcoded in the file
- PostgreSQL: `admin` / `admin123`
- Redis: `redis123`
- RabbitMQ: `admin` / `admin123`

**Pros**:
- ✅ No .env file needed
- ✅ Works immediately
- ✅ Simple for testing

**Cons**:
- ❌ Hardcoded passwords (not secure for production)
- ❌ Can't change credentials without editing file

**Usage**:
```bash
docker-compose -f docker-compose.minimal.yml up -d
```

### 2. docker-compose.prod.yml (Recommended for Production)
**For**: Production deployment with security

**Credentials**: From `.env` file
- PostgreSQL: `${POSTGRES_USER}` / `${POSTGRES_PASSWORD}`
- Redis: `${REDIS_PASSWORD}`
- RabbitMQ: `${RABBITMQ_USER}` / `${RABBITMQ_PASS}`

**Pros**:
- ✅ Secure - passwords in .env (not in Git)
- ✅ Easy to change credentials
- ✅ Production-ready
- ✅ Logging configured
- ✅ Auto-restart enabled

**Cons**:
- ❌ Requires .env file setup

**Usage**:
```bash
# Copy and edit .env
cp .env.production .env
nano .env  # Update passwords

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## Current GitHub Actions Setup

The workflow currently uses `docker-compose.minimal.yml` for simplicity.

### To Switch to Production Mode

Update `.github/workflows/deploy.yml`:

```yaml
# Change this line:
docker-compose -f docker-compose.minimal.yml up -d

# To this:
docker-compose -f docker-compose.prod.yml up -d
```

## Recommendation

### For Demo/Testing
Use `docker-compose.minimal.yml` - it's already configured and working.

### For Production
Switch to `docker-compose.prod.yml`:

1. **Update workflow** to use `docker-compose.prod.yml`
2. **Create .env** on EC2 with strong passwords
3. **Restart services**

## Security Note

**docker-compose.minimal.yml** has these hardcoded credentials:
```yaml
POSTGRES_PASSWORD: admin123
REDIS_PASSWORD: redis123
RABBITMQ_PASS: admin123
```

These are **publicly visible** in your repository!

For production:
- Use `docker-compose.prod.yml`
- Set strong passwords in `.env`
- Don't commit `.env` to Git (it's in .gitignore)

## Quick Comparison

| Feature | minimal.yml | prod.yml |
|---------|-------------|----------|
| Credentials | Hardcoded | From .env |
| Security | Low | High |
| Setup | Instant | Requires .env |
| Production Ready | No | Yes |
| Logging | Basic | Configured |
| Auto-restart | unless-stopped | always |
| Best For | Demo/Dev | Production |

## How to Switch

### Option 1: Keep Using minimal.yml (Current)
No changes needed. Accept that credentials are hardcoded.

**Security mitigation**:
- Restrict ports via firewall
- Only allow localhost connections to PostgreSQL/Redis/RabbitMQ
- Use nginx reverse proxy

### Option 2: Switch to prod.yml (Recommended)

**Step 1**: Update workflow
```bash
# Edit .github/workflows/deploy.yml
# Replace all instances of:
docker-compose.minimal.yml
# With:
docker-compose.prod.yml
```

**Step 2**: Update .env.production template
```bash
# Already done! The file has:
POSTGRES_PASSWORD=CHANGE_THIS_STRONG_PASSWORD
REDIS_PASSWORD=CHANGE_THIS_REDIS_PASSWORD
RABBITMQ_PASS=CHANGE_THIS_RABBITMQ_PASSWORD
```

**Step 3**: After first deployment, SSH to EC2
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
cd ~/notification-system
nano .env

# Update all passwords
# Save and restart:
docker-compose -f docker-compose.prod.yml restart
```

## Current Status

✅ Both files exist and work
✅ Workflow uses `docker-compose.minimal.yml` (hardcoded credentials)
✅ `.env.production` is ready for `docker-compose.prod.yml`

**Your choice**: Keep simple (minimal) or switch to secure (prod)

## My Recommendation

**For your current demo/testing**: Keep using `docker-compose.minimal.yml`
- It works
- Simple
- No extra setup needed

**Before going to production**: Switch to `docker-compose.prod.yml`
- More secure
- Industry standard
- Easy to manage credentials
