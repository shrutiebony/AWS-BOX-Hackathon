#!/bin/bash
# Deploy EC2 Instance for Contract Protection System

set -e

REGION="${AWS_DEFAULT_REGION:-us-east-1}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.micro}"
KEY_NAME="${KEY_NAME:-contract-protection-key}"
# Get latest Amazon Linux 2023 AMI
AMI_ID="${AMI_ID:-$(aws ec2 describe-images --owners amazon --filters "Name=name,Values=al2023-ami-*" "Name=architecture,Values=x86_64" --region us-east-1 --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' --output text 2>/dev/null || echo 'ami-0c02fb55956c7d316')}"
SECURITY_GROUP_NAME="contract-protection-system-sg"
INSTANCE_PROFILE_NAME="ContractProtectionSystemInstanceProfile"

echo "🚀 Deploying EC2 Instance for Contract Protection System"
echo "Region: $REGION"
echo "Instance Type: $INSTANCE_TYPE"

# Check if infrastructure is set up
if ! aws iam get-instance-profile --instance-profile-name "$INSTANCE_PROFILE_NAME" &>/dev/null; then
    echo "❌ Infrastructure not set up. Please run: ./setup-aws-infrastructure.sh first"
    exit 1
fi

# 1. Create Security Group
echo ""
echo "📋 Step 1: Creating Security Group..."
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
    --region "$REGION" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "")

if [ -z "$SG_ID" ] || [ "$SG_ID" == "None" ]; then
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP_NAME" \
        --description "Security group for Contract Protection System" \
        --region "$REGION" \
        --query 'GroupId' --output text)
    
    # Allow SSH (optional, for debugging)
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region "$REGION" 2>/dev/null || true
    
    echo "   ✅ Created Security Group: $SG_ID"
else
    echo "   Security Group already exists: $SG_ID"
fi

# 2. Get User Data script
USER_DATA_FILE="ec2-user-data.sh"
if [ ! -f "$USER_DATA_FILE" ]; then
    echo "❌ User data file not found: $USER_DATA_FILE"
    exit 1
fi

# Encode user data (base64)
if command -v base64 &> /dev/null; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        USER_DATA=$(base64 < "$USER_DATA_FILE")
    else
        USER_DATA=$(base64 -w 0 < "$USER_DATA_FILE")
    fi
else
    echo "❌ base64 command not found"
    exit 1
fi

# 3. Get Instance Profile ARN
INSTANCE_PROFILE_ARN=$(aws iam get-instance-profile \
    --instance-profile-name "$INSTANCE_PROFILE_NAME" \
    --query 'InstanceProfile.Arn' \
    --output text \
    --region "$REGION")

# 4. Launch EC2 Instance
echo ""
echo "📋 Step 2: Launching EC2 Instance..."

# Check if key pair exists
if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" &>/dev/null; then
    echo "   ⚠️  Key pair '$KEY_NAME' not found. Creating..."
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --region "$REGION" \
        --query 'KeyMaterial' \
        --output text > "${KEY_NAME}.pem"
    chmod 400 "${KEY_NAME}.pem"
    echo "   ✅ Created key pair: ${KEY_NAME}.pem"
fi

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --iam-instance-profile "Arn=$INSTANCE_PROFILE_ARN" \
    --user-data "$USER_DATA" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=ContractProtectionSystem}]" \
    --region "$REGION" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "   ✅ Launched EC2 Instance: $INSTANCE_ID"

# Wait for instance to be running
echo ""
echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region "$REGION" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo ""
echo "✅ EC2 Instance deployed successfully!"
echo ""
echo "📋 Instance Details:"
echo "   Instance ID: $INSTANCE_ID"
echo "   Public IP: $PUBLIC_IP"
echo "   SSH Command: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""
echo "📝 Next steps:"
echo "   1. Wait 2-3 minutes for instance setup to complete"
echo "   2. Run: ./deploy-app-to-ec2.sh $INSTANCE_ID to deploy the application"
echo "   3. Check logs: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP 'sudo journalctl -u contract-protection-system -f'"

