---
name: mcp-mem0
description: Persistent agent memory via mem0 FastAPI service. Store/search/list/delete facts, preferences, session context for agents (esp. Sonique voice assistant). Requires mem0 service at http://localhost:8127 running + valid agent_name. Semantic vector search over stored memories.
---

# Mem0 Memory MCP

The `mem0` MCP server (proxy name `mem0`, Python FastMCP launcher at
`/Users/charlieseay/Projects/mem0-mcp/.venv/bin/mem0-mcp`) bridges the **local
mem0 FastAPI service** (http://localhost:8127) to the Model Context Protocol.
It provides persistent memory operations for agents — storing facts,
preferences, session context, and retrieving them via semantic search.

**Designed for:** Sonique (voice assistant), Hermes Agent, and any MCP-compatible
client that needs long-term agent memory independent of conversation context.

**Hard dependency:** The mem0 FastAPI service must be running at
http://localhost:8127. Without it, all tool calls fail immediately with
"Cannot reach mem0 service" errors on startup. The server performs a health
check during initialization and exits with status 2 if the service is
unreachable.

## How it differs from Claude's built-in memory system

This is **not** Claude's conversation memory or @memory tool. It is a **separate
persistent store**:
- **Claude memory:** Persists facts across Claude sessions (built-in, managed by Anthropic)
- **mem0 memory:** Agent-specific facts, queryable by agent name, stored in a
  **separate HTTP service** (not Claude's system). Useful for Sonique to remember
  user preferences across voice sessions, or for Hermes to retain state across
  workflow runs.

Do not confuse them. If you need to store state specifically for an agent (e.g.,
"Sonique knows the user's favorite music genre"), use mem0. If you need to teach
Claude a fact for this conversation, use Claude's @memory or your own notes.

## Tool catalog (4 tools, tested live 2026-09-30 against /Users/charlieseay/Projects/mem0-mcp/src/mem0_mcp/server.py:29-187)

**Write memory:**
- `memory_write(agent_name, content, memory_type="long_term", session_id="", expires_in_days=0)` → str
  - Stores a fact, preference, or piece of information in persistent memory.
  - **Parameters:**
    - `agent_name` (string, required) — agent identifier (e.g., "sonique", "helmsman")
    - `content` (string, required) — the memory content to store (e.g., "User prefers jazz music")
    - `memory_type` (string, default "long_term") — type classification ("long_term", "short_term", or custom types)
    - `session_id` (string, default "") — optional session identifier for context grouping
    - `expires_in_days` (int, default 0) — auto-expiry in N days (0 = never expires)
  - **Returns:** JSON with `status: "success"` and `data` object (includes memory_id)
  - **Error:** HTTP errors or timeouts return `"Error: Failed to write memory — <details>"`

**Search memory:**
- `memory_search(agent_name, query, limit=5)` → str
  - Semantic vector search across an agent's stored memories.
  - **Parameters:**
    - `agent_name` (string, required) — agent to search memories for
    - `query` (string, required) — search query (e.g., "What music does the user like?")
    - `limit` (int, default 5) — max results to return (typical use: 1–10)
  - **Returns:** JSON with `status: "success"` and `data` array of memories + similarity scores
  - **Error:** HTTP errors return `"Error: Failed to search memories — <details>"`
  - **Behavior:** Embeddings are pre-computed server-side; this tool queries by semantic similarity, not keyword matching.

**List memory:**
- `memory_list(agent_name, memory_type="", limit=10)` → str
  - List stored memories for an agent (optionally filtered by type).
  - **Parameters:**
    - `agent_name` (string, required) — agent identifier
    - `memory_type` (string, default "") — optional filter ("long_term", "short_term", etc.). Empty = all types.
    - `limit` (int, default 10) — max memories to return (clamped by server)
  - **Returns:** JSON with `status: "success"` and `data` array of memories (most recent first)
  - **Error:** HTTP errors return `"Error: Failed to list memories — <details>"`

**Delete memory:**
- `memory_delete(memory_id)` → str
  - Permanently remove a single memory by ID.
  - **Parameters:**
    - `memory_id` (string, required) — unique ID of the memory to delete (returned by `memory_write` or `memory_list`)
  - **Returns:** JSON with `status: "success"` and `message: "Memory <id> deleted"`
  - **Error:** HTTP errors return `"Error: Failed to delete memory — <details>"`

## mem0 service health & diagnostics

**Startup check:**

The server performs this health check on startup (blocking):
```python
response = await client.get(f"{MEM0_BASE_URL}/health")
return response.status_code == 200
```

If unreachable, stderr prints:
```
mem0-mcp v<version> — startup failed:
  Cannot reach mem0 service at http://localhost:8127/health
  
Required:
  mem0 FastAPI service running at http://localhost:8127
```

Server exits with status 2 (not 1 — intentional to signal config error, not crash).

**Runtime checks:**

Tool calls use a 10-second timeout per request. If the service is slow or down:
```
Error: Request to mem0 service timed out (>10.0s)
```

If the service returns an HTTP error (e.g., 500, 404):
```
Error: Failed to write memory — HTTP 500 Internal Server Error
```

**To verify the service is running:**
```bash
curl -s http://localhost:8127/health
```

Should return HTTP 200 with a JSON health response. If it returns 404 or times out,
the service is not running — check `/Volumes/data/containers/` for a mem0 Docker
container or systemd service.

## Known issues & real-world gotchas (tested 2026-09-30)

**1. mem0 service is NOT auto-started; must run externally**
- This MCP server is a **client** to mem0. It assumes the service is already
  running.
- If you stop the mem0 service, all tool calls will fail with timeouts.
- **Fix:** Restart mem0 (Docker, systemd, or manual process). The MCP server
  will reconnect automatically on the next tool call.

**2. Agent names are case-sensitive and not auto-validated**
- `agent_name="sonique"` ≠ `agent_name="Sonique"`
- If you write memories with `agent_name="sonique"` and later query with
  `agent_name="Sonique"`, the search returns nothing (they're separate namespaces).
- **Best practice:** Establish a convention and stick to it (e.g., always lowercase).

**3. Memory search is semantic, not keyword-based**
- `memory_search(agent_name="sonique", query="favorite jazz artists")` returns
  memories **semantically similar** to "favorite jazz artists", not necessarily
  containing those exact words.
- If a memory says "User loves Charlie Parker and John Coltrane", a search for
  "jazz" may not match (depends on embeddings).
- **Workaround:** Use `memory_list()` and filter client-side if keyword search is critical.

**4. No built-in TTL enforcement; `expires_in_days` is advisory**
- When writing a memory with `expires_in_days=7`, the server **stores** that
  metadata.
- The server does **not** automatically delete expired memories on a schedule.
- **Behavior:** Expired memories may still appear in list/search until manually
  deleted or the mem0 backend runs cleanup.
- **Workaround:** Periodically call `memory_list()` and `memory_delete()` stale memories.

**5. Request timeout is hard-coded at 10 seconds**
- The server uses `timeout=10.0` for all HTTP requests to mem0.
- If the mem0 service is slow or under load, tools timeout and fail.
- No retry logic; timeout = immediate failure.
- **Fix:** Scale the mem0 service (increase replicas, optimize queries) or tune the timeout in source code.

**6. No authentication between MCP server and mem0 service**
- Both run on localhost; traffic is not encrypted.
- If mem0 is exposed to the network, anyone on that network can read/write memories.
- **Security posture:** This setup is only safe in a **trusted local environment** (single machine or private network).

## Real-world example: Sonique using mem0

Sonique (voice assistant) calls the MCP:
```
User says: "Remember, I like jazz and coffee."

→ memory_write(agent_name="sonique", content="User likes jazz and coffee", memory_type="long_term")
→ Returns: {"status": "success", "data": {"memory_id": "abc123"}}

Later, user asks: "What do I like?"

→ memory_search(agent_name="sonique", query="What do you like?")
→ Returns: {"status": "success", "data": [
    {"id": "abc123", "content": "User likes jazz and coffee", "score": 0.92},
    ...
  ]}

→ Sonique speaks back: "You like jazz and coffee."
```

## Quick self-check

**Confirm mem0 service is running:**
```bash
curl -s http://localhost:8127/health
```

Should return HTTP 200. If it times out or returns 404, start the mem0 service.

**Test a memory write (requires mem0 service running):**

```bash
python3 -c "
import httpx
import json

response = httpx.post(
    'http://localhost:8127/memories',
    json={'agent_name': 'test_agent', 'content': 'Test memory', 'memory_type': 'long_term'}
)
print(response.status_code)
print(response.json())
"
```

Should return HTTP 200 with a JSON object containing `memory_id`.
