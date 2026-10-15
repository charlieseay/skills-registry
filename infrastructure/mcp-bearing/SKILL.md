---
name: mcp-bearing
description: Model routing cockpit — use when deciding which LLM (Claude, Gemini, NVIDIA, local Ollama) best fits a task. Bearing analyzes task keywords, tags, and urgency to recommend escalation routes. Includes diagnostics (`bearing doctor`) and routing simulation (`bearing test-route`).
---

# Bearing MCP — Model Routing Cockpit

Bearing is a **local MCP server + CLI hybrid** at `/Users/charlieseay/Projects/bearing` that helps
route tasks to the right LLM (Claude, Gemini, NVIDIA Integrate API, or local Ollama). It's
designed for Cursor/VSCode integration but also works as a standalone MCP server via mcp-proxy.

The MCP server exposes 2–5 tools depending on configuration (see `_effective_tools()` in
server.py); the CLI offers separate diagnostic and simulation commands. This skill covers both,
with an emphasis on real-world gotchas found by reading the source.

## TL;DR: When to use Bearing

- **Routing a task to the right model** when you're unsure which LLM is best: call `suggest_escalation`.
- **Debugging a routing decision** or understanding why Bearing recommends Claude over Gemini: run
  `bearing test-route "<task>"` or call `suggest_escalation` with the same task + tags.
- **Health check** the routing setup: call `health()` tool or run `bearing doctor`.
- **Don't use it for:** simple queries that fit one model (Claude is almost always right for
  writing/code); Bearing shines when you have multiple models available and want an evidence-based
  choice.

## Tool catalog (2 core tools + conditional 3, verified against server.py 2026-09-30)

### Core tools (always present if config is valid)

**`suggest_escalation(task_description: str, tags: list[str] | None = None) -> dict`**
- Analyzes a task string (and optional tags list) to recommend which route to use.
- Returns a routing decision with:
  - `recommendation`: "claude" | "gemini" | "nvidia" | "local" (whichever is enabled and best fit)
  - `reason`: Explanation of the decision (e.g., "Code/architecture task.")
  - `confidence`: 0.65–0.99 (how sure Bearing is about this recommendation)
  - `auto_route`: true/false (whether confidence meets the auto_route_confidence threshold)
  - `priority`: "HIGH" | "MEDIUM" | "LOW" (based on confidence)
  - `router`: "keyword" (currently only keyword-based routing is implemented)
  - `fallback`: true/false (whether this is a fallback if the recommended route is disabled)
- Example:
  ```json
  {
    "task_description": "refactor the API retry logic",
    "recommendation": "claude",
    "reason": "Code/architecture task.",
    "confidence": 0.9,
    "auto_route": true,
    "priority": "HIGH"
  }
  ```
- **Tags parameter:** Pass a list of categories (e.g., `["pii", "private_code"]`) to trigger
  policy-based routing. If any tag is in `config.policy.local_only_categories`, Bearing forces
  `recommendation: "local"` with `confidence: 0.99` and `auto_route: true` regardless of task content.
  This is the **only way to force local routing** without modifying the task text to include
  "calendar" or other local keywords.

**`health() -> dict`**
- Returns a dict summarizing the routing config's health: which routes are available, which CLIs
  are installed, whether proxies/runtimes are reachable.
- Calls `run_doctor()` internally (see below) and returns only the checks dict (not the exit code).
- Example: `{"status": "ok", "checks": [{"name": "claude_cli", "ok": true, "message": "Found /opt/homebrew/bin/claude in PATH."}], "effective_tools": ["suggest_escalation", "health", "ask_claude", ...]}`
- Use this to confirm all your routes are healthy before dispatching a high-stakes task.

### Conditional tools (present if config enables them + health checks pass)

**`ask_claude(prompt: str, context: str = "") -> dict`**
**`ask_gemini(prompt: str, context: str = "") -> dict`**
**`ask_nvidia(prompt: str, context: str = "", lane: str = "balanced", max_tokens: int = 2048) -> dict`**
- Direct query tools — if enabled in config and the corresponding CLI is installed.
- All return `{"success": true/false, "response": "...", "elapsed_s": <float>, "model": "..."}`
  or `{"success": false, "error": "<reason>", ...}`.
- `ask_claude` and `ask_gemini`: pass task + context; they run the installed CLI tool in a
  subprocess and return the response.
- `ask_nvidia`: includes `lane` (routing preference; valid: "fast", "balanced", "large", "code",
  "thinking") and `max_tokens` (64–8192, auto-clamped). Runs `~/.local/bin/ask_nvidia` subprocess.
- **Gotcha:** Each query runs a subprocess, which has subprocess overhead (300–500ms on this Mac
  even for a trivial call). For simple queries, consider calling the CLI directly rather than
  via the MCP tool.

**`ask_local_model(prompt: str, context: str = "") -> dict`**
- Direct query to Ollama (or other local runtime) if `config.routes.local.enabled=true`.
- Posts to the local model's `/api/chat` endpoint and returns `{"success": true, "response": "...",
  "model": "local:<model_id>", "runtime": "ollama"}`.
- Returns error if the runtime is not reachable.

## CLI commands (use instead of MCP tools for one-off inspection)

All commands read from `~/.config/bearing/bearing.config.json` unless you pass `--config <path>`.

**`bearing init`** — interactive onboarding (one-time setup)
- Asks: mcp-proxy? local model runtime? which CLIs are installed? which model for local?
- Writes:
  - `~/.config/bearing/bearing.config.json` (the config this MCP server reads)
  - `~/.config/bearing/routing-policy.json` (local-only policy rules)
  - `~/.config/bearing/.env.example` (env var reference)
  - `~/.config/bearing/NEXT-STEPS.md` (copy/paste MCP snippet for editor integration)

**`bearing doctor [--json]`** — health check (run before dispatching a high-stakes task)
- Validates config thresholds, checks CLI availability, tests Ollama/proxy reachability.
- Exit code 0 if all checks pass, 1 if any fail.
- Output: formatted table by default, JSON with `--json`.
- Example output:
  ```
  [PASS] config         Loaded config.
  [PASS] thresholds     Thresholds valid.
  [PASS] claude_cli     Found /opt/homebrew/bin/claude in PATH.
  [PASS] gemini_cli     Found /opt/homebrew/bin/gemini in PATH.
  [PASS] ask_nvidia     ask_nvidia script at ~/.local/bin/ask_nvidia
  [FAIL] local_runtime  Ollama not reachable at http://localhost:11434.
  
  Effective tools:
  - suggest_escalation
  - health
  - ask_claude
  - ask_gemini
  
  STATUS: DEGRADED
  ```

**`bearing list-tools [--json]`** — show which tools are available (subset of `doctor`)
- Faster than `doctor` if you only care about effective tool availability.
- Returns a list of tool names that will work given the current config + health.

**`bearing test-route "<task>" [--tags "tag1,tag2"] [--json]`** — simulate a routing decision
- Same as calling `suggest_escalation()` but as a one-liner; useful for validating routing
  policies without writing a script.
- Example:
  ```bash
  bearing test-route "refactor the API retry logic" --tags code,architecture
  bearing test-route "Is Ollama running?" --json
  ```
- Output (default): formatted decision tree; with `--json`: just the dict.

**`bearing serve [--config <path>]`** — run as MCP server
- Starts the MCP stdio server. Used by mcp-proxy or editor integrations.
- Config path defaults to `~/.config/bearing/bearing.config.json` or env var `BEARING_CONFIG_PATH`.

## Configuration deep-dive (read ~/.config/bearing/bearing.config.json)

The config is a JSON file with these key sections:

### routes (which LLMs are available)

```json
{
  "claude": {
    "enabled": true,
    "command": "/opt/homebrew/bin/claude",
    "args": ["-p", "{prompt}"],
    "timeout_seconds": 60
  },
  "gemini": {..., "enabled": true},
  "nvidia": {..., "enabled": true, "command": "~/.local/bin/ask_nvidia", ...},
  "local": {
    "enabled": false,
    "runtime": "ollama",
    "model": "qwen2.5vl:7b",
    "endpoint": "http://localhost:11434",
    "timeout_seconds": 45,
    "tool_enabled": false,
    "routing_enabled": false
  }
}
```

- `enabled`: if false, that route is unavailable for routing decisions + its tool won't be registered.
- `timeout_seconds`: subprocess timeout. If the CLI hangs, the MCP tool fails after this period.
- `args` (Claude/Gemini): template strings; `{prompt}` is replaced with the actual task at runtime.
- `local.tool_enabled`: if true, `ask_local_model` MCP tool is registered (requires `enabled=true` + valid `model`).
- `local.routing_enabled`: if true, the router can choose "local" as a recommendation (otherwise
  local is only used for policy local-only tags).

### routing (how Bearing decides)

```json
{
  "ambiguous_default": "claude",
  "auto_route_confidence": 0.85,
  "confirm_min_confidence": 0.6,
  "incident_bypass_to": "claude",
  "urgency_signals": ["down", "outage", "broken", "500", "not responding", "incident", "failing"]
}
```

- `ambiguous_default`: which route to pick when no keyword matches (Bearing can't decide).
- `auto_route_confidence` (default 0.85): if confidence >= this, set `auto_route: true`.
- `confirm_min_confidence` (default 0.6): if confidence < this, force `ambiguous_default` regardless
  of matched keywords (super-low confidence = don't trust the keyword match).
- `incident_bypass_to`: if any urgency signal is in the task text, immediately route to this model
  with confidence 0.95 (overrides all other routing logic).
- `urgency_signals`: keywords that trigger the bypass (e.g., "500", "outage", "down").

### policy (local-only enforcement)

```json
{
  "local_only_categories": ["secrets", "credentials", "pii", "private_code"]
}
```

- If `suggest_escalation` is called with tags in this list (e.g., `tags=["pii"]`), Bearing forces
  `recommendation: "local"` and `confidence: 0.99`, overriding all routing logic.
- This is the only way to enforce local-only processing without changing task text.

## Routing algorithm (how Bearing makes decisions)

In order, Bearing checks:

1. **Policy bypass:** If any tag is in `local_only_categories`, recommend local with 0.99 confidence.
2. **Urgency bypass:** If any `urgency_signal` is in the task text (case-insensitive substring),
   recommend `incident_bypass_to` (default Claude) with 0.95 confidence.
3. **Keyword matching:**
   - CODE_KEYWORDS include "implement", "refactor", "debug", "code", "python", "typescript", "mcp" → Claude (0.9 confidence)
   - RESEARCH_KEYWORDS include "research", "latest", "news", "compare", "search" → Gemini (0.88 confidence)
   - LOCAL_KEYWORDS include "calendar", "reminder", "file", "summarize", "extract" → Local (0.8 confidence)
   - If no keyword matches → `ambiguous_default` (0.65 confidence)
4. **Threshold enforcement:**
   - If confidence >= `auto_route_confidence` (0.85), set `auto_route: true`
   - If confidence < `confirm_min_confidence` (0.6), override to `ambiguous_default` and set `auto_route: false`
5. **Route availability:** If the recommended route is disabled, fall back to the next enabled route
   (Claude → Gemini → Local, in preference order).

## Known gotchas (found by reading server.py directly)

1. **Keywords are case-insensitive substring matches.** "refactor" in the task text triggers Claude
   routing; so do "REFACTOR", "refactoring", etc. If your task says "don't refactor this" (negation),
   Bearing still routes to Claude because the keyword matching doesn't understand negation. Use
   `tags=` to force routing if negation matters.

2. **Confidence can't exceed 0.99.** Policy local-only tags and urgency bypass both max out at 0.99–0.95.
   The router always leaves a tiny margin of uncertainty. This is intentional; it means Bearing
   never claims 100% certainty.

3. **MCP subprocess overhead is real.** Each `ask_*` tool call forks a subprocess (Claude CLI,
   Gemini CLI, or ask_nvidia script). Overhead is 300–500ms even for a trivial query. If you're
   calling Bearing MCP tools in a loop (e.g., "route 100 tasks"), consider batching or calling
   the CLI directly instead.

4. **Stdio corruption on nested MCP calls.** Bearing's `ask_claude` / `ask_gemini` tools run a
   subprocess with `stdin=subprocess.DEVNULL` to prevent the subprocess from consuming bytes from
   the MCP transport. If you're testing Bearing nested inside another MCP server, be aware that
   stdio handling is fragile. The tool includes workarounds (flushing stdout/stderr before/after
   subprocess calls) but it's not bulletproof.

5. **Config validation is silent.** If `confirm_min_confidence > auto_route_confidence`, Bearing
   raises ValueError on load. But typos in the config file (e.g., "claude" spelled "claud")
   silently load as disabled routes. Run `bearing doctor` to catch these.

6. **Local routing requires Ollama by default.** The code says "only Ollama runtime is implemented
   for ask_local_model in this release" (see ask_local_model() at line 356). If you configure
   a different runtime, `ask_local_model` will fail with "Only Ollama runtime is implemented...".
   The config accepts `runtime: "lmstudio"` etc., but the tool doesn't support it yet.

7. **NVIDIA Integrate API requires `~/.local/bin/ask_nvidia`.** Bearing assumes this script exists
   and is executable. If it's missing or broken, `ask_nvidia` tool will fail with "Command not found"
   and `bearing doctor` will mark it FAIL. The script is not part of Bearing; it's an external
   wrapper around the NVIDIA CLI.

8. **Tags parameter is optional but powerful.** Most uses of `suggest_escalation` don't pass tags
   (just the task string). But if you want to force local routing or override keyword matching,
   pass tags = `["pii"]` or `["private_code"]` and the policy will take over. This is the only
   escape hatch from keyword matching.

## Environment facts (cross-check before relying on)

- Bearing source: `/Users/charlieseay/Projects/bearing/src/bearing/server.py`
- Bearing CLI: `/Users/charlieseay/Projects/bearing/.venv/bin/bearing` (installed to path via entry point)
- Config: `~/.config/bearing/bearing.config.json` (created by `bearing init`)
- MCP entry point: `bearing serve` (registered in pyproject.toml)
- Python version: 3.12+ (see pyproject.toml)

## Quick self-check: Is this skill stale?

```bash
# 1. Check that bearing is in the proxy config
python3 -c "import json; d=json.load(open('/Users/charlieseay/.config/mcp-proxy/config.json')); \
  print(json.dumps(d['mcpServers'].get('bearing', {}), indent=2))"

# 2. Run bearing doctor to see current effective tools
bearing doctor

# 3. Check the source for new @server.tool() decorators (should be 2 core + up to 3 conditional)
grep -n '@server.tool()' /Users/charlieseay/Projects/bearing/src/bearing/server.py
```

If the tool count has changed, this skill needs updating. Also re-check if the routing algorithm
has new keywords or thresholds (search for `URGENCY_SIGNALS`, `CODE_KEYWORDS` etc. in server.py).

## When to use vs. alternatives

**Use Bearing MCP tools when:**
- You're deciding between multiple LLMs and want an evidence-based recommendation.
- You have a config with multiple routes enabled (Claude + Gemini + local Ollama).
- You want to avoid manual routing decisions and trust the keyword heuristics.
- The task has sensitivity tags (PII, private code) and you want policy-based enforcement.

**Use CLI (`bearing test-route`) instead when:**
- You're testing a routing decision ad hoc (faster to run from bash than set up MCP).
- You don't have MCP set up or don't want the subprocess overhead of the MCP wrapper.

**Don't use Bearing at all when:**
- You already know which LLM is best for your task (e.g., "I need Claude for writing").
- You only have one LLM available (routing is meaningless if you have no choice).
- You're in a context where calling a subprocess is forbidden (some sandboxes).
