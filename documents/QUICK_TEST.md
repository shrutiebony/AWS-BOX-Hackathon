# 🚀 Quick Local Test - 3 Steps

## Step 1: Start the Processor

```bash
cd /Users/sameer/Documents/hackathon/AWS-BOX
./test_local.sh
```

**What you'll see:**
- Environment checks
- "Starting continuous monitoring"
- Logs every 60 seconds checking for contracts

---

## Step 2: Upload a Test Contract

1. **Go to your Box account** (box.com)
2. **Look for the `contracts/` folder** (created automatically)
3. **Upload any PDF or DOCX file** (can be a dummy contract)

**Wait 60 seconds** - The processor checks every minute!

---

## Step 3: Check Results

1. **In Box, go to `protect_your_interests/` folder**
2. **You should see:** `[your_file_name]_mirror/` folder
3. **Inside, you'll find 3 files:**
   - `1_mirror_contract_protecting_YOUR_interests.docx`
   - `2_clean_redline_comparison.pdf`
   - `3_negotiation_guide.docx`

---

## ✅ Success Indicators

**In Terminal:**
```
INFO - Processing contract: test.pdf
INFO - Contract classified as: Employment Contract
INFO - ✅ Successfully processed: test.pdf
```

**In Box:**
- New folder in `protect_your_interests/`
- 3 output files generated

---

## 🛑 To Stop

Press `Ctrl+C` in the terminal

---

## 📖 Full Testing Guide

See `TESTING_GUIDE.md` for detailed testing scenarios!

