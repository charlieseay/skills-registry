---
name: mcp-agy
description: Delegate code archaeology, web lookups, and heavy analysis to the Antigravity CLI via the `agy` MCP server. Use when a task needs git history spelunking, wide repository greps, documentation lookups, adversarial code review, or delegating large/complex analysis that would exhaust Claude's context. Faster than running many search commands yourself; returns only the answer, not the raw data.
---

# AGY Bridge MCP Server

The `agy` MCP server (proxy name `agy`, npx
`agy-bridge`) delegates work to the Antigravity CLI, which has full tool access
(shell, file reads, web) and a separate, fresh model context per call. Use it
to offload heavy analysis, git spelunking, and documentation lookups that would
be tedious or expensive to do locally.

**Model routing:** Tasks automatically route to appropriate models (Claude,
Gemini, or others) based on task type. Pass `model:` override only if you have a
strong reason — the tool's default routing is usually better.

## Tool catalog (6 tools, confirmed live 2026-09-30)

### Core tools (use these for most tasks)

- **`deep_search`** — Git archaeology: "When was X refactored and why?"
  - Searches `git log`, `git blame`, `git diff` across a repo
  - Best for: tracing when/why code changed, finding related commits,
    understanding refactoring decisions
  - Example: `deep_search("when was the auth middleware refactored and why")`
  - Returns: Structured findings with commit messages, authors, dates, diffs

- **`web_lookup`** — Documentation & external knowledge
  - Web search with result summaries (not raw HTML)
  - Best for: library docs, API references, current versions, error messages,
    external knowledge newer than training data
  - Example: `web_lookup("Notion MCP server capabilities tools available")`
  - Returns: Curated answers, not full web pages

- **`analyze_files`** — Heavy file analysis without loading into your context
  - Analyzes large/multiple files (logs, diffs, generated code, database dumps)
  - Best for: cross-file reviews, comparisons, summarizing large outputs
  - Files never enter your context — only the answer does
  - Example: `analyze_files(["Dockerfile", "docker-compose.yml"], "What ports
    are exposed and what services use them?")`
  - Returns: Structured analysis, not raw file content

- **`delegate`** — Raw delegation for open-ended tasks
  - Pass a complete task prompt; agy executes it with full tool access
  - Best for: complex multi-step tasks that don't fit other tools
  - Example: `delegate("Find all uses of the 'AuthContext' hook in the React
    codebase and identify the components that depend on it")`
  - Returns: Task-specific output (code snippets, lists, structured data)

### Specialized tools (use when feedback/iteration is needed)

- **`adversarial_review`** — Second opinion from a different model family
  - Gemini Pro reviews your plan, code, or design for flaws/edge cases
  - Best for: pre-merge review, design critiques, security/edge-case hunting
  - Example: `adversarial_review(files=["new-auth.ts"], focus="security")`
  - Returns: Critical feedback, not affirmation

- **`follow_up`** — Continue a prior agy session without context reload
  - Use the `session_id` from any prior agy call
  - Best for: refinement questions about results, clarifying findings
  - Example: `follow_up(session_id="abc123", "Can you provide the exact line
    numbers?")`
  - Returns: Answer based on prior session context (no reload needed)

## Real behavior & gotchas (tested 2026-09-30)

### 1. Web lookup can timeout on slow/large responses

`web_lookup` has an internal print timeout — if the query returns massive
amounts of text (e.g., full API reference docs), the tool may emit empty output
even though it found something. Symptom: "agy returned empty output (likely hit
its print-timeout without a response)."

**Workaround:** Narrow the query. Instead of `"Notion API documentation"`, ask
`"Notion database query pagination limits"`. More specific → faster → completes.

### 2. `deep_search` requires a specific question format

Git archaeology works best when phrased as "when/why" questions:
- Good: `"When was error handling refactored and why?"`
- Less effective: `"Error handling changes"` (too vague, may miss commits)

The tool searches commit messages, diffs, and blame output. A specific question
helps it zero in on relevant commits.

### 3. `analyze_files` input limits

- Works well on files up to ~50KB each (logs, code files, CSVs)
- For very large files (>200KB): use `deep_search` on git history instead, or
  split the file and call multiple times
- File paths: absolute or relative to `cwd` (defaults to current directory)

### 4. `delegate` is a catch-all but has session cost

Every `delegate` call opens a fresh agy session. For related questions, use
`follow_up` instead to avoid re-establishing context:

```
# Expensive (two fresh sessions):
delegate("Find all React hooks in src/")
delegate("Now tell me which ones are custom hooks")

# Better (one session, one follow-up):
delegate("Find all React hooks in src/")
follow_up(session_id, "Now tell me which ones are custom hooks")
```

### 5. `adversarial_review` uses Gemini Pro, not Claude

When you pass `focus: "security"` or no focus, Gemini reviews independently.
This is intentional — different model families catch different flaws. Expect
findings that might not match Claude's style.

### 6. Model override is rare; don't pass `model:` unless you have a specific reason

Default routing:
- `deep_search`, `web_lookup`: Claude
- `adversarial_review`: Gemini Pro (by design)
- `analyze_files`, `delegate`: Claude (unless you override)

Overriding to `"Gemini 3.1 Pro (High)"` or similar is supported but usually
unnecessary — the tool knows what it's doing.

## Workflow patterns for common tasks

### Trace when code changed and why

```
1. deep_search("When was the payment handler refactored and why?")
   → Returns: Commits touching payment handler, with messages and diffs
2. If you need more detail on a specific commit, ask follow-up:
   follow_up(session_id, "Show the exact diff from commit X")
```

### Look up API or library documentation

```
web_lookup("Express.js middleware order and execution sequence")
→ Returns: Curated answer about middleware pipeline, not raw docs
```

### Analyze logs or database output without loading full context

```
analyze_files(["error.log", "metrics.csv"], 
  "How many errors occurred per service and what were the top 3 error types?")
→ Returns: Structured summary (no raw logs in your context)
```

### Review code for security issues before merging

```
adversarial_review(files=["auth.ts", "api.ts"], focus="security")
→ Returns: Gemini's critical feedback on auth/API safety
```

### Complex multi-step investigation

```
delegate("""
1. Find all database migrations touching the 'users' table
2. For each migration, extract the schema change
3. Identify any breaking changes (columns removed, types changed)
4. Return a timeline showing schema evolution
""")
```

## When to use each tool

| Task | Tool | Why |
|------|------|-----|
| When was X added/changed in git? | `deep_search` | Fast commit archaeology |
| What does library X do? | `web_lookup` | External knowledge |
| Summarize a large log file | `analyze_files` | Avoids loading huge data |
| Review for bugs/security | `adversarial_review` | Independent model review |
| Multi-step complex task | `delegate` | Full tool access, fresh context |
| Follow-up to prior agy work | `follow_up` | Reuses prior session, cheaper |

## Known environment facts

- Agy installed: `npx -y agy-bridge` (from npm, auto-installs on first use)
- Session IDs are returned by every agy call; save them if you might need
  follow-ups
- Each tool has different latency: web_lookup (~2-5s), deep_search (~1-3s),
  analyze_files (~2-5s for large files)
- Web access: agy can fetch external URLs; DNS and SSL work as normal

## Quick self-check for this skill

```bash
# Verify agy is callable
npx -y agy-bridge --help | head -5

# Verify it's in the MCP proxy config
grep -A 3 '"agy":' /Users/charlieseay/.config/mcp-proxy/config.json
# Should show: "command": "npx", "args": ["-y", "agy-bridge"]

# Quick test (list available models)
npx -y agy-bridge models
```

---

**Last Updated:** 2026-09-30  
**Tools tested:** All 6 live (deep_search, web_lookup, analyze_files, delegate,
adversarial_review, follow_up)  
**Known limitation:** web_lookup can timeout on massive responses; narrow query
if empty output
