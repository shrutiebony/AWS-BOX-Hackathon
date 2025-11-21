# AWS Deployment Guide - Contract Protection System

This guide walks you through deploying the Contract Protection System on AWS EC2.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Box API Credentials** (Client ID and Secret)
4. **SSH Key Pair** (will be created automatically if needed)

## Architecture

```
┌─────────────────┐
│   Box API       │
│   (Contracts)   │
└────────┬────────┘
         │
         │ OAuth
         │
┌────────▼────────────────────────┐
│   EC2 Instance                 │
│   ┌──────────────────────────┐ │
│   │ Contract Processor        │ │
│   │ - Monitors Box folder    │ │
│   │ - Processes contracts     │ │
│   │ - Detects action items    │ │
│   └──────────────────────────┘ │
│                                 │
│   ┌──────────────────────────┐ │
│   │ AWS Secrets Manager      │ │
│   │ (Stores credentials)      │ │
│   └──────────────────────────┘ │
└────────┬───────────────────────┘
         │
         │ SNS
         │
┌────────▼────────┐
│   AWS SNS        │
│   (Email Alerts) │
└──────────────────┘
```

## Step-by-Step Deployment

### Step 1: Prepare Credentials

1. Copy the secrets template:
   ```bash
   cd deploy/
   cp secrets.json.example secrets.json
   ```

2. Edit `secrets.json` with your credentials:
   ```json
   {
     "BOX_CLIENT_ID": "your_actual_client_id",
     "BOX_CLIENT_SECRET": "your_actual_client_secret",
     "BOX_REDIRECT_URL": "http://localhost:8080/callback",
     "BOX_MCP_SERVER_AUTH_TOKEN": "generate_random_token",
     "AWS_SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:ACCOUNT_ID:contract-action-items",
     "USER_EMAIL": "your_email@example.com"
   }
   ```

### Step 2: Setup AWS Infrastructure

Run the infrastructure setup script:

```bash
cd deploy/
chmod +x *.sh
./setup-aws-infrastructure.sh
```

This script will:
- ✅ Create IAM role and instance profile
- ✅ Create IAM policy for Secrets Manager and SNS access
- ✅ Create AWS Secrets Manager secret
- ✅ Create/verify SNS topic
- ✅ Configure all necessary permissions

**Note:** If `secrets.json` doesn't exist, the script will create a template. Edit it and run the script again.

### Step 3: Update Secrets (if needed)

If you need to update secrets after initial setup:

```bash
aws secretsmanager update-secret \
    --secret-id contract-protection-system/credentials \
    --secret-string file://secrets.json \
    --region us-east-1
```

### Step 4: Deploy EC2 Instance

Launch the EC2 instance:

```bash
./deploy-ec2.sh
```

This will:
- ✅ Create security group
- ✅ Launch EC2 instance with Amazon Linux 2023
- ✅ Install Python, dependencies, and setup scripts
- ✅ Configure systemd service

**Wait 2-3 minutes** for the instance setup to complete.

### Step 5: Deploy Application Code

Deploy the application to the EC2 instance:

```bash
# Get instance ID from previous step output, then:
./deploy-app-to-ec2.sh <instance-id>
```

For example:
```bash
./deploy-app-to-ec2.sh i-1234567890abcdef0
```

This will:
- ✅ Upload application files
- ✅ Install dependencies
- ✅ Fetch secrets from AWS Secrets Manager
- ✅ Start the service

### Step 6: Verify Deployment

Check service status:

```bash
# Get instance IP from deploy-ec2.sh output
ssh -i contract-protection-key.pem ec2-user@<public-ip> \
    'sudo systemctl status contract-protection-system'
```

View logs:

```bash
ssh -i contract-protection-key.pem ec2-user@<public-ip> \
    'sudo journalctl -u contract-protection-system -f'
```

## Configuration

### Environment Variables

The application reads from:
1. **AWS Secrets Manager** (primary) - automatically fetched on startup
2. **`.env` file** (fallback) - created from secrets

### Service Management

**Start service:**
```bash
sudo systemctl start contract-protection-system
```

**Stop service:**
```bash
sudo systemctl stop contract-protection-system
```

**Restart service:**
```bash
sudo systemctl restart contract-protection-system
```

**View logs:**
```bash
sudo journalctl -u contract-protection-system -f
```

**Check status:**
```bash
sudo systemctl status contract-protection-system
```

## Monitoring

### Application Logs

Logs are stored in systemd journal:
```bash
sudo journalctl -u contract-protection-system -f
```

### CloudWatch Logs (Optional)

To send logs to CloudWatch, install CloudWatch agent:
```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm
```

## Troubleshooting

### Service won't start

1. Check logs:
   ```bash
   sudo journalctl -u contract-protection-system -n 50
   ```

2. Verify secrets are accessible:
   ```bash
   sudo python3.11 /opt/contract-protection-system/fetch-secrets.py
   ```

3. Check Box OAuth:
   - Ensure OAuth flow is completed
   - Verify credentials in Secrets Manager

### Can't connect to Box API

1. Verify Box credentials in Secrets Manager
2. Check OAuth token is valid
3. Ensure Box app is authorized

### SNS notifications not working

1. Verify SNS topic ARN in secrets
2. Check email subscription is confirmed
3. Verify IAM permissions for SNS

### Instance not accessible

1. Check security group allows SSH (port 22)
2. Verify instance is running
3. Check key file permissions: `chmod 400 contract-protection-key.pem`

## Cost Estimation

**EC2 Instance (t3.micro):**
- ~$7-10/month (depending on usage)

**AWS Secrets Manager:**
- $0.40/secret/month
- $0.05 per 10,000 API calls

**SNS:**
- First 1 million requests/month: Free
- Email notifications: Free

**Total estimated cost: ~$8-11/month**

## Security Best Practices

1. **Secrets Management:**
   - ✅ Credentials stored in AWS Secrets Manager
   - ✅ Never commit secrets to git
   - ✅ Rotate secrets regularly

2. **IAM Permissions:**
   - ✅ Least privilege principle
   - ✅ Instance profile (no access keys on instance)

3. **Network Security:**
   - ✅ Security group restricts access
   - ✅ SSH key-based authentication

4. **Application Security:**
   - ✅ Service runs as non-root user
   - ✅ Logs stored securely
   - ✅ Automatic restarts on failure

## Cleanup

To remove all resources:

```bash
# Terminate EC2 instance
aws ec2 terminate-instances --instance-ids <instance-id>

# Delete security group
aws ec2 delete-security-group --group-id <sg-id>

# Delete secret (optional)
aws secretsmanager delete-secret --secret-id contract-protection-system/credentials --force-delete-without-recovery

# Delete IAM role and policy
aws iam detach-role-policy --role-name ContractProtectionSystemRole --policy-arn <policy-arn>
aws iam delete-role --role-name ContractProtectionSystemRole
aws iam delete-policy --policy-arn <policy-arn>
aws iam delete-instance-profile --instance-profile-name ContractProtectionSystemInstanceProfile
```

## Support

For issues or questions:
1. Check application logs
2. Verify AWS resources are configured correctly
3. Ensure Box OAuth is completed
4. Review IAM permissions

