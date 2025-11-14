# Fix: SSH Key Error in GitHub Actions

## Error Message
```
Load key "/home/runner/.ssh/deploy_key": error in libcrypto
Permission denied (publickey)
```

## Problem
The SSH key in your GitHub secret `EC2_SSH_KEY` has formatting issues or extra characters.

## Solution: Re-add SSH Key Correctly

### Step 1: Get Your SSH Key Properly

```bash
# Display your key
cat your-key.pem

# The output should look EXACTLY like this:
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(many lines of base64 encoded data)
...
-----END RSA PRIVATE KEY-----
```

Or for newer keys:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEA...
(many lines of base64 encoded data)
...
-----END OPENSSH PRIVATE KEY-----
```

### Step 2: Copy Key Correctly

**Option A: Using cat (Recommended)**
```bash
# Copy to clipboard (macOS)
cat your-key.pem | pbcopy

# Copy to clipboard (Linux with xclip)
cat your-key.pem | xclip -selection clipboard

# Or just display and manually copy
cat your-key.pem
```

**Option B: Using a text editor**
```bash
# Open in nano
nano your-key.pem

# Select all (Ctrl+A), Copy (Ctrl+K), then exit without saving
```

### Step 3: Update GitHub Secret

1. Go to: `https://github.com/HNG-NINJAS/stage-4-hng/settings/secrets/actions`
2. Find `EC2_SSH_KEY`
3. Click **Update** (or delete and create new)
4. Paste the key content
5. **Important checks:**
   - ✅ First line is `-----BEGIN RSA PRIVATE KEY-----` or `-----BEGIN OPENSSH PRIVATE KEY-----`
   - ✅ Last line is `-----END RSA PRIVATE KEY-----` or `-----END OPENSSH PRIVATE KEY-----`
   - ✅ No extra spaces before or after
   - ✅ No extra blank lines at the end
   - ✅ All lines are present

### Step 4: Verify Key Format

Before adding to GitHub, verify your key is valid:

```bash
# Check key format
head -1 your-key.pem
# Should show: -----BEGIN RSA PRIVATE KEY----- or -----BEGIN OPENSSH PRIVATE KEY-----

tail -1 your-key.pem
# Should show: -----END RSA PRIVATE KEY----- or -----END OPENSSH PRIVATE KEY-----

# Test the key locally
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
# If this works, the key is valid
```

### Step 5: Test Again

After updating the secret:
1. Go to GitHub Actions
2. Click **Actions** tab
3. Select your workflow
4. Click **Run workflow** → **Run workflow**
5. Watch the logs

## Common Issues

### Issue 1: Extra Newlines
**Problem**: Extra blank lines at the end of the key

**Fix**: 
```bash
# Remove trailing newlines
cat your-key.pem | sed '/^$/d' > your-key-clean.pem
cat your-key-clean.pem
# Copy this output
```

### Issue 2: Windows Line Endings
**Problem**: Key was edited on Windows (CRLF instead of LF)

**Fix**:
```bash
# Convert to Unix format
dos2unix your-key.pem

# Or use sed
sed -i 's/\r$//' your-key.pem
```

### Issue 3: Wrong Key File
**Problem**: Using the wrong .pem file

**Fix**: Make sure you're using the key that matches your EC2 instance
```bash
# Check which key your EC2 uses
# AWS Console → EC2 → Instances → Select instance → Key pair name
```

### Issue 4: Key Permissions on Local Machine
**Problem**: Key has wrong permissions locally

**Fix**:
```bash
chmod 400 your-key.pem
```

## Verification Checklist

Before adding to GitHub, verify:

- [ ] Key file has correct permissions (400 or 600)
- [ ] Can SSH to EC2 manually: `ssh -i your-key.pem ubuntu@YOUR_EC2_IP`
- [ ] Key starts with `-----BEGIN`
- [ ] Key ends with `-----END`
- [ ] No extra spaces or blank lines
- [ ] Using the correct key for your EC2 instance

## Alternative: Use GitHub CLI

If you have GitHub CLI installed:

```bash
# Set secret using file
gh secret set EC2_SSH_KEY < your-key.pem

# Or set interactively
gh secret set EC2_SSH_KEY
# Then paste the key and press Ctrl+D
```

## Test SSH Connection Manually

Before running GitHub Actions, test SSH manually:

```bash
# Test connection
ssh -i your-key.pem -v ubuntu@YOUR_EC2_IP

# The -v flag shows verbose output
# Look for "Authentication succeeded (publickey)"
```

## Quick Fix Commands

```bash
# 1. Verify key format
cat your-key.pem | head -1
cat your-key.pem | tail -1

# 2. Test SSH locally
ssh -i your-key.pem ubuntu@YOUR_EC2_IP "echo 'SSH works!'"

# 3. Copy key correctly
cat your-key.pem | pbcopy  # macOS
cat your-key.pem | xclip -selection clipboard  # Linux

# 4. Update GitHub secret
# Go to GitHub → Settings → Secrets → Update EC2_SSH_KEY

# 5. Re-run workflow
# GitHub → Actions → Re-run jobs
```

## Still Not Working?

### Check EC2 Security Group
```bash
# Ensure port 22 is open
# AWS Console → EC2 → Security Groups → Inbound rules
# Should have: SSH (22) from 0.0.0.0/0
```

### Check EC2 Instance
```bash
# Verify instance is running
# AWS Console → EC2 → Instances → Instance state: Running
```

### Check Key Pair Name
```bash
# Verify you're using the right key
# AWS Console → EC2 → Instances → Key pair name
# Should match your .pem file name
```

## Example: Correct Key Format

```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAyXxJz1234567890abcdefghijklmnopqrstuvwxyzABCDEFGH
IJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKL
MNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOP
... (many more lines) ...
QRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRST
UVWXYZ1234567890abcdefghijklmnopqrstuvwxyz==
-----END RSA PRIVATE KEY-----
```

**No blank lines before or after!**
