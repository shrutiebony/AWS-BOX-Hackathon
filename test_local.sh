#!/bin/bash
# Local Testing Script for Contract Protection System

set -e

cd "$(dirname "$0")"

echo "🧪 Contract Protection System - Local Testing"
echo "=============================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Check if .env exists
if [ ! -f "mcp-server-box/.env" ]; then
    echo "❌ .env file not found in mcp-server-box/"
    echo "   Please ensure Box credentials are configured."
    exit 1
fi

# Load AWS credentials if available
if [ -f "aws-credentials.sh" ]; then
    echo "✅ Loading AWS credentials..."
    source aws-credentials.sh
else
    echo "⚠️  AWS credentials file not found. SNS notifications may not work."
    echo "   You can still test contract processing without notifications."
fi

# Check environment variables
echo ""
echo "📋 Environment Check:"
echo "-------------------"

if grep -q "BOX_CLIENT_ID" mcp-server-box/.env 2>/dev/null; then
    echo "✅ Box credentials found in .env"
else
    echo "❌ Box credentials not found in .env"
    exit 1
fi

if [ -n "$AWS_SNS_TOPIC_ARN" ] || grep -q "AWS_SNS_TOPIC_ARN" mcp-server-box/.env 2>/dev/null; then
    echo "✅ SNS Topic ARN configured"
else
    echo "⚠️  SNS Topic ARN not set (notifications may not work)"
fi

if [ -n "$USER_EMAIL" ] || grep -q "USER_EMAIL" mcp-server-box/.env 2>/dev/null; then
    echo "✅ User email configured"
else
    echo "⚠️  User email not set (notifications may not work)"
fi

echo ""
echo "🚀 Starting Contract Processor..."
echo "   - Press Ctrl+C to stop"
echo "   - Check logs below for activity"
echo ""
echo "=============================================="
echo ""

# Run the contract processor
python3 contract_processor.py

