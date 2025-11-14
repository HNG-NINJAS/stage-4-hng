# Fix Corrupted .env File on EC2

## The Problem

Your `.env` file on EC2 has corrupted content:
```
line 44: unexpected character "@" in variable name "USER TTY FROM LOGIN@ IDLE JCPU PCPU WHAT"
```

This looks like output from the `w` or `who` command was accidentally pasted into the file.

## Quick Fix (SSH to EC2)

### Option 1: Delete and Let Workflow Recreate (Easiest)

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Navigate to project
cd ~/notification-system

# Delete corrupted .env
rm .env

# Re-run GitHub Actions workflow
# It will recreate the .env file automatically
```

### Option 2: Manually Recreate

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Navigate to project
cd ~/notification-system

# Recreate from template
cp .env.production .env

# Verify it's correct
head .env
# Should show: # Production Environment Variables
```

### Option 3: Fix via SSH Command (One-liner)

```bash
# From your local machine
ssh -i your-key.pem ubuntu@YOUR_EC2_IP "cd ~/notification-system && rm .env && cp .env.production .env"
```

## Verify the Fix

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Check .env file
cd ~/notification-system
cat .env | head -20

# Should show proper environment variables, not command output
```

## Then Re-run Deployment

After fixing the .env file:

1. Go to: https://github.com/HNG-NINJAS/stage-4-hng/actions
2. Click **Re-run jobs**

Or just push a new commit to trigger deployment.

## What Happened?

Someone likely ran a command like `w` or `who` while editing the .env file, and the output got pasted into it.

The workflow now validates the .env file and recreates it if corrupted.

## Quick Commands

```bash
# Fix it now
ssh -i your-key.pem ubuntu@YOUR_EC2_IP "cd ~/notification-system && rm .env && cp .env.production .env && echo 'Fixed!'"

# Then re-run GitHub Actions
```
