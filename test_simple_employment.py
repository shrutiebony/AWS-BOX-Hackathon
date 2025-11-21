#!/usr/bin/env python3
"""
Test with a simple employment contract - upload, process, and verify.
"""

import asyncio
import logging
import time
from box_contract_service import BoxContractService
from contract_processor import ContractProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_simple_employment():
    """Test with a simple employment contract."""
    
    logger.info("=" * 80)
    logger.info("TESTING WITH SIMPLE EMPLOYMENT CONTRACT")
    logger.info("=" * 80)
    logger.info("")
    
    # Step 1: Upload contract
    service = BoxContractService()
    await service.initialize()
    
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    
    # Read the simple contract
    with open("SIMPLE_EMPLOYMENT.txt", "r") as f:
        contract_content = f.read()
    
    filename = "SIMPLE_EMPLOYMENT.txt"
    logger.info(f"Step 1: Uploading {filename}...")
    file_id = await service.upload_text_file(
        contracts_folder_id,
        filename,
        contract_content
    )
    
    logger.info(f"✅ Uploaded {filename}")
    logger.info(f"   File ID: {file_id}")
    logger.info("")
    
    # Step 2: Process the contract
    logger.info("Step 2: Processing contract...")
    processor = ContractProcessor()
    await processor.initialize()
    
    contract_name = "SIMPLE_EMPLOYMENT"
    contract_key = f"{contract_name}_{file_id}"
    
    # Remove from processed set if already there
    if contract_key in processor.processed_contracts:
        processor.processed_contracts.discard(contract_key)
        logger.info("Removed from processed set to allow reprocessing")
    
    try:
        await processor.process_contract(file_id, filename, contract_name)
        logger.info("✅ Contract processed successfully")
    except Exception as e:
        logger.error(f"❌ Error processing contract: {e}")
        import traceback
        traceback.print_exc()
        return
    
    logger.info("")
    
    # Step 3: Wait a moment for files to be fully uploaded
    logger.info("Step 3: Waiting for files to be fully uploaded...")
    await asyncio.sleep(5)
    
    # Step 4: Verify generated files
    logger.info("Step 4: Verifying generated files...")
    logger.info("")
    
    protect_folder_id = await service.find_or_create_folder(root_id, "protect_your_interests")
    employment_folder_id = await service.find_or_create_folder(protect_folder_id, "Employment Contract")
    
    items = await service.list_folder_items(employment_folder_id)
    
    simple_folder_found = False
    for item in items:
        if item['type'] == 'folder' and 'SIMPLE_EMPLOYMENT' in item['name']:
            simple_folder_found = True
            logger.info(f"✅ Found mirror folder: {item['name']}")
            logger.info("")
            
            files = await service.list_folder_items(item['id'])
            file_list = [f for f in files if f['type'] == 'file']
            
            logger.info(f"   Files found: {len(file_list)}")
            logger.info("")
            
            expected_files = [
                "1_mirror_contract_protecting_YOUR_interests.txt",
                "2_clean_redline_comparison.txt",
                "3_negotiation_guide.txt"
            ]
            
            found_files = []
            for f in file_list:
                logger.info(f"   📄 {f['name']}")
                found_files.append(f['name'])
            
            logger.info("")
            
            # Check if all expected files are present
            all_found = True
            for expected in expected_files:
                if expected not in found_files:
                    logger.warning(f"   ⚠️  Missing: {expected}")
                    all_found = False
            
            if all_found and len(file_list) == 3:
                logger.info("=" * 80)
                logger.info("✅ SUCCESS: All 3 files generated correctly!")
                logger.info("=" * 80)
                logger.info("")
                logger.info("Generated files location:")
                logger.info("  protect_your_interests → Employment Contract → SIMPLE_EMPLOYMENT_mirror")
                logger.info("")
                logger.info("Files:")
                logger.info("  1. 1_mirror_contract_protecting_YOUR_interests.txt")
                logger.info("  2. 2_clean_redline_comparison.txt")
                logger.info("  3. 3_negotiation_guide.txt")
            else:
                logger.warning("⚠️  Some files may be missing or incorrect")
    
    if not simple_folder_found:
        logger.error("❌ Mirror folder not found - processing may have failed")
        logger.info("   Check logs for errors")
    
    logger.info("")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_simple_employment())


