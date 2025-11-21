#!/usr/bin/env python3
"""
Upload test files to Box for testing the contract processor.
"""

import asyncio
import logging
from pathlib import Path
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def upload_test_files():
    """Upload test contract and interests file to Box."""
    
    service = BoxContractService()
    
    try:
        # Initialize Box service
        await service.initialize()
        logger.info("✅ Box service initialized")
        
        # Get root folder ID
        root_id = "0"
        
        # Find or create contracts folder
        contracts_folder_id = await service.find_or_create_folder(root_id, "contracts")
        logger.info(f"✅ Contracts folder ID: {contracts_folder_id}")
        
        # Find or create my_interests folder
        interests_folder_id = await service.find_or_create_folder(root_id, "my_interests")
        logger.info(f"✅ Interests folder ID: {interests_folder_id}")
        
        # Upload test contract
        contract_path = Path(__file__).parent / "test_contract.txt"
        if contract_path.exists():
            logger.info("📤 Uploading test contract...")
            with open(contract_path, 'r') as f:
                contract_content = f.read()
            
            # Upload as text file (will be processed as contract)
            file_id = await service.upload_text_file(
                contracts_folder_id,
                "test_contract.txt",
                contract_content
            )
            logger.info(f"✅ Uploaded test contract: {file_id}")
        else:
            logger.warning(f"❌ Test contract file not found: {contract_path}")
        
        # Upload interests file
        interests_path = Path(__file__).parent / "MY_INTERESTS.txt"
        if interests_path.exists():
            logger.info("📤 Uploading interests file...")
            with open(interests_path, 'r') as f:
                interests_content = f.read()
            
            file_id = await service.upload_text_file(
                interests_folder_id,
                "MY_INTERESTS.txt",
                interests_content
            )
            logger.info(f"✅ Uploaded interests file: {file_id}")
        else:
            logger.warning(f"❌ Interests file not found: {interests_path}")
        
        logger.info("\n🎉 Test files uploaded successfully!")
        logger.info("📋 Next steps:")
        logger.info("   1. The contract processor should detect the new contract")
        logger.info("   2. Check Box 'protect_your_interests/' folder for output")
        logger.info("   3. Wait up to 60 seconds for processing")
        
    except Exception as e:
        logger.error(f"❌ Error uploading files: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(upload_test_files())

