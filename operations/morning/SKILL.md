---
name: morning
description: Run the mandatory session-start sequence deterministically — rules registry, knowledge base, project handoff, task sweep, in a fixed order with no steps skipped or reordered under time pressure. Use this at the start of every working session, when the user says "let's get started," "what's the status," "morning," or any variant, and whenever CLAUDE.md's Session Start section would otherwise be reconstructed from memory rather than followed exactly.
---

# Morning / Session Start

## Why this exists

CLAUDE.md's "Session Start — MANDATORY BLOCKING REQUIREMENTS" has always been a
list of instructions in a config file, not an invocable skill. That meant each
session re-derived the sequence from memory rather than following one fixed
procedure — and on 2026-09-21, exactly that happened: a step was skipped and
another reordered under time pressure once things got busy (specifically,
circling back to the notebook/rules/KB/task-sweep steps if the session's first
actions came back empty, rather than treating that as a hard stop). A
skill file with concrete, copy-pasteable commands removes the
reconstruction-from-memory step entirely — the sequence is identical every
session because it's read, not recalled.

**This is enforcement infrastructure, not new judgment.** Nothing here is a new
policy; it's the existing CLAUDE.md sequence made deterministic. If CLAUDE.md's
Session Start section changes, update this file to match — don't let the two
drift into different sequences.

## The sequence — run in this order, don't skip, don't reorder

Each step is a hard stop, not a suggestion: if a step comes back empty or
errors, that is itself information (see "If a step returns nothing" below) —
it is not a reason to skip ahead to the next step and treat the empty result
as "nothing to report."

### 1. Load the Execution Protocol

Read `Standards/Agent Execution Protocol.md` (vault root) before any other
work. This sets the ground rules everything else operates under.

### 2. Query the Rules Registry

```bash
curl -s "http://localhost:5682/rules?tier=golden"
```

If this reports 0 rules or errors, **stop** — do not proceed on assumed
rules. This is the one step CLAUDE.md itself already calls a hard blocker;
treat it that way here too.

### 3. Query the knowledge base

```bash
kb search "<project> recent activity" -n handoffs -l 5
```

open-notebook is the KB. Do not substitute the vault for this step — vault
project notes are frozen historical record (per `feedback_vault_historical_only`),
not a live source, even though they're easy to reach in this same working
directory.

### 4. Read the project handoff

```bash
# Prefer the repo's own HANDOFF.md:
# ~/Projects/<repo>/HANDOFF.md
# If no local repo, fall back to the KB:
kb search "<project> HANDOFF" -n handoffs
```

### 5. Task sweep

```bash
curl -s "http://localhost:5682/tasks?owner=CLAUDE&status=pending"
```

REST only — never a SQLite file directly (`rest-api-only`).

## If a step returns nothing

An empty result from step 3, 4, or 5 is a legitimate outcome (nothing
pending, nothing recent) — but it must be an *observed* empty result, not an
*assumed* one because time was short and the step got skipped. If you find
yourself about to summarize "nothing much going on" without having actually
run all five commands this session, that's the failure mode this skill
exists to prevent — go back and run the ones you skipped before reporting
status to the user.

## After the sweep

Summarize what steps 2–5 actually returned (rules count, KB hits, handoff
state, pending task count) before doing anything else. This summary is the
proof the sequence ran, not just a courtesy.
