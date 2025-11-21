# Action Items & Notifications Setup

## Overview

The system now automatically detects time-sensitive action items from contracts and sends email notifications via AWS SNS.

## Action Items Detected

The system monitors for:
- **Contract expiration** (within 10 days)
- **Payment due dates** (upcoming)
- **Audit deadlines** (within 5 days)
- **Renewal deadlines** (within 10 days)
- **Notice periods** (within 7 days)
- **Other time-sensitive obligations** (within 5 days)

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install boto3
# Or if using requirements.txt:
pip install -r requirements.txt
```

### Step 2: Set Up AWS SNS Topic

Run the setup script:

```bash
source aws-credentials.sh
./setup_sns_topic.sh
```

This will:
1. Create an SNS topic named `contract-action-items`
2. Subscribe your email to the topic
3. Show you the topic ARN to add to your `.env` file

### Step 3: Confirm Email Subscription

1. Check your email inbox
2. Look for a confirmation email from AWS SNS
3. Click the confirmation link

### Step 4: Configure Environment Variables

Add these to your `.env` file (or export them):

```bash
AWS_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:440588070262:contract-action-items
USER_EMAIL=your-email@example.com
```

Or add to `aws-credentials.sh`:

```bash
export AWS_SNS_TOPIC_ARN="arn:aws:sns:us-east-1:440588070262:contract-action-items"
export USER_EMAIL="your-email@example.com"
```

## How It Works

1. **Periodic Checks**: System checks all contracts for action items every hour (3600 seconds)
2. **AI Analysis**: Uses Box AI to analyze each contract and extract action items
3. **Urgency Filtering**: Filters items based on urgency thresholds:
   - Expiration: ≤ 10 days
   - Audit: ≤ 5 days
   - Payment: ≤ 14 days
   - Renewal: ≤ 10 days
   - Notice: ≤ 7 days
   - Other: ≤ 5 days
4. **Email Notification**: Sends email via AWS SNS if urgent items are found

## Notification Email Format

```
Subject: ⚠️ Contract Action Items - X Urgent Item(s)

Contract Action Items Alert

You have X urgent action item(s) requiring attention:

1. EXPIRATION
   Contract: Employment_Offer_ABC.pdf
   Description: Contract expires on December 31, 2024
   Due Date: 2024-12-31
   Days Until Due: 5
   Priority: HIGH
   Action Required: Review and decide on renewal or termination

2. PAYMENT DUE
   Contract: Service_Agreement_XYZ.pdf
   Description: Quarterly payment due on January 15, 2025
   Due Date: 2025-01-15
   Days Until Due: 8
   Priority: MEDIUM
   Action Required: Ensure payment is processed before due date
```

## Configuration

### Adjust Check Intervals

In `contract_processor.py`, you can adjust:

```python
await processor.run_continuous_monitoring(
    check_interval=60,              # Check for new contracts every 60 seconds
    action_item_check_interval=3600  # Check action items every hour (3600 seconds)
)
```

### Adjust Urgency Thresholds

In `action_item_detector.py`, modify the `filter_urgent_action_items` method:

```python
if item.get('type') == 'expiration' and 0 <= days_until <= 10:  # Change 10 to your preference
    is_urgent = True
```

## Testing

### Test Action Item Detection

```python
# In Python
from action_item_detector import ActionItemDetector

detector = ActionItemDetector()
# Test with a contract file ID
action_items = await detector.analyze_contract_for_action_items(...)
```

### Test SNS Notification

```bash
# Send a test notification
aws sns publish \
    --topic-arn "arn:aws:sns:us-east-1:440588070262:contract-action-items" \
    --message "Test notification" \
    --subject "Test"
```

## Troubleshooting

### No Emails Received

1. **Check email subscription**: Make sure you confirmed the SNS subscription email
2. **Check topic ARN**: Verify `AWS_SNS_TOPIC_ARN` is set correctly
3. **Check AWS credentials**: Ensure AWS credentials are loaded
4. **Check logs**: Look for SNS errors in the application logs

### Action Items Not Detected

1. **Check Box AI**: Ensure Box AI is working and can analyze contracts
2. **Check date formats**: The AI needs to extract dates in a parseable format
3. **Check logs**: Look for parsing errors in the logs

### AWS SNS Errors

1. **Check credentials**: Verify AWS credentials are valid
2. **Check permissions**: Ensure the AWS account has SNS publish permissions
3. **Check region**: Make sure SNS topic is in the same region as credentials

## Manual Check

You can manually trigger an action item check:

```python
from contract_processor import ContractProcessor
import asyncio

async def check():
    processor = ContractProcessor()
    await processor.initialize()
    await processor.check_all_contracts_for_action_items()

asyncio.run(check())
```

---

**Ready to use!** The system will automatically check contracts and send notifications when urgent action items are found.

