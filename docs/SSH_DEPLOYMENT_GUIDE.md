# SSH Deployment Guide for EC2

## Overview

This notification system uses **SSH-only deployment** to AWS EC2. No AWS credentials are needed in GitHub Actions - just your SSH key!

## How It Works

```
GitHub Actions
    ↓ (SSH connection)
EC2 Instance
    ↓ (git pull)
    ↓ (docker-compose build)
    ↓ (docker-compose up)
Deployed Services
```

## Required GitHub Secrets (Only 3!)

| Secret | What It Is | How to Get It |
|--------|------------|---------------|
| `EC2_HOST` | EC2 public IP | AWS Console → EC2 → Your Instance → Public IPv4 |
| `EC2_USER` | SSH username | `ubuntu` (for Ubuntu AMI) |
| `EC2_SSH_KEY` | Private key | The `.pem` file you downloaded when creating EC2 |

## Setting Up SSH Secrets

### 1. Get Your EC2 Public IP

```bash
# From AWS Console
AWS Console → EC2 → Instances → Select your instance → Copy "Public IPv4 address"

# Example: 54.123.45.67
```

### 2. Get Your SSH Private Key

```bash
# Display the key
cat your-key.pem

# Copy to clipboard (macOS)
cat your-key.pem | pbcopy

# Copy to clipboard (Linux)
cat your-key.pem | xclip -selection clipboard
```

**The key should look like this:**
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAyXxJ...
(many lines)
...
-----END RSA PRIVATE KEY-----
```

Or for newer keys:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEA...
(many lines)
...
-----END OPENSSH PRIVATE KEY-----
```

### 3. Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:

**Secret 1: EC2_HOST**
- Name: `EC2_HOST`
- Value: `54.123.45.67` (your actual IP)

**Secret 2: EC2_USER**
- Name: `EC2_USER`
- Value: `ubuntu`

**Secret 3: EC2_SSH_KEY**
- Name: `EC2_SSH_KEY`
- Value: Paste the **entire** content of your `.pem` file
  - Include the `-----BEGIN` line
  - Include all the key data
  - Include the `-----END` line
  - No extra spaces before or after

## Testing SSH Connection

Before setting up GitHub Actions, test SSH manually:

```bash
# From your local machine
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# If this works, you should see:
ubuntu@ip-xxx-xxx-xxx-xxx:~$

# If it works, GitHub Actions will work too!
```

## Common SSH Issues

### Issue 1: Permission Denied

**Problem**: `Permission denied (publickey)`

**Solutions**:
```bash
# Check key permissions
chmod 400 your-key.pem

# Verify you're using the correct key
ssh -i your-key.pem ubuntu@YOUR_EC2_IP -v

# Check EC2 security group allows SSH (port 22)
```

### Issue 2: Connection Timeout

**Problem**: `Connection timed out`

**Solutions**:
1. Check EC2 security group allows SSH from anywhere (0.0.0.0/0)
2. Verify EC2 instance is running
3. Check you're using the **public IP** (not private IP)

### Issue 3: Wrong User

**Problem**: `Please login as the user "ubuntu" rather than the user "root"`

**Solution**: Use `ubuntu` as the username (not `root` or `ec2-user`)

### Issue 4: Key Format Issues in GitHub

**Problem**: GitHub Actions fails with SSH error

**Solutions**:
1. Verify the key includes BEGIN and END lines
2. No extra spaces or line breaks
3. Copy the raw key content (not from a text editor that might add formatting)

```bash
# Verify key format
cat your-key.pem | head -1
# Should show: -----BEGIN RSA PRIVATE KEY----- or -----BEGIN OPENSSH PRIVATE KEY-----

cat your-key.pem | tail -1
# Should show: -----END RSA PRIVATE KEY----- or -----END OPENSSH PRIVATE KEY-----
```

## EC2 Security Group Configuration

Your EC2 security group **must** allow SSH:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | 0.0.0.0/0 | Allow SSH from anywhere |

**Why 0.0.0.0/0?**
- GitHub Actions uses dynamic IPs
- You can't restrict to specific GitHub IPs
- SSH key authentication provides security

## Deployment Workflow

When you push to GitHub:

1. **GitHub Actions starts**
2. **Sets up SSH key** from `EC2_SSH_KEY` secret
3. **Connects to EC2** using `EC2_USER@EC2_HOST`
4. **Runs commands on EC2**:
   ```bash
   cd ~/notification-system
   git pull
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```
5. **Runs health checks** via SSH
6. **Reports success/failure**

## Manual Deployment via SSH

You can also deploy manually:

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Navigate to project
cd ~/notification-system

# Pull latest code
git pull

# Deploy
docker-compose -f docker-compose.minimal.yml down
docker-compose -f docker-compose.minimal.yml build
docker-compose -f docker-compose.minimal.yml up -d

# Check status
docker-compose -f docker-compose.minimal.yml ps
```

## Verifying GitHub Actions SSH

After setting up secrets, test the workflow:

1. Make a small change (e.g., update README)
2. Commit and push to main branch
3. Go to GitHub → Actions tab
4. Watch the workflow run
5. Check the "Deploy to EC2 via SSH" step

**Successful output should show:**
```
Setting up SSH key...
Connecting to EC2...
Deploying...
✅ Deployment completed successfully!
```

## SSH Key Security

**Best Practices:**
- ✅ Never commit `.pem` files to Git
- ✅ Store keys securely on your local machine
- ✅ Use GitHub Secrets for CI/CD
- ✅ Rotate keys periodically
- ✅ Use different keys for different environments

**Key Permissions:**
```bash
# Your .pem file should have restricted permissions
chmod 400 your-key.pem

# Verify
ls -l your-key.pem
# Should show: -r-------- (read-only for owner)
```

## Troubleshooting GitHub Actions

### View Detailed Logs

1. Go to GitHub → Actions
2. Click on the failed workflow
3. Click on "Deploy to EC2 via SSH" step
4. Look for SSH errors

### Common Error Messages

**"Host key verification failed"**
- The workflow handles this automatically with `ssh-keyscan`
- If it persists, check EC2_HOST is correct

**"Permission denied (publickey)"**
- Check EC2_SSH_KEY secret contains full key
- Verify key format (BEGIN/END lines included)
- Ensure no extra spaces

**"Connection refused"**
- Check EC2 security group allows SSH (port 22)
- Verify EC2 instance is running
- Check EC2_HOST is the public IP

## Alternative: Using SSH Config

For local development, you can create an SSH config:

```bash
# ~/.ssh/config
Host my-ec2
    HostName YOUR_EC2_IP
    User ubuntu
    IdentityFile ~/.ssh/your-key.pem
    StrictHostKeyChecking no
```

Then connect with:
```bash
ssh my-ec2
```

## Summary

✅ **SSH-only deployment** - No AWS credentials needed
✅ **3 simple secrets** - EC2_HOST, EC2_USER, EC2_SSH_KEY
✅ **Secure** - Key-based authentication
✅ **Simple** - Direct SSH connection
✅ **Reliable** - No complex AWS API calls

**Next Steps:**
1. Test SSH connection manually
2. Add secrets to GitHub
3. Push to main branch
4. Watch automatic deployment! 🚀
