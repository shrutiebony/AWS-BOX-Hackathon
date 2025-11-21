#!/usr/bin/env python3
"""
Upload test employment contract to Box and monitor processing.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def upload_and_monitor():
    """Upload test contract and monitor processing."""
    
    service = BoxContractService()
    await service.initialize()
    
    # Read the test contract
    with open("TEST_EMPLOYMENT_CONTRACT.txt", "r") as f:
        contract_content = f.read()
    
    # Find Smart_Contracts folder
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    
    logger.info("=" * 80)
    logger.info("UPLOADING TEST EMPLOYMENT CONTRACT")
    logger.info("=" * 80)
    
    # Upload the contract
    filename = "TEST_EMPLOYMENT_CONTRACT.txt"
    file_id = await service.upload_text_file(
        contracts_folder_id,
        filename,
        contract_content
    )
    
    logger.info(f"✅ Uploaded {filename} to Smart_Contracts folder")
    logger.info(f"   File ID: {file_id}")
    logger.info("")
    logger.info("The contract processor should detect this file within 3 seconds")
    logger.info("and generate 3 files in:")
    logger.info("  protect_your_interests → Employment Contract → TEST_EMPLOYMENT_CONTRACT_mirror")
    logger.info("")
    logger.info("Waiting 90 seconds for processing to complete...")
    logger.info("")
    
    # Wait and check
    await asyncio.sleep(90)
    
    logger.info("=" * 80)
    logger.info("CHECKING FOR GENERATED FILES")
    logger.info("=" * 80)
    
    # Check for generated files
    protect_folder_id = await service.find_or_create_folder(root_id, "protect_your_interests")
    employment_folder_id = await service.find_or_create_folder(protect_folder_id, "Employment Contract")
    
    items = await service.list_folder_items(employment_folder_id)
    
    test_folder_found = False
    for item in items:
        if item['type'] == 'folder' and 'TEST_EMPLOYMENT_CONTRACT' in item['name']:
            test_folder_found = True
            logger.info(f"✅ Found mirror folder: {item['name']}")
            
            files = await service.list_folder_items(item['id'])
            logger.info(f"   Files in folder: {len([f for f in files if f['type'] == 'file'])}")
            
            for f in files:
                if f['type'] == 'file':
                    logger.info(f"   📄 {f['name']}")
    
    if not test_folder_found:
        logger.warning("⚠️  Mirror folder not found yet - processing may still be in progress")
        logger.info("   Check again in a few moments")
    
    logger.info("")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(upload_and_monitor())


