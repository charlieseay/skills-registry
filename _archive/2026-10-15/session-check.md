---
name: session-check
category: operations
description: Session health check and status review
triggers:
  patterns:
  - session check
  - status check
  - health check
  contexts:
  - monitoring
  - health check
  - status
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when session health check and status review
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 5
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Enforce golden rules and query the Rules Registry at session start.

## Usage

Run this at the start of every session to load current golden/standing rules:

```bash
~/.local/bin/claude-session-start-check
```

## What it does

1. Queries `http://localhost:5682/rules?tier=golden` — loads all golden rules (always apply)
2. Queries `http://localhost:5682/rules?tier=standing` — loads all standing rules (context-triggered)
3. Reports scopes and enforcement methods
4. Confirms the Rules Registry is reachable

## When to run

- **At session start** (before any work)
- **After `/checkpoint`** (verify no new rules were added)
- **Before `/compact`** (already in PreCompact hook)

## Why this exists

Golden Rule #1 in CLAUDE.md says to query the Rules Registry before non-trivial work. This skill makes it one command instead of 3-4 manual curls.

The output is shown directly in the Claude Code console so the AI sees which rules are currently active.
