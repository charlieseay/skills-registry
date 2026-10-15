---
name: charlie-bank-statements
description: Process manually uploaded US Bank statements and extract balances
trigger_patterns: bank statement|us bank|manual balance
contexts: finance, banking, statements
access: [charlie]
success_indicators: statement parsed, balance extracted
---

# charlie-bank-statements

**Manual Bank Statement Processing**

**Access:** Charlie only  
**Data Source:** Uploaded PDF/CSV statements in notebook  
**Purpose:** Extract current balances from manually uploaded bank statements

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user != "charlie":
    print(f"ERROR: Access denied. Bank statements are only accessible to Charlie.")
    print(f"User '{user}' does not have access.")
    exit(1)
```

---

## Commands

### balance

Extract current balance from most recent statement.

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import os
import json
from pathlib import Path
from datetime import datetime

# Look for uploaded statements in notebook
statements_dir = Path("/Volumes/data/notebooks/agent-scratchpad/bank-statements")
statements_dir.mkdir(parents=True, exist_ok=True)

# Also check for a simple balance file
balance_file = statements_dir / "current_balance.json"

if balance_file.exists():
    with open(balance_file) as f:
        data = json.load(f)
    
    # Display as HTML
    balance = data.get("balance", 0)
    account_name = data.get("account_name", "US Bank Checking")
    last_updated = data.get("last_updated", "Unknown")
    
    html = f"""<div style="background: #1a202c; color: #e2e8f0; padding: 20px; border-radius: 8px; max-width: 600px;">
<h3 style="margin: 0 0 16px 0; color: #34d399; display: flex; align-items: center;">
    <span style="display: inline-block; width: 28px; height: 28px; background: #34d399; border-radius: 6px; margin-right: 10px; text-align: center; line-height: 28px; color: white; font-size: 16px;">U</span>
    {account_name}
</h3>
<div style="padding-left: 38px;">
    <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2d3748;">
        <span style="color: #a0aec0;">Current Balance</span>
        <span style="font-weight: 600; color: #e2e8f0; font-size: 18px;">${balance:,.2f}</span>
    </div>
    <div style="padding: 10px 0; font-size: 11px; color: #718096;">
        Last updated: {last_updated}
    </div>
    <div style="padding: 10px 0; margin-top: 10px; border-top: 1px solid #2d3748;">
        <div style="font-size: 11px; color: #a0aec0; margin-bottom: 6px;">📄 Manual Entry</div>
        <div style="font-size: 11px; color: #718096;">Upload statements to update balance</div>
    </div>
</div>
</div>"""
    print(html)
else:
    # No balance file yet
    print("""<div style="background: #2d1b1b; color: #f87171; padding: 20px; border-radius: 8px; max-width: 600px; border: 1px solid #7f1d1d;">
<h3 style="margin: 0 0 12px 0; color: #f87171;">⚠️ No Bank Balance on File</h3>
<p style="margin: 0 0 12px 0; font-size: 13px; color: #fca5a5;">Upload a bank statement or manually enter your balance.</p>
<div style="background: #1a202c; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 11px; color: #e2e8f0;">
To set balance manually:<br><br>
1. Upload statement to PAC notebook → "bank-statements" folder<br>
2. Or create: /Volumes/data/notebooks/agent-scratchpad/bank-statements/current_balance.json<br><br>
Format:<br>
{<br>
&nbsp;&nbsp;"balance": 5000.00,<br>
&nbsp;&nbsp;"account_name": "US Bank Checking",<br>
&nbsp;&nbsp;"last_updated": "2026-08-24"<br>
}
</div>
</div>""")
EOF
```

---

## Usage Examples

```bash
# Check current balance
/charlie-bank-statements balance
```

---

## Manual Balance Entry

**Option 1: Via JSON file (recommended)**

SSH to M5 and create:
```bash
cat > /Volumes/data/notebooks/agent-scratchpad/bank-statements/current_balance.json << 'EOF'
{
  "balance": 5000.00,
  "account_name": "US Bank Checking",
  "last_updated": "2026-08-24",
  "notes": "From monthly statement"
}
EOF
```

**Option 2: Via PAC Notebook Upload**

1. In PAC → Open Notebooks panel
2. Select "agent-scratchpad" notebook
3. Create note titled "Bank Statement - US Bank - YYYY-MM-DD"
4. Upload PDF statement as attachment
5. PAC will extract balance automatically (future feature)

---

## Integration with Finance Skill

The charlie-finance skill will automatically check for this balance file and include it in the overview if present.

---

## Notes

- **Privacy:** Balance file is stored locally on M5, never sent to external APIs
- **Updates:** Update the JSON file whenever you receive a new statement
- **Multiple Accounts:** Create separate JSON files for each account
- **Future:** Auto-parsing of uploaded PDF statements (OCR + extraction)

---

## Security

Balance file location:
```
/Volumes/data/notebooks/agent-scratchpad/bank-statements/current_balance.json
```

Permissions: `600` (owner read/write only)
Owner: charlieseay
