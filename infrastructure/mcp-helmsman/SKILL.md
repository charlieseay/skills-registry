---
name: mcp-helmsman
description: Query and dispatch the helmsman task queue via MCP (task summaries, status lookup, task creation). The MCP wrapper is redundant with the REST API at http://localhost:5682 used throughout the fleet; use the REST API directly for simplicity unless you're in a tool-constrained environment (e.g., testing MCP specifically). MCP is a thin wrapper exposing 6 tools.
---

# Helmsman MCP — Task Queue Tools

The helmsman MCP server at `/Users/charlieseay/Projects/helmsman-mcp/server.py` is a
**thin wrapper around the helmsman REST API** (http://localhost:5682). Every tool
translates directly into one or more REST calls to `:5682/tasks`. The REST API is
already used extensively throughout this fleet and is the canonical interface; the MCP
wrapper exists primarily for environments where you want MCP-standardized tool access
instead of raw HTTP.

**Verdict: MCP adds no functionality beyond REST.** If you're already familiar with
`curl http://localhost:5682/tasks`, use that directly for simpler, faster lookups.
Use the MCP tools only if integrating with a tool-constrained MCP client or testing
MCP specifically.

## Quick comparison: MCP vs REST for the same query

Both return the same data. Pick your interface:

```bash
# REST — direct HTTP
curl -s http://localhost:5682/tasks?status=pending

# MCP — via the helmsman tool wrapper (slower due to MCP overhead, same result)
task_queue_summary()  # returns count + breakdown
```

## Tool catalog (6 tools, verified against server.py 2026-09-30)

All tools are read-only (`task_*` prefix) or one-way dispatch (`dispatch_task`,
`update_task_status`). All return JSON.

### Read tools (query existing tasks)

**`task_queue_summary()`** — no arguments
- Returns total active count + breakdown by status, owner, project, and 10 most recent tasks.
- "Active" = status in (pending, assigned, standby, qa_failed).
- Fastest way to see fleet health and what's in the queue right now.
- Returns: `{"total": <int>, "by_status": {...}, "by_owner": {...}, "by_project": {...}, "recent_tasks": [...]}`

**`tasks_by_owner(owner: str)`** — case-insensitive owner name
- Returns all active tasks assigned to a specific owner.
- Valid owners: `claude`, `cursor`, `gem`, `charlie`, `bosun`, `helmsman`,
  `nvidia-agent`, `NVIDIA-BAL`, `NVIDIA-FAST`, `NVIDIA-THINK`, `AIDER-GEM`.
- Returns: `{"owner": "<canonical>", "total": <int>, "tasks": [...]}`
- Example: `tasks_by_owner("claude")` returns all tasks owned by CLAUDE or its aliases (C+Y).

**`tasks_by_project(project: str)`** — partial match, case-insensitive
- Returns all active tasks for a project (fuzzy substring match against project names).
- Example: `tasks_by_project("enchapter")` matches "Enchapter", "enchapter-api", etc.
- Returns: `{"query": "<original>", "total": <int>, "tasks": [...]}`

**`get_task(task_num: int)`** — fetch one task by number
- Returns full task details including `brief_text`, `status`, `owner`, `qa_results`.
- Example: `get_task(1000744)` returns all fields for task #1000744.
- Returns: full task JSON object or `{"error": "<message>"}`

### Write tools (create/update tasks)

**`dispatch_task(task, owner, project, effort, brief_text)`** — create and queue a new task
- **Required fields:**
  - `task`: Short title (1 sentence).
  - `owner`: See valid owners in `tasks_by_owner` above. DO NOT use CURSOR, GEM, GEMINI,
    C+C, C+G — these are `ROUTING_BLOCKED` and will never execute.
  - `project`: Project name (e.g. "Enchapter", "Lab", "Hone").
  - `effort`: One of `S | M | L | XL` (size bucket).
  - `brief_text`: Full brief including these exact ## sections (dispatch rejects with 422 if missing):
    ```
    ## Prior Lessons
    ## Goal
    ## Context
    ## Steps
    ## Dependencies
    ## Potential Issues
    ## Research Questions
    ## Expected Output
    ## Success
    ## Verification
    ## Security Review
    ## Functional Test
    ## Recovery
    ## QA Checklist
    ```
- Returns: `{"task_num": <int>, "status": "...", "owner": "...", ...}` on success, or
  `{"error": "<message>", "hint": "Check brief_text has all required ## sections"}` on failure.
- **Post-dispatch webhook note:** dispatch POSTs to `http://localhost:5680/webhook/task-dispatch`
  with a secret header loaded from `/Volumes/data/secrets/dispatch_webhook_secret` — the tool
  handles this automatically, but if the webhook is down, you'll get a fallback error message
  telling you to use the REST API directly at `:5682/tasks`.

**`update_task_status(task_num, status, note="")`** — flip a task's status
- **Valid transitions:**
  - `pending` → `assigned` (picking up a task)
  - `assigned` → `standby` (blocked, waiting on dependency)
  - `assigned` → `qa_failed` (QA found issues)
  - Any active → `cancelled` (abort the task)
  - Cannot change shipped/complete tasks.
- `note` (optional): explanatory string to append to the task's brief.
- Returns: `{"updated": true, "task_num": <int>, "new_status": "...", ...}` or `{"error": "..."}`

## Known gotchas (found by reading server.py directly)

1. **Owner aliasing is transparent but exact.** `tasks_by_owner("claude")` matches both
   `"CLAUDE"` and `"C+Y"` in the DB (see OWNER_ALIASES dict in server.py line 44–58).
   Canonical output always normalizes to a single name (e.g., "CLAUDE" or "GEM"), but the
   raw DB can have variations. If a task seems to disappear or reappear depending on which
   owner name you query, check if the raw DB owner is one of the aliases.

2. **dispatch_task requires ALL 13 ## sections verbatim.** Missing even one (e.g., accidentally
   writing `# Goals` instead of `## Goal`) returns 422 from the webhook. The tool can't
   validate the brief before POSTing; it only tells you after the fact. **Pro tip:** construct
   your brief programmatically with a template function rather than hand-crafting it each time.

3. **REST fallback on webhook failure.** If the dispatch webhook at `:5680/webhook/task-dispatch`
   is unreachable, the tool returns an error and suggests using the REST API directly at
   `:5682/tasks`. This is not a bug; the webhook is a convenience. You can POST to `:5682/tasks`
   directly if needed, but it bypasses the dispatch secret-header validation (the REST API at
   `:5682` has its own auth model).

4. **task_queue_summary fetches all active tasks every call.** On a queue with thousands of tasks,
   this can be slow. If you only need one task, use `get_task(num)` instead. If you need to batch
   query by owner, call `tasks_by_owner` once rather than looping `get_task`.

5. **No pagination.** All `task_*` read tools return the entire result set. If the queue is large,
   expect a large JSON response. The tool does not support limit/offset/cursor pagination.

## Environment facts (cross-check in MEMORY.md or live query)

- Helmsman REST API: `http://localhost:5682` (canonical).
- Dispatch webhook: `http://localhost:5680/webhook/task-dispatch` (with secret header).
- Config: `/Users/charlieseay/Projects/helmsman-mcp/server.py` (source of truth for tools/parameters).
- MCP command: `/Users/charlieseay/Projects/helmsman-mcp/venv/bin/python3 server.py`.

## Quick self-check: Is this skill stale?

```bash
# Check that helmsman MCP is running
python3 -c "import json; d=json.load(open('/Users/charlieseay/.config/mcp-proxy/config.json')); \
  print(json.dumps(d['mcpServers']['helmsman'], indent=2))"

# Query the MCP server's own tools/list to see if new tools were added
# (Not a simple one-liner; requires MCP handshake. If you need to update this,
#  re-run the MCP client's tools/list and compare against the 6 tools above.)

# Or just check the source directly for new @mcp.tool() decorators:
grep -n '@mcp.tool()' /Users/charlieseay/Projects/helmsman-mcp/server.py
```

If grep returns more than 6 tools, this skill is missing documentation for new tools — update it.

## When NOT to use this MCP wrapper

- **Direct REST queries are faster.** If you're already using curl or requests, stick with HTTP.
- **CLI scripts.** The `helmsman` tool is implemented in Python; if you're in a bash script, curl
  is simpler and doesn't require Python.
- **Task creation at scale.** Dispatching 100 tasks via MCP will be slower than batching via REST;
  the webhook itself is synchronous and has no bulk API.

## When to use the MCP wrapper

- **Tool-constrained environments** where you can only call registered MCP tools (e.g., testing MCP
  integration, or working within an MCP-only client).
- **Standardized tooling.** If other tools you're using are already MCP-based, using helmsman MCP
  keeps your interface consistent.
- **Learning/validation.** Use the MCP wrapper if you're testing MCP itself or want to see how a
  thin REST-to-MCP adapter works.
