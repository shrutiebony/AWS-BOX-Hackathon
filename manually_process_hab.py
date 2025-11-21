#!/usr/bin/env python3
"""
Manually process HAB-2-17.docx to debug why files aren't being generated.
"""

import asyncio
import logging
from contract_processor import ContractProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def manually_process_hab():
    """Manually process HAB-2-17.docx."""
    
    processor = ContractProcessor()
    await processor.initialize()
    
    # HAB-2-17.docx file ID from check_hab_file.py output
    file_id = "2052516976658"
    filename = "HAB-2-17.docx"
    contract_name = "HAB-2-17"
    
    logger.info("=" * 80)
    logger.info("MANUALLY PROCESSING HAB-2-17.docx")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        # Check if already processed
        contract_key = f"{contract_name}_{file_id}"
        if contract_key in processor.processed_contracts:
            logger.warning(f"⚠️  Contract {contract_name} already processed (key: {contract_key})")
            logger.info("Removing from processed set to reprocess...")
            processor.processed_contracts.discard(contract_key)
        
        # Try to process
        logger.info(f"Starting processing of {filename}...")
        await processor.process_contract(file_id, filename, contract_name)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ PROCESSING COMPLETE!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ ERROR PROCESSING: {e}")
        import traceback
        traceback.print_exc()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("ERROR DETAILS")
        logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(manually_process_hab())


