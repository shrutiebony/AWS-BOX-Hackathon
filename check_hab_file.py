#!/usr/bin/env python3
"""
Check if HAB-2-17.docx is being processed.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_hab_file():
    """Check HAB-2-17.docx processing status."""
    
    service = BoxContractService()
    await service.initialize()
    client = service._get_client()
    
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    
    logger.info("=" * 80)
    logger.info("CHECKING HAB-2-17.docx FILE")
    logger.info("=" * 80)
    logger.info("")
    
    # List all files in Smart_Contracts folder
    items = await service.list_folder_items(contracts_folder_id)
    
    logger.info(f"Files in Smart_Contracts folder ({len(items)} total):")
    hab_found = False
    
    for item in items:
        if item['type'] == 'file':
            logger.info(f"  📄 {item['name']} (ID: {item['id']})")
            if 'HAB-2-17' in item['name'] or 'hab-2-17' in item['name'].lower():
                hab_found = True
                logger.info(f"     ✅ HAB-2-17 file found!")
                logger.info(f"     File ID: {item['id']}")
                
                # Try to read it
                try:
                    content = await service.read_file(item['id'])
                    logger.info(f"     Content length: {len(content)} characters")
                    logger.info(f"     First 200 chars: {content[:200]}...")
                except Exception as e:
                    logger.error(f"     Error reading file: {e}")
    
    if not hab_found:
        logger.warning("❌ HAB-2-17.docx not found in Smart_Contracts folder")
        logger.info("")
        logger.info("Please check:")
        logger.info("1. File name is exactly 'HAB-2-17.docx'")
        logger.info("2. File is in the 'Smart_Contracts' folder (not a subfolder)")
        logger.info("3. File was uploaded successfully")
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("CHECKING FOR GENERATED FILES")
    logger.info("=" * 80)
    
    # Check protect_your_interests folder
    protect_folder_id = await service.find_or_create_folder(root_id, "protect_your_interests")
    
    # Check Lease and Rent Agreement folder
    lease_folder_id = await service.find_or_create_folder(protect_folder_id, "Lease and Rent Agreement")
    
    items = await service.list_folder_items(lease_folder_id)
    
    logger.info(f"Folders in 'Lease and Rent Agreement' ({len(items)} total):")
    
    hab_mirror_found = False
    for item in items:
        if item['type'] == 'folder':
            logger.info(f"  📁 {item['name']} (ID: {item['id']})")
            if 'HAB-2-17' in item['name'] or 'hab-2-17' in item['name'].lower():
                hab_mirror_found = True
                logger.info(f"     ✅ HAB-2-17 mirror folder found!")
                
                # List files in mirror folder
                mirror_items = await service.list_folder_items(item['id'])
                logger.info(f"     Files in mirror folder ({len(mirror_items)}):")
                
                if len(mirror_items) == 0:
                    logger.warning(f"     ⚠️  No files in mirror folder yet - still processing?")
                else:
                    for file_item in mirror_items:
                        logger.info(f"       📄 {file_item['name']}")
    
    if not hab_mirror_found:
        logger.warning("❌ HAB-2-17 mirror folder not found yet")
        logger.info("")
        logger.info("Possible reasons:")
        logger.info("1. File is still being processed (check logs)")
        logger.info("2. File was not detected (check if it's in Smart_Contracts folder)")
        logger.info("3. Processing failed (check for errors in logs)")
    
    logger.info("")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(check_hab_file())


