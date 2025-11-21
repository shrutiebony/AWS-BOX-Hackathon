#!/bin/bash
# Setup AWS SNS Topic for Contract Action Item Notifications

echo "Setting up AWS SNS Topic for contract notifications..."

# Load AWS credentials
source aws-credentials.sh

# Get user email from environment or prompt
if [ -z "$USER_EMAIL" ]; then
    read -p "Enter your email address for notifications: " USER_EMAIL
    export USER_EMAIL
fi

# Create SNS topic
TOPIC_NAME="contract-action-items"
echo "Creating SNS topic: $TOPIC_NAME"

TOPIC_ARN=$(aws sns create-topic --name $TOPIC_NAME --query 'TopicArn' --output text)

if [ $? -eq 0 ]; then
    echo "✅ Topic created: $TOPIC_ARN"
    
    # Subscribe email to topic
    echo "Subscribing $USER_EMAIL to topic..."
    aws sns subscribe \
        --topic-arn "$TOPIC_ARN" \
        --protocol email \
        --notification-endpoint "$USER_EMAIL"
    
    if [ $? -eq 0 ]; then
        echo "✅ Subscription request sent to $USER_EMAIL"
        echo "⚠️  Please check your email and confirm the subscription"
        echo ""
        echo "Add these to your .env file:"
        echo "AWS_SNS_TOPIC_ARN=$TOPIC_ARN"
        echo "USER_EMAIL=$USER_EMAIL"
    else
        echo "❌ Error subscribing email"
    fi
else
    echo "❌ Error creating topic"
    exit 1
fi

