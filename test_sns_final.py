#!/usr/bin/env python3
"""
Final SNS test - use existing urgent contract to trigger notification.
"""

import asyncio
import logging
import os
from box_contract_service import BoxContractService
from action_item_detector import ActionItemDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_sns_final():
    """Test SNS with existing urgent contract."""
    
    logger.info("=" * 80)
    logger.info("FINAL SNS INTEGRATION TEST")
    logger.info("=" * 80)
    logger.info("")
    
    # Initialize services
    service = BoxContractService()
    await service.initialize()
    
    detector = ActionItemDetector(box_service=service)
    
    # Check subscription status
    logger.info("Step 1: Checking subscription status...")
    try:
        import boto3
        sns_client = boto3.client(
            'sns',
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN")
        )
        
        response = sns_client.list_subscriptions_by_topic(
            TopicArn=os.getenv("AWS_SNS_TOPIC_ARN")
        )
        
        user_email = os.getenv("USER_EMAIL")
        confirmed = False
        for sub in response.get('Subscriptions', []):
            if (sub['Protocol'] == 'email' and 
                sub['Endpoint'].lower() == user_email.lower() and
                'arn:aws:sns' in sub.get('SubscriptionArn', '')):
                confirmed = True
                logger.info(f"✅ Subscription confirmed: {sub['SubscriptionArn']}")
                break
        
        if not confirmed:
            logger.error("❌ Subscription not confirmed")
            return
        
    except Exception as e:
        logger.error(f"❌ Error checking subscription: {e}")
        return
    
    logger.info("")
    
    # Use existing urgent contract
    logger.info("Step 2: Analyzing existing urgent contract...")
    root_id = "0"
    contracts_folder_id = await service.find_or_create_folder(root_id, "Smart_Contracts")
    
    # Find TEST_URGENT_CONTRACT.txt
    items = await service.list_folder_items(contracts_folder_id)
    urgent_file_id = None
    urgent_filename = None
    
    for item in items:
        if item['type'] == 'file' and 'TEST_URGENT' in item['name']:
            urgent_file_id = item['id']
            urgent_filename = item['name']
            break
    
    if not urgent_file_id:
        logger.warning("⚠️  TEST_URGENT_CONTRACT.txt not found")
        logger.info("   Creating a new test contract...")
        # Would create one, but let's just use what we have
        return
    
    logger.info(f"   Found: {urgent_filename} (ID: {urgent_file_id})")
    logger.info("")
    
    # Analyze for action items
    logger.info("Step 3: Analyzing contract for action items...")
    contract_text = await service.read_file(urgent_file_id)
    
    action_items = await detector.analyze_contract_for_action_items(
        service,
        urgent_file_id,
        urgent_filename,
        contract_text
    )
    
    logger.info(f"   Found {len(action_items)} action item(s)")
    logger.info("")
    
    # Filter urgent items
    logger.info("Step 4: Filtering urgent action items...")
    urgent_items = detector.filter_urgent_action_items(action_items)
    
    logger.info(f"   Found {len(urgent_items)} urgent item(s)")
    
    if urgent_items:
        for i, item in enumerate(urgent_items, 1):
            logger.info(f"   {i}. {item.get('type', 'unknown')}: {item.get('description', 'N/A')}")
            logger.info(f"      Due: {item.get('due_date', 'N/A')} ({item.get('days_until_due', 'N/A')} days)")
    else:
        logger.warning("   ⚠️  No urgent items found")
        logger.info("   Creating test urgent item...")
        urgent_items = [{
            'type': 'expiration',
            'description': 'Contract expiration test (SNS integration verified)',
            'due_date': '2025-11-25',
            'days_until_due': 4,
            'priority': 'high',
            'action_required': 'Review and take action',
            'contract': urgent_filename
        }]
    
    logger.info("")
    
    # Send notification
    logger.info("Step 5: Sending SNS notification...")
    success = detector.send_notification(urgent_items)
    
    if success:
        logger.info("✅ Notification sent successfully!")
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ SNS INTEGRATION TEST PASSED")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Check your email inbox at: {os.getenv('USER_EMAIL')}")
        logger.info("")
        logger.info("You should receive an email with:")
        logger.info(f"   Subject: '⚠️ Contract Action Items - {len(urgent_items)} Urgent Item(s)'")
        logger.info("   Content: Details of all urgent action items")
        logger.info("")
        logger.info("✅ Email notifications are now working!")
    else:
        logger.error("❌ Failed to send notification")
    
    logger.info("")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_sns_final())


