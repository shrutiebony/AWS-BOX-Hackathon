# Email Notification Configuration

## ✅ Email Address Updated

**Notification Email:** `sameersah7365@gmail.com`

## Configuration

The email address is configured in `aws-credentials.sh`:

```bash
export USER_EMAIL="sameersah7365@gmail.com"
export AWS_SNS_TOPIC_ARN="arn:aws:sns:us-east-1:440588070262:contract-action-items"
```

## SNS Subscription

The email has been subscribed to the AWS SNS topic for notifications.

**⚠️ IMPORTANT:** You need to confirm the subscription:

1. Check your email inbox: `sameersah7365@gmail.com`
2. Look for an email from AWS SNS with subject: **"AWS Notification - Subscription Confirmation"**
3. Click the confirmation link in the email
4. After confirmation, you will receive notifications for urgent contract action items

## How Notifications Work

The system will send email notifications when:
- Contract expiration dates are within 10 days
- Payment due dates are upcoming (within 14 days)
- Audit deadlines are within 5 days
- Renewal deadlines are within 10 days
- Notice periods require action (within 7 days)
- Any other urgent action items (within 5 days)

## Notification Frequency

- Action items are checked **every hour** (3600 seconds)
- Notifications are sent only for **urgent** items
- Each notification includes:
  - Contract name
  - Action item type
  - Due date
  - Days until due
  - Priority level
  - Required action

## Testing

To test notifications:
1. Upload a contract with an upcoming deadline
2. Wait for the hourly check (or trigger manually)
3. If urgent items are found, you'll receive an email at `sameersah7365@gmail.com`

## Current Status

- ✅ Email configured: `sameersah7365@gmail.com`
- ✅ SNS topic ARN configured
- ✅ Subscription request sent
- ⏳ **Waiting for email confirmation** (check your inbox)

