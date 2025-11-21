#!/usr/bin/env python3
"""
Verify SNS subscription status and test notification after confirmation.
"""

import boto3
import os
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_subscription():
    """Verify SNS subscription is confirmed and test notification."""
    
    logger.info("=" * 80)
    logger.info("VERIFYING SNS SUBSCRIPTION STATUS")
    logger.info("=" * 80)
    logger.info("")
    
    sns_topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")
    user_email = os.getenv("USER_EMAIL")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    if not sns_topic_arn or not user_email:
        logger.error("❌ Missing SNS configuration")
        return False
    
    # Initialize SNS client
    try:
        sns_client = boto3.client(
            'sns',
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN")
        )
    except Exception as e:
        logger.error(f"❌ Error initializing SNS client: {e}")
        return False
    
    # Check subscriptions
    try:
        response = sns_client.list_subscriptions_by_topic(TopicArn=sns_topic_arn)
        subscriptions = response.get('Subscriptions', [])
        
        email_confirmed = False
        for sub in subscriptions:
            if sub['Protocol'] == 'email' and sub['Endpoint'].lower() == user_email.lower():
                subscription_arn = sub.get('SubscriptionArn', '')
                
                if subscription_arn == 'PendingConfirmation':
                    logger.warning("⚠️  Subscription is still PENDING CONFIRMATION")
                    logger.info("")
                    logger.info("   Please check your email and click the confirmation link")
                    logger.info(f"   Email: {user_email}")
                    logger.info("   Look for: 'AWS Notification - Subscription Confirmation'")
                    return False
                elif 'arn:aws:sns' in subscription_arn:
                    logger.info(f"✅ Subscription CONFIRMED!")
                    logger.info(f"   Subscription ARN: {subscription_arn}")
                    email_confirmed = True
                    break
        
        if not email_confirmed:
            logger.error("❌ Email subscription not found")
            logger.info("   You may need to subscribe your email first")
            logger.info("   Run: python3 fix_sns_subscription.py")
            return False
        
    except ClientError as e:
        logger.error(f"❌ Error checking subscriptions: {e}")
        return False
    
    logger.info("")
    
    # Test notification
    logger.info("Sending test notification...")
    try:
        test_message = f"""✅ SNS Integration Test Successful!

Your email subscription is confirmed and working.

You will now receive notifications for urgent contract action items.

Test Details:
- Email: {user_email}
- Topic: {sns_topic_arn}
- Status: Confirmed and Active
"""
        
        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=test_message,
            Subject="✅ SNS Integration Verified - Contract Protection System"
        )
        
        message_id = response['MessageId']
        logger.info(f"✅ Test notification sent!")
        logger.info(f"   Message ID: {message_id}")
        logger.info("")
        logger.info("   Check your email inbox in a few seconds")
        logger.info(f"   Email: {user_email}")
        logger.info("   Subject: '✅ SNS Integration Verified - Contract Protection System'")
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ SNS INTEGRATION IS WORKING!")
        logger.info("=" * 80)
        return True
        
    except ClientError as e:
        logger.error(f"❌ Error sending test notification: {e}")
        return False


if __name__ == "__main__":
    verify_subscription()


