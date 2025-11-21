#!/usr/bin/env python3
"""
Test contract processing system end-to-end.
"""

import asyncio
import logging
from contract_processor import ContractProcessor
from box_contract_service import BoxContractService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_processing():
    """Test the contract processing system."""
    
    logger.info("=" * 80)
    logger.info("TESTING CONTRACT PROCESSING SYSTEM")
    logger.info("=" * 80)
    logger.info("")
    
    # Initialize processor
    processor = ContractProcessor()
    await processor.initialize()
    
    logger.info("✅ Processor initialized")
    logger.info("")
    
    # Check for new contracts
    logger.info("Checking for new contracts...")
    await processor.process_new_contracts()
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("VERIFYING GENERATED FILES")
    logger.info("=" * 80)
    
    # Check what files were generated
    box_service = BoxContractService()
    await box_service.initialize()
    
    root_id = "0"
    protect_folder_id = await box_service.find_or_create_folder(root_id, "protect_your_interests")
    
    # List all category folders
    items = await box_service.list_folder_items(protect_folder_id)
    
    logger.info(f"Category folders found: {len(items)}")
    
    total_files = 0
    for item in items:
        if item['type'] == 'folder':
            logger.info(f"")
            logger.info(f"📁 {item['name']}")
            
            # List mirror folders
            category_items = await box_service.list_folder_items(item['id'])
            
            for mirror_item in category_items:
                if mirror_item['type'] == 'folder':
                    logger.info(f"  └── 📁 {mirror_item['name']}")
                    
                    # List files in mirror folder
                    files = await box_service.list_folder_items(mirror_item['id'])
                    
                    for file_item in files:
                        if file_item['type'] == 'file':
                            logger.info(f"      └── 📄 {file_item['name']}")
                            total_files += 1
    
    logger.info("")
    logger.info("=" * 80)
    logger.info(f"✅ TOTAL FILES GENERATED: {total_files}")
    logger.info("=" * 80)
    
    # Check processed contracts
    logger.info("")
    logger.info(f"Processed contracts: {len(processor.processed_contracts)}")
    for contract_key in sorted(processor.processed_contracts):
        logger.info(f"  - {contract_key}")


if __name__ == "__main__":
    asyncio.run(test_processing())


