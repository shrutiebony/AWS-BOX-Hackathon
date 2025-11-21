#!/bin/bash
# Test AWS deployment by uploading contract and verifying processing

INSTANCE_IP="3.239.89.25"
KEY_FILE="deploy/contract-protection-key.pem"

echo "🧪 Testing AWS Deployed Contract Protection System"
echo "=================================================="
echo ""

# Upload test contract using the service's Python environment
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$INSTANCE_IP" << 'EOF'
cd /opt/contract-protection-system

# Create upload script in the mcp-server-box directory where dependencies are available
cat > mcp-server-box/upload_test.py << 'PYEOF'
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Import after changing to correct directory
sys.path.insert(0, '/opt/contract-protection-system')
sys.path.insert(0, '/opt/contract-protection-system/mcp-server-box/src')

# Load environment
import os
env_file = Path('/opt/contract-protection-system/.env')
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

# Now import
from box_contract_service import BoxContractService

async def upload():
    print("📄 Reading test contract...")
    with open('/tmp/test_minimal_employment.txt', 'r') as f:
        content = f.read()
    print(f"   Contract length: {len(content)} characters")
    
    print("\n🔐 Initializing Box service...")
    service = BoxContractService()
    await service.initialize()
    print("✅ Box service initialized")
    
    print("\n📁 Finding Smart_Contracts folder...")
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    print(f"✅ Contracts folder ID: {contracts_folder_id}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_minimal_employment_{timestamp}.txt"
    
    print(f"\n📤 Uploading contract: {filename}")
    file_id = await service.upload_text_file(contracts_folder_id, filename, content)
    
    print(f"\n✅ SUCCESS!")
    print(f"   File ID: {file_id}")
    print(f"   File name: {filename}")
    print(f"   Location: Smart_Contracts/{filename}")
    print(f"\n⏳ The AWS application will process this within 60 seconds")
    print(f"   Monitor logs: sudo journalctl -u contract-protection-system -f")

asyncio.run(upload())
PYEOF

source ~/.cargo/env
cd mcp-server-box
uv run python3 upload_test.py

EOF

echo ""
echo "✅ Test contract upload complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Monitor EC2 logs:"
echo "      ssh -i $KEY_FILE ec2-user@$INSTANCE_IP 'sudo journalctl -u contract-protection-system -f'"
echo ""
echo "   2. Check Box for generated files:"
echo "      - Go to: https://app.box.com"
echo "      - Navigate to: protect_your_interests → Employment Contract"
echo "      - Look for a folder ending in '_mirror'"
echo ""


