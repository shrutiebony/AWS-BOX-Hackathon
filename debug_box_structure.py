#!/usr/bin/env python3
"""
Debug script to check the exact Box folder structure and file locations.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def debug_box_structure():
    """Debug Box folder structure."""
    
    service = BoxContractService()
    await service.initialize()
    
    root_id = "0"
    client = service._get_client()
    
    logger.info("=" * 70)
    logger.info("DEBUGGING BOX FOLDER STRUCTURE")
    logger.info("=" * 70)
    logger.info("")
    
    # Check root folder
    logger.info("📁 ROOT FOLDER (ID: 0):")
    try:
        root_items = client.folders.get_folder_items(root_id)
        for item in root_items.entries:
            if item.type.value == 'folder':
                logger.info(f"  📁 {item.name} (ID: {item.id})")
    except Exception as e:
        logger.error(f"Error listing root: {e}")
    
    logger.info("")
    
    # Check protect_your_interests folder
    logger.info("📁 protect_your_interests FOLDER:")
    protect_folder_id = await service.find_or_create_folder(root_id, "protect_your_interests")
    logger.info(f"  Folder ID: {protect_folder_id}")
    
    try:
        protect_items = client.folders.get_folder_items(protect_folder_id)
        logger.info(f"  Found {len(protect_items.entries)} items:")
        
        for item in protect_items.entries:
            if item.type.value == 'folder':
                logger.info(f"    📁 {item.name} (ID: {item.id})")
                
                # List items in category folder
                try:
                    category_items = client.folders.get_folder_items(item.id)
                    for sub_item in category_items.entries:
                        if sub_item.type.value == 'folder':
                            logger.info(f"      📁 {sub_item.name} (ID: {sub_item.id})")
                            
                            # List files in mirror folder
                            try:
                                mirror_items = client.folders.get_folder_items(sub_item.id)
                                for file_item in mirror_items.entries:
                                    if file_item.type.value == 'file':
                                        logger.info(f"        📄 {file_item.name} (ID: {file_item.id})")
                                        # Get file info
                                        file_info = client.files.get_file_by_id(file_item.id)
                                        logger.info(f"          Size: {file_info.size} bytes")
                                        logger.info(f"          Created: {file_info.created_at}")
                                        logger.info(f"          Modified: {file_info.modified_at}")
                            except Exception as e:
                                logger.error(f"        Error listing mirror folder: {e}")
                        elif sub_item.type.value == 'file':
                            logger.info(f"      📄 {sub_item.name} (ID: {sub_item.id})")
                except Exception as e:
                    logger.error(f"    Error listing category folder: {e}")
            elif item.type.value == 'file':
                logger.info(f"    📄 {item.name} (ID: {item.id})")
    except Exception as e:
        logger.error(f"Error listing protect_your_interests: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("CHECKING FILE PERMISSIONS AND VISIBILITY")
    logger.info("=" * 70)
    
    # Check a specific file's permissions
    try:
        protect_items = client.folders.get_folder_items(protect_folder_id)
        for item in protect_items.entries:
            if item.type.value == 'folder' and 'Service Contract' in item.name:
                category_items = client.folders.get_folder_items(item.id)
                for sub_item in category_items.entries:
                    if sub_item.type.value == 'folder' and 'mirror' in sub_item.name:
                        mirror_items = client.folders.get_folder_items(sub_item.id)
                        if mirror_items.entries:
                            first_file = mirror_items.entries[0]
                            logger.info(f"Checking file: {first_file.name} (ID: {first_file.id})")
                            
                            # Get file metadata
                            file_info = client.files.get_file_by_id(first_file.id)
                            logger.info(f"  File name: {file_info.name}")
                            logger.info(f"  Parent folder ID: {file_info.parent.id}")
                            logger.info(f"  Parent folder name: {file_info.parent.name}")
                            
                            # Get parent folder path
                            parent_id = file_info.parent.id
                            parent_info = client.folders.get_folder_by_id(parent_id)
                            logger.info(f"  Parent folder: {parent_info.name} (ID: {parent_id})")
                            
                            # Try to get folder path
                            try:
                                # Get all parent folders
                                path_parts = []
                                current_id = parent_id
                                while current_id and current_id != "0":
                                    folder_info = client.folders.get_folder_by_id(current_id)
                                    path_parts.insert(0, folder_info.name)
                                    if hasattr(folder_info, 'parent') and folder_info.parent:
                                        current_id = folder_info.parent.id if hasattr(folder_info.parent, 'id') else None
                                    else:
                                        break
                                
                                logger.info(f"  Full path: /{'/'.join(path_parts)}/{file_info.name}")
                            except Exception as e:
                                logger.warning(f"  Could not get full path: {e}")
                            
                            break
    except Exception as e:
        logger.error(f"Error checking file permissions: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_box_structure())

