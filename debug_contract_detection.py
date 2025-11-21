#!/usr/bin/env python3
"""
Debug script to check why contracts aren't being detected.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def debug_contract_detection():
    """Debug contract detection."""
    
    service = BoxContractService()
    await service.initialize()
    
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    
    logger.info(f"📁 Smart_Contracts folder ID: {contracts_folder_id}")
    logger.info("")
    
    # Try using client.folders directly
    client = service._get_client()
    logger.info("Listing using client.folders.get_folder_items...")
    
    try:
        items = client.folders.get_folder_items(contracts_folder_id)
        logger.info(f"Found {len(items.entries)} items using SDK:")
        
        for item in items.entries:
            logger.info(f"  📄 {item.name} (ID: {item.id}, Type: {item.type})")
            logger.info(f"      Created: {item.created_at if hasattr(item, 'created_at') else 'N/A'}")
    except Exception as e:
        logger.error(f"Error listing with SDK: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("")
    logger.info("Listing using list_folder_items method...")
    
    try:
        items = await service.list_folder_items(contracts_folder_id)
        logger.info(f"Found {len(items)} items using list_folder_items:")
        for item in items:
            logger.info(f"  {item}")
    except Exception as e:
        logger.error(f"Error listing with list_folder_items: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_contract_detection())

