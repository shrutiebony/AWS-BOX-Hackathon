#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock integration.
"""

import asyncio
import logging
from box_contract_service import BoxContractService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_bedrock_integration():
    """Test Bedrock integration with a simple prompt."""
    
    service = BoxContractService()
    await service.initialize()
    
    # Find a test contract file
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    
    items = await service.list_folder_items(contracts_folder_id)
    
    if not items:
        logger.error("No contracts found to test with")
        return
    
    # Use the first contract file
    test_file = None
    for item in items:
        if item['type'] == 'file':
            test_file = item
            break
    
    if not test_file:
        logger.error("No contract files found")
        return
    
    logger.info(f"Testing with file: {test_file['name']} (ID: {test_file['id']})")
    
    # Test prompt
    test_prompt = """Analyze this contract and provide a brief summary (2-3 sentences) of what type of contract this is and its main purpose."""
    
    try:
        logger.info("Calling ask_ai_about_file (which should use Bedrock)...")
        result = await service.ask_ai_about_file(test_file['id'], test_prompt)
        
        logger.info("=" * 70)
        logger.info("✅ BEDROCK INTEGRATION TEST SUCCESSFUL!")
        logger.info("=" * 70)
        logger.info(f"\nResponse from Bedrock:\n{result[:500]}...")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_bedrock_integration())

