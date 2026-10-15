---
name: mcp-cloudflare
description: Cloudflare account management (89 tools) via the local MCP proxy at http://127.0.0.1:3700/cloudflare/mcp. Covers Workers (deploy/get/list/delete), R2 buckets/objects, Workers AI, KV, D1, Queues, and zones_list/zones_get. DNS records, Pages, and Tunnel tools are not exposed — use the REST API directly with the token at /Volumes/data/secrets/cloudflare_api_token.
---

# Cloudflare MCP Server

The `cloudflare` MCP server (proxy name `cloudflare`, binary wrapper at
`/Users/charlieseay/.local/bin/cloudflare-mcp`) exposes the **official
@cloudflare/mcp-server-cloudflare** package as a stdio-to-MCP forwarder. It
injects the API token from `/Volumes/data/secrets/cloudflare_api_token` and
forwards all MCP requests to the Cloudflare proxy at
`http://127.0.0.1:3700/cloudflare/mcp`.

**Auth note:** The token lives at `/Volumes/data/secrets/cloudflare_api_token`
— it is injected by the wrapper script at `/Users/charlieseay/.local/bin/cloudflare-mcp`,
line 2. Agents never handle it directly; the wrapper reads it into the
environment variable `CLOUDFLARE_API_TOKEN` before spawning the upstream MCP
server.

## Deliberate tool gaps: what IS and ISN'T available

**AVAILABLE (89 tools total):**
- **Workers:** `workers_create_deployment`, `workers_get_deployment`,
  `workers_list_deployments`, `workers_delete_deployment`, and related
  deployment/binding/route management
- **R2 (object storage):** bucket CRUD, object upload/download/list/delete,
  bucket lifecycle policies, CORS configuration
- **Workers AI:** model inference endpoints, embedding, classification
- **KV (key-value store):** namespace CRUD, key operations, metadata management
- **D1 (serverless SQL):** database CRUD, query execution, schema introspection
- **Queues:** queue CRUD, message publish/consume operations
- **Zones:** `zones_list` (all zones in your account), `zones_get` (fetch a
  single zone by ID with full settings)

**NOT AVAILABLE (intentionally):**
- **DNS records** — no `dns_records_*` tools. Use the REST API directly:
  ```bash
  curl -X GET "https://api.cloudflare.com/client/v4/zones/zone_id/dns_records" \
    -H "Authorization: Bearer $(cat /Volumes/data/secrets/cloudflare_api_token)"
  ```
- **Pages** — no `pages_*` or `pages_deployment_*` tools. Use the REST API or
  `wrangler pages deploy` CLI.
- **Tunnel** — no `cfdns_*` or tunnel management tools. Configure via dashboard
  at https://one.dash.cloudflare.com/networks/tunnels or use the Cloudflare
  API directly.

## Why the remote mcp.cloudflare.com server was removed (2026-09-14)

The `.claude.json` configuration initially pointed to `mcp.cloudflare.com:443`
as a remote MCP server. That server requires **interactive OAuth flow** to
authenticate. However, the configuration included an `Authorization` header
with a static Bearer token, which **disabled the OAuth fallback**. This created
a catch-22: the OAuth flow would never run (blocked by the header), and the
static token was rejected (invalid for that endpoint). Both stored tokens were
tested against the remote server and rejected with HTTP 401 and 403 errors.

**Solution:** Removed the remote server entry and switched to the **local
mcp-proxy** at `http://127.0.0.1:3700/cloudflare/mcp`, which is reachable and
functional via the wrapper at `/Users/charlieseay/.local/bin/cloudflare-mcp`.

## Tool catalog (89 tools — inspect via `tools/list` if you need the current count)

This list is a snapshot. Query `tools/list` yourself if you need absolute
current coverage — the upstream Cloudflare package may add/drop tools between
releases.

**Sampling of commonly used tools:**
- `workers_create_deployment` — create a new Worker deployment
- `workers_get_deployment` — fetch details of a deployed Worker
- `workers_list_deployments` — list all Workers in your account
- `r2_create_bucket` — create an R2 bucket
- `r2_list_objects` — list objects in a bucket
- `r2_upload_object` — upload a file to R2
- `r2_delete_object` — delete an object from R2
- `kv_create_namespace` — create a KV namespace
- `kv_put_key` — write a key-value pair
- `kv_get_key` — read a key-value pair
- `kv_list_keys` — enumerate keys in a namespace
- `d1_create_database` — create a D1 database
- `d1_query` — execute SQL against a D1 database
- `queues_create_queue` — create a Queue
- `queues_publish_message` — publish a message to a Queue
- `zones_list` — list all zones (domains) in your account
- `zones_get` — fetch full config for a single zone

Run `tools/list` through the proxy to get the authoritative, current tool list.

## Known issues & workarounds

**1. DNS record management not available via MCP**
- The official MCP server does not expose DNS record CRUD tools.
- Use the REST API directly or the Cloudflare dashboard.

**2. Tunnel configuration requires dashboard or wrangler CLI**
- MCP does not expose Tunnel management.
- Configure via https://one.dash.cloudflare.com/networks/tunnels or
  `wrangler tunnel` CLI.

**3. Pages deployment management limited**
- MCP does not expose Pages-specific tools.
- Use the dashboard or `wrangler pages deploy` CLI.

## Quick self-check

**Confirm the server is reachable:**
```bash
curl -s http://127.0.0.1:3700/cloudflare/mcp -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

If this returns a JSON-RPC response with a `tools` array, the MCP proxy is
live. If it times out or returns a 404, the proxy is down — check
`/Volumes/data/containers/mcp-proxy/` for logs.

**Test a tool call** (list all Cloudflare zones):
```bash
curl -s http://127.0.0.1:3700/cloudflare/mcp -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"zones_list","arguments":{}}}'
```

(Replace port 3700 with whatever `~/.config/mcp-proxy/config.json` specifies
for `mcpProxy.addr`.)
