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
sys.path.insert(0, 'lib')
from stripe_finance import get_balance as get_stripe_balance
from mercury_finance import get_total_balance as get_mercury_balance

async def main():
    try:
        # Fetch all balances concurrently
        stripe_data, mercury_data = await asyncio.gather(
            get_stripe_balance(),
            get_mercury_balance()
        )
        
        # Parse Stripe
        stripe_avail = stripe_data.get("available", [{}])[0].get("amount", 0) / 100
        stripe_pending = stripe_data.get("pending", [{}])[0].get("amount", 0) / 100
        stripe_total = stripe_avail + stripe_pending
        
        # Parse Mercury
        mercury_total = mercury_data.get("total_balance", 0)
        mercury_accounts = mercury_data.get("accounts", [])
        
        # Calculate grand total
        grand_total = stripe_total + mercury_total
        
        # Display formatted overview as rich HTML with dark theme
        html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; max-height: 600px; overflow-y: auto;">
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
