#!/usr/bin/env python3
"""Verify the content of generated files."""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_content():
    """Verify content of generated files."""
    service = BoxContractService()
    await service.initialize()
    
    root_id = "0"
    protect_folder_id = await service.find_or_create_folder(root_id, "protect_your_interests")
    employment_folder_id = await service.find_or_create_folder(protect_folder_id, "Employment Contract")
    
    items = await service.list_folder_items(employment_folder_id)
    
    for item in items:
        if item['type'] == 'folder' and 'SIMPLE_EMPLOYMENT' in item['name']:
            logger.info(f"Checking files in: {item['name']}")
            logger.info("")
            
            files = await service.list_folder_items(item['id'])
            
            for f in files:
                if f['type'] == 'file' and f['name'] == '1_mirror_contract_protecting_YOUR_interests.txt':
                    logger.info(f"Reading: {f['name']}")
                    content = await service.read_file(f['id'])
                    
                    logger.info("")
                    logger.info("=" * 80)
                    logger.info("FILE CONTENT (first 500 characters):")
                    logger.info("=" * 80)
                    logger.info(content[:500])
                    logger.info("...")
                    logger.info("")
                    logger.info(f"Total length: {len(content)} characters")
                    logger.info("=" * 80)
                    
                    # Check if it's meaningful content
                    if len(content) > 100 and "contract" in content.lower():
                        logger.info("✅ Content appears to be meaningful (not placeholder)")
                    else:
                        logger.warning("⚠️  Content may be placeholder or too short")
                    break


if __name__ == "__main__":
    asyncio.run(verify_content())


