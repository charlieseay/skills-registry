---
name: charlie-email
description: Charlie's email via FastMail MCP - inbox, unread, send drafts
trigger_patterns: email|inbox|unread|mail
contexts: email, communication, fastmail
access: [charlie]
success_indicators: inbox listed, unread shown, draft sent
---

# charlie-email

**Charlie's Email (FastMail)**

**Access:** Charlie only  
**Data Source:** FastMail MCP (`mcp-proxy-fastmail-bin`)  
**Purpose:** Read inbox, check unread, send drafts

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user != "charlie":
    print(f"ERROR: Access denied. Charlie's email is only accessible to Charlie.")
    print(f"User '{user}' does not have access.")
    exit(1)
```

---

## Commands

### unread

Show unread emails.

```bash
# TODO: Wire to FastMail MCP
# For now, placeholder
echo "FastMail MCP integration pending"
echo "Unread email count: (integration needed)"
```

### inbox

Show recent inbox.

```bash
# TODO: Wire to FastMail MCP
echo "FastMail MCP integration pending"
echo "Recent inbox: (integration needed)"
```

---

## Usage Examples

```bash
# Check unread
/charlie-email unread

# Show inbox
/charlie-email inbox
```

---

## Notes

- **MCP Server:** `mcp-proxy-fastmail-bin` running on M5
- **Status:** MCP verified running, skill integration TODO
- **Next:** Wire to actual FastMail MCP tools via ToolSearch

---

## TODO

1. Use ToolSearch to discover FastMail MCP tools
2. Implement actual MCP tool calls
3. Add HTML formatting for email list display
4. Add send draft functionality
