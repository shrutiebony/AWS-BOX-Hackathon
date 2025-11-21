#!/usr/bin/env python3
"""Manually process the test employment contract."""

import asyncio
import logging
from contract_processor import ContractProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def process_test_employment():
    """Manually process TEST_EMPLOYMENT_CONTRACT.txt."""
    
    processor = ContractProcessor()
    await processor.initialize()
    
    # File ID from upload
    file_id = "2052525439199"
    filename = "TEST_EMPLOYMENT_CONTRACT.txt"
    contract_name = "TEST_EMPLOYMENT_CONTRACT"
    
    logger.info("=" * 80)
    logger.info("PROCESSING TEST EMPLOYMENT CONTRACT")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        # Remove from processed set if already there
        contract_key = f"{contract_name}_{file_id}"
        if contract_key in processor.processed_contracts:
            logger.info(f"Removing from processed set to reprocess...")
            processor.processed_contracts.discard(contract_key)
        
        logger.info(f"Processing {filename}...")
        await processor.process_contract(file_id, filename, contract_name)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ PROCESSING COMPLETE!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(process_test_employment())


