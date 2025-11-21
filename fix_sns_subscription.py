#!/usr/bin/env python3
"""
Fix SNS subscription - resubscribe email and provide confirmation instructions.
"""

import boto3
import os
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_sns_subscription():
    """Resubscribe email to SNS topic."""
    
    logger.info("=" * 80)
    logger.info("FIXING SNS EMAIL SUBSCRIPTION")
    logger.info("=" * 80)
    logger.info("")
    
    sns_topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")
    user_email = os.getenv("USER_EMAIL")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    if not sns_topic_arn or not user_email:
        logger.error("❌ Missing SNS configuration")
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
    except Exception as e:
        logger.error(f"❌ Error initializing SNS client: {e}")
        return
    
    logger.info(f"Topic ARN: {sns_topic_arn}")
    logger.info(f"Email: {user_email}")
    logger.info("")
    
    # Check existing subscriptions
    logger.info("Checking existing subscriptions...")
    try:
        response = sns_client.list_subscriptions_by_topic(TopicArn=sns_topic_arn)
        subscriptions = response.get('Subscriptions', [])
        
        # Check if email is already subscribed (even if pending)
        email_subscribed = False
        for sub in subscriptions:
            if sub['Protocol'] == 'email' and sub['Endpoint'].lower() == user_email.lower():
                email_subscribed = True
                if sub['SubscriptionArn'] != 'PendingConfirmation':
                    logger.info(f"✅ Email already confirmed: {sub['SubscriptionArn']}")
                    return
                else:
                    logger.info("⚠️  Email subscription is pending confirmation")
                    logger.info("   Resubscribing to send new confirmation email...")
                    break
    except ClientError as e:
        logger.error(f"❌ Error checking subscriptions: {e}")
        return
    
    logger.info("")
    
    # Subscribe email to topic
    logger.info("Subscribing email to SNS topic...")
    try:
        response = sns_client.subscribe(
            TopicArn=sns_topic_arn,
            Protocol='email',
            Endpoint=user_email
        )
        
        subscription_arn = response['SubscriptionArn']
        logger.info(f"✅ Subscription request sent!")
        logger.info(f"   Subscription ARN: {subscription_arn}")
        logger.info("")
        logger.info("=" * 80)
        logger.info("ACTION REQUIRED: CONFIRM EMAIL SUBSCRIPTION")
        logger.info("=" * 80)
        logger.info("")
        logger.info("1. Check your email inbox: " + user_email)
        logger.info("2. Look for an email from: no-reply@sns.amazonaws.com")
        logger.info("3. Subject: 'AWS Notification - Subscription Confirmation'")
        logger.info("4. Click the 'Confirm subscription' link in the email")
        logger.info("5. You will be redirected to a confirmation page")
        logger.info("")
        logger.info("⚠️  IMPORTANT:")
        logger.info("   - The confirmation email may be in your SPAM/JUNK folder")
        logger.info("   - Check all email folders if you don't see it")
        logger.info("   - The confirmation link expires after 3 days")
        logger.info("")
        logger.info("After confirmation, you will receive notifications for urgent contract action items.")
        logger.info("")
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', 'Unknown')
        
        if error_code == 'SubscriptionLimitExceeded':
            logger.warning("⚠️  Subscription limit reached")
            logger.info("   AWS SNS allows only 10 pending subscriptions per topic")
            logger.info("   You may need to wait for old subscriptions to expire")
        else:
            logger.error(f"❌ Error subscribing: {error_code}")
            logger.error(f"   {error_msg}")
    
    logger.info("")
    logger.info("=" * 80)


if __name__ == "__main__":
    fix_sns_subscription()


