#!/bin/bash
# Run the contract processor with proper environment setup

cd "$(dirname "$0")"

# Activate virtual environment if using uv
if [ -d "mcp-server-box/.venv" ]; then
    source mcp-server-box/.venv/bin/activate
fi

# Load AWS credentials if needed
if [ -f "aws-credentials.sh" ]; then
    source aws-credentials.sh
fi

# Run the contract processor
python3 contract_processor.py

