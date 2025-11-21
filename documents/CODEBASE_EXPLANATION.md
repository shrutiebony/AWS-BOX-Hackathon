# 📖 Codebase Explanation - Simple Flow

## 🎯 What This Application Does (In One Sentence)

**It watches a Box folder for new contracts, uses AI to analyze them, and creates protected versions that favor your interests.**

---

## 🚀 Startup Flow (When You Run `contract_processor.py`)

### Step 1: `main()` Function Starts
```python
# Line 700-726 in contract_processor.py
async def main():
    processor = ContractProcessor()  # Create the main processor
    await processor.initialize()     # Set up everything
    await processor.process_new_contracts()  # Process any existing contracts
    await processor.check_all_contracts_for_action_items()  # Check for deadlines
    await processor.run_continuous_monitoring()  # Start the loop
```

**What happens:**
1. Creates a `ContractProcessor` object (the brain of the system)
2. Initializes Box connection and creates folders
3. Processes any contracts already in the folder
4. Starts an infinite loop that runs forever

---

## 🔄 Main Loop (Runs Forever)

### The Continuous Monitoring Loop
```python
# Line 668-696 in contract_processor.py
while True:
    await process_new_contracts()      # Check for new contracts (every 3 seconds)
    if time_for_action_check:         # Every hour
        await check_all_contracts_for_action_items()
    await asyncio.sleep(3)            # Wait 3 seconds, then repeat
```

**What happens:**
- Every 3 seconds: Check if new contracts were uploaded
- Every hour: Check all contracts for urgent deadlines
- Repeat forever

---

## 📄 Contract Processing Flow (When New Contract Detected)

### Step 1: Detect New Contract
```python
# Line 215-253 in contract_processor.py
async def process_new_contracts():
    items = await box_service.list_folder_items()  # Get all files in folder
    for item in items:
        if item not in processed_contracts:  # If we haven't seen it before
            contracts_to_process.append(item)  # Add to list
```

**What happens:**
- Lists all files in `Smart_Contracts` folder
- Compares with `processed_contracts` set (memory of what we've done)
- If new file found → add to processing queue

---

### Step 2: Process Each Contract
```python
# Line 322-376 in contract_processor.py
async def process_contract():
    # 1. Read the contract text from Box
    contract_text = await box_service.read_file(contract_file_id)
    
    # 2. Figure out what type of contract it is
    contract_category = await classify_contract(contract_file_id, contract_text)
    # Uses AWS Bedrock to analyze and say "This is an Employment Contract"
    
    # 3. Get your preferences
    user_interests = await get_user_interests()
    # Reads MY_INTERESTS.txt from Box
    
    # 4. Create output folder
    mirror_folder = await box_service.find_or_create_folder(category_folder, "{contract}_mirror")
    
    # 5. Generate 3 output files
    await _generate_protected_contract(...)
```

**What happens:**
1. **Read Contract**: Downloads contract text from Box
2. **Classify**: Asks AI "What type of contract is this?" → Gets answer like "Employment Contract"
3. **Load Interests**: Reads your `MY_INTERESTS.txt` file
4. **Create Folder**: Makes a folder like `test_contract_mirror` inside the category folder
5. **Generate Files**: Creates 3 protected versions

---

### Step 3: Generate Protected Contract Files

```python
# Line 378-463 in contract_processor.py
async def _generate_protected_contract():
    # Build a big prompt with:
    # - Contract text
    # - Your interests
    # - Instructions for AI
    
    prompt = _build_analysis_prompt(contract_text, user_interests, ...)
    
    # File 1: Mirror Contract
    mirror_contract = await box_service.ask_ai_about_file(
        contract_file_id, 
        "Generate a protected version of this contract..."
    )
    
    # File 2: Redline Comparison
    redline_comparison = await box_service.ask_ai_about_file(
        contract_file_id,
        "Create a comparison showing changes..."
    )
    
    # File 3: Negotiation Guide
    negotiation_guide = await box_service.ask_ai_about_file(
        contract_file_id,
        "Create a guide for negotiations..."
    )
    
    # Upload all 3 files
    await _upload_output_files(mirror_folder_id, ...)
```

**What happens:**
1. **Build Prompt**: Combines contract text + your interests into instructions for AI
2. **Call AI 3 Times**: 
   - First call: "Rewrite this contract to protect my interests"
   - Second call: "Show me what changed (redline)"
   - Third call: "Give me a negotiation guide"
3. **Upload Files**: Saves all 3 as `.txt` files in the mirror folder

---

## 🤖 AI Analysis Flow (How Bedrock is Used)

### When `ask_ai_about_file()` is Called

```python
# Line 307-356 in box_contract_service.py
async def ask_ai_about_file(file_id, prompt):
    # 1. Read the file from Box first
    contract_text = await read_file(file_id)
    
    # 2. Create Bedrock service
    bedrock = BedrockService()
    
    # 3. Send to AWS Bedrock
    result = await bedrock.analyze_contract(
        contract_text=contract_text,
        prompt=prompt
    )
    
    return result  # Return AI's response
```

**What happens:**
1. **Read File**: Gets contract text from Box
2. **Create Bedrock Client**: Connects to AWS Bedrock
3. **Send Request**: Sends contract + prompt to Claude AI
4. **Get Response**: Claude analyzes and returns text
5. **Return**: Passes the AI response back

---

### Inside Bedrock Service

```python
# Line 44-99 in bedrock_service.py
def invoke_model(prompt):
    # Prepare request for Claude
    body = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096
    }
    
    # Call AWS Bedrock API
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps(body)
    )
    
    # Extract text from response
    text = response['content'][0]['text']
    return text
```

**What happens:**
1. **Format Request**: Puts prompt in the format Claude expects
2. **Call AWS**: Sends HTTP request to AWS Bedrock API
3. **Parse Response**: Extracts the text from Claude's response
4. **Return**: Returns the generated text

---

## 📧 Action Item Detection Flow (Deadline Alerts)

### How It Works

```python
# Line 255-320 in contract_processor.py
async def check_all_contracts_for_action_items():
    # Get all contracts
    contracts = await list_all_contracts()
    
    for contract in contracts:
        # Analyze each contract for deadlines
        action_items = await action_detector.analyze_contract_for_action_items(...)
        
        # Find urgent ones
        urgent_items = action_detector.filter_urgent_items(action_items)
        
        if urgent_items:
            # Send email notification
            action_detector.send_notification(urgent_items)
```

**What happens:**
1. **Get All Contracts**: Lists all contracts in the folder
2. **Analyze Each**: Uses AI to find deadlines and action items
3. **Filter Urgent**: Keeps only items due soon (within 5-14 days)
4. **Send Email**: If urgent items found → sends email via AWS SNS

---

### Action Item Detection Details

```python
# Line 49-112 in action_item_detector.py
async def analyze_contract_for_action_items():
    # Build prompt asking AI to find deadlines
    prompt = "Find expiration dates, payment due dates, audit deadlines..."
    
    # Call AI
    response = await box_service.ask_ai_about_file(contract_file_id, prompt)
    
    # Parse AI response into structured data
    action_items = _parse_action_items(response)
    
    return action_items
```

**What happens:**
1. **Ask AI**: "Find all deadlines in this contract"
2. **AI Responds**: Returns list like "Expiration: Dec 31, Payment: Jan 15"
3. **Parse**: Converts AI text into structured data (dictionaries)
4. **Check Urgency**: Calculates days until due, marks as urgent if < 10 days

---

## 📁 Box Service (How We Talk to Box)

### Main Functions

```python
# box_contract_service.py

class BoxContractService:
    # 1. Connect to Box
    async def initialize():
        # Sets up OAuth authentication
        # Creates Box client
    
    # 2. Read files
    async def read_file(file_id):
        # Downloads file from Box
        # Extracts text content
        # Returns as string
    
    # 3. List files
    async def list_folder_items(folder_id):
        # Gets list of all files/folders
        # Returns list of dictionaries
    
    # 4. Create folders
    async def find_or_create_folder(parent_id, folder_name):
        # Checks if folder exists
        # If not, creates it
        # Returns folder ID
    
    # 5. Upload files
    async def upload_text_file(folder_id, filename, content):
        # Converts text to bytes
        # Uploads to Box
        # Returns file ID
    
    # 6. Use AI
    async def ask_ai_about_file(file_id, prompt):
        # Reads file from Box
        # Sends to Bedrock
        # Returns AI response
```

**What happens:**
- This class is the "translator" between our code and Box API
- Every Box operation goes through this service
- Handles authentication, errors, and data conversion

---

## 🔑 Key Data Structures

### `processed_contracts` Set
```python
self.processed_contracts = set()  # Memory of what we've done
# Example: {"test_contract_123_2052467931905", "another_contract_456_2052473786192"}
```
**Purpose**: Prevents processing the same contract twice

### `category_folder_ids` Dictionary
```python
self.category_folder_ids = {
    "Employment Contract": "352188171927",
    "Service Contract": "352186168439",
    ...
}
```
**Purpose**: Stores Box folder IDs so we know where to save files

### Action Items List
```python
action_items = [
    {
        "type": "expiration",
        "description": "Contract expires on Dec 31",
        "due_date": "2025-12-31",
        "days_until_due": 5,
        "priority": "high",
        "action_required": "Review and decide on renewal"
    },
    ...
]
```
**Purpose**: Structured data about deadlines and actions needed

---

## 🔄 Complete Flow Diagram (Code Level)

```
START
  │
  ├─> main()
  │   ├─> Create ContractProcessor
  │   ├─> initialize()
  │   │   ├─> Initialize BoxService (OAuth)
  │   │   ├─> Create folders in Box
  │   │   └─> Store folder IDs
  │   │
  │   ├─> process_new_contracts()
  │   │   ├─> list_folder_items() → Get all files
  │   │   ├─> Filter new files (not in processed_contracts)
  │   │   └─> For each new file:
  │   │       └─> process_contract()
  │   │
  │   └─> run_continuous_monitoring()
  │       └─> while True:
  │           ├─> process_new_contracts() [every 3s]
  │           └─> check_all_contracts_for_action_items() [every hour]
  │
  └─> process_contract()
      ├─> read_file() → Get contract text from Box
      ├─> classify_contract()
      │   └─> ask_ai_about_file() → Bedrock → "Employment Contract"
      │
      ├─> get_user_interests() → Read MY_INTERESTS.txt from Box
      ├─> find_or_create_folder() → Create {contract}_mirror folder
      │
      └─> _generate_protected_contract()
          ├─> ask_ai_about_file() → Bedrock → Mirror contract text
          ├─> ask_ai_about_file() → Bedrock → Redline comparison text
          ├─> ask_ai_about_file() → Bedrock → Negotiation guide text
          └─> upload_text_file() × 3 → Save all files to Box
```

---

## 🧩 Component Responsibilities

### `ContractProcessor` (contract_processor.py)
- **Job**: Orchestrates everything
- **Does**: Monitors, processes, coordinates
- **Uses**: BoxService, ActionItemDetector

### `BoxContractService` (box_contract_service.py)
- **Job**: Talks to Box API
- **Does**: Read/write files, create folders, authenticate
- **Uses**: Box SDK, BedrockService

### `BedrockService` (bedrock_service.py)
- **Job**: Talks to AWS Bedrock
- **Does**: Sends prompts to Claude AI, gets responses
- **Uses**: boto3 (AWS SDK)

### `ActionItemDetector` (action_item_detector.py)
- **Job**: Finds deadlines and sends alerts
- **Does**: Analyzes contracts, filters urgent items, sends emails
- **Uses**: BoxService, AWS SNS

---

## 💡 Simple Analogy

Think of it like a **smart assistant**:

1. **Watches a mailbox** (monitors Box folder every 3 seconds)
2. **Opens new mail** (reads contract files)
3. **Asks an expert** (sends to AI for analysis)
4. **Takes notes** (reads your preferences)
5. **Creates a better version** (generates protected contract)
6. **Files it away** (saves to organized folders)
7. **Reminds you of deadlines** (sends email alerts)

---

## 🔍 Key Code Patterns

### 1. Async/Await Pattern
```python
async def function_name():
    result = await other_function()  # Wait for this to finish
    return result
```
**Why**: Box API and AI calls take time, so we wait without blocking

### 2. Try/Except Error Handling
```python
try:
    result = await risky_operation()
except Exception as e:
    logger.error(f"Error: {e}")
    # Continue anyway, don't crash
```
**Why**: If one contract fails, others can still be processed

### 3. Set for Tracking
```python
processed_contracts.add(contract_key)  # Remember we did this
if contract_key not in processed_contracts:  # Check if new
```
**Why**: Fast lookup to avoid duplicate work

### 4. Dictionary for Configuration
```python
category_folder_ids[category] = folder_id  # Store mapping
folder_id = category_folder_ids.get(category)  # Lookup
```
**Why**: Easy way to store and retrieve folder IDs by category

---

## 📊 Data Flow Example

**When you upload `EMPLOYMENT_AGREEMENT.txt`:**

```
1. File uploaded to Box → Smart_Contracts/EMPLOYMENT_AGREEMENT.txt
   │
2. Processor detects (3 seconds later)
   │
3. Reads file → Gets text content
   │
4. Sends to Bedrock: "What type of contract?"
   │
5. Bedrock responds: "Employment Contract"
   │
6. Reads MY_INTERESTS.txt from Box
   │
7. Creates folder: protect_your_interests/Employment Contract/EMPLOYMENT_AGREEMENT_mirror
   │
8. Sends to Bedrock 3 times:
   ├─> "Generate protected version" → Gets mirror contract text
   ├─> "Generate redline comparison" → Gets comparison text
   └─> "Generate negotiation guide" → Gets guide text
   │
9. Uploads 3 files:
   ├─> 1_mirror_contract_protecting_YOUR_interests.txt
   ├─> 2_clean_redline_comparison.txt
   └─> 3_negotiation_guide.txt
   │
10. Marks as processed → Won't process again
```

---

## 🎯 Summary

**The code does 4 main things:**

1. **Watches** → Checks Box folder every 3 seconds
2. **Reads** → Downloads contract text from Box
3. **Thinks** → Uses AI to analyze and generate content
4. **Saves** → Uploads results back to Box

**All wrapped in an infinite loop that runs forever!**

