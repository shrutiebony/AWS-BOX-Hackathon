#!/usr/bin/env python3
"""Quick test - just check files without processing."""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def quick_test():
    """Quick test of generated files."""
    service = BoxContractService()
    await service.initialize()
    
    root_id = "0"
    protect_folder_id = await service.find_or_create_folder(root_id, "protect_your_interests")
    
    logger.info("=" * 80)
    logger.info("QUICK TEST - CHECKING GENERATED FILES")
    logger.info("=" * 80)
    
    # Check Lease and Rent Agreement folder
    lease_folder_id = await service.find_or_create_folder(protect_folder_id, "Lease and Rent Agreement")
    items = await service.list_folder_items(lease_folder_id)
    
    logger.info(f"\nFolders in 'Lease and Rent Agreement': {len(items)}")
    
    for item in items:
        if item['type'] == 'folder':
            logger.info(f"\n📁 {item['name']}")
            files = await service.list_folder_items(item['id'])
            logger.info(f"   Files: {len(files)}")
            for f in files:
                if f['type'] == 'file':
                    logger.info(f"   📄 {f['name']}")
    
    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(quick_test())


