#!/usr/bin/env python3
"""
Check if contract is being detected and processed.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_contract_status():
    """Check contract detection status."""
    
    service = BoxContractService()
    await service.initialize()
    
    # Check Smart_Contracts folder
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    
    logger.info(f"📁 Smart_Contracts folder ID: {contracts_folder_id}")
    logger.info("")
    logger.info("Listing files in Smart_Contracts folder...")
    
    items = await service.list_folder_items(contracts_folder_id)
    
    logger.info(f"Found {len(items)} items:")
    for item in items:
        item_type = "📁" if item['type'] == 'folder' else "📄"
        logger.info(f"  {item_type} {item['name']} (ID: {item['id']}, Type: {item['type']})")
    
    # Check protect_your_interests folder
    logger.info("")
    logger.info("Checking protect_your_interests folder...")
    protect_folder_id = await service.find_or_create_folder(root_id, "protect_your_interests")
    logger.info(f"📁 protect_your_interests folder ID: {protect_folder_id}")
    
    items = await service.list_folder_items(protect_folder_id)
    logger.info(f"Found {len(items)} items in protect_your_interests:")
    
    for item in items:
        if item['type'] == 'folder':
            logger.info(f"  📁 {item['name']} (ID: {item['id']})")
            # List items in this folder
            sub_items = await service.list_folder_items(item['id'])
            for sub_item in sub_items:
                logger.info(f"      📁 {sub_item['name']} (ID: {sub_item['id']})")
                # List files in mirror folder
                if '_mirror' in sub_item['name']:
                    mirror_items = await service.list_folder_items(sub_item['id'])
                    for file_item in mirror_items:
                        logger.info(f"          📄 {file_item['name']} (ID: {file_item['id']})")


if __name__ == "__main__":
    asyncio.run(check_contract_status())

