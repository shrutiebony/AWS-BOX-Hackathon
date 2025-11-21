#!/bin/bash
# Subscribe email to SNS topic

source aws-credentials.sh

TOPIC_ARN="arn:aws:sns:us-east-1:440588070262:contract-action-items"

if [ -z "$1" ]; then
    echo "Usage: ./subscribe_email.sh your-email@example.com"
    exit 1
fi

USER_EMAIL="$1"

echo "Subscribing $USER_EMAIL to SNS topic..."
aws sns subscribe \
    --topic-arn "$TOPIC_ARN" \
    --protocol email \
    --notification-endpoint "$USER_EMAIL"

if [ $? -eq 0 ]; then
    echo "✅ Subscription request sent to $USER_EMAIL"
    echo "⚠️  Please check your email and confirm the subscription"
    echo ""
    echo "After confirming, add to your environment:"
    echo "export AWS_SNS_TOPIC_ARN=\"$TOPIC_ARN\""
    echo "export USER_EMAIL=\"$USER_EMAIL\""
else
    echo "❌ Error subscribing email"
fi

