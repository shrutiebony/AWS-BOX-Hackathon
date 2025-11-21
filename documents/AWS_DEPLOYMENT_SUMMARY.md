# AWS Deployment - Complete Setup ✅

Your Contract Protection System is now ready to deploy on AWS!

## 📁 What Was Created

### Deployment Scripts (`deploy/` folder)

1. **`setup-aws-infrastructure.sh`**
   - Creates IAM roles and policies
   - Sets up AWS Secrets Manager
   - Configures SNS topic
   - Sets up instance profile

2. **`deploy-ec2.sh`**
   - Launches EC2 instance (Amazon Linux 2023)
   - Creates security group
   - Installs system dependencies
   - Configures systemd service

3. **`deploy-app-to-ec2.sh`**
   - Uploads application code
   - Installs Python dependencies
   - Fetches secrets from AWS Secrets Manager
   - Starts the service

4. **`quick-deploy.sh`** ⚡
   - **One-command deployment** - runs all steps automatically

5. **`ec2-user-data.sh`**
   - EC2 initialization script (runs on instance launch)
   - Installs Python, uv, AWS CLI
   - Sets up systemd service

6. **`iam-policy.json`**
   - IAM policy for EC2 instance permissions

7. **`secrets.json.example`**
   - Template for storing credentials

8. **`DEPLOYMENT_GUIDE.md`**
   - Complete deployment documentation

9. **`README.md`**
   - Quick reference guide

## 🚀 Quick Start (3 Steps)

### Step 1: Prepare Secrets

```bash
cd deploy/
cp secrets.json.example secrets.json
# Edit secrets.json with your Box credentials
```

Required fields in `secrets.json`:
- `BOX_CLIENT_ID`
- `BOX_CLIENT_SECRET`
- `BOX_REDIRECT_URL`
- `BOX_MCP_SERVER_AUTH_TOKEN`
- `AWS_SNS_TOPIC_ARN`
- `USER_EMAIL`

### Step 2: Load AWS Credentials

```bash
cd ..
source aws-credentials.sh
```

### Step 3: Deploy

```bash
cd deploy/
./quick-deploy.sh
```

That's it! The script will:
1. ✅ Setup AWS infrastructure
2. ✅ Deploy EC2 instance
3. ✅ Install application
4. ✅ Start the service

## 📋 Architecture

```
┌─────────────────┐
│   Box API       │ ← Monitors contracts folder
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   EC2 Instance          │
│   (t3.micro)           │
│                         │
│  ┌──────────────────┐ │
│  │ Contract Processor│ │
│  │ - Monitors Box    │ │
│  │ - Processes files │ │
│  │ - Detects actions │ │
│  └──────────────────┘ │
│                         │
│  ┌──────────────────┐ │
│  │ Secrets Manager   │ │ ← Stores credentials
│  └──────────────────┘ │
└──────────┬─────────────┘
           │
           ▼
┌─────────────────┐
│   AWS SNS       │ ← Sends email alerts
└─────────────────┘
```

## 🔧 What Happens on Deployment

1. **Infrastructure Setup:**
   - IAM role with Secrets Manager and SNS permissions
   - AWS Secrets Manager secret for credentials
   - SNS topic for notifications
   - Security group for EC2

2. **EC2 Instance Launch:**
   - Amazon Linux 2023 AMI
   - t3.micro instance (free tier eligible)
   - User data script installs dependencies
   - Systemd service configured

3. **Application Deployment:**
   - Application code uploaded
   - Python dependencies installed
   - Secrets fetched from Secrets Manager
   - Service started automatically

4. **Service Running:**
   - Monitors Box `contracts/` folder every 60 seconds
   - Checks for action items every hour
   - Processes new contracts automatically
   - Sends email notifications via SNS

## 📊 Monitoring

### Check Service Status

```bash
ssh -i deploy/contract-protection-key.pem ec2-user@<public-ip> \
    'sudo systemctl status contract-protection-system'
```

### View Logs

```bash
ssh -i deploy/contract-protection-key.pem ec2-user@<public-ip> \
    'sudo journalctl -u contract-protection-system -f'
```

### Service Management

```bash
# Start
sudo systemctl start contract-protection-system

# Stop
sudo systemctl stop contract-protection-system

# Restart
sudo systemctl restart contract-protection-system

# Status
sudo systemctl status contract-protection-system
```

## 💰 Cost Estimate

- **EC2 t3.micro**: ~$7-10/month
- **Secrets Manager**: ~$0.40/month
- **SNS**: Free (first 1M requests)
- **Total**: ~$8-11/month

## 🔒 Security Features

✅ **Credentials Management:**
- Stored in AWS Secrets Manager (encrypted)
- Never stored on disk or in code
- Automatically fetched on startup

✅ **IAM Permissions:**
- Least privilege principle
- Instance profile (no access keys)
- Only necessary permissions granted

✅ **Network Security:**
- Security group restricts access
- SSH key-based authentication

✅ **Application Security:**
- Runs as non-root user
- Automatic restarts on failure
- Secure logging

## 📝 Next Steps After Deployment

1. **Verify Service:**
   ```bash
   # Get instance IP from deployment output
   ssh -i deploy/contract-protection-key.pem ec2-user@<ip> \
       'sudo systemctl status contract-protection-system'
   ```

2. **Test Contract Processing:**
   - Upload a contract to Box `contracts/` folder
   - Wait 60 seconds
   - Check `protect_your_interests/` folder for outputs

3. **Test Action Items:**
   - Upload a contract with upcoming deadlines
   - Wait for hourly check
   - Verify email notification received

4. **Monitor Logs:**
   - Watch logs for any errors
   - Verify Box API connections
   - Check SNS notifications

## 🐛 Troubleshooting

### Service Won't Start

1. Check logs:
   ```bash
   sudo journalctl -u contract-protection-system -n 50
   ```

2. Verify secrets:
   ```bash
   sudo python3.11 /opt/contract-protection-system/fetch-secrets.py
   ```

3. Check Box OAuth:
   - Ensure OAuth flow completed
   - Verify credentials in Secrets Manager

### Can't Connect to Box

- Verify Box credentials in Secrets Manager
- Check OAuth token is valid
- Ensure Box app is authorized

### SNS Not Working

- Verify SNS topic ARN in secrets
- Check email subscription confirmed
- Verify IAM permissions

## 📚 Documentation

- **`DEPLOYMENT_GUIDE.md`** - Detailed step-by-step guide
- **`README.md`** - Quick reference
- **`secrets.json.example`** - Credentials template

## 🎯 Summary

Your application is now ready to deploy on AWS! The deployment is:

- ✅ **Automated** - One command deployment
- ✅ **Secure** - Credentials in Secrets Manager
- ✅ **Scalable** - Easy to upgrade instance size
- ✅ **Monitored** - Systemd service with logging
- ✅ **Cost-effective** - ~$8-11/month

Just run `./quick-deploy.sh` and you're done! 🚀

