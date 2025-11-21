#!/usr/bin/env python3
"""
Test script to check Box folders and create a test folder.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_box_folders():
    """Test Box folder operations."""
    
    service = BoxContractService()
    
    try:
        # Initialize Box service
        logger.info("Initializing Box service...")
        await service.initialize()
        logger.info("✅ Box service initialized successfully\n")
        
        # Test 1: List all folders in root
        logger.info("=" * 60)
        logger.info("TEST 1: Listing all folders in root (folder ID: 0)")
        logger.info("=" * 60)
        
        try:
            items = await service.list_folder_items("0")
            folders = [item for item in items if item['type'] == 'folder']
            
            logger.info(f"\nFound {len(folders)} folders in root:\n")
            for folder in folders:
                logger.info(f"  📁 {folder['name']:<40} ID: {folder['id']}")
            
            if len(folders) == 0:
                logger.info("  (No folders found in root)")
            
        except Exception as e:
            logger.error(f"❌ Error listing folders: {e}")
            return
        
        # Test 2: Check specific folders we use
        logger.info("\n" + "=" * 60)
        logger.info("TEST 2: Checking application-specific folders")
        logger.info("=" * 60)
        
        root_id = "0"
        folders_to_check = [
            "Smart_Contracts",
            "protect_your_interests",
            "my_interests"
        ]
        
        for folder_name in folders_to_check:
            try:
                folder_id = await service.find_or_create_folder(root_id, folder_name)
                logger.info(f"  ✅ {folder_name:<40} ID: {folder_id}")
            except Exception as e:
                logger.error(f"  ❌ {folder_name:<40} Error: {e}")
        
        # Test 3: Create a dummy test folder
        logger.info("\n" + "=" * 60)
        logger.info("TEST 3: Creating a dummy test folder")
        logger.info("=" * 60)
        
        dummy_folder_name = "TEST_DUMMY_FOLDER"
        
        try:
            # First, check if it exists
            logger.info(f"\nChecking if '{dummy_folder_name}' exists...")
            items = await service.list_folder_items(root_id)
            existing = [item for item in items if item['type'] == 'folder' and item['name'] == dummy_folder_name]
            
            if existing:
                logger.info(f"  ℹ️  Folder '{dummy_folder_name}' already exists")
                dummy_folder_id = existing[0]['id']
                logger.info(f"  📁 Existing folder ID: {dummy_folder_id}")
            else:
                logger.info(f"  Creating new folder '{dummy_folder_name}'...")
                dummy_folder_id = await service.find_or_create_folder(root_id, dummy_folder_name)
                logger.info(f"  ✅ Created folder '{dummy_folder_name}'")
                logger.info(f"  📁 New folder ID: {dummy_folder_id}")
            
            logger.info(f"\n🎯 DUMMY FOLDER ID: {dummy_folder_id}")
            
        except Exception as e:
            logger.error(f"❌ Error creating dummy folder: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 4: List items in the dummy folder
        logger.info("\n" + "=" * 60)
        logger.info("TEST 4: Listing items in dummy folder")
        logger.info("=" * 60)
        
        try:
            items = await service.list_folder_items(dummy_folder_id)
            logger.info(f"\nFound {len(items)} items in '{dummy_folder_name}':")
            if len(items) == 0:
                logger.info("  (Folder is empty)")
            else:
                for item in items:
                    item_type = "📁" if item['type'] == 'folder' else "📄"
                    logger.info(f"  {item_type} {item['name']:<40} ID: {item['id']}")
        except Exception as e:
            logger.error(f"❌ Error listing items in dummy folder: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ All tests completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_box_folders())

