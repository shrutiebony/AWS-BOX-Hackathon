# Contract Protection System - User Guide

## 🎯 System Overview

**What it does:** Automatically analyzes contracts you upload and creates "mirror" versions that protect your interests while keeping non-negotiables intact.

## 📁 Folder Structure

```
AWS-BOX/
├── contracts/                          # ← You upload contracts here
│   ├── Employment_Offer_ABC_Company.pdf
│   ├── Service_Agreement_XYZ.pdf
│   └── Lease_Agreement_123.pdf
│
├── protect_your_interests/             # ← System creates mirror folders here
│   ├── Employment_Offer_ABC_Company_mirror/
│   │   ├── 1_mirror_contract_protecting_YOUR_interests.docx
│   │   ├── 2_clean_redline_comparison.pdf
│   │   └── 3_negotiation_guide.docx
│   └── Service_Agreement_XYZ_mirror/
│       └── ...
│
└── my_interests/                       # ← You define your interests here
    └── MY_INTERESTS.txt                # (or .md, .json)
```

---

## 🔑 How You Define Your Interests

### Option 1: One-Time "My Interests" File (Recommended)

**Location:** `/my_interests/MY_INTERESTS.txt` (or `.md`)

**Format:** Plain text, natural language - just write what matters to you!

#### Example: `MY_INTERESTS.txt`

```
MY CONTRACT INTERESTS & PREFERENCES
====================================

GENERAL PRINCIPLES:
- I prefer shorter contract terms (1-2 years max) with renewal options
- I want clear termination clauses that favor me
- I need flexibility to exit contracts with reasonable notice
- I prefer fixed pricing over variable/additional fees
- I want to retain ownership of my work/products when possible

EMPLOYMENT CONTRACTS:
- Non-compete clauses should be limited to 6 months max and specific geographic areas
- I want to retain rights to work on personal projects outside work hours
- Severance should be at least 2 weeks per year of service
- I prefer unlimited PTO or at least 20+ days
- I want clear ownership rights - company owns work done on company time, I own personal projects

SERVICE AGREEMENTS:
- Payment terms should be Net 15 or Net 30, not Net 60+
- I want early termination options with prorated refunds
- Liability caps should be reasonable (not unlimited)
- I prefer monthly billing over annual prepayment
- I want data ownership and portability rights

LEASE AGREEMENTS:
- Security deposits should not exceed 1 month's rent
- I want early termination option with 30 days notice
- Maintenance responsibilities should be clearly defined
- I prefer month-to-month after initial term
- Pet policies should be reasonable (not blanket bans)

INTELLECTUAL PROPERTY:
- I want to retain rights to pre-existing IP
- Work-for-hire should be clearly defined and limited
- I prefer joint ownership over exclusive assignment when possible

NEGOTIATION STYLE:
- I'm willing to compromise on payment terms if other protections are strong
- I prioritize flexibility over long-term commitments
- I value clear communication and dispute resolution processes
```

#### Alternative: Structured Format (JSON)

**File:** `/my_interests/MY_INTERESTS.json`

```json
{
  "general_principles": [
    "Prefer shorter contract terms (1-2 years) with renewal options",
    "Clear termination clauses that favor me",
    "Flexibility to exit with reasonable notice",
    "Fixed pricing over variable fees"
  ],
  "employment_contracts": {
    "non_compete": {
      "max_duration": "6 months",
      "geographic_scope": "specific areas only",
      "preference": "limited and reasonable"
    },
    "ip_ownership": {
      "company_time": "company owns",
      "personal_time": "I own",
      "pre_existing": "I retain rights"
    },
    "severance": {
      "minimum": "2 weeks per year of service"
    },
    "pto": {
      "preference": "unlimited or 20+ days"
    }
  },
  "service_agreements": {
    "payment_terms": "Net 15 or Net 30 preferred",
    "termination": "Early exit with prorated refunds",
    "liability": "Reasonable caps, not unlimited",
    "billing": "Monthly preferred over annual prepayment"
  },
  "negotiation_priorities": [
    "Flexibility over long-term commitments",
    "Clear communication and dispute resolution",
    "Reasonable protections over strict terms"
  ]
}
```

---

### Option 2: Per-Contract Specific Instructions

**When to use:** 
- You have specific concerns for a particular contract
- This contract has unique terms that need special attention
- You want to override or supplement your general interests for this one contract

**How it works:** Create a file with the same name as the contract (plus `.instructions`):

```
contracts/
├── Employment_Offer_ABC_Company.pdf
└── Employment_Offer_ABC_Company.pdf.instructions    ← Your specific notes
```

**Important:** The instructions file must have the exact same name as the contract file, plus `.instructions`

#### Example 1: Employment Contract

**File:** `Employment_Offer_ABC_Company.pdf.instructions`

```
SPECIFIC CONCERNS FOR THIS CONTRACT:
=====================================

CRITICAL ISSUES:
1. Non-compete clause (Section 8.3)
   - Current: "12 months, any industry, anywhere in the US"
   - Need: "6 months, software development only, within 50 miles of office"
   - Why: Too broad, limits my career options unfairly

2. IP Ownership (Section 12.1)
   - Current: "All work belongs to company, including personal projects"
   - Need: "Work on company time belongs to company; personal projects remain mine"
   - Why: I have side projects I want to keep

3. Severance (Section 9.2)
   - Current: "1 week per year of service"
   - Need: "At least 4 weeks minimum, or 2 weeks per year (whichever is higher)"
   - Why: 1 week is below industry standard

4. Termination Notice (Section 9.1)
   - Current: "90 days notice required from employee"
   - Need: "30 days notice, either party"
   - Why: 90 days is unusually long and restrictive

NON-NEGOTIABLES (Keep exactly as-is):
- Salary: $120,000 (must stay the same)
- Start date: January 15, 2025 (must stay the same)
- Location: Remote work option (must stay the same)
- Stock options: 1,000 shares (must stay the same)

ADDITIONAL REQUESTS:
- Add clause about equipment reimbursement (laptop, monitor, etc.)
- Clarify that company will cover professional development courses
- Specify that unused PTO can be carried over or paid out

NEGOTIATION PRIORITY:
1. High priority: Non-compete and IP ownership (deal-breakers)
2. Medium priority: Severance and termination notice
3. Low priority: Equipment and professional development (nice to have)
```

#### Example 2: Service Agreement

**File:** `Service_Agreement_XYZ_Corp.pdf.instructions`

```
SPECIFIC CONCERNS FOR THIS SERVICE AGREEMENT:
=============================================

PAYMENT TERMS:
- Current: Net 60 payment terms
- Need: Net 30 maximum
- Why: Net 60 is too long, affects cash flow

TERMINATION:
- Current: No early termination, must complete full term
- Need: 30-day cancellation option with prorated refund
- Why: Need flexibility if service doesn't meet expectations

LIABILITY:
- Current: Unlimited liability for any damages
- Need: Cap liability at contract value (or reasonable amount)
- Why: Unlimited liability is unreasonable and risky

AUTO-RENEWAL:
- Current: Auto-renews for another year unless cancelled 90 days before
- Need: Month-to-month after initial term, 30-day notice to cancel
- Why: Don't want to be locked in for another full year

DATA OWNERSHIP:
- Current: All data belongs to service provider
- Need: I retain ownership, provider gets usage rights during service period
- Why: My data should remain mine

NON-NEGOTIABLES:
- Service fee: $500/month (must stay the same)
- Service start date: March 1, 2025 (must stay the same)
- Core features: Must include all listed features (must stay the same)
```

#### Example 3: Lease Agreement

**File:** `Apartment_Lease_123_Main_St.pdf.instructions`

```
SPECIFIC CONCERNS FOR THIS LEASE:
=================================

SECURITY DEPOSIT:
- Current: 2 months rent ($4,000)
- Need: 1 month maximum ($2,000)
- Why: 2 months is excessive, 1 month is standard

EARLY TERMINATION:
- Current: No early termination, must pay full lease term
- Need: 30-day notice option with 1 month penalty
- Why: Need flexibility if job situation changes

PET POLICY:
- Current: No pets allowed
- Need: Allow one small pet (under 25 lbs) with pet deposit
- Why: I have a small dog that's well-behaved

MAINTENANCE:
- Current: Tenant responsible for all repairs
- Need: Landlord responsible for major repairs (HVAC, plumbing, structural)
- Why: Standard lease terms should apply

RENEWAL:
- Current: Auto-renews for another year
- Need: Month-to-month after initial term
- Why: Want flexibility after first year

NON-NEGOTIABLES:
- Monthly rent: $2,000 (must stay the same)
- Lease start: February 1, 2025 (must stay the same)
- Parking: 1 space included (must stay the same)
```

#### Example 4: Simple/Quick Instructions

**File:** `Simple_Contract.pdf.instructions`

```
QUICK NOTES:
- Payment terms: Change from Net 60 to Net 30
- Termination: Add 30-day cancellation option
- Keep everything else the same
```

#### File Naming Rules

**Correct naming:**
```
✅ Employment_Offer_ABC.pdf
✅ Employment_Offer_ABC.pdf.instructions

✅ Service-Agreement-2025.docx
✅ Service-Agreement-2025.docx.instructions

✅ contract_v2_final.pdf
✅ contract_v2_final.pdf.instructions
```

**Incorrect naming:**
```
❌ Employment_Offer_ABC_instructions.txt  (wrong - missing .pdf)
❌ Employment_Offer_ABC.instructions        (wrong - missing .pdf)
❌ instructions_Employment_Offer_ABC.pdf  (wrong - wrong order)
```

**Key rule:** Instructions file name = Contract file name + `.instructions`

#### How Per-Contract Instructions Work with General Interests

**Priority order:**
1. **Per-contract instructions** (highest priority) - Used first
2. **General interests file** - Used to fill in gaps
3. **Default LLM knowledge** - Used for anything not specified

**Example:**
- Your general interests say: "Non-competes: 6 months max"
- This contract's instructions say: "Non-compete: 3 months only for this role"
- **Result:** System uses 3 months (per-contract overrides general)

**If per-contract doesn't mention something:**
- System falls back to your general interests
- If general interests don't cover it, uses LLM's best judgment

#### When to Use Per-Contract Instructions

**Use per-contract instructions when:**
- ✅ Contract has unique terms that need special attention
- ✅ You want to override your general preferences for this specific case
- ✅ Contract has sections your general interests don't cover
- ✅ You have specific negotiation priorities for this contract
- ✅ Contract is complex and needs detailed guidance

**Don't need per-contract instructions when:**
- ❌ Your general interests file covers everything
- ❌ Contract is straightforward and standard
- ❌ You're happy applying your default preferences

---

## 📥 Input Flow (What You Do)

### Step 1: Set Up Your Interests (One Time)

1. Create folder: `my_interests/`
2. Create file: `MY_INTERESTS.txt`
3. Write your preferences in plain English
4. Save it

**That's it!** The system will use this for all future contracts.

### Step 2: Upload a Contract

1. Take any contract (PDF, Word, etc.)
2. Drop it in: `/contracts/`
3. **That's it!** The system automatically:
   - Detects the new file
   - Reads your interests from `MY_INTERESTS.txt`
   - Analyzes the contract
   - Creates the mirror folder

---

## 📤 Output Flow (What You Get)

### Automatic Output Structure

For every contract you upload, you get:

```
protect_your_interests/
└── {ContractName}_mirror/
    ├── 1_mirror_contract_protecting_YOUR_interests.docx
    ├── 2_clean_redline_comparison.pdf
    └── 3_negotiation_guide.docx
```

### File 1: `1_mirror_contract_protecting_YOUR_interests.docx`

**What it is:** The rewritten contract with your interests protected.

**What it contains:**
- Same structure as original
- Key terms modified to protect your interests
- Non-negotiables kept exactly as-is
- Clear, professional language

**Example changes:**
- Non-compete: "12 months, any industry" → "6 months, software development only"
- Termination: "90 days notice required" → "30 days notice, either party"
- IP: "All work belongs to company" → "Work on company time belongs to company; personal projects remain mine"

### File 2: `2_clean_redline_comparison.pdf`

**What it is:** Visual comparison showing every change.

**What it contains:**
- Original text (strikethrough)
- New text (highlighted/underlined)
- Side-by-side or inline comparison
- Easy to read format

**Visual example:**
```
ORIGINAL:                          NEW:
Term: 24 months                   Term: 12 months with automatic
                                   renewal option
                                   
Non-compete: 12 months,           Non-compete: 6 months, limited
any industry                      to software development in
                                  [specific geographic area]
```

### File 3: `3_negotiation_guide.docx`

**What it is:** Your negotiation playbook.

**What it contains:**
- Summary of all changes made
- Why each change protects your interests
- Which items are negotiable vs non-negotiable
- How to present each change to the other party
- Talking points and rationale

**Example structure:**

```
NEGOTIATION GUIDE: Employment_Offer_ABC_Company
===============================================

CHANGES MADE:
-------------

1. NON-COMPETE CLAUSE
   Original: 12 months, any industry, anywhere
   Changed to: 6 months, software development only, within 50 miles
   
   Why: Protects your ability to work in other industries and locations
   
   How to negotiate:
   - "I'm happy to protect your legitimate business interests, but 
     this scope is too broad. A 6-month restriction in my specific 
     field and local area is industry standard."
   - Reference: Most courts find overly broad non-competes unenforceable
   
   Negotiability: HIGH - This is very negotiable

2. TERMINATION NOTICE
   Original: 90 days notice required
   Changed to: 30 days notice, either party
   
   Why: 90 days is unusually long and limits your flexibility
   
   How to negotiate:
   - "30 days is standard in the industry and provides reasonable 
     transition time for both parties."
   - Offer: "I'm open to 45 days if that works better for you"
   
   Negotiability: MEDIUM - Reasonable to negotiate

3. IP OWNERSHIP
   Original: All work belongs to company
   Changed to: Work on company time belongs to company; personal 
               projects remain mine
   
   Why: Protects your right to work on personal projects
   
   How to negotiate:
   - "I want to ensure I can continue working on my personal projects 
     outside of work hours. This is standard in tech employment."
   - Show: Your personal projects don't compete with company
   
   Negotiability: MEDIUM - Common request

NON-NEGOTIABLES (Kept as-is):
- Salary: $120,000 ✓
- Start date: January 15, 2025 ✓
- Remote work option ✓

RECOMMENDED NEGOTIATION ORDER:
1. Start with non-compete (easiest to justify)
2. Then IP ownership (common concern)
3. Finally termination notice (if needed)

TALKING POINTS:
- "I'm excited about this opportunity and want to make sure the 
  contract works for both of us."
- "These changes align with industry standards and protect both 
  parties fairly."
```

---

## 🔄 Complete User Workflow Example

### Scenario: You get a new employment contract

**Step 1: Upload**
```
You: [Drag and drop] Employment_Offer_TechCorp.pdf → contracts/
```

**Step 2: System Processes (Automatic)**
```
System: 
  ✓ Detected new contract: Employment_Offer_TechCorp.pdf
  ✓ Reading contract...
  ✓ Loading your interests from MY_INTERESTS.txt...
  ✓ Analyzing contract against your interests...
  ✓ Generating mirror contract...
  ✓ Creating comparison document...
  ✓ Writing negotiation guide...
  ✓ Done! Created: protect_your_interests/Employment_Offer_TechCorp_mirror/
```

**Step 3: You Review Output**
```
You open: protect_your_interests/Employment_Offer_TechCorp_mirror/

You see:
  1_mirror_contract_protecting_YOUR_interests.docx  ← Your improved version
  2_clean_redline_comparison.pdf                    ← See all changes
  3_negotiation_guide.docx                          ← How to negotiate
```

**Step 4: You Use It**
```
You:
  - Review the mirror contract (File 1)
  - Check what changed (File 2)
  - Read negotiation tips (File 3)
  - Use the talking points to negotiate with employer
```

---

## 💡 Pro Tips

### 1. Keep Your Interests File Updated
- Add new preferences as you learn what matters to you
- Update it based on past negotiations
- Make it specific to your industry/role

### 2. Use Per-Contract Instructions for Special Cases
- Complex contracts might need specific guidance
- Create `.instructions` file alongside the contract
- System will prioritize these over general interests

### 3. Review the Negotiation Guide First
- Start with File 3 (negotiation guide)
- Understand what changed and why
- Then review the actual contract (File 1)

### 4. Iterate
- After negotiating, update your interests file
- Note what worked and what didn't
- System gets smarter as you use it

---

## 🎯 Summary: How the LLM Knows Your Interests

**Simple Answer:**
1. You write your preferences once in `MY_INTERESTS.txt` (plain English)
2. System reads it every time it processes a contract
3. LLM compares contract against your interests
4. LLM generates mirror contract protecting your interests
5. You get 3 files: improved contract, comparison, negotiation guide

**No complex setup needed** - just write what matters to you in natural language!

---

## 📝 Example: Complete Interest File Template

```markdown
MY CONTRACT INTERESTS
====================

I am a software developer who values flexibility, fair compensation, 
and protection of my personal projects.

EMPLOYMENT:
- Non-competes: Max 6 months, specific to my role
- IP: Company owns work on company time; I own personal projects
- Severance: At least 2 weeks per year
- PTO: 20+ days or unlimited
- Remote work: Prefer flexible/hybrid

SERVICE AGREEMENTS:
- Payment: Net 15-30, not Net 60+
- Termination: Early exit with refunds
- Liability: Reasonable caps

LEASE:
- Deposit: Max 1 month
- Termination: 30 days notice option
- Pets: Reasonable policy

GENERAL:
- Prefer shorter terms with renewal options
- Clear dispute resolution
- Fair termination clauses
```

**That's it!** The LLM understands this and applies it to every contract.

