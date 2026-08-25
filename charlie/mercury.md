---
name: charlie-mercury
description: Mercury Bank financial data for Charlie's Seaynic Labs LLC account
trigger_patterns: mercury|mercury bank|bank balance|bank account
contexts: finance, seaynic-labs, charlie-only, banking
access: [charlie]
success_indicators: balance retrieved, accounts listed, transactions shown
---

# charlie-mercury

**Mercury Bank Tools for Seaynic Labs LLC**

**Access:** Charlie only (Seaynic Labs LLC owner)  
**Data Source:** Mercury Bank API via read-only credentials

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user != "charlie":
    print(f"ERROR: Access denied. This Mercury account belongs to Charlie (Seaynic Labs LLC).")
    print(f"User '{user}' does not have access to Seaynic Labs banking data.")
    exit(1)
```

---

## Commands

### balance

Get total balance across all Seaynic Labs Mercury accounts.

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, 'lib')
from mercury_finance import get_total_balance

async def main():
    try:
        data = await get_total_balance()
        total = data.get("total_balance", 0)
        accounts = data.get("accounts", [])
        
        html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #0066ff 0%, #0047b3 100%); color: white; padding: 24px; border-radius: 12px 12px 0 0;">
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
            <span style="display: inline-block; width: 48px; height: 48px; background: white; border-radius: 10px; margin-right: 16px; display: flex; align-items: center; justify-content: center; color: #0066ff; font-size: 24px; font-weight: 700;">M</span>
            <div>
                <h2 style="margin: 0; font-size: 24px; font-weight: 600;">Mercury Bank</h2>
                <p style="margin: 4px 0 0 0; font-size: 14px; opacity: 0.9;">Seaynic Labs LLC</p>
            </div>
        </div>
    </div>
    
    <div style="background: #ffffff; padding: 32px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="text-align: center; padding: 24px; background: #f0f7ff; border-radius: 8px; margin-bottom: 24px;">
            <div style="font-size: 14px; color: #0066ff; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Total Balance</div>
            <div style="font-size: 42px; font-weight: 700; color: #2d3748;">${total:,.2f}</div>
        </div>
        
        <h3 style="font-size: 16px; font-weight: 600; color: #2d3748; margin: 0 0 16px 0;">Accounts</h3>
"""
        
        for acc in accounts:
            name = acc.get("name", "Unknown")
            balance = acc.get("balance", 0)
            available = acc.get("available", 0)
            acc_type = acc.get("type", "").replace("mercury", "").strip().title() or "Account"
            acc_num = name.split("••")[-1] if "••" in name else ""
            
            html += f"""
        <div style="background: #f7fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #0066ff; margin-bottom: 16px;">
            <div style="font-weight: 600; color: #2d3748; font-size: 16px; margin-bottom: 12px;">
                {acc_type} {f"••{acc_num}" if acc_num else ""}
            </div>
            <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span style="color: #718096;">Balance</span>
                <span style="font-weight: 600; color: #2d3748;">${balance:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span style="color: #718096;">Available</span>
                <span style="font-weight: 600; color: #48bb78;">${available:,.2f}</span>
            </div>
        </div>
"""
        
        html += """
    </div>
</div>
"""
        print(html)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

asyncio.run(main())
EOF
```

### accounts

List all Mercury accounts for Seaynic Labs.

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, 'lib')
from mercury_finance import list_accounts

async def main():
    try:
        accounts = await list_accounts()
        if not accounts:
            print("No Mercury accounts found.")
            return
        
        print(f"Seaynic Labs Mercury Accounts ({len(accounts)}):")
        print()
        for acc in accounts:
            acc_id = acc.get("id", "")
            name = acc.get("name", "Unknown")
            acc_type = acc.get("type", "")
            balance = acc.get("balance", 0)
            available = acc.get("available", 0)
            
            print(f"ID: {acc_id}")
            print(f"  Name:      {name}")
            print(f"  Type:      {acc_type}")
            print(f"  Balance:   ${balance:,.2f}")
            print(f"  Available: ${available:,.2f}")
            print()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

asyncio.run(main())
EOF
```

### transactions

List recent transactions for a specific account.

**Arguments:** `account_id` (required), `limit=N` (optional, default 20)

```bash
ACCOUNT_ID="$1"
LIMIT=${2:-20}

if [ -z "$ACCOUNT_ID" ]; then
    echo "ERROR: account_id required"
    echo "Usage: /charlie-mercury transactions <account_id> [limit]"
    echo ""
    echo "Run '/charlie-mercury accounts' to get account IDs"
    exit 1
fi

cd ~/Projects/m5-agents
python3 << EOF
import asyncio
import sys
sys.path.insert(0, 'lib')
from mercury_finance import get_recent_transactions

async def main():
    try:
        txns = await get_recent_transactions("${ACCOUNT_ID}", limit=${LIMIT})
        if not txns:
            print("No recent transactions found for this account.")
            return
        
        print(f"Recent Transactions (last {len(txns)}):")
        print()
        for txn in txns:
            date = txn.get('date', '')[:10]
            amount = txn.get('amount', 0)
            desc = txn.get('description', 'No description')
            status = txn.get('status', '')
            
            print(f"{date} | \${amount:,.2f} | {status} | {desc}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

asyncio.run(main())
EOF
```

---

## Usage Examples

```bash
# Get total Mercury balance
/charlie-mercury balance

# List all accounts
/charlie-mercury accounts

# List transactions for specific account
/charlie-mercury transactions <account-id>

# List last 50 transactions
/charlie-mercury transactions <account-id> 50
```

---

## Error Handling

- **Access Denied:** If user is not Charlie, exits with error
- **Auth Failure:** If Mercury API key is invalid/revoked
- **Invalid Account:** If account_id doesn't exist
- **Network Error:** If Mercury API is unreachable

All errors are logged with clear messages.
