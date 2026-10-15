---
name: charlie-financial-search
description: Search and analyze transactions across ALL financial accounts (Stripe, Mercury, PayPal, US Bank)
trigger_patterns: transaction|transactions|spent|purchase|payment|financial search
contexts: finance, transactions, analytics
access: [charlie]
success_indicators: transaction data retrieved and analyzed
---

# charlie-financial-search

**Cross-Account Transaction Search & Analytics**

**Access:** Charlie only  
**Data Sources:** Stripe, Mercury, PayPal CSVs, US Bank statements

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user != "charlie":
    print(f"ERROR: Access denied. Financial data belongs to Charlie (Seaynic Labs LLC).")
    print(f"User '{user}' does not have access to financial data.")
    exit(1)
```

---

## Commands

### search

Search transactions across all accounts with filters.

**Arguments:** `<query>` (merchant name, description, or keyword), `[days=30]`

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, 'lib')

query = """<QUERY>""".lower()
days = <DAYS:30>

# Load transaction data from all sources
transactions = []

# PayPal transactions
paypal_files = Path("/Volumes/data/financial/charlie/paypal").glob("paypal_*.json")
for file in sorted(paypal_files, reverse=True):
    try:
        with open(file) as f:
            data = json.load(f)
            for tx in data.get('transactions', []):
                transactions.append({
                    'date': tx.get('date', ''),
                    'merchant': tx.get('name', tx.get('description', 'Unknown')),
                    'amount': float(tx.get('amount', '0').replace('$', '').replace(',', '').strip()),
                    'account': 'PayPal',
                    'type': tx.get('type', ''),
                })
    except Exception as e:
        print(f"Warning: Could not load {file.name}: {e}")

# US Bank transactions
usbank_files = Path("/Volumes/data/financial/household/usbank").glob("usbank_*.json")
for file in sorted(usbank_files, reverse=True):
    try:
        with open(file) as f:
            data = json.load(f)
            for tx in data.get('transactions', []):
                transactions.append({
                    'date': tx.get('date', ''),
                    'merchant': tx.get('description', 'Unknown'),
                    'amount': abs(float(tx.get('amount', 0))),
                    'account': 'US Bank',
                    'type': tx.get('type', ''),
                })
    except Exception as e:
        print(f"Warning: Could not load {file.name}: {e}")

# Filter by query and date
cutoff = datetime.now() - timedelta(days=days)
matched = []

for tx in transactions:
    # Parse date (multiple formats)
    try:
        tx_date = datetime.strptime(tx['date'], '%Y-%m-%d')
    except:
        try:
            tx_date = datetime.strptime(tx['date'], '%m/%d/%Y')
        except:
            continue

    # Date filter
    if tx_date < cutoff:
        continue

    # Query filter
    merchant_lower = tx['merchant'].lower()
    if query in merchant_lower or query in tx.get('type', '').lower():
        matched.append(tx)

if not matched:
    print(f"No transactions matching '{query}' in last {days} days")
    exit(0)

# Sort by date (newest first)
matched.sort(key=lambda x: x['date'], reverse=True)

print(f"**Found {len(matched)} transactions matching '{query}':**\n")

total = sum(t['amount'] for t in matched)
print(f"**Total:** ${total:,.2f}\n")

# Group by merchant
by_merchant = {}
for tx in matched:
    merchant = tx['merchant']
    by_merchant.setdefault(merchant, []).append(tx)

for merchant, txs in sorted(by_merchant.items(), key=lambda x: sum(t['amount'] for t in x[1]), reverse=True):
    merchant_total = sum(t['amount'] for t in txs)
    print(f"**{merchant}** - ${merchant_total:,.2f} ({len(txs)} transactions)")
    for tx in txs[:3]:  # Show first 3 per merchant
        print(f"  - {tx['date']}: ${tx['amount']:,.2f} ({tx['account']})")
    if len(txs) > 3:
        print(f"  ... and {len(txs) - 3} more")
    print()
EOF
```

### range

Show transactions in a specific date range.

**Arguments:** `<start_date>` (YYYY-MM-DD), `<end_date>` (YYYY-MM-DD), `[min_amount=0]`

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import sys
import json
from datetime import datetime
from pathlib import Path
sys.path.insert(0, 'lib')

start_date = datetime.strptime("<START_DATE>", "%Y-%m-%d")
end_date = datetime.strptime("<END_DATE>", "%Y-%m-%d")
min_amount = <MIN_AMOUNT:0>

# Load all transactions
transactions = []

# PayPal
for file in Path("/Volumes/data/financial/charlie/paypal").glob("paypal_*.json"):
    try:
        with open(file) as f:
            data = json.load(f)
            for tx in data.get('transactions', []):
                transactions.append({
                    'date': tx.get('date', ''),
                    'merchant': tx.get('name', 'Unknown'),
                    'amount': abs(float(tx.get('amount', '0').replace('$', '').replace(',', '').strip())),
                    'account': 'PayPal',
                })
    except:
        pass

# US Bank
for file in Path("/Volumes/data/financial/household/usbank").glob("usbank_*.json"):
    try:
        with open(file) as f:
            data = json.load(f)
            for tx in data.get('transactions', []):
                transactions.append({
                    'date': tx.get('date', ''),
                    'merchant': tx.get('description', 'Unknown'),
                    'amount': abs(float(tx.get('amount', 0))),
                    'account': 'US Bank',
                })
    except:
        pass

# Filter
matched = []
for tx in transactions:
    try:
        tx_date = datetime.strptime(tx['date'], '%Y-%m-%d')
    except:
        try:
            tx_date = datetime.strptime(tx['date'], '%m/%d/%Y')
        except:
            continue

    if start_date <= tx_date <= end_date and tx['amount'] >= min_amount:
        matched.append(tx)

if not matched:
    print(f"No transactions found between {start_date.date()} and {end_date.date()}")
    exit(0)

matched.sort(key=lambda x: x['date'], reverse=True)

total = sum(t['amount'] for t in matched)
print(f"**Transactions: {start_date.date()} to {end_date.date()}**\n")
print(f"**Total:** ${total:,.2f} ({len(matched)} transactions)\n")

# By account
by_account = {}
for tx in matched:
    account = tx['account']
    by_account.setdefault(account, []).append(tx)

for account, txs in by_account.items():
    account_total = sum(t['amount'] for t in txs)
    print(f"**{account}:** ${account_total:,.2f} ({len(txs)} transactions)")

print()
print("**Recent Transactions:**")
for tx in matched[:20]:
    print(f"- {tx['date']}: {tx['merchant']} - ${tx['amount']:,.2f} ({tx['account']})")
EOF
```

### top-merchants

Show top spending by merchant.

**Arguments:** `[days=30]`, `[limit=10]`

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, 'lib')

days = <DAYS:30>
limit = <LIMIT:10>

# Load all transactions
transactions = []

# PayPal
for file in Path("/Volumes/data/financial/charlie/paypal").glob("paypal_*.json"):
    try:
        with open(file) as f:
            data = json.load(f)
            for tx in data.get('transactions', []):
                transactions.append({
                    'date': tx.get('date', ''),
                    'merchant': tx.get('name', 'Unknown'),
                    'amount': abs(float(tx.get('amount', '0').replace('$', '').replace(',', '').strip())),
                })
    except:
        pass

# US Bank
for file in Path("/Volumes/data/financial/household/usbank").glob("usbank_*.json"):
    try:
        with open(file) as f:
            data = json.load(f)
            for tx in data.get('transactions', []):
                transactions.append({
                    'date': tx.get('date', ''),
                    'merchant': tx.get('description', 'Unknown'),
                    'amount': abs(float(tx.get('amount', 0))),
                })
    except:
        pass

# Filter by date
cutoff = datetime.now() - timedelta(days=days)
recent = []

for tx in transactions:
    try:
        tx_date = datetime.strptime(tx['date'], '%Y-%m-%d')
    except:
        try:
            tx_date = datetime.strptime(tx['date'], '%m/%d/%Y')
        except:
            continue

    if tx_date >= cutoff:
        recent.append(tx)

# Aggregate by merchant
by_merchant = {}
for tx in recent:
    merchant = tx['merchant']
    by_merchant[merchant] = by_merchant.get(merchant, 0) + tx['amount']

# Sort and limit
top = sorted(by_merchant.items(), key=lambda x: x[1], reverse=True)[:limit]

total = sum(tx['amount'] for tx in recent)
print(f"**Top {limit} Merchants (Last {days} Days)**\n")
print(f"**Total Spending:** ${total:,.2f}\n")

for i, (merchant, amount) in enumerate(top, 1):
    pct = (amount / total * 100) if total > 0 else 0
    print(f"{i}. **{merchant}** - ${amount:,.2f} ({pct:.1f}%)")
EOF
```

---

## Usage Examples

```bash
# Search for Amazon transactions
/charlie-financial-search search "amazon"

# Find all transactions over $100 in January
/charlie-financial-search range "2026-01-01" "2026-01-31" 100

# Top 15 merchants in last 60 days
/charlie-financial-search top-merchants 60 15

# Search for specific merchant across last 90 days
/charlie-financial-search search "starbucks" 90
```

---

## Notes

- **Multi-account:** Searches Stripe, Mercury, PayPal, AND US Bank
- **Live + historical:** Combines live API data (Stripe/Mercury) with uploaded data (PayPal/US Bank)
- **Flexible dates:** Handles multiple date formats automatically
- **Transaction deduplication:** Future enhancement (not yet implemented)

---

## Error Handling

- **Missing data files:** Skips accounts with no uploaded data
- **Invalid dates:** Skips malformed transactions
- **Zero results:** Clear message when no matches found

All errors logged with clear messages.
