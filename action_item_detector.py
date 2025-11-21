#!/usr/bin/env python3
"""
Action Item Detector
Analyzes contracts for time-sensitive action items and sends notifications via AWS SNS.
"""

import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ActionItemDetector:
    """Detects action items from contracts and sends notifications."""
    
    def __init__(self, box_service=None):
        self.sns_client = None
        self.sns_topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")
        self.user_email = os.getenv("USER_EMAIL")
        self.box_service = box_service  # Store box service for getting email
        self._initialize_sns()
    
    def _initialize_sns(self):
        """Initialize AWS SNS client."""
        try:
            # Load AWS credentials from environment
            region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            self.sns_client = boto3.client(
                'sns',
                region_name=region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.getenv("AWS_SESSION_TOKEN")
            )
            logger.info("AWS SNS client initialized")
        except Exception as e:
            logger.error(f"Error initializing SNS client: {e}")
            self.sns_client = None
    
    async def analyze_contract_for_action_items(
        self,
        box_service,
        contract_file_id: str,
        contract_filename: str,
        contract_text: str
    ) -> List[Dict]:
        """Analyze contract for action items using Box AI."""
        
        action_items_prompt = f"""Analyze this contract and identify any time-sensitive action items or deadlines.

Look for:
1. Contract expiration dates (within 10 days)
2. Payment due dates (upcoming)
3. Audit deadlines (within 5 days)
4. Renewal deadlines
5. Notice periods that need action
6. Any other time-sensitive obligations

Contract content:
{contract_text[:5000]}...

For each action item found, provide:
- Type: (expiration, payment_due, audit_due, renewal, notice_period, other)
- Description: Brief description of the action item
- Due Date: The specific date (format: YYYY-MM-DD)
- Days Until Due: Number of days until the deadline
- Priority: (high, medium, low)
- Action Required: What the user needs to do

Format your response as a structured list. If no action items found, respond with "No action items found."

Example format:
ACTION ITEM 1:
Type: expiration
Description: Contract expires on December 31, 2024
Due Date: 2024-12-31
Days Until Due: 5
Priority: high
Action Required: Review and decide on renewal or termination

ACTION ITEM 2:
Type: payment_due
Description: Quarterly payment due on January 15, 2025
Due Date: 2025-01-15
Days Until Due: 8
Priority: medium
Action Required: Ensure payment is processed before due date
"""
        
        try:
            # Box AI call is async
            response = await box_service.ask_ai_about_file(
                contract_file_id, action_items_prompt
            )
            
            # Parse the response to extract action items
            action_items = self._parse_action_items(response, contract_filename)
            
            return action_items
            
        except Exception as e:
            logger.error(f"Error analyzing contract for action items: {e}")
            return []
    
    def _parse_action_items(self, ai_response: str, contract_filename: str) -> List[Dict]:
        """Parse AI response to extract structured action items."""
        action_items = []
        
        if "no action items found" in ai_response.lower():
            return []
        
        # Split by "ACTION ITEM" markers
        items_text = re.split(r'ACTION ITEM\s*\d+:', ai_response, flags=re.IGNORECASE)
        
        for item_text in items_text[1:]:  # Skip first empty split
            try:
                item = {}
                
                # Extract type
                type_match = re.search(r'Type:\s*(\w+)', item_text, re.IGNORECASE)
                if type_match:
                    item['type'] = type_match.group(1).lower()
                
                # Extract description
                desc_match = re.search(r'Description:\s*(.+?)(?:\n|Due Date:)', item_text, re.IGNORECASE | re.DOTALL)
                if desc_match:
                    item['description'] = desc_match.group(1).strip()
                
                # Extract due date
                date_match = re.search(r'Due Date:\s*(\d{4}-\d{2}-\d{2})', item_text)
                if date_match:
                    item['due_date'] = date_match.group(1)
                    item['due_date_obj'] = datetime.strptime(item['due_date'], '%Y-%m-%d')
                    
                    # Calculate days until due
                    days_until = (item['due_date_obj'] - datetime.now()).days
                    item['days_until_due'] = days_until
                else:
                    # Try to extract date from description
                    date_patterns = [
                        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                        r'(\w+\s+\d{1,2},?\s+\d{4})',
                    ]
                    for pattern in date_patterns:
                        date_match = re.search(pattern, item_text)
                        if date_match:
                            try:
                                # Try to parse the date
                                date_str = date_match.group(1)
                                # This is a simplified parser - you might need more robust date parsing
                                item['due_date'] = date_str
                                break
                            except:
                                pass
                
                # Extract priority
                priority_match = re.search(r'Priority:\s*(\w+)', item_text, re.IGNORECASE)
                if priority_match:
                    item['priority'] = priority_match.group(1).lower()
                
                # Extract action required
                action_match = re.search(r'Action Required:\s*(.+?)(?:\n\n|\Z)', item_text, re.IGNORECASE | re.DOTALL)
                if action_match:
                    item['action_required'] = action_match.group(1).strip()
                
                # Add contract filename
                item['contract'] = contract_filename
                
                # Only add if it has required fields
                if 'type' in item and 'description' in item:
                    action_items.append(item)
                    
            except Exception as e:
                logger.error(f"Error parsing action item: {e}")
                continue
        
        return action_items
    
    def filter_urgent_action_items(self, action_items: List[Dict]) -> List[Dict]:
        """Filter action items that need immediate attention."""
        urgent_items = []
        
        for item in action_items:
            days_until = item.get('days_until_due')
            
            # Check if item is urgent based on type and days until due
            is_urgent = False
            
            if days_until is not None:
                if item.get('type') == 'expiration' and 0 <= days_until <= 10:
                    is_urgent = True
                elif item.get('type') == 'audit_due' and 0 <= days_until <= 5:
                    is_urgent = True
                elif item.get('type') == 'payment_due' and 0 <= days_until <= 14:
                    is_urgent = True
                elif item.get('type') == 'renewal' and 0 <= days_until <= 10:
                    is_urgent = True
                elif item.get('type') == 'notice_period' and 0 <= days_until <= 7:
                    is_urgent = True
                elif days_until <= 5:  # Any item due within 5 days
                    is_urgent = True
            
            if is_urgent:
                urgent_items.append(item)
        
        return urgent_items
    
    async def get_user_email_from_box(self) -> Optional[str]:
        """Get user email from Box if not set in environment."""
        if self.user_email:
            return self.user_email
        
        if self.box_service:
            try:
                email = await self.box_service.get_current_user_email()
                if email:
                    self.user_email = email
                    logger.info(f"Retrieved email from Box: {email}")
                    # Also ensure SNS topic ARN is set
                    if not self.sns_topic_arn:
                        self.sns_topic_arn = os.getenv(
                            "AWS_SNS_TOPIC_ARN",
                            "arn:aws:sns:us-east-1:440588070262:contract-action-items"
                        )
                    return email
            except Exception as e:
                logger.error(f"Error getting email from Box: {e}")
        
        return None
    
    def send_notification(self, action_items: List[Dict]) -> bool:
        """Send email notification via AWS SNS."""
        if not self.sns_client:
            logger.error("SNS client not initialized")
            return False
        
        if not self.user_email:
            logger.error("USER_EMAIL not set in environment and could not get from Box")
            return False
        
        if not action_items:
            return True  # Nothing to send
        
        try:
            # Build email message
            subject = f"⚠️ Contract Action Items - {len(action_items)} Urgent Item(s)"
            
            message_body = self._build_email_message(action_items)
            
            # If SNS topic ARN is provided, publish to topic
            if self.sns_topic_arn:
                response = self.sns_client.publish(
                    TopicArn=self.sns_topic_arn,
                    Message=message_body,
                    Subject=subject
                )
                logger.info(f"Notification sent to SNS topic: {response['MessageId']}")
            else:
                # Otherwise, send directly to email (requires email subscription)
                # For direct email, you'd need to subscribe the email to a topic first
                logger.warning("AWS_SNS_TOPIC_ARN not set. Cannot send notification.")
                logger.info("To enable notifications:")
                logger.info("1. Create an SNS topic in AWS")
                logger.info("2. Subscribe your email to the topic")
                logger.info("3. Set AWS_SNS_TOPIC_ARN in environment")
                return False
            
            return True
            
        except ClientError as e:
            logger.error(f"AWS SNS error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def _build_email_message(self, action_items: List[Dict]) -> str:
        """Build the email message body."""
        message = f"""Contract Action Items Alert

You have {len(action_items)} urgent action item(s) requiring attention:

"""
        
        for i, item in enumerate(action_items, 1):
            message += f"""
{i}. {item.get('type', 'unknown').upper().replace('_', ' ')}
   Contract: {item.get('contract', 'Unknown')}
   Description: {item.get('description', 'N/A')}
   Due Date: {item.get('due_date', 'N/A')}
   Days Until Due: {item.get('days_until_due', 'N/A')}
   Priority: {item.get('priority', 'medium').upper()}
   Action Required: {item.get('action_required', 'Review contract')}
   
"""
        
        message += """
---
This is an automated notification from the Contract Protection System.
Please review these contracts and take appropriate action.
"""
        
        return message

