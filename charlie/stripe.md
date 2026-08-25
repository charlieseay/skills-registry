---
name: charlie-stripe
description: Stripe financial data for Charlie's Seaynic Labs LLC account
trigger_patterns: stripe|seaynic labs revenue|stripe balance|stripe charges
contexts: finance, seaynic-labs, charlie-only
access: [charlie]
success_indicators: balance retrieved, charges listed, revenue calculated
---

# charlie-stripe

**Stripe Financial Tools for Seaynic Labs LLC**

**Access:** Charlie only (Seaynic Labs LLC owner)  
**Data Source:** Stripe API via read-only credentials

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user != "charlie":
    print(f"ERROR: Access denied. This Stripe account belongs to Charlie (Seaynic Labs LLC).")
    print(f"User '{user}' does not have access to Seaynic Labs financial data.")
    exit(1)
```

---

## Commands

### balance

Get current Stripe balance for Seaynic Labs.

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, 'lib')
from stripe_finance import get_balance

async def main():
    try:
        bal = await get_balance()
        available = bal.get("available", [{}])[0]
        pending = bal.get("pending", [{}])[0]
        
        avail_amt = available.get("amount", 0) / 100
        avail_curr = available.get("currency", "usd").upper()
        pend_amt = pending.get("amount", 0) / 100
        pend_curr = pending.get("currency", "usd").upper()
        
        print(f"Seaynic Labs Stripe Balance:")
        print(f"  Available: ${avail_amt:,.2f} {avail_curr}")
        print(f"  Pending:   ${pend_amt:,.2f} {pend_curr}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

asyncio.run(main())
EOF
```

### charges

List recent Stripe charges (default: last 20).

**Arguments:** `limit=N` (optional, default 20, max 100)

```bash
LIMIT=${1:-20}
cd ~/Projects/m5-agents
python3 << EOF
import asyncio
import sys
sys.path.insert(0, 'lib')
from stripe_finance import list_recent_charges

async def main():
    try:
        charges = await list_recent_charges(limit=${LIMIT})
        if not charges:
            print("No recent charges found.")
            return
        
        print(f"Recent Stripe Charges (last {len(charges)}):")
        print()
        for ch in charges:
            amt = ch.get('amount', 0)
            curr = ch.get('currency', 'usd').upper()
            desc = ch.get('description', 'No description')
            status = ch.get('status', 'unknown')
            created = ch.get('created', '')[:10]  # YYYY-MM-DD
            
            print(f"{created} | \${amt:,.2f} {curr} | {status} | {desc}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

asyncio.run(main())
EOF
```

### payments

List recent payment intents (default: last 20).

**Arguments:** `limit=N` (optional, default 20, max 100)

```bash
LIMIT=${1:-20}
cd ~/Projects/m5-agents
python3 << EOF
import asyncio
import sys
sys.path.insert(0, 'lib')
from stripe_finance import list_recent_payment_intents

async def main():
    try:
        payments = await list_recent_payment_intents(limit=${LIMIT})
        if not payments:
            print("No recent payment intents found.")
            return
        
        print(f"Recent Payment Intents (last {len(payments)}):")
        print()
        for pi in payments:
            amt = pi.get('amount', 0)
            curr = pi.get('currency', 'usd').upper()
            desc = pi.get('description', 'No description')
            status = pi.get('status', 'unknown')
            created = pi.get('created', '')[:10]
            
            print(f"{created} | \${amt:,.2f} {curr} | {status} | {desc}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

asyncio.run(main())
EOF
```

---

## Usage Examples

```bash
# Get Seaynic Labs Stripe balance
/charlie-stripe balance

# List last 20 charges
/charlie-stripe charges

# List last 50 charges
/charlie-stripe charges 50

# List recent payment intents
/charlie-stripe payments
```

---

## Error Handling

- **Access Denied:** If user is not Charlie, exits with error
- **Auth Failure:** If Stripe API key is invalid/revoked
- **Network Error:** If Stripe API is unreachable

All errors are logged with clear messages.
