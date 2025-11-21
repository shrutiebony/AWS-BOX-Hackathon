#!/usr/bin/env python3
"""
Check the actual contents of files in Box to see if they're empty.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_file_contents():
    """Check file contents."""
    
    service = BoxContractService()
    await service.initialize()
    
    client = service._get_client()
    
    # Get the mirror folder
    protect_folder_id = "352189258961"  # protect_your_interests
    service_contract_folder_id = "352186168439"  # Service Contract
    mirror_folder_id = "352192846963"  # test_contract_20251120_143447_mirror
    
    logger.info("Checking files in mirror folder...")
    
    try:
        mirror_items = client.folders.get_folder_items(mirror_folder_id)
        for item in mirror_items.entries:
            if item.type.value == 'file':
                logger.info(f"\n📄 File: {item.name} (ID: {item.id})")
                logger.info(f"   Size: {item.size} bytes")
                
                # Read file content
                try:
                    file_content = await service.read_file(item.id)
                    logger.info(f"   Content length: {len(file_content)} characters")
                    logger.info(f"   First 500 chars:")
                    logger.info(f"   {file_content[:500]}")
                except Exception as e:
                    logger.error(f"   Error reading file: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_file_contents())

