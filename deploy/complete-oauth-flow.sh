#!/bin/bash
# Complete Box OAuth Flow for EC2 Deployment

set -e

INSTANCE_IP="3.239.89.25"
KEY_FILE="contract-protection-key.pem"

echo "🔐 Box OAuth Authorization Flow"
echo "=============================="
echo ""

# Step 1: Get authorization URL
echo "📋 Step 1: Getting authorization URL..."
AUTH_URL=$(ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$INSTANCE_IP" \
    "cd /opt/contract-protection-system/mcp-server-box && \
     source ~/.cargo/env && \
     uv run python3 /tmp/get_oauth_url.py 2>&1 | grep -A 1 'https://account.box.com' | head -1 | tr -d ' '")

if [ -z "$AUTH_URL" ]; then
    echo "❌ Failed to get authorization URL"
    exit 1
fi

echo ""
echo "✅ Authorization URL generated!"
echo ""
echo "📋 Step 2: Authorize the application"
echo ""
echo "Please open this URL in your browser:"
echo ""
echo "$AUTH_URL"
echo ""
echo "After authorization, Box will redirect you to a URL like:"
echo "  http://localhost:8000/callback?code=AUTHORIZATION_CODE"
echo ""
echo "⚠️  Note: The redirect page won't load (localhost), but that's OK!"
echo "   Just copy the AUTHORIZATION_CODE from the URL bar."
echo ""

# Step 3: Get authorization code
read -p "Enter the authorization code from the redirect URL: " AUTH_CODE

if [ -z "$AUTH_CODE" ]; then
    echo "❌ No authorization code provided"
    exit 1
fi

# Step 4: Complete OAuth
echo ""
echo "📋 Step 3: Completing OAuth authorization..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$INSTANCE_IP" \
    "cd /opt/contract-protection-system/mcp-server-box && \
     source ~/.cargo/env && \
     uv run python3 /tmp/complete_oauth.py '$AUTH_CODE'"

echo ""
echo "📋 Step 4: Verifying service status..."
sleep 3
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$INSTANCE_IP" \
    "sudo systemctl status contract-protection-system --no-pager | head -15"

echo ""
echo "✅ OAuth flow complete!"
echo ""
echo "The service should now be running. Check logs with:"
echo "  ssh -i $KEY_FILE ec2-user@$INSTANCE_IP 'sudo journalctl -u contract-protection-system -f'"

