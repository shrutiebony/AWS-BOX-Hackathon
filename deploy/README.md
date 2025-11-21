# AWS Deployment - Contract Protection System

Complete AWS deployment solution for the Contract Protection System.

## Quick Start

1. **Prepare secrets:**
   ```bash
   cd deploy/
   cp secrets.json.example secrets.json
   # Edit secrets.json with your credentials
   ```

2. **Deploy everything:**
   ```bash
   source ../aws-credentials.sh  # Load AWS credentials
   ./quick-deploy.sh
   ```

That's it! The script will:
- ✅ Setup AWS infrastructure (IAM, Secrets Manager, SNS)
- ✅ Deploy EC2 instance
- ✅ Install and configure the application
- ✅ Start the service

## Manual Deployment Steps

If you prefer step-by-step:

### 1. Setup Infrastructure
```bash
./setup-aws-infrastructure.sh
```

### 2. Update Secrets
Edit `secrets.json` and update:
```bash
aws secretsmanager update-secret \
    --secret-id contract-protection-system/credentials \
    --secret-string file://secrets.json
```

### 3. Deploy EC2 Instance
```bash
./deploy-ec2.sh
```

### 4. Deploy Application
```bash
./deploy-app-to-ec2.sh <instance-id>
```

## Files

- **`setup-aws-infrastructure.sh`** - Creates IAM roles, Secrets Manager, SNS
- **`deploy-ec2.sh`** - Launches EC2 instance with user data
- **`deploy-app-to-ec2.sh`** - Uploads and deploys application code
- **`ec2-user-data.sh`** - EC2 initialization script (runs on instance launch)
- **`iam-policy.json`** - IAM policy for EC2 instance
- **`secrets.json.example`** - Template for credentials
- **`quick-deploy.sh`** - Automated full deployment
- **`DEPLOYMENT_GUIDE.md`** - Detailed deployment documentation

## Architecture

```
┌─────────────┐
│   Box API   │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│   EC2 Instance       │
│  ┌────────────────┐ │
│  │ Contract       │ │
│  │ Processor      │ │
│  └────────────────┘ │
│                      │
│  ┌────────────────┐ │
│  │ Secrets       │ │
│  │ Manager       │ │
│  └────────────────┘ │
└──────────┬───────────┘
           │
           ▼
┌─────────────┐
│   AWS SNS   │
└─────────────┘
```

## Requirements

- AWS CLI configured
- Box API credentials
- SSH key pair (auto-created if needed)

## Cost

- **EC2 t3.micro**: ~$7-10/month
- **Secrets Manager**: ~$0.40/month
- **SNS**: Free tier
- **Total**: ~$8-11/month

## Troubleshooting

See `DEPLOYMENT_GUIDE.md` for detailed troubleshooting steps.

## Security

- ✅ Credentials stored in AWS Secrets Manager
- ✅ IAM roles (no access keys on instance)
- ✅ Security groups restrict access
- ✅ Service runs as non-root user

