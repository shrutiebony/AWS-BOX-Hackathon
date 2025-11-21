#!/usr/bin/env python3
"""
Verify that files are being created as plain text (.txt) format.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_txt_files():
    """Verify files are in .txt format."""
    
    service = BoxContractService()
    await service.initialize()
    client = service._get_client()
    
    protect_folder_id = "352189258961"  # protect_your_interests
    
    logger.info("=" * 80)
    logger.info("VERIFYING PLAIN TEXT FILES")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        protect_items = client.folders.get_folder_items(protect_folder_id)
        category_folders = [item for item in protect_items.entries if item.type.value == 'folder']
        
        for category in sorted(category_folders, key=lambda x: x.name):
            logger.info(f"📂 {category.name}")
            
            try:
                category_items = client.folders.get_folder_items(category.id)
                mirror_folders = [item for item in category_items.entries 
                                if item.type.value == 'folder' and 'mirror' in item.name]
                
                if mirror_folders:
                    # Get the most recent mirror folder
                    latest_mirror = sorted(mirror_folders, key=lambda x: x.name, reverse=True)[0]
                    logger.info(f"  └── 📁 {latest_mirror.name}")
                    
                    # List files
                    mirror_items = client.folders.get_folder_items(latest_mirror.id)
                    files = [item for item in mirror_items.entries if item.type.value == 'file']
                    
                    if files:
                        logger.info(f"      Files ({len(files)}):")
                        all_txt = True
                        for file_item in sorted(files, key=lambda x: x.name):
                            is_txt = file_item.name.endswith('.txt')
                            status = "✅" if is_txt else "❌"
                            logger.info(f"        {status} {file_item.name}")
                            if not is_txt:
                                all_txt = False
                        
                        if all_txt:
                            logger.info(f"      ✅ All files are in .txt format!")
                        else:
                            logger.warning(f"      ⚠️  Some files are not in .txt format")
                    else:
                        logger.info(f"      (No files yet)")
            except Exception as e:
                logger.warning(f"  Error: {e}")
            
            logger.info("")
        
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(verify_txt_files())

