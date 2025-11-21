# Quick AWS Start Guide

## ⚡ Load AWS Credentials

```bash
source aws-credentials.sh
```

## ✅ Verify It Works

```bash
aws sts get-caller-identity
```

## 🎯 Common Commands

```bash
# List S3 buckets
aws s3 ls

# List EC2 instances
aws ec2 describe-instances

# Check available services
aws service-quotas list-services --region us-east-1
```

## 📖 Full Documentation

See [AWS_SETUP.md](./AWS_SETUP.md) for complete setup guide.

