#!/usr/bin/env python3
"""
Get user email from Box and subscribe to SNS topic
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add mcp-server-box src to path
mcp_server_path = Path(__file__).parent / "mcp-server-box" / "src"
sys.path.insert(0, str(mcp_server_path))

import boto3
from box_contract_service import BoxContractService
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_and_subscribe_email():
    """Get email from Box and subscribe to SNS."""
    service = BoxContractService()
    
    try:
        # Initialize Box service
        await service.initialize()
        
        # Get user email from Box
        email = await service.get_current_user_email()
        
        if not email:
            print("\n❌ Could not retrieve email from Box")
            return
        
        print(f"\n✅ Retrieved email from Box: {email}\n")
        
        # Load AWS credentials
        source_script = Path(__file__).parent / "aws-credentials.sh"
        if source_script.exists():
            # Credentials should already be in environment from aws-credentials.sh
            pass
        
        # Initialize SNS client
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        sns_client = boto3.client(
            'sns',
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN")
        )
        
        # SNS Topic ARN
        topic_arn = os.getenv(
            "AWS_SNS_TOPIC_ARN",
            "arn:aws:sns:us-east-1:440588070262:contract-action-items"
        )
        
        print(f"Subscribing {email} to SNS topic...")
        print(f"Topic ARN: {topic_arn}\n")
        
        # Subscribe email to topic
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )
        
        subscription_arn = response.get('SubscriptionArn')
        
        print(f"✅ Subscription request sent!")
        print(f"   Subscription ARN: {subscription_arn}")
        print(f"\n⚠️  IMPORTANT: Check your email ({email}) and confirm the subscription")
        print(f"   Look for an email from AWS SNS with subject 'AWS Notification - Subscription Confirmation'")
        print(f"\nAfter confirming, the system will automatically send notifications to this email.")
        print(f"\nTo set in environment:")
        print(f"export AWS_SNS_TOPIC_ARN=\"{topic_arn}\"")
        print(f"export USER_EMAIL=\"{email}\"")
        
        return email
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(get_and_subscribe_email())

