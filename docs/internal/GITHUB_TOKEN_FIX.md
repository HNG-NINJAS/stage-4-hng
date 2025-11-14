# Fix: GitHub Workflow Push Error

## Problem

```
[remote rejected] main -> main (refusing to allow a Personal Access Token 
to create or update workflow `.github/workflows/deploy.yml` without `workflow` scope)
```

## Solution: Update Your GitHub Personal Access Token

### Step 1: Create New Token with Workflow Scope

1. Go to GitHub.com
2. Click your profile picture → **Settings**
3. Scroll down → **Developer settings** (left sidebar)
4. Click **Personal access tokens** → **Tokens (classic)**
5. Click **Generate new token** → **Generate new token (classic)**

### Step 2: Configure Token Scopes

Give your token a name: `HNG-NINJAS-Workflow-Access`

Select these scopes:
- ✅ **repo** (Full control of private repositories)
  - ✅ repo:status
  - ✅ repo_deployment
  - ✅ public_repo
  - ✅ repo:invite
  - ✅ security_events
- ✅ **workflow** ← **THIS IS THE IMPORTANT ONE!**

### Step 3: Generate and Copy Token

1. Click **Generate token** at the bottom
2. **Copy the token immediately** (you won't see it again!)
3. Save it somewhere safe temporarily

### Step 4: Update Git Credentials

#### On Linux/macOS:
```bash
# Remove old credential
git credential reject << EOF
protocol=https
host=github.com
EOF

# Next push will ask for credentials
git push -u origin main
# Username: your-github-username
# Password: paste-your-new-token
```

#### Or update credential helper:
```bash
# Check current credential helper
git config --global credential.helper

# If using store
nano ~/.git-credentials
# Update the line with your new token:
# https://YOUR_USERNAME:NEW_TOKEN@github.com

# If using cache, just push again and enter new token
git push -u origin main
```

### Step 5: Test
```bash
git push -u origin main
# Should work now! ✅
```

## Alternative: Push Without Workflow File First

If you can't update the token right now:

```bash
# Temporarily remove workflow file from staging
git reset HEAD .github/workflows/deploy.yml

# Commit and push other files
git commit -m "Add AWS deployment setup (without workflow)"
git push -u origin main

# Add workflow file later via GitHub web interface
# or after updating your token
```

## Quick Fix Commands

```bash
# Option A: Update token and retry
git credential reject << EOF
protocol=https
host=github.com
EOF
git push -u origin main
# Enter username and NEW token

# Option B: Push without workflow file
git reset HEAD .github/workflows/deploy.yml
git commit -m "Add AWS deployment documentation and scripts"
git push -u origin main
```

## Why This Happens

GitHub requires the `workflow` scope for security reasons:
- Workflow files can run code on GitHub's servers
- They can access secrets
- They need special permission to modify

## Verify Token Scopes

After creating new token, verify it has `workflow` scope:
```bash
# Test with curl
curl -H "Authorization: token YOUR_NEW_TOKEN" \
  https://api.github.com/user

# Check scopes in response headers
curl -I -H "Authorization: token YOUR_NEW_TOKEN" \
  https://api.github.com/user | grep x-oauth-scopes
```

Should show: `x-oauth-scopes: repo, workflow, ...`
