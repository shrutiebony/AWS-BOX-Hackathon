#!/usr/bin/env python3
"""
Show the exact Box UI path to generated files.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def show_box_path():
    """Show the exact path to generated files in Box UI."""
    
    service = BoxContractService()
    await service.initialize()
    client = service._get_client()
    
    root_id = "0"
    
    logger.info("=" * 80)
    logger.info("BOX UI PATH TO GENERATED FILES")
    logger.info("=" * 80)
    logger.info("")
    
    # Get protect_your_interests folder
    protect_folder_id = await service.find_or_create_folder(root_id, "protect_your_interests")
    
    logger.info("📁 STEP 1: Navigate to Box Root Folder")
    logger.info("   (This is your main Box folder - usually 'All Files' or your account name)")
    logger.info("")
    
    logger.info("📁 STEP 2: Open folder: 'protect_your_interests'")
    logger.info(f"   Folder ID: {protect_folder_id}")
    logger.info("")
    
    # List all category folders
    try:
        protect_items = client.folders.get_folder_items(protect_folder_id)
        category_folders = [item for item in protect_items.entries if item.type.value == 'folder']
        
        logger.info("📁 STEP 3: Open the Contract Category folder")
        logger.info("   Available categories:")
        logger.info("")
        
        for category in sorted(category_folders, key=lambda x: x.name):
            logger.info(f"   📂 {category.name}")
            logger.info(f"      Folder ID: {category.id}")
            
            # Check for mirror folders inside
            try:
                category_items = client.folders.get_folder_items(category.id)
                mirror_folders = [item for item in category_items.entries 
                                if item.type.value == 'folder' and 'mirror' in item.name]
                
                if mirror_folders:
                    # Show the most recent mirror folder
                    latest_mirror = sorted(mirror_folders, key=lambda x: x.name, reverse=True)[0]
                    logger.info(f"      └── 📁 {latest_mirror.name}")
                    logger.info(f"          Folder ID: {latest_mirror.id}")
                    
                    # List files in mirror folder
                    try:
                        mirror_items = client.folders.get_folder_items(latest_mirror.id)
                        files = [item for item in mirror_items.entries if item.type.value == 'file']
                        
                        if files:
                            logger.info(f"          Files ({len(files)}):")
                            for file_item in sorted(files, key=lambda x: x.name):
                                file_size = file_item.size if hasattr(file_item, 'size') and file_item.size else "N/A"
                                logger.info(f"            📄 {file_item.name} ({file_size} bytes)")
                                logger.info(f"               File ID: {file_item.id}")
                    except Exception as e:
                        logger.warning(f"          Could not list files: {e}")
                else:
                    logger.info(f"      (No mirror folders yet)")
                    
            except Exception as e:
                logger.warning(f"      Error checking category: {e}")
            
            logger.info("")
        
        logger.info("=" * 80)
        logger.info("COMPLETE PATH EXAMPLE:")
        logger.info("=" * 80)
        logger.info("")
        
        if category_folders:
            example_category = category_folders[0]
            logger.info(f"Box Root → protect_your_interests → {example_category.name}")
            
            try:
                category_items = client.folders.get_folder_items(example_category.id)
                mirror_folders = [item for item in category_items.entries 
                                if item.type.value == 'folder' and 'mirror' in item.name]
                
                if mirror_folders:
                    latest_mirror = sorted(mirror_folders, key=lambda x: x.name, reverse=True)[0]
                    logger.info(f"  → {latest_mirror.name}")
                    
                    mirror_items = client.folders.get_folder_items(latest_mirror.id)
                    files = [item for item in mirror_items.entries if item.type.value == 'file']
                    
                    if files:
                        logger.info("")
                        logger.info("  Generated Files:")
                        for file_item in sorted(files, key=lambda x: x.name):
                            logger.info(f"    • {file_item.name}")
            except:
                pass
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("HOW TO ACCESS IN BOX UI:")
        logger.info("=" * 80)
        logger.info("")
        logger.info("1. Go to https://app.box.com (or open Box app)")
        logger.info("2. Navigate to: All Files → protect_your_interests")
        logger.info("3. Click on the contract category (e.g., 'Employment Contract')")
        logger.info("4. Click on the mirror folder (e.g., 'test_contract_*_mirror')")
        logger.info("5. You'll see 3 files:")
        logger.info("   - 1_mirror_contract_protecting_YOUR_interests.docx")
        logger.info("   - 2_clean_redline_comparison.pdf")
        logger.info("   - 3_negotiation_guide.docx")
        logger.info("")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(show_box_path())

