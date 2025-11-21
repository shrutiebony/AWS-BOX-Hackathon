#!/usr/bin/env python3
"""
Test SNS integration - upload contract with urgent deadline and verify notification.
"""

import asyncio
import logging
import os
from box_contract_service import BoxContractService
from contract_processor import ContractProcessor
from action_item_detector import ActionItemDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_sns_integration():
    """Test SNS notification flow."""
    
    logger.info("=" * 80)
    logger.info("TESTING SNS INTEGRATION")
    logger.info("=" * 80)
    logger.info("")
    
    # Step 1: Check SNS configuration
    logger.info("Step 1: Checking SNS configuration...")
    sns_topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")
    user_email = os.getenv("USER_EMAIL")
    
    logger.info(f"   SNS Topic ARN: {sns_topic_arn}")
    logger.info(f"   User Email: {user_email}")
    
    if not sns_topic_arn:
        logger.error("❌ AWS_SNS_TOPIC_ARN not set in environment")
        logger.info("   Please set it in aws-credentials.sh or .env file")
        return
    
    if not user_email:
        logger.error("❌ USER_EMAIL not set in environment")
        logger.info("   Please set it in aws-credentials.sh or .env file")
        return
    
    logger.info("✅ SNS configuration found")
    logger.info("")
    
    # Step 2: Upload test contract with urgent deadline
    logger.info("Step 2: Uploading test contract with urgent deadline...")
    service = BoxContractService()
    await service.initialize()
    
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    
    # Read the urgent contract
    with open("TEST_URGENT_CONTRACT.txt", "r") as f:
        contract_content = f.read()
    
    filename = "TEST_URGENT_CONTRACT.txt"
    file_id = await service.upload_text_file(
        contracts_folder_id,
        filename,
        contract_content
    )
    
    logger.info(f"✅ Uploaded {filename}")
    logger.info(f"   File ID: {file_id}")
    logger.info("")
    
    # Step 3: Initialize action item detector
    logger.info("Step 3: Initializing action item detector...")
    detector = ActionItemDetector(box_service=service)
    
    if not detector.sns_client:
        logger.error("❌ SNS client not initialized")
        return
    
    logger.info("✅ Action item detector initialized")
    logger.info("")
    
    # Step 4: Analyze contract for action items
    logger.info("Step 4: Analyzing contract for action items...")
    logger.info("   (This may take 10-20 seconds for AI analysis)")
    
    contract_text = await service.read_file(file_id)
    action_items = await detector.analyze_contract_for_action_items(
        service,
        file_id,
        filename,
        contract_text
    )
    
    logger.info(f"   Found {len(action_items)} action item(s)")
    
    for i, item in enumerate(action_items, 1):
        logger.info(f"   {i}. {item.get('type', 'unknown')}: {item.get('description', 'N/A')}")
        logger.info(f"      Due: {item.get('due_date', 'N/A')} ({item.get('days_until_due', 'N/A')} days)")
    
    logger.info("")
    
    # Step 5: Filter urgent items
    logger.info("Step 5: Filtering urgent action items...")
    urgent_items = detector.filter_urgent_action_items(action_items)
    
    logger.info(f"   Found {len(urgent_items)} urgent item(s)")
    
    if urgent_items:
        for i, item in enumerate(urgent_items, 1):
            logger.info(f"   {i}. {item.get('type', 'unknown')}: {item.get('description', 'N/A')}")
            logger.info(f"      Due: {item.get('due_date', 'N/A')} ({item.get('days_until_due', 'N/A')} days)")
            logger.info(f"      Priority: {item.get('priority', 'medium')}")
    else:
        logger.warning("   ⚠️  No urgent items found (may need to adjust dates in contract)")
    
    logger.info("")
    
    # Step 6: Send notification
    if urgent_items:
        logger.info("Step 6: Sending SNS notification...")
        success = detector.send_notification(urgent_items)
        
        if success:
            logger.info("✅ Notification sent successfully!")
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ SNS INTEGRATION TEST PASSED")
            logger.info("=" * 80)
            logger.info("")
            logger.info("Check your email inbox at:")
            logger.info(f"   {user_email}")
            logger.info("")
            logger.info("You should receive an email with subject:")
            logger.info(f"   '⚠️ Contract Action Items - {len(urgent_items)} Urgent Item(s)'")
            logger.info("")
        else:
            logger.error("❌ Failed to send notification")
            logger.info("   Check logs for errors")
    else:
        logger.warning("⚠️  No urgent items to send notification for")
        logger.info("   Creating test notification with dummy data...")
        
        # Create a test urgent item
        test_item = {
            'type': 'expiration',
            'description': 'Test contract expiration (SNS integration test)',
            'due_date': '2025-11-25',
            'days_until_due': 5,
            'priority': 'high',
            'action_required': 'Review and renew contract',
            'contract': filename
        }
        
        success = detector.send_notification([test_item])
        
        if success:
            logger.info("✅ Test notification sent successfully!")
            logger.info("   Check your email for the test notification")
        else:
            logger.error("❌ Failed to send test notification")
    
    logger.info("")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_sns_integration())


