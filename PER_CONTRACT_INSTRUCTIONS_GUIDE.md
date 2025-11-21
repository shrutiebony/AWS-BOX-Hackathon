# Per-Contract Instructions - Quick Guide

## 🎯 What Are Per-Contract Instructions?

Special instructions you provide for a **specific contract** that override or supplement your general interests file.

## 📝 How It Works

### Step 1: Upload Your Contract
```
contracts/
└── Employment_Offer_ABC_Company.pdf
```

### Step 2: Create Instructions File
Create a file with the **exact same name** + `.instructions`:

```
contracts/
├── Employment_Offer_ABC_Company.pdf
└── Employment_Offer_ABC_Company.pdf.instructions    ← Create this
```

### Step 3: Write Your Instructions
Just write what you want changed in plain English!

## ✅ File Naming Rules

**Rule:** Instructions filename = Contract filename + `.instructions`

### ✅ Correct Examples:
```
Contract: Employment_Offer.pdf
Instructions: Employment_Offer.pdf.instructions ✓

Contract: Service-Agreement-2025.docx
Instructions: Service-Agreement-2025.docx.instructions ✓

Contract: contract_v2_final.pdf
Instructions: contract_v2_final.pdf.instructions ✓
```

### ❌ Wrong Examples:
```
❌ Employment_Offer_instructions.txt        (missing .pdf)
❌ Employment_Offer.instructions            (missing .pdf)
❌ instructions_Employment_Offer.pdf       (wrong order)
❌ Employment_Offer_ABC_Company.instructions (missing .pdf)
```

## 📋 What to Include

### Essential Sections:

1. **CRITICAL ISSUES** - What must be changed
2. **NON-NEGOTIABLES** - What must stay the same
3. **ADDITIONAL REQUESTS** - Nice-to-have items
4. **NEGOTIATION PRIORITY** - What matters most

## 📝 Template

```
SPECIFIC CONCERNS FOR THIS CONTRACT:
=====================================

CRITICAL ISSUES:
1. [Section/Clause Name]
   - Current: [what it says now]
   - Need: [what you want]
   - Why: [your reason]

2. [Another issue]
   - Current: ...
   - Need: ...
   - Why: ...

NON-NEGOTIABLES (Keep exactly as-is):
- [Item 1]: [value] (must stay the same)
- [Item 2]: [value] (must stay the same)

ADDITIONAL REQUESTS:
- [Nice to have item 1]
- [Nice to have item 2]

NEGOTIATION PRIORITY:
1. High priority: [most important items]
2. Medium priority: [moderately important]
3. Low priority: [nice to have]
```

## 💡 Quick Examples

### Example 1: Simple & Quick
```
QUICK NOTES:
- Payment terms: Change from Net 60 to Net 30
- Termination: Add 30-day cancellation option
- Keep everything else the same
```

### Example 2: Detailed
```
CRITICAL ISSUES:
1. Non-compete (Section 8.3)
   - Current: "12 months, any industry, anywhere"
   - Need: "6 months, software development only, within 50 miles"
   - Why: Too broad, limits my career options

2. IP Ownership (Section 12.1)
   - Current: "All work belongs to company"
   - Need: "Work on company time = company; personal projects = mine"
   - Why: I have side projects to protect

NON-NEGOTIABLES:
- Salary: $120,000 (must stay)
- Start date: Jan 15, 2025 (must stay)
- Remote work option (must stay)
```

## 🔄 How It Works with General Interests

**Priority Order:**
1. **Per-contract instructions** ← Highest priority (used first)
2. **General interests file** ← Fills in gaps
3. **LLM default knowledge** ← For anything not specified

**Example:**
- General interests: "Non-competes: 6 months max"
- This contract instructions: "Non-compete: 3 months only"
- **Result:** System uses 3 months (per-contract wins)

## 🎯 When to Use Per-Contract Instructions

### ✅ Use When:
- Contract has unique terms needing special attention
- You want to override general preferences for this case
- Contract has sections your general interests don't cover
- You have specific negotiation priorities
- Contract is complex and needs detailed guidance

### ❌ Don't Need When:
- Your general interests file covers everything
- Contract is straightforward and standard
- You're happy with default preferences

## 🚀 Quick Start

1. **Upload contract** → `contracts/MyContract.pdf`
2. **Create instructions** → `contracts/MyContract.pdf.instructions`
3. **Write your concerns** in plain English
4. **Save** - System processes automatically!

## 📚 Full Examples

See `CONTRACT_PROTECTION_SYSTEM.md` for complete examples including:
- Employment contracts
- Service agreements
- Lease agreements
- And more!

---

**That's it!** Just create a file with the same name + `.instructions` and write what you want changed.

