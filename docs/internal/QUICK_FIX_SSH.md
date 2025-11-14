# Quick Fix: SSH Key Error

## Your Error
```
Load key "/home/runner/.ssh/deploy_key": error in libcrypto
Permission denied (publickey)
```

## Fix in 3 Steps

### 1. Get Your SSH Key Correctly
```bash
# Display your .pem file
cat your-key.pem

# Should look like this (no extra spaces or blank lines):
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(many lines)
...
-----END RSA PRIVATE KEY-----
```

### 2. Test SSH Locally First
```bash
# Test that your key works
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# If this works, the key is valid ✅
# If this fails, fix your EC2 security group or key
```

### 3. Update GitHub Secret
1. Go to: https://github.com/HNG-NINJAS/stage-4-hng/settings/secrets/actions
2. Click on `EC2_SSH_KEY`
3. Click **Update**
4. Paste the **entire** key content (including BEGIN/END lines)
5. Click **Update secret**

### 4. Re-run Workflow
1. Go to: https://github.com/HNG-NINJAS/stage-4-hng/actions
2. Click on the failed workflow
3. Click **Re-run jobs** → **Re-run failed jobs**

## Common Mistakes

❌ **Missing BEGIN/END lines**
```
MIIEpAIBAAKCAQEA...  ← WRONG! Missing -----BEGIN line
```

❌ **Extra blank lines**
```
-----BEGIN RSA PRIVATE KEY-----

MIIEpAIBAAKCAQEA...  ← WRONG! Extra blank line
```

❌ **Extra spaces**
```
  -----BEGIN RSA PRIVATE KEY-----  ← WRONG! Spaces before/after
```

✅ **Correct format**
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----
```

## Still Not Working?

### Check EC2 Security Group
- Port 22 must be open from 0.0.0.0/0
- AWS Console → EC2 → Security Groups → Inbound rules

### Check You're Using the Right Key
- AWS Console → EC2 → Instances → Your instance → Key pair name
- Must match your .pem file

### Check EC2 User
- For Ubuntu AMI: use `ubuntu`
- For Amazon Linux: use `ec2-user`

## Need More Help?

See detailed guide: `docs/FIX_SSH_KEY_ERROR.md`
