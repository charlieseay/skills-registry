---
name: charlie-finance
description: Unified financial overview for Charlie's Seaynic Labs LLC accounts (Stripe + Mercury)
trigger_patterns: finance|financial|money|balance|accounts|how much money
contexts: finance, seaynic-labs, charlie-only
access: [charlie]
success_indicators: complete financial overview shown, all accounts included
---

# charlie-finance

**Financial Overview for Seaynic Labs LLC**

**Access:** Charlie only  
**Data Sources:** Stripe API + Mercury Bank API (read-only)

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user != "charlie":
    print(f"ERROR: Access denied. Financial data belongs to Charlie (Seaynic Labs LLC).")
    print(f"User '{user}' does not have access to Seaynic Labs financial data.")
    exit(1)
```

---

## Commands

### overview

Show complete financial overview across all connected accounts.

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import asyncio
import sys
import subprocess
import json
sys.path.insert(0, 'lib')
from stripe_finance import get_balance as get_stripe_balance
from mercury_finance import get_total_balance as get_mercury_balance

def get_manual_bank_balance():
    """Fetch manually uploaded bank balance from JSON file."""
    try:
        balance_file = '/Volumes/data/notebooks/agent-scratchpad/bank-statements/current_balance.json'
        if not os.path.exists(balance_file):
            return {"total": 0, "setup_needed": True, "accounts": []}
        
        with open(balance_file, 'r') as f:
            data = json.load(f)
        
        return {
            "total": data.get("balance", 0),
            "accounts": [{
                "name": data.get("account_name", "US Bank"),
                "balance": data.get("balance", 0),
                "last_updated": data.get("last_updated", "Unknown")
            }],
            "setup_needed": False
        }
    except Exception as e:
        return {"error": str(e), "total": 0, "setup_needed": True, "accounts": []}

def get_paypal_balance():
    """Fetch PayPal balance via integration script."""
    try:
        result = subprocess.run(
            ['python3', '/Volumes/data/integrations/paypal_balance.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return json.loads(result.stdout) if result.returncode == 0 else {"error": "Failed to fetch", "total_usd": 0}
    except Exception as e:
        return {"error": str(e), "total_usd": 0, "setup_needed": True}

async def main():
    try:
        # Fetch all balances concurrently
        stripe_data, mercury_data = await asyncio.gather(
            get_stripe_balance(),
            get_mercury_balance()
        )
        
        # Fetch manual bank balance and PayPal synchronously (not async yet)
        bank_data = get_manual_bank_balance()
        paypal_data = get_paypal_balance()
        
        # Parse Stripe
        stripe_avail = stripe_data.get("available", [{}])[0].get("amount", 0) / 100
        stripe_pending = stripe_data.get("pending", [{}])[0].get("amount", 0) / 100
        stripe_total = stripe_avail + stripe_pending
        
        # Parse Mercury
        mercury_total = mercury_data.get("total_balance", 0)
        mercury_accounts = mercury_data.get("accounts", [])
        
        # Parse Manual Bank Balance
        bank_total = bank_data.get("total", 0)
        bank_accounts = bank_data.get("accounts", [])
        bank_needs_setup = bank_data.get("setup_needed", False)
        
        # Parse PayPal
        paypal_total = paypal_data.get("total_usd", 0)
        paypal_balances = paypal_data.get("balances", [])
        paypal_needs_setup = paypal_data.get("setup_needed", False)
        
        # Calculate grand total
        grand_total = stripe_total + mercury_total + bank_total + paypal_total
        
        # Display formatted overview as rich HTML with dark theme
        html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
        <h2 style="margin: 0; font-size: 20px; font-weight: 600;">SEAYNIC LABS LLC</h2>
        <p style="margin: 6px 0 0 0; font-size: 13px; opacity: 0.9;">Financial Overview</p>
    </div>
    
    <div style="background: #1a202c; padding: 24px; border-radius: 0 0 8px 8px; border: 1px solid #2d3748;">
        <!-- Total -->
        <div style="text-align: center; padding: 20px; background: #2d3748; border-radius: 6px; margin-bottom: 24px;">
            <div style="font-size: 12px; color: #a0aec0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">Total Across All Accounts</div>
            <div style="font-size: 36px; font-weight: 700; color: #48bb78;">${grand_total:,.2f}</div>
        </div>
        
        <!-- Stripe Section -->
        <div style="margin-bottom: 24px;">
            <h3 style="font-size: 14px; font-weight: 600; color: #9f7aea; margin: 0 0 12px 0; display: flex; align-items: center;">
                <span style="display: inline-block; width: 28px; height: 28px; background: #9f7aea; border-radius: 6px; margin-right: 10px; text-align: center; line-height: 28px; color: white; font-size: 16px;">S</span>
                Stripe Payments
            </h3>
            <div style="padding-left: 38px;">
                <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2d3748;">
                    <span style="color: #a0aec0;">Available</span>
                    <span style="font-weight: 600; color: #e2e8f0;">${stripe_avail:,.2f}</span>
                </div>
                {"" if stripe_pending == 0 else f'''<div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2d3748;">
                    <span style="color: #a0aec0;">Pending</span>
                    <span style="font-weight: 600; color: #e2e8f0;">${stripe_pending:,.2f}</span>
                </div>'''}
                <div style="display: flex; justify-content: space-between; padding: 10px 0; font-weight: 600;">
                    <span style="color: #e2e8f0;">Subtotal</span>
                    <span style="color: #9f7aea;">${stripe_total:,.2f}</span>
                </div>
            </div>
        </div>
        
        <!-- Mercury Section -->
        <div style="margin-bottom: 20px;">
            <h3 style="font-size: 14px; font-weight: 600; color: #4299e1; margin: 0 0 12px 0; display: flex; align-items: center;">
                <span style="display: inline-block; width: 28px; height: 28px; background: #4299e1; border-radius: 6px; margin-right: 10px; text-align: center; line-height: 28px; color: white; font-size: 16px;">M</span>
                Mercury Bank
            </h3>
            <div style="padding-left: 38px;">
                {"".join([f'''<div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2d3748;">
                    <span style="color: #a0aec0;">{acc.get("type", "Account").replace("mercury", "").strip().title()} ••{acc.get("name", "").split("••")[-1] if "••" in acc.get("name", "") else acc.get("name", "")}</span>
                    <span style="font-weight: 600; color: #e2e8f0;">${acc.get("balance", 0):,.2f}</span>
                </div>''' for acc in mercury_accounts if acc.get("balance", 0) > 0])}
                <div style="display: flex; justify-content: space-between; padding: 10px 0; font-weight: 600;">
                    <span style="color: #e2e8f0;">Subtotal</span>
                    <span style="color: #4299e1;">${mercury_total:,.2f}</span>
                </div>
            </div>
        </div>
        
        <!-- US Bank Section (Manual Upload) -->
        {"" if bank_needs_setup else f'''<div style="margin-bottom: 20px;">
            <h3 style="font-size: 14px; font-weight: 600; color: #34d399; margin: 0 0 12px 0; display: flex; align-items: center;">
                <span style="display: inline-block; width: 28px; height: 28px; background: #34d399; border-radius: 6px; margin-right: 10px; text-align: center; line-height: 28px; color: white; font-size: 16px;">U</span>
                US Bank (Manual)
            </h3>
            <div style="padding-left: 38px;">
                {"".join([f"""<div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2d3748;">
                    <span style="color: #a0aec0;">{acc.get("name", "Account")}</span>
                    <span style="font-weight: 600; color: #e2e8f0;">${acc.get("balance", 0):,.2f}</span>
                </div>""" for acc in bank_accounts])}
                <div style="display: flex; justify-content: space-between; padding: 10px 0; font-weight: 600;">
                    <span style="color: #e2e8f0;">Subtotal</span>
                    <span style="color: #34d399;">${bank_total:,.2f}</span>
                </div>
                {"" if not bank_accounts else f'''<div style="padding: 6px 0; font-size: 10px; color: #718096;">
                    📄 Updated: {bank_accounts[0].get("last_updated", "Unknown")}
                </div>'''}
            </div>
        </div>'''}
        
        <!-- PayPal Section -->
        {"" if paypal_needs_setup else f'''<div style="margin-bottom: 20px;">
            <h3 style="font-size: 14px; font-weight: 600; color: #fbbf24; margin: 0 0 12px 0; display: flex; align-items: center;">
                <span style="display: inline-block; width: 28px; height: 28px; background: #fbbf24; border-radius: 6px; margin-right: 10px; text-align: center; line-height: 28px; color: white; font-size: 16px;">P</span>
                PayPal (Personal)
            </h3>
            <div style="padding-left: 38px;">
                <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2d3748;">
                    <span style="color: #a0aec0;">Available</span>
                    <span style="font-weight: 600; color: #e2e8f0;">${paypal_total:,.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 10px 0; font-weight: 600;">
                    <span style="color: #e2e8f0;">Subtotal</span>
                    <span style="color: #fbbf24;">${paypal_total:,.2f}</span>
                </div>
            </div>
        </div>'''}
        
        <!-- Footer -->
        <div style="border-top: 2px solid #2d3748; padding-top: 16px; margin-top: 24px;">
            <div style="display: flex; justify-content: space-between; font-size: 16px; font-weight: 700;">
                <span style="color: #e2e8f0;">Liquid Assets (Total)</span>
                <span style="color: #48bb78;">${grand_total:,.2f}</span>
            </div>
        </div>
    </div>
</div>
"""
        print(html)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

asyncio.run(main())
EOF
```

---

## Usage Examples

```bash
# Complete financial overview
/charlie-finance overview

# Or just ask naturally:
# "What's my financial situation?"
# "How much money do I have?"
# "Show me my accounts"
```

---

## Notes

- **Comprehensive:** Shows ALL connected financial accounts
- **Real-time:** Pulls live data from Stripe and Mercury APIs
- **Read-only:** Cannot modify balances or make transfers
- **Formatted:** Clean dashboard-style display
- **Sources:** Clearly shows Stripe vs Mercury breakdown

---

## Error Handling

- **Access Denied:** If user is not Charlie
- **Auth Failure:** If API keys are invalid/revoked
- **Network Error:** If APIs are unreachable

All errors are logged with clear messages.
