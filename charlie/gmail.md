---
name: charlie-gmail
description: Query Charlie's Gmail inbox, search emails, extract receipts
trigger_patterns: email|inbox|gmail|receipt|message from
contexts: email, receipts, financial
access: [charlie]
success_indicators: email data retrieved, receipts extracted
---

# charlie-gmail

**Gmail Access for Charlie**

**Access:** Charlie only  
**Data Sources:** Gmail API (OAuth)

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user != "charlie":
    print(f"ERROR: Access denied. Gmail access is limited to Charlie.")
    print(f"User '{user}' does not have Gmail access.")
    exit(1)
```

---

## Commands

### search

Search emails with Gmail query syntax.

**Arguments:** `<query>` (Gmail search query)

**Query examples:**
- `subject:receipt` - messages with "receipt" in subject
- `from:noreply@amazon.com` - from specific sender  
- `after:2024/01/01` - messages after date
- `has:attachment` - messages with attachments
- `is:unread` - unread messages only

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import sys
sys.path.insert(0, 'lib')
from gmail_oauth import search_emails

query = """<QUERY>"""
results = search_emails(query, user="charlie", max_results=10)

if not results:
    print(f"No emails found matching: {query}")
else:
    print(f"Found {len(results)} emails:\n")
    for email in results:
        print(f"**From:** {email['from']}")
        print(f"**Subject:** {email['subject']}")
        print(f"**Date:** {email['date']}")
        print(f"**Preview:** {email['snippet'][:200]}")
        print("---")
EOF
```

### receipts

Find and extract receipts from recent emails.

**Arguments:** `[days=30]` (how many days back to search)

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import sys
sys.path.insert(0, 'lib')
from gmail_oauth import get_gmail_client
from receipt_extractor import ReceiptExtractor

days = <DAYS:30>

# Search for receipt emails
client = get_gmail_client(user="charlie")
emails = client.search_receipts(days=days)

if not emails:
    print(f"No receipt emails found in last {days} days")
    exit(0)

# Extract structured data
extractor = ReceiptExtractor()
receipts = extractor.batch_extract(emails)

print(f"Found {len(receipts)} receipts in last {days} days:\n")

total_spend = sum(r.get('amount', 0) for r in receipts)
print(f"**Total Spending:** ${total_spend:,.2f}\n")

# Group by merchant
by_merchant = {}
for receipt in receipts:
    merchant = receipt.get('merchant', receipt.get('from', 'Unknown'))
    amount = receipt.get('amount', 0)
    by_merchant[merchant] = by_merchant.get(merchant, 0) + amount

print("**By Merchant:**")
for merchant, amount in sorted(by_merchant.items(), key=lambda x: x[1], reverse=True):
    print(f"- {merchant}: ${amount:,.2f}")

print("\n**Recent Receipts:**")
for receipt in receipts[:10]:
    print(f"- {receipt.get('subject', 'Unknown')} - ${receipt.get('amount', 0):,.2f}")
EOF
```

### unread

Show unread message count and recent unread emails.

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import sys
sys.path.insert(0, 'lib')
from gmail_oauth import search_emails

results = search_emails("is:unread", user="charlie", max_results=20)

print(f"**Unread Messages:** {len(results)}\n")

if results:
    print("**Recent Unread:**")
    for email in results[:10]:
        print(f"- **From:** {email['from']}")
        print(f"  **Subject:** {email['subject']}")
        print(f"  **Date:** {email['date']}")
        print()
EOF
```

---

## Setup

**First-time OAuth setup required:**

1. Download OAuth credentials from Google Cloud Console
2. Save as `/Volumes/data/secrets/gmail-oauth-credentials.json`
3. Run any command - browser will open for authorization
4. Token saved at `/Volumes/data/secrets/gmail-oauth-charlie.json`

**Subsequent uses:** Automatic (tokens refresh automatically)

---

## Usage Examples

```bash
# Search for Amazon orders
/charlie-gmail search "from:amazon.com subject:order"

# Find all receipts from last 7 days
/charlie-gmail receipts 7

# Check unread count
/charlie-gmail unread

# Find PayPal transactions
/charlie-gmail search "from:paypal.com"
```

---

## Notes

- **Read-only:** Can read emails, cannot send or delete
- **OAuth refresh:** Tokens refresh automatically when expired
- **Privacy:** Tokens stored securely at `/Volumes/data/secrets/` (mode 0600)
- **Receipts:** Extracted data saved to `/Volumes/data/financial/receipts/`

---

## Error Handling

- **OAuth expired:** Re-run command, browser opens for re-auth
- **No credentials:** Download from Google Cloud Console
- **Network error:** Gmail API unavailable (retry later)

All errors logged with clear messages.
