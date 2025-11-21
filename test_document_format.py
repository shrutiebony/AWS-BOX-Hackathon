#!/usr/bin/env python3
"""
Test script to verify document files are properly formatted.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_document_format():
    """Test that generated documents are properly formatted."""
    
    service = BoxContractService()
    await service.initialize()
    client = service._get_client()
    
    # Find the latest mirror folder
    protect_folder_id = "352189258961"  # protect_your_interests
    service_contract_folder_id = "352188171927"  # Employment Contract
    
    try:
        items = client.folders.get_folder_items(service_contract_folder_id)
        
        # Find the most recent mirror folder
        mirror_folders = [item for item in items.entries if item.type.value == 'folder' and 'mirror' in item.name]
        if not mirror_folders:
            logger.error("No mirror folders found")
            return
        
        # Get the most recent one (by name which includes timestamp)
        latest_mirror = sorted(mirror_folders, key=lambda x: x.name, reverse=True)[0]
        logger.info(f"Checking mirror folder: {latest_mirror.name} (ID: {latest_mirror.id})")
        
        # List files in mirror folder
        mirror_items = client.folders.get_folder_items(latest_mirror.id)
        
        logger.info(f"\nFound {len(mirror_items.entries)} files:")
        for item in mirror_items.entries:
            if item.type.value == 'file':
                logger.info(f"\n📄 {item.name}")
                logger.info(f"   ID: {item.id}")
                logger.info(f"   Size: {item.size} bytes")
                
                # Check file format by reading first bytes
                try:
                    file_info = client.files.get_file_by_id(item.id)
                    # Download first few bytes to check format using Box SDK
                    from box_sdk_gen.managers.files import Files
                    files_manager = Files(client)
                    file_content_stream = files_manager.get_file_content(item.id)
                    first_bytes = file_content_stream.read(100)
                    
                    # Check file type
                    if item.name.endswith('.docx'):
                        if first_bytes.startswith(b'PK'):
                            logger.info(f"   ✅ Valid DOCX file (ZIP format detected)")
                        else:
                            logger.warning(f"   ⚠️  Invalid DOCX format (expected ZIP header)")
                            logger.info(f"   First bytes: {first_bytes[:50]}")
                    elif item.name.endswith('.pdf'):
                        if first_bytes.startswith(b'%PDF'):
                            logger.info(f"   ✅ Valid PDF file (PDF header detected)")
                        else:
                            logger.warning(f"   ⚠️  Invalid PDF format (expected PDF header)")
                            logger.info(f"   First bytes: {first_bytes[:50]}")
                    else:
                        logger.info(f"   File type: {item.name.split('.')[-1]}")
                        
                except Exception as e:
                    logger.error(f"   Error checking file: {e}")
                    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_document_format())

