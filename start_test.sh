#!/bin/bash
cd /Users/sameer/Documents/hackathon/AWS-BOX
source venv/bin/activate
[ -f aws-credentials.sh ] && source aws-credentials.sh
python3 contract_processor.py
