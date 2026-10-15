---
name: mcp-resend
description: Transactional email delivery via Resend API through the `resend` MCP server (3 tools). Send emails, list recent sent emails, and verify verified sending domains. Critical: sending email is a side-effecting action — only use this when email is genuinely required by the task, never for testing without explicit confirmation. Use when automating notifications, alerts, or confirmations that need to reach real mailboxes.
---

# Resend Email MCP

The `resend` MCP server (proxy name `resend`, Python bridge at `/Users/charlieseay/Projects/resend-mcp/.venv/bin/resend-mcp`) is a wrapper around the Resend transactional email API. It connects to `https://api.resend.com` and sends emails from the verified domain `helmsman@seayniclabs.com`. All 3 tools confirmed live against source at `/Users/charlieseay/Projects/resend-mcp/src/resend_mcp/server.py:30-176`.

**Auth requirement**: Resend API key at `/Volumes/data/secrets/resend_api_key` (36 bytes, `re_*` format). The bridge reads this file; agents never need to see the key. Fallback: `RESEND_API_KEY` environment variable.

**⚠️ CRITICAL — This skill sends real emails**: Every call to `email_send` will deliver a message to real mailboxes. Do NOT test by sending to real addresses casually. If you need to verify functionality, use a test address that belongs to Charlie or discuss first.

## Quick patterns before calling any tool

**From address**: All emails are sent from `{from_name} <helmsman@seayniclabs.com>`. The `from_name` parameter (default: "Sonique") controls the display name only; the actual email address is always `helmsman@seayniclabs.com`.

**Recipient list**: The `to` parameter accepts:
- Single email: `user@example.com`
- Multiple emails (comma-separated): `user1@example.com,user2@example.com`
- Leading/trailing whitespace is stripped from each address
- **All domains must be on the verified domain list** (or in Resend's allowlist). Use `domains_list` to check.

**Email content**: The `body` parameter accepts:
- Plain text (preferred for clarity)
- HTML markup (will be sent as-is; wrap in proper `<html>` tags if needed)
- No size limit enforced by the MCP tool (Resend API limit is 25 MB)

**Return values**: Success returns "Email sent to X (id: Y)" where Y is the Resend email ID. Failures return "Error: <reason>" with diagnostic info.

## Tool catalog (3 tools, verified live 2026-10-01 against source)

**`email_send`** — Send an email via Resend (side-effecting, sends real email).
- `to` (string, required): Recipient email address or comma-separated list
- `subject` (string, required): Email subject line
- `body` (string, required): Email body (plain text or HTML)
- `from_name` (string, optional): Display name for sender (default: "Sonique")
- Returns: "Email sent to {to} (id: {email_id})" on success, or "Error: ..." on failure
- **Examples of failure**:
  - "Error: RESEND_API_KEY not set..." — token file missing or env var not set
  - "Error: Could not connect to Resend API..." — network error, Resend API down
  - "Error: Resend API returned 400: invalid_from_address" — domain not verified in Resend
  - "Error: Resend API returned 401: ..." — token invalid or expired
- **Sends a real email** — every successful call delivers to the inbox

**`emails_list`** — List recently sent emails.
- `limit` (integer, optional): Number of emails to retrieve (default: 10, must be 1-100)
- Returns: Formatted list showing: subject → recipient (timestamp)
  ```
  • Weekly Digest → user@example.com (2026-10-01T14:23:00Z)
  • Alert: High CPU → ops@example.com (2026-10-01T13:15:22Z)
  ```
- Returns "No emails found." if none were sent yet
- Returns error if limit is outside 1-100 range
- **This is read-only** — lists what was sent, does not filter or search by content

**`domains_list`** — List verified sending domains in Resend.
- No parameters
- Returns: Formatted list of domains with verification status
  ```
  • seayniclabs.com (verified)
  • example.com (pending)
  ```
- Domains show status: `verified`, `pending` (awaiting DNS validation), or `failed`
- Use this to confirm which domains are available for sending (only `verified` domains can send real emails)
- Returns "No domains found." if no domains are configured in Resend

## Known environment facts and limitations

- **From domain**: `seayniclabs.com` (configured hardcoded in server.py:12). All emails originate from `helmsman@seayniclabs.com`
- **From name**: Defaults to "Sonique"; override with `from_name` parameter (e.g., "Helmsman", "Alert System")
- **API base**: `https://api.resend.com` (server.py:11)
- **Token location**: `/Volumes/data/secrets/resend_api_key` (server.py:18) or `RESEND_API_KEY` env var
- **API timeout**: 10 seconds per request (server.py:13)
- **Max email size**: 25 MB (Resend API limit, not enforced by MCP tool)

If the token is missing or invalid, all tools return "Error: RESEND_API_KEY not set..." — this blocks sending entirely.

## Gotchas, limitations, and operational warnings

**⚠️ REAL EMAIL DELIVERY**: Every successful `email_send` call sends an email to real mailboxes. There is no "dry run" or test mode. Do NOT send to real addresses to test functionality without explicit confirmation.

**No unverified domain sending**: If a domain is not verified in Resend, you cannot send from it. The API will return "Error: Resend API returned 400: invalid_from_address". Use `domains_list` to check status first.

**No bulk send tool**: This skill's `email_send` accepts comma-separated recipients but sends a single API call per unique `to` parameter. Sending to 100 recipients is one API call with one email ID returned; Resend may deliver to each recipient individually (check Resend's docs for multi-recipient behavior).

**From name only**: The `from_name` parameter only controls the display name in email clients (the "From:" header name). The actual email address (`helmsman@seayniclabs.com`) is fixed and cannot be overridden.

**No reply-to, CC, BCC in this skill**: The MCP tool only supports `to`, `from_name`, `subject`, `body`. If you need CC/BCC/Reply-To, that requires modifying the resend-mcp source or using Resend's API directly.

**No HTML validation**: If you pass malformed HTML in `body`, it will be sent as-is. The recipient's email client may render it poorly or as plain text.

**Email ID returned, not tracking URL**: `email_send` returns the Resend email ID (e.g., `2025_abc123def456`). Use this ID with Resend's dashboard to check delivery status, bounces, or opens. The MCP tool does not expose a "get email status" call — that requires reading the Resend dashboard or API directly.

**`emails_list` is recent-only**: The list shows recently sent emails (default last 10), not a full history. For full historical search, use Resend's dashboard.

**No delivery status in this skill**: `email_send` returns immediately with an ID once Resend accepts the email. It does NOT wait for delivery to the recipient's mailbox. Bounces, failures, and non-delivery reports happen asynchronously and are visible in Resend's dashboard, not in this MCP tool.

**Domain verification is asynchronous**: If you add a new domain to Resend and call `domains_list` immediately, it may show as `pending` for several minutes while DNS propagates. Wait for DNS TXT/CNAME records to be recognized before sending.

## Workflow: when and how to use

**Safe pattern**:
1. Call `domains_list` to verify the sending domain is `verified`
2. If using `email_send`, **always confirm the recipient address is correct** — there is no undo
3. Call `email_send` with explicit recipient and subject (not templatized; confirm each)
4. Store the returned email ID for audit trail
5. Optionally call `emails_list` after sending to confirm it appears in recent history

**Never**:
- Send to `test@`, `admin@`, or similar placeholder addresses for testing — they're real addresses on someone's server
- Use `email_send` to bulk-send to marketing lists without explicit per-recipient confirmation
- Assume delivery succeeded just because the MCP returned an ID — check Resend dashboard for bounces/failures

## Quick verification pattern for this skill

```bash
# Test that the API key is valid and Resend is reachable
KEY=$(cat /Volumes/data/secrets/resend_api_key)
curl -s -X GET \
  -H "Authorization: Bearer $KEY" \
  https://api.resend.com/domains | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print('PASS: Resend reachable' if 'data' in d else f'FAIL: {d}')"
```

If this fails:
- Check that the token file exists: `ls -la /Volumes/data/secrets/resend_api_key`
- Verify the token is readable: `cat /Volumes/data/secrets/resend_api_key` (should output ~36 chars starting with `re_`)
- Verify the token is not expired (check Resend dashboard)
- Verify network access to `https://api.resend.com` (should be reachable from this machine)
- If the API returns `{"error": "..."}`, the token is likely invalid or expired — regenerate it in Resend dashboard
