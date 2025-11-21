#!/bin/bash
# Quick OAuth completion - generates URL and waits for code

INSTANCE_IP="3.239.89.25"
KEY_FILE="contract-protection-key.pem"

echo "🔐 Quick Box OAuth Setup"
echo "======================="
echo ""

# Get fresh authorization URL
echo "📋 Generating fresh authorization URL..."
AUTH_URL=$(ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$INSTANCE_IP" \
    "cd /opt/contract-protection-system/mcp-server-box && \
     source ~/.cargo/env && \
     uv run python3 /tmp/get_oauth_url.py 2>&1 | grep 'https://account.box.com' | head -1")

if [ -z "$AUTH_URL" ]; then
    echo "❌ Failed to get URL. Trying alternative method..."
    AUTH_URL=$(ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$INSTANCE_IP" \
        "cd /opt/contract-protection-system/mcp-server-box && \
         source ~/.cargo/env && \
         uv run python3 << 'PYEOF'
import os, sys
from pathlib import Path
env_file = Path('/opt/contract-protection-system/.env')
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()
os.chdir('/opt/contract-protection-system/mcp-server-box')
sys.path.insert(0, '/opt/contract-protection-system/mcp-server-box/src')
from box_sdk_gen import BoxOAuth, OAuthConfig, FileWithInMemoryCacheTokenStorage, GetAuthorizeUrlOptions
from config import AppConfig
app_config = AppConfig.from_env()
box_config = app_config.box_api
redirect_url = os.getenv('BOX_REDIRECT_URL', 'http://localhost:8000/callback')
token_file = Path('/opt/contract-protection-system/mcp-server-box/.auth.oauth')
oauth_config = OAuthConfig(
    client_id=box_config.client_id,
    client_secret=box_config.client_secret,
    token_storage=FileWithInMemoryCacheTokenStorage(str(token_file)),
)
oauth = BoxOAuth(oauth_config)
auth_url_options = GetAuthorizeUrlOptions(redirect_uri=redirect_url)
auth_url = oauth.get_authorize_url(options=auth_url_options)
print(auth_url)
PYEOF
")
fi

echo ""
echo "✅ Fresh Authorization URL:"
echo ""
echo "$AUTH_URL"
echo ""
echo "⚠️  IMPORTANT: Authorization codes expire in ~30 seconds!"
echo ""
echo "📝 Quick Steps:"
echo "   1. Open the URL above NOW"
echo "   2. Authorize immediately"
echo "   3. Copy the code from the redirect URL"
echo "   4. Run this command immediately:"
echo ""
echo "   ssh -i $KEY_FILE ec2-user@$INSTANCE_IP \\"
echo "       \"cd /opt/contract-protection-system/mcp-server-box && \\"
echo "        source ~/.cargo/env && \\"
echo "        uv run python3 /tmp/complete_oauth.py YOUR_CODE\""
echo ""


