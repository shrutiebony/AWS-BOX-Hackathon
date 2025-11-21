#!/bin/bash
# EC2 User Data Script - Runs on instance launch
# This script installs dependencies and sets up the Contract Protection System

# Don't exit on error - log and continue
set +e
exec > >(tee /var/log/user-data.log) 2>&1

REGION="${AWS_DEFAULT_REGION:-us-east-1}"
SECRET_NAME="contract-protection-system/credentials"
APP_DIR="/opt/contract-protection-system"
LOG_DIR="/var/log/contract-protection-system"

echo "🚀 Starting Contract Protection System setup on EC2..."

# Update system (skip to speed up - can update later)
# yum update -y

# Install Python 3 and pip (works for both AL2 and AL2023)
if command -v dnf &> /dev/null; then
    # Amazon Linux 2023
    dnf install -y python3 python3-pip git curl unzip
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    # Amazon Linux 2
    yum install -y python3 python3-pip git curl unzip
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Create application directory
mkdir -p "$APP_DIR"
mkdir -p "$LOG_DIR"

# Install AWS CLI v2 (if not already installed)
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
    unzip -q /tmp/awscliv2.zip -d /tmp
    /tmp/aws/install
fi

# Install boto3 for Secrets Manager access
$PIP_CMD install boto3 python-dotenv

# Create script to fetch secrets and create .env file
cat > "$APP_DIR/fetch-secrets.py" <<'PYTHON_SCRIPT'
#!/usr/bin/env python3
import boto3
import json
import os
from pathlib import Path

REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
SECRET_NAME = os.getenv('SECRET_NAME', 'contract-protection-system/credentials')
ENV_FILE = Path('/opt/contract-protection-system/.env')

try:
    # Create Secrets Manager client
    client = boto3.client('secretsmanager', region_name=REGION)
    
    # Get secret
    response = client.get_secret_value(SecretId=SECRET_NAME)
    secret = json.loads(response['SecretString'])
    
    # Write to .env file
    with open(ENV_FILE, 'w') as f:
        for key, value in secret.items():
            f.write(f"{key}={value}\n")
    
    # Set permissions
    os.chmod(ENV_FILE, 0o600)
    
    print(f"✅ Secrets fetched and written to {ENV_FILE}")
except Exception as e:
    print(f"❌ Error fetching secrets: {e}")
    exit(1)
PYTHON_SCRIPT

chmod +x "$APP_DIR/fetch-secrets.py"

# Create systemd service file
cat > /etc/systemd/system/contract-protection-system.service <<EOF
[Unit]
Description=Contract Protection System
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$APP_DIR
Environment=AWS_DEFAULT_REGION=$REGION
Environment=SECRET_NAME=$SECRET_NAME
ExecStartPre=$PYTHON_CMD $APP_DIR/fetch-secrets.py
Environment="PATH=/home/ec2-user/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
WorkingDirectory=$APP_DIR
ExecStart=/home/ec2-user/.local/bin/uv run --directory $APP_DIR/mcp-server-box $APP_DIR/contract_processor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=contract-protection-system

[Install]
WantedBy=multi-user.target
EOF

# Create deployment script
cat > "$APP_DIR/deploy-app.sh" <<'DEPLOY_SCRIPT'
#!/bin/bash
set -e

APP_DIR="/opt/contract-protection-system"
cd "$APP_DIR"

echo "📦 Deploying Contract Protection System..."

# Fetch secrets
cd "$APP_DIR"
$PYTHON_CMD fetch-secrets.py

# Clone or update application code
if [ ! -d "mcp-server-box" ]; then
    echo "Cloning mcp-server-box..."
    git clone https://github.com/box-community/mcp-server-box.git
fi

# Copy application files
cp /tmp/contract_processor.py .
cp /tmp/box_contract_service.py .
cp /tmp/action_item_detector.py .
cp /tmp/requirements.txt .

# Install dependencies using pip (faster than uv for initial setup)
# Note: uv can be installed later if needed
$PIP_CMD install -r requirements.txt

# For mcp-server-box, install its dependencies
if [ -d "mcp-server-box" ]; then
    cd mcp-server-box
    $PIP_CMD install -e . || $PIP_CMD install -r requirements.txt 2>/dev/null || true
    cd ..
fi

# Set permissions
chown -R ec2-user:ec2-user "$APP_DIR"
chmod +x contract_processor.py

echo "✅ Application deployed successfully!"
DEPLOY_SCRIPT

chmod +x "$APP_DIR/deploy-app.sh"

# Enable and start the service (will fail until app is deployed, that's ok)
systemctl daemon-reload
systemctl enable contract-protection-system.service

echo "✅ EC2 setup complete!"
echo "📝 Application files need to be uploaded and deployed"
echo "   Run: ./deploy-app-to-ec2.sh to upload and start the application"

