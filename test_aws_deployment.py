#!/usr/bin/env python3
"""
Test script to upload a minimal employment contract to Box and verify
the AWS deployed application processes it correctly.
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add mcp-server-box to path
sys.path.insert(0, str(Path(__file__).parent / "mcp-server-box" / "src"))

from box_contract_service import BoxContractService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_aws_deployment():
    """Upload test contract and verify processing."""
    
    logger.info("=" * 80)
    logger.info("Testing AWS Deployed Contract Protection System")
    logger.info("=" * 80)
    logger.info("")
    
    # Initialize Box service
    service = BoxContractService()
    try:
        await service.initialize()
        logger.info("✅ Box service initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Box service: {e}")
        return
    
    # Read test contract
    contract_path = Path(__file__).parent / "test_minimal_employment.txt"
    if not contract_path.exists():
        logger.error(f"❌ Test contract file not found: {contract_path}")
        return
    
    with open(contract_path, 'r') as f:
        contract_content = f.read()
    
    logger.info(f"📄 Read test contract: {contract_path.name}")
    logger.info(f"   Contract length: {len(contract_content)} characters")
    logger.info("")
    
    # Get root folder ID
    root_id = "0"
    
    # Find or create Smart_Contracts folder
    try:
        contracts_folder_id = await service.find_or_create_folder(
            root_id, "Smart_Contracts"
        )
        logger.info(f"✅ Contracts folder ID: {contracts_folder_id}")
    except Exception as e:
        logger.error(f"❌ Failed to find/create contracts folder: {e}")
        return
    
    # Create unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f"test_minimal_employment_{timestamp}.txt"
    
    # Upload contract to Box
    logger.info("")
    logger.info(f"📤 Uploading contract to Box: {test_filename}")
    try:
        file_id = await service.upload_text_file(
            contracts_folder_id,
            test_filename,
            contract_content
        )
        logger.info(f"✅ Contract uploaded successfully!")
        logger.info(f"   File ID: {file_id}")
        logger.info(f"   Location: Smart_Contracts/{test_filename}")
    except Exception as e:
        logger.error(f"❌ Failed to upload contract: {e}")
        return
    
    # Wait a moment
    logger.info("")
    logger.info("⏳ Waiting 5 seconds for file to be indexed by Box...")
    await asyncio.sleep(5)
    
    # Check if protect_your_interests folder exists
    logger.info("")
    logger.info("🔍 Verifying folder structure...")
    try:
        protect_folder_id = await service.find_or_create_folder(
            root_id, "protect_your_interests"
        )
        logger.info(f"✅ protect_your_interests folder ID: {protect_folder_id}")
        
        # List category folders
        category_folders = await service.list_folder_items(protect_folder_id)
        logger.info(f"   Found {len(category_folders)} category folders")
        
        # Look for Employment Contract folder
        employment_folder = None
        for folder in category_folders:
            if folder.get('name') == 'Employment Contract':
                employment_folder = folder
                break
        
        if employment_folder:
            logger.info(f"✅ Employment Contract folder found: {employment_folder['id']}")
        else:
            logger.info("⚠️  Employment Contract folder not found yet (will be created on processing)")
        
    except Exception as e:
        logger.error(f"❌ Error checking folder structure: {e}")
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ TEST CONTRACT UPLOADED SUCCESSFULLY!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📋 Next Steps:")
    logger.info("   1. The AWS deployed application will detect the new contract")
    logger.info("   2. It will process it within 60 seconds (monitoring interval)")
    logger.info("   3. Generated files will appear in:")
    logger.info(f"      protect_your_interests → Employment Contract → {test_filename.replace('.txt', '')}_mirror")
    logger.info("")
    logger.info("📋 To monitor processing:")
    logger.info("   ssh -i deploy/contract-protection-key.pem ec2-user@3.239.89.25 \\")
    logger.info("       'sudo journalctl -u contract-protection-system -f'")
    logger.info("")
    logger.info("📋 To check for generated files:")
    logger.info("   1. Go to Box UI: https://app.box.com")
    logger.info("   2. Navigate to: protect_your_interests → Employment Contract")
    logger.info(f"   3. Look for folder: {test_filename.replace('.txt', '')}_mirror")
    logger.info("")


if __name__ == "__main__":
    asyncio.run(test_aws_deployment())


