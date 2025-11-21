#!/bin/bash
# Quick Deploy Script - Runs all deployment steps in sequence

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Quick Deploy - Contract Protection System"
echo "=============================================="
echo ""

# Check AWS credentials
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS credentials not configured"
    echo "   Please run: source ../aws-credentials.sh"
    exit 1
fi

# Step 1: Setup infrastructure
echo "📋 Step 1/4: Setting up AWS infrastructure..."
./setup-aws-infrastructure.sh

# Check if secrets.json exists
if [ ! -f "secrets.json" ]; then
    echo ""
    echo "⚠️  secrets.json not found!"
    echo "   Please create secrets.json from secrets.json.example"
    echo "   Then run this script again"
    exit 1
fi

# Step 2: Update secrets
echo ""
echo "📋 Step 2/4: Updating secrets in AWS Secrets Manager..."
SECRET_NAME="contract-protection-system/credentials"
aws secretsmanager update-secret \
    --secret-id "$SECRET_NAME" \
    --secret-string file://secrets.json \
    --region "${AWS_DEFAULT_REGION:-us-east-1}" \
    > /dev/null 2>&1 || \
aws secretsmanager create-secret \
    --name "$SECRET_NAME" \
    --description "Credentials for Contract Protection System" \
    --secret-string file://secrets.json \
    --region "${AWS_DEFAULT_REGION:-us-east-1}" \
    > /dev/null

echo "   ✅ Secrets updated"

# Step 3: Deploy EC2
echo ""
echo "📋 Step 3/4: Deploying EC2 instance..."
INSTANCE_ID=$(./deploy-ec2.sh 2>&1 | grep "Instance ID:" | awk '{print $3}')

if [ -z "$INSTANCE_ID" ]; then
    echo "   ❌ Failed to get instance ID"
    exit 1
fi

echo "   ✅ Instance deployed: $INSTANCE_ID"

# Wait a bit for instance to be ready
echo ""
echo "⏳ Waiting 60 seconds for instance setup..."
sleep 60

# Step 4: Deploy application
echo ""
echo "📋 Step 4/4: Deploying application..."
./deploy-app-to-ec2.sh "$INSTANCE_ID"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Wait 2-3 minutes for service to start"
echo "   2. Check service status (get IP from above output):"
echo "      ssh -i contract-protection-key.pem ec2-user@<ip> 'sudo systemctl status contract-protection-system'"
echo "   3. View logs:"
echo "      ssh -i contract-protection-key.pem ec2-user@<ip> 'sudo journalctl -u contract-protection-system -f'"

