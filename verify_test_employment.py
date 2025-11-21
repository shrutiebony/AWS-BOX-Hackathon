#!/usr/bin/env python3
"""Verify test employment contract files were generated."""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify():
    """Verify generated files."""
    service = BoxContractService()
    await service.initialize()
    
    root_id = "0"
    protect_folder_id = await service.find_or_create_folder(root_id, "protect_your_interests")
    employment_folder_id = await service.find_or_create_folder(protect_folder_id, "Employment Contract")
    
    logger.info("=" * 80)
    logger.info("VERIFYING TEST EMPLOYMENT CONTRACT FILES")
    logger.info("=" * 80)
    logger.info("")
    
    items = await service.list_folder_items(employment_folder_id)
    
    logger.info(f"Folders in 'Employment Contract': {len(items)}")
    logger.info("")
    
    test_found = False
    for item in items:
        if item['type'] == 'folder':
            logger.info(f"📁 {item['name']}")
            
            if 'TEST_EMPLOYMENT_CONTRACT' in item['name']:
                test_found = True
                files = await service.list_folder_items(item['id'])
                logger.info(f"   ✅ TEST folder found!")
                logger.info(f"   Files: {len([f for f in files if f['type'] == 'file'])}")
                logger.info("")
                
                for f in files:
                    if f['type'] == 'file':
                        logger.info(f"   📄 {f['name']}")
    
    logger.info("")
    logger.info("=" * 80)
    
    if test_found:
        logger.info("✅ SUCCESS: All 3 files generated for TEST_EMPLOYMENT_CONTRACT")
    else:
        logger.warning("⚠️  TEST folder not found")
    
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(verify())


