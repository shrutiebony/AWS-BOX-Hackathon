#!/usr/bin/env python3
"""
Debug SNS email delivery - check subscriptions and test notification.
"""

import boto3
import os
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_sns():
    """Debug SNS configuration and subscriptions."""
    
    logger.info("=" * 80)
    logger.info("DEBUGGING SNS EMAIL DELIVERY")
    logger.info("=" * 80)
    logger.info("")
    
    # Get configuration
    sns_topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")
    user_email = os.getenv("USER_EMAIL")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    logger.info("Configuration:")
    logger.info(f"   SNS Topic ARN: {sns_topic_arn}")
    logger.info(f"   User Email: {user_email}")
    logger.info(f"   Region: {region}")
    logger.info("")
    
    if not sns_topic_arn:
        logger.error("❌ AWS_SNS_TOPIC_ARN not set")
        return
    
    if not user_email:
        logger.error("❌ USER_EMAIL not set")
        return
    
    # Initialize SNS client
    try:
        sns_client = boto3.client(
            'sns',
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN")
        )
        logger.info("✅ SNS client initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing SNS client: {e}")
        return
    
    logger.info("")
    
    # Step 1: Check topic exists
    logger.info("Step 1: Checking if topic exists...")
    try:
        topic_attrs = sns_client.get_topic_attributes(TopicArn=sns_topic_arn)
        logger.info(f"✅ Topic exists: {topic_attrs['Attributes']['TopicArn']}")
        logger.info(f"   Display Name: {topic_attrs['Attributes'].get('DisplayName', 'N/A')}")
    except ClientError as e:
        logger.error(f"❌ Topic not found: {e}")
        logger.info("   The topic may not exist or ARN is incorrect")
        return
    
    logger.info("")
    
    # Step 2: List subscriptions
    logger.info("Step 2: Checking topic subscriptions...")
    try:
        response = sns_client.list_subscriptions_by_topic(TopicArn=sns_topic_arn)
        subscriptions = response.get('Subscriptions', [])
        
        logger.info(f"   Found {len(subscriptions)} subscription(s)")
        logger.info("")
        
        if not subscriptions:
            logger.warning("⚠️  No subscriptions found!")
            logger.info("   You need to subscribe your email to the topic")
            logger.info("")
            logger.info("   To subscribe, run:")
            logger.info(f"   aws sns subscribe --topic-arn {sns_topic_arn} --protocol email --notification-endpoint {user_email}")
            return
        
        email_subscription = None
        for sub in subscriptions:
            logger.info(f"   Subscription: {sub['SubscriptionArn']}")
            logger.info(f"   Protocol: {sub['Protocol']}")
            logger.info(f"   Endpoint: {sub['Endpoint']}")
            logger.info(f"   Owner: {sub.get('Owner', 'N/A')}")
            
            if sub['Protocol'] == 'email' and sub['Endpoint'].lower() == user_email.lower():
                email_subscription = sub
                logger.info(f"   Status: {sub.get('SubscriptionArn', 'PendingConfirmation')}")
            
            logger.info("")
        
        if not email_subscription:
            logger.warning(f"⚠️  No subscription found for {user_email}")
            logger.info("   You need to subscribe this email to the topic")
            return
        
        # Check subscription status
        subscription_arn = email_subscription.get('SubscriptionArn', '')
        if subscription_arn == 'PendingConfirmation':
            logger.warning("⚠️  Subscription is PENDING CONFIRMATION")
            logger.info("")
            logger.info("   ACTION REQUIRED:")
            logger.info("   1. Check your email inbox: " + user_email)
            logger.info("   2. Look for an email from AWS SNS")
            logger.info("   3. Subject: 'AWS Notification - Subscription Confirmation'")
            logger.info("   4. Click the confirmation link in the email")
            logger.info("   5. After confirmation, you will receive notifications")
            logger.info("")
            return
        elif 'arn:aws:sns' in subscription_arn:
            logger.info(f"✅ Subscription confirmed: {subscription_arn}")
        else:
            logger.warning(f"⚠️  Subscription status unclear: {subscription_arn}")
        
    except ClientError as e:
        logger.error(f"❌ Error listing subscriptions: {e}")
        return
    
    logger.info("")
    
    # Step 3: Test notification
    logger.info("Step 3: Sending test notification...")
    try:
        test_message = f"""Test Notification from Contract Protection System

This is a test email to verify SNS integration is working.

If you receive this email, the SNS integration is functioning correctly.

Test Details:
- Topic ARN: {sns_topic_arn}
- Email: {user_email}
- Time: {os.popen('date').read().strip()}
"""
        
        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=test_message,
            Subject="🧪 Test: Contract Protection System SNS Integration"
        )
        
        message_id = response['MessageId']
        logger.info(f"✅ Test notification sent!")
        logger.info(f"   Message ID: {message_id}")
        logger.info("")
        logger.info("   Check your email inbox in a few seconds")
        logger.info(f"   Email: {user_email}")
        logger.info("   Subject: '🧪 Test: Contract Protection System SNS Integration'")
        
    except ClientError as e:
        logger.error(f"❌ Error sending test notification: {e}")
        logger.info(f"   Error Code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
        logger.info(f"   Error Message: {e.response.get('Error', {}).get('Message', 'Unknown')}")
        return
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("DEBUG COMPLETE")
    logger.info("=" * 80)


if __name__ == "__main__":
    debug_sns()


