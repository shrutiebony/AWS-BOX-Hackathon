# Contract Protection System - Implementation

## Overview

Automated contract analysis system that monitors Box for new contracts and generates protected versions with your interests in mind.

## Setup

1. **Install dependencies:**
   ```bash
   cd /Users/sameer/Documents/hackathon/AWS-BOX
   pip install -r requirements.txt
   # Or if using uv:
   uv pip install -r requirements.txt
   ```

2. **Configure Box credentials:**
   - Ensure `.env` file in `mcp-server-box/` has your Box credentials
   - Or set environment variables:
     ```bash
     export BOX_CLIENT_ID="your_client_id"
     export BOX_CLIENT_SECRET="your_client_secret"
     ```

3. **Authorize Box app (first time):**
   ```bash
   python -c "from box_ai_agents_toolkit import authorize_app; authorize_app()"
   ```

## Usage

### Run the Contract Processor

```bash
python contract_processor.py
```

The system will:
1. Create necessary folders in Box (`contracts/`, `protect_your_interests/`, `my_interests/`)
2. Monitor the `contracts/` folder for new files
3. Process each contract and generate 3 output files
4. Save results to `protect_your_interests/{contract_name}_mirror/`

### Folder Structure in Box

```
Box Root/
├── contracts/                    # Upload contracts here
│   ├── Employment_Offer.pdf
│   └── Employment_Offer.pdf.instructions  (optional)
│
├── protect_your_interests/       # Generated outputs
│   └── Employment_Offer_mirror/
│       ├── 1_mirror_contract_protecting_YOUR_interests.docx
│       ├── 2_clean_redline_comparison.pdf
│       └── 3_negotiation_guide.docx
│
└── my_interests/                 # Your preferences
    └── MY_INTERESTS.txt
```

## How It Works

1. **Upload Contract**: Drop a contract PDF/DOCX in `contracts/` folder in Box
2. **System Detects**: Automatically detects new files (checks every 60 seconds)
3. **Loads Interests**: Reads `my_interests/MY_INTERESTS.txt` from Box
4. **Checks Instructions**: Looks for `{contract_name}.instructions` file (optional)
5. **Analyzes**: Uses Box AI to analyze contract against your interests
6. **Generates**: Creates 3 output files using Box AI
7. **Saves**: Uploads results to `protect_your_interests/{contract_name}_mirror/`

## Files

- `contract_processor.py` - Main processing logic
- `box_contract_service.py` - Box API interactions
- `requirements.txt` - Python dependencies

## Configuration

### User Interests File

Create `MY_INTERESTS.txt` in Box folder `my_interests/`:

```
MY CONTRACT INTERESTS
====================

EMPLOYMENT:
- Non-competes: Max 6 months, specific to role
- IP: Company owns work on company time; I own personal projects
- Severance: At least 2 weeks per year

SERVICE AGREEMENTS:
- Payment: Net 15-30, not Net 60+
- Termination: Early exit with refunds
```

### Per-Contract Instructions (Optional)

For specific contracts, create `{contract_name}.instructions` in `contracts/` folder:

```
CRITICAL ISSUES:
1. Non-compete clause
   - Current: "12 months, any industry"
   - Need: "6 months, software development only"
   - Why: Too broad

NON-NEGOTIABLES:
- Salary: $120,000 (must stay)
```

## Monitoring

The system runs continuously and checks for new contracts every 60 seconds. To stop, press `Ctrl+C`.

## Troubleshooting

- **Authentication errors**: Run authorization again
- **File not found**: Ensure folders exist in Box
- **AI errors**: Check Box AI is enabled for your account
- **Import errors**: Install dependencies: `pip install -r requirements.txt`

