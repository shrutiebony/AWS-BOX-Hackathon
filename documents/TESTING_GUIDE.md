# Local Testing Guide

## 🎯 Quick Start

### Step 1: Run the Test Script

```bash
cd /Users/sameer/Documents/hackathon/AWS-BOX
./test_local.sh
```

This will:
- ✅ Activate the virtual environment
- ✅ Check environment configuration
- ✅ Start the contract processor
- ✅ Monitor Box for new contracts

---

## 📝 Testing Steps

### Test 1: Basic Contract Processing

**Goal:** Verify the system can detect and process a new contract.

1. **Start the processor:**
   ```bash
   ./test_local.sh
   ```

2. **Upload a test contract to Box:**
   - Go to your Box account
   - Navigate to the `contracts/` folder (will be created automatically)
   - Upload a PDF or DOCX contract file
   - Example: `test_contract.pdf`

3. **Watch the terminal:**
   - You should see logs like:
     ```
     INFO - Detected new contract: test_contract.pdf
     INFO - Processing contract: test_contract.pdf
     INFO - Contract classified as: Employment Contract
     INFO - ✅ Successfully processed: test_contract.pdf
     ```

4. **Check Box output:**
   - Go to `protect_your_interests/` folder in Box
   - You should see a new folder: `test_contract_mirror/`
   - Inside, you should find 3 files:
     - `1_mirror_contract_protecting_YOUR_interests.docx`
     - `2_clean_redline_comparison.pdf`
     - `3_negotiation_guide.docx`

**Expected Result:** ✅ Contract processed and 3 output files created

---

### Test 2: User Interests File

**Goal:** Verify the system uses your preferences.

1. **Create interests file in Box:**
   - Go to `my_interests/` folder in Box
   - Create a file: `MY_INTERESTS.txt`
   - Add your preferences:
     ```
     MY CONTRACT INTERESTS
     ====================
     
     EMPLOYMENT:
     - Non-competes: Max 6 months, specific to role
     - IP: Company owns work on company time; I own personal projects
     - Severance: At least 2 weeks per year
     ```

2. **Upload a new contract:**
   - Upload another contract to `contracts/` folder
   - Watch the processor logs

3. **Check the output:**
   - Review the generated `1_mirror_contract_protecting_YOUR_interests.docx`
   - Verify it reflects your preferences

**Expected Result:** ✅ Contract modified according to your interests

---

### Test 3: Per-Contract Instructions

**Goal:** Test contract-specific instructions.

1. **Upload a contract:**
   - Upload `employment_contract.pdf` to `contracts/` folder

2. **Create instructions file:**
   - In the same `contracts/` folder
   - Create: `employment_contract.pdf.instructions`
   - Add specific instructions:
     ```
     CRITICAL ISSUES:
     1. Non-compete clause
        - Current: "12 months, any industry"
        - Need: "6 months, software development only"
     
     NON-NEGOTIABLES:
     - Salary: $120,000 (must stay)
     ```

3. **Check the output:**
   - Review the generated contract
   - Verify it follows the specific instructions

**Expected Result:** ✅ Contract modified according to per-contract instructions

---

### Test 4: Action Item Detection (Email Notifications)

**Goal:** Test deadline detection and email notifications.

**Prerequisites:**
- AWS credentials configured
- SNS topic ARN set
- Email subscribed to SNS topic

1. **Upload a contract with a deadline:**
   - Create or upload a contract with an expiration date within 10 days
   - Example: Contract expires on December 31, 2024 (if today is Dec 21)

2. **Wait for hourly check:**
   - The system checks for action items every hour
   - Or modify `action_item_check_interval` in code for faster testing

3. **Check your email:**
   - You should receive an email notification
   - Subject: "⚠️ Contract Action Items - X Urgent Item(s)"

**Expected Result:** ✅ Email notification received with action items

---

### Test 5: Continuous Monitoring

**Goal:** Verify the system keeps running and monitoring.

1. **Start the processor:**
   ```bash
   ./test_local.sh
   ```

2. **Let it run for a few minutes:**
   - You should see periodic logs:
     ```
     INFO - Checking for new contracts...
     INFO - No new contracts found
     ```

3. **Upload multiple contracts:**
   - Upload 2-3 contracts at different times
   - Verify each is processed

4. **Check processing order:**
   - Contracts should be processed in order of upload
   - Each should get its own output folder

**Expected Result:** ✅ System continuously monitors and processes new contracts

---

## 🔍 What to Look For

### ✅ Success Indicators

- **Logs show:**
  - "Box service initialized successfully"
  - "Starting continuous monitoring"
  - "Processing contract: [filename]"
  - "✅ Successfully processed"

- **Box folders created:**
  - `contracts/` - Input folder
  - `protect_your_interests/` - Output folder
  - `my_interests/` - Preferences folder

- **Output files generated:**
  - 3 files per contract in `protect_your_interests/[contract_name]_mirror/`

### ❌ Common Issues

1. **Authentication Error:**
   ```
   Error: BOX_CLIENT_ID and BOX_CLIENT_SECRET must be set
   ```
   **Fix:** Check `mcp-server-box/.env` file has correct credentials

2. **No contracts detected:**
   ```
   No new contracts found
   ```
   **Fix:** Make sure contracts are in the `contracts/` folder in Box

3. **Import errors:**
   ```
   ModuleNotFoundError: No module named 'box_ai_agents_toolkit'
   ```
   **Fix:** Activate virtual environment: `source venv/bin/activate`

4. **SNS notification errors:**
   ```
   AWS SNS error: ...
   ```
   **Fix:** Check AWS credentials and SNS topic ARN

---

## 🛠️ Manual Testing Commands

### Check if processor is running:
```bash
ps aux | grep contract_processor
```

### View recent logs:
```bash
# If running in terminal, logs appear in real-time
# Or check the terminal output
```

### Stop the processor:
```bash
# Press Ctrl+C in the terminal where it's running
```

### Test with a specific contract:
1. Upload contract to Box `contracts/` folder
2. Wait 60 seconds (check interval)
3. Check `protect_your_interests/` folder for output

---

## 📊 Testing Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Box credentials configured
- [ ] Processor starts without errors
- [ ] Folders created in Box
- [ ] Contract uploaded and detected
- [ ] Contract processed successfully
- [ ] 3 output files generated
- [ ] User interests file works (if created)
- [ ] Per-contract instructions work (if created)
- [ ] Action items detected (if contract has deadlines)
- [ ] Email notification received (if configured)

---

## 🎉 Next Steps

Once local testing is successful:

1. **Verify all features work:**
   - Contract processing
   - User interests
   - Action item detection
   - Email notifications

2. **Test edge cases:**
   - Large contracts
   - Multiple contracts
   - Contracts with no deadlines
   - Contracts with multiple deadlines

3. **Monitor AWS deployment:**
   - Check deployment status
   - Verify EC2 instance is running
   - Test production environment

---

## 💡 Tips

- **Faster testing:** Modify `check_interval` in code to check more frequently (e.g., 10 seconds)
- **Debug mode:** Add more logging or use Python debugger
- **Test files:** Keep a few test contracts ready for quick testing
- **Monitor Box:** Keep Box open in browser to see files appear in real-time

---

**Happy Testing! 🚀**

