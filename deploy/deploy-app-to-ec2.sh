#!/bin/bash
# Deploy application code to EC2 instance

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <instance-id> [public-ip]"
    echo "Example: $0 i-1234567890abcdef0"
    exit 1
fi

INSTANCE_ID="$1"
PUBLIC_IP="${2:-}"

REGION="${AWS_DEFAULT_REGION:-us-east-1}"
KEY_NAME="${KEY_NAME:-contract-protection-key}"
APP_DIR="/opt/contract-protection-system"
KEY_FILE="${KEY_NAME}.pem"

echo "🚀 Deploying application to EC2 instance: $INSTANCE_ID"

# Get public IP if not provided
if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids "$INSTANCE_ID" \
        --region "$REGION" \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
fi

if [ -z "$PUBLIC_IP" ] || [ "$PUBLIC_IP" == "None" ]; then
    echo "❌ Could not get public IP for instance"
    exit 1
fi

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ Key file not found: $KEY_FILE"
    exit 1
fi

chmod 400 "$KEY_FILE"

# Wait for SSH to be available
echo "⏳ Waiting for SSH to be available..."
for i in {1..30}; do
    if ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no -o ConnectTimeout=5 ec2-user@"$PUBLIC_IP" "echo 'SSH ready'" &>/dev/null; then
        echo "✅ SSH is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ SSH not available after 5 minutes"
        exit 1
    fi
    sleep 10
done

# Create temporary directory for files
TEMP_DIR=$(mktemp -d)
echo "📦 Preparing application files..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Copy application files
cp "$PROJECT_ROOT/contract_processor.py" "$TEMP_DIR/"
cp "$PROJECT_ROOT/box_contract_service.py" "$TEMP_DIR/"
cp "$PROJECT_ROOT/action_item_detector.py" "$TEMP_DIR/"
cp "$PROJECT_ROOT/requirements.txt" "$TEMP_DIR/"

# Copy to EC2
echo "📤 Uploading files to EC2..."
scp -i "$KEY_FILE" -o StrictHostKeyChecking=no \
    "$TEMP_DIR"/*.py \
    "$TEMP_DIR"/*.txt \
    ec2-user@"$PUBLIC_IP":/tmp/

# Deploy application on EC2
echo "🔧 Deploying application on EC2..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$PUBLIC_IP" <<'ENDSSH'
    sudo /opt/contract-protection-system/deploy-app.sh
    sudo systemctl restart contract-protection-system.service
    echo "✅ Application deployed and service restarted"
ENDSSH

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Application deployed successfully!"
echo ""
echo "📋 Check service status:"
echo "   ssh -i $KEY_FILE ec2-user@$PUBLIC_IP 'sudo systemctl status contract-protection-system'"
echo ""
echo "📋 View logs:"
echo "   ssh -i $KEY_FILE ec2-user@$PUBLIC_IP 'sudo journalctl -u contract-protection-system -f'"

