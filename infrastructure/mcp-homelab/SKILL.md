---
name: mcp-homelab
description: Unified NPM (Nginx Proxy Manager)/Docker-Portainer/Cloudflare DNS/Home Assistant infrastructure management via the `homelab` MCP server — expose/teardown services, check infrastructure-wide status, manage Docker containers, and DNS records in one tool surface, with a safety-mode system (normal/readonly/dryrun) and two-step confirmation for destructive actions. CURRENTLY BROKEN as of 2026-10-01 (see below) — check whether it's been fixed before relying on it; if still broken, use the individual mcp-portainer and mcp-cloudflare skills instead for those specific domains.
---

# Homelab Infrastructure MCP — CURRENTLY BROKEN

**Confirmed broken live, 2026-10-01.** Running the server directly crashes on
startup:
```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'. This is mcp 2.x,
where FastMCP was renamed to MCPServer (from mcp.server.mcpserver import
MCPServer) and other APIs changed; see the migration guide at
https://py.sdk.modelcontextprotocol.io/v2/migration/#fastmcp-renamed-to-mcpserver
or pin 'mcp<2' to keep running v1 code.
```

**Root cause:** the `mcp` Python package in this project's venv
(`/Users/charlieseay/Projects/homelab-infra-mcp/.venv`) was upgraded to 2.x,
which renamed `FastMCP` to `MCPServer` and changed other APIs. The source at
`/Volumes/data/projects/homelab-infra-mcp/src/homelab_infra_mcp/server.py`
line 7 still does `from mcp.server.fastmcp import FastMCP`, which no longer
exists in the installed package version.

**Before trusting anything below, re-run this check** — if it's been fixed,
delete this warning section and this skill becomes immediately useful (it
documents a well-designed, cross-domain tool):
```bash
timeout 10 bash -c '
printf "%s\n" \
  "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"test\",\"version\":\"1\"}}}" \
  "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}" \
  "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\",\"params\":{}}" \
  | /Users/charlieseay/Projects/homelab-infra-mcp/.venv/bin/homelab-infra
'
```
**Likely fix** (not applied — this skill is documentation, not a fix PR):
either pin `mcp<2` in homelab-infra-mcp's dependencies, or update
server.py's import to `from mcp.server.mcpserver import MCPServer` and
adjust the `FastMCP(...)` constructor call to match the 2.x API per the
migration guide linked in the error.

## What it's designed to do (from source, since live testing isn't possible)

This is a genuinely well-architected cross-domain tool, not a thin wrapper —
worth fixing rather than working around. Real module breakdown from
`server.py`'s `_register_modules()` (lines 111-140):

- **4 base tools** always loaded: `set_mode`, `get_mode`, `confirm_destructive`,
  `server_health` (defined directly in server.py lines 27-108)
- **4 cross-domain tools** (always loaded): `expose_service`,
  `teardown_service`, `service_status`, `infrastructure_overview` — per the
  server's own `instructions` string (lines 17-23), these span NPM +
  Docker/Portainer + Cloudflare DNS in one call each
- **14 NPM tools** (conditional on `"npm" in config.modules`)
- **16 or 18 Docker tools** depending on backend — 18 if using Portainer as
  the backend, 16 if talking to the Docker socket directly
  (`config.docker_backend`)
- **8 DNS/Cloudflare tools** (conditional on `"dns" in config.modules`)
- **Home Assistant module** — present but explicitly marked optional in the
  log line (no tool count logged for it, unlike the others)

**Safety design worth noting even while broken:** `set_mode` supports
`normal`/`readonly`/`dryrun` (with aliases `read-only`/`dry-run` accepted),
and `confirm_destructive(token)` requires a token from a prior call before
executing anything destructive — `validate_confirmation(token)` returns
`None` for an invalid/expired token rather than silently proceeding. This is
a two-step confirm pattern, not a single blind action — if/when this gets
fixed, expect destructive calls to first return a confirmation token, not
execute immediately.

## What to use instead while this is broken

- Docker/Portainer-specific needs → `mcp-portainer` skill (confirmed working,
  5 tools)
- Cloudflare DNS/Workers needs → `mcp-cloudflare` skill (confirmed working,
  89 tools via the local mcp-proxy route)
- Home Assistant needs → `mcp-home-assistant` skill (confirmed working, 20
  tools)
- There is currently no working single-call cross-domain
  `infrastructure_overview` equivalent — you'll need to query each backend
  separately until this is fixed.
