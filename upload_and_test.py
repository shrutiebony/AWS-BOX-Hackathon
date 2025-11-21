#!/usr/bin/env python3
"""
Upload test files to Box and verify the application works.
"""

import asyncio
import logging
import time
from pathlib import Path
from box_contract_service import BoxContractService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def upload_and_test():
    """Upload test files and verify processing."""
    
    service = BoxContractService()
    
    try:
        # Initialize Box service
        logger.info("=" * 70)
        logger.info("UPLOADING TEST FILES TO BOX")
        logger.info("=" * 70)
        logger.info("")
        
        await service.initialize()
        logger.info("✅ Box service initialized\n")
        
        root_id = "0"
        
        # Step 1: Upload MY_INTERESTS.txt to my_interests folder
        logger.info("Step 1: Uploading MY_INTERESTS.txt...")
        interests_folder_id = await service.find_or_create_folder(root_id, "my_interests")
        logger.info(f"   📁 my_interests folder ID: {interests_folder_id}")
        
        interests_path = Path(__file__).parent / "MY_INTERESTS.txt"
        if interests_path.exists():
            with open(interests_path, 'r') as f:
                interests_content = f.read()
            
            # Check if file already exists
            existing_file_id = await service.find_file_in_folder(interests_folder_id, "MY_INTERESTS.txt")
            if existing_file_id:
                logger.info(f"   ℹ️  MY_INTERESTS.txt already exists (ID: {existing_file_id})")
                logger.info(f"   ✅ Using existing file")
            else:
                file_id = await service.upload_text_file(
                    interests_folder_id,
                    "MY_INTERESTS.txt",
                    interests_content
                )
                logger.info(f"   ✅ Uploaded MY_INTERESTS.txt (ID: {file_id})")
        else:
            logger.warning(f"   ❌ MY_INTERESTS.txt not found at {interests_path}")
        
        logger.info("")
        
        # Step 2: Upload test contract to Smart_Contracts folder
        logger.info("Step 2: Uploading test contract...")
        contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
        logger.info(f"   📁 Smart_Contracts folder ID: {contracts_folder_id}")
        
        contract_path = Path(__file__).parent / "test_contract.txt"
        if contract_path.exists():
            with open(contract_path, 'r') as f:
                contract_content = f.read()
            
            # Upload with a unique name to avoid conflicts
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            contract_filename = f"test_contract_{timestamp}.txt"
            
            file_id = await service.upload_text_file(
                contracts_folder_id,
                contract_filename,
                contract_content
            )
            logger.info(f"   ✅ Uploaded {contract_filename} (ID: {file_id})")
            logger.info(f"   📄 Contract file ID: {file_id}")
        else:
            logger.warning(f"   ❌ test_contract.txt not found at {contract_path}")
            return
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ FILES UPLOADED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("📋 Upload Summary:")
        logger.info(f"   📁 my_interests folder: {interests_folder_id}")
        logger.info(f"   📁 Smart_Contracts folder: {contracts_folder_id}")
        logger.info(f"   📄 Contract file: {contract_filename}")
        logger.info("")
        logger.info("⏳ The contract processor should detect and process this contract")
        logger.info("   within 60 seconds (check interval)")
        logger.info("")
        logger.info("🔍 To verify processing:")
        logger.info("   1. Check protect_your_interests folder in Box")
        logger.info("   2. Look for a folder named: test_contract_*_mirror")
        logger.info("   3. Inside should be 3 output files")
        logger.info("")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(upload_and_test())

