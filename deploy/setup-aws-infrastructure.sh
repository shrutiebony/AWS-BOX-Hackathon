#!/bin/bash
# Setup AWS Infrastructure for Contract Protection System
# This script creates IAM roles, Secrets Manager secrets, and prepares for EC2 deployment

set -e

REGION="${AWS_DEFAULT_REGION:-us-east-1}"
STACK_NAME="contract-protection-system"
SECRET_NAME="contract-protection-system/credentials"
IAM_ROLE_NAME="ContractProtectionSystemRole"
INSTANCE_PROFILE_NAME="ContractProtectionSystemInstanceProfile"

echo "🚀 Setting up AWS Infrastructure for Contract Protection System"
echo "Region: $REGION"

# Check AWS credentials
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS credentials not configured. Please run: source aws-credentials.sh"
    exit 1
fi

# 1. Create IAM Role for EC2
echo ""
echo "📋 Step 1: Creating IAM Role..."
if aws iam get-role --role-name "$IAM_ROLE_NAME" &>/dev/null; then
    echo "   IAM Role already exists: $IAM_ROLE_NAME"
else
    # Create trust policy
    cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Create IAM role
    aws iam create-role \
        --role-name "$IAM_ROLE_NAME" \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --description "IAM role for Contract Protection System EC2 instance" \
        --region "$REGION"
    
    echo "   ✅ Created IAM Role: $IAM_ROLE_NAME"
fi

# 2. Attach IAM Policy
echo ""
echo "📋 Step 2: Attaching IAM Policy..."
POLICY_ARN="arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/ContractProtectionSystemPolicy"

# Create policy if it doesn't exist
if ! aws iam get-policy --policy-arn "$POLICY_ARN" &>/dev/null; then
    aws iam create-policy \
        --policy-name "ContractProtectionSystemPolicy" \
        --policy-document file://iam-policy.json \
        --description "Policy for Contract Protection System" \
        --region "$REGION"
    echo "   ✅ Created IAM Policy"
else
    echo "   IAM Policy already exists"
fi

# Attach policy to role
aws iam attach-role-policy \
    --role-name "$IAM_ROLE_NAME" \
    --policy-arn "$POLICY_ARN" \
    --region "$REGION" 2>/dev/null || echo "   Policy already attached"

# 3. Create Instance Profile
echo ""
echo "📋 Step 3: Creating Instance Profile..."
if aws iam get-instance-profile --instance-profile-name "$INSTANCE_PROFILE_NAME" &>/dev/null; then
    echo "   Instance Profile already exists"
else
    aws iam create-instance-profile \
        --instance-profile-name "$INSTANCE_PROFILE_NAME" \
        --region "$REGION"
    
    aws iam add-role-to-instance-profile \
        --instance-profile-name "$INSTANCE_PROFILE_NAME" \
        --role-name "$IAM_ROLE_NAME" \
        --region "$REGION"
    
    echo "   ✅ Created Instance Profile: $INSTANCE_PROFILE_NAME"
fi

# Wait for instance profile to be ready
echo "   Waiting for instance profile to be ready..."
sleep 5

# 4. Create Secrets Manager Secret
echo ""
echo "📋 Step 4: Setting up Secrets Manager..."
if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --region "$REGION" &>/dev/null; then
    echo "   Secret already exists: $SECRET_NAME"
    echo "   To update, run: aws secretsmanager update-secret --secret-id $SECRET_NAME --secret-string file://secrets.json"
else
    # Check if secrets.json exists
    if [ ! -f "secrets.json" ]; then
        echo "   ⚠️  secrets.json not found. Creating template..."
        cat > secrets.json <<EOF
{
  "BOX_CLIENT_ID": "your_box_client_id",
  "BOX_CLIENT_SECRET": "your_box_client_secret",
  "BOX_REDIRECT_URL": "http://localhost:8080/callback",
  "BOX_MCP_SERVER_AUTH_TOKEN": "generate_random_token_here",
  "AWS_SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:contract-action-items",
  "USER_EMAIL": "your_email@example.com"
}
EOF
        echo "   📝 Please edit secrets.json with your credentials, then run this script again"
        exit 1
    fi
    
    aws secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --description "Credentials for Contract Protection System" \
        --secret-string file://secrets.json \
        --region "$REGION"
    
    echo "   ✅ Created Secret: $SECRET_NAME"
fi

# 5. Get SNS Topic ARN (create if doesn't exist)
echo ""
echo "📋 Step 5: Checking SNS Topic..."
SNS_TOPIC_NAME="contract-action-items"
SNS_TOPIC_ARN=$(aws sns list-topics --region "$REGION" --query "Topics[?contains(TopicArn, '$SNS_TOPIC_NAME')].TopicArn" --output text)

if [ -z "$SNS_TOPIC_ARN" ]; then
    echo "   Creating SNS Topic..."
    SNS_TOPIC_ARN=$(aws sns create-topic \
        --name "$SNS_TOPIC_NAME" \
        --region "$REGION" \
        --query 'TopicArn' --output text)
    echo "   ✅ Created SNS Topic: $SNS_TOPIC_ARN"
else
    echo "   ✅ SNS Topic exists: $SNS_TOPIC_ARN"
fi

echo ""
echo "✅ Infrastructure setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit secrets.json with your Box credentials"
echo "   2. Update SNS Topic ARN in secrets.json: $SNS_TOPIC_ARN"
echo "   3. Run: aws secretsmanager update-secret --secret-id $SECRET_NAME --secret-string file://secrets.json"
echo "   4. Run: ./deploy-ec2.sh to launch EC2 instance"
echo ""
echo "📋 Summary:"
echo "   IAM Role: $IAM_ROLE_NAME"
echo "   Instance Profile: $INSTANCE_PROFILE_NAME"
echo "   Secret: $SECRET_NAME"
echo "   SNS Topic: $SNS_TOPIC_ARN"

