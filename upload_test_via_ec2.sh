#!/bin/bash
# Upload test contract to Box via EC2 instance

INSTANCE_IP="3.239.89.25"
KEY_FILE="deploy/contract-protection-key.pem"

echo "🚀 Uploading test contract via EC2 instance..."
echo ""

# Create a temporary upload script on EC2
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$INSTANCE_IP" << 'EOF'
# Read test contract content
cat > /tmp/upload_test_contract.py << 'PYEOF'
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, '/opt/contract-protection-system')
sys.path.insert(0, '/opt/contract-protection-system/mcp-server-box/src')

from box_contract_service import BoxContractService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def upload_test():
    # Test contract content
    contract_content = """EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into on November 21, 2025, between ABC Company ("Employer") and John Doe ("Employee").

1. POSITION AND DUTIES
Employee shall serve as Software Engineer. Employee shall perform all duties assigned by Employer.

2. COMPENSATION
Employee shall receive a salary of $100,000 per year, payable bi-weekly.

3. TERM
This Agreement shall commence on December 1, 2025 and continue until terminated by either party.

4. TERMINATION
Either party may terminate this Agreement at any time, with or without cause, with 2 weeks notice.

5. CONFIDENTIALITY
Employee agrees to maintain confidentiality of all proprietary information during and after employment.

6. NON-COMPETE
Employee agrees not to work for competing companies for a period of 12 months after termination.

7. ARBITRATION
All disputes shall be resolved through binding arbitration. Employee waives right to jury trial.

8. INTELLECTUAL PROPERTY
All work product created by Employee during employment shall be the exclusive property of Employer.

9. AT-WILL EMPLOYMENT
This Agreement does not guarantee employment for any specific period. Employment is at-will.

10. ENTIRE AGREEMENT
This Agreement constitutes the entire agreement between the parties.

IN WITNESS WHEREOF, the parties have executed this Agreement.

ABC Company
_________________________
John Doe
"""

    service = BoxContractService()
    await service.initialize()
    
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f"test_minimal_employment_{timestamp}.txt"
    
    logger.info(f"Uploading: {test_filename}")
    file_id = await service.upload_text_file(contracts_folder_id, test_filename, contract_content)
    
    logger.info(f"✅ Uploaded successfully!")
    logger.info(f"   File ID: {file_id}")
    logger.info(f"   File name: {test_filename}")
    logger.info(f"   Location: Smart_Contracts/{test_filename}")
    print(f"\n✅ SUCCESS: Contract uploaded with ID {file_id}")
    print(f"   The AWS application will process it within 60 seconds")

asyncio.run(upload_test())
PYEOF

cd /opt/contract-protection-system
source ~/.cargo/env
uv run python3 /tmp/upload_test_contract.py

EOF

echo ""
echo "✅ Test contract uploaded!"
echo ""
echo "📋 Monitor processing on EC2:"
echo "   ssh -i $KEY_FILE ec2-user@$INSTANCE_IP 'sudo journalctl -u contract-protection-system -f'"
echo ""


