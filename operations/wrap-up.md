---
name: wrap-up
category: operations
description: End-of-session retrospective and handoff
triggers:
  patterns:
  - wrap up
  - end session
  - session wrap
  - retrospective
  contexts:
  - session management
  - retrospective
  - handoff
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when end-of-session retrospective and handoff
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 15
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Close out the session properly: retrospective first, then knowledge capture, then notes, then checkpoint. `/checkpoint` is a save point you hit constantly mid-session; `/wrap-up` is the true end-of-session ritual and should run once.

**Trigger phrases:** "let's wrap up", "wrap up", "/wrap-up", "call it a day/night".

Run the five phases IN ORDER — retrospective comes first because it's the part that needs the full session context while it's still hot, and checkpoint comes last so everything the wrap-up produces gets committed.

## Phase 1 — Retrospective (do this from memory of the session, before touching files)

Look back across the ENTIRE session and answer honestly:

1. **Biggest wins** — what shipped, what got fixed, what breakthrough happened. For each: *what made it work?* If the winning move is repeatable (a diagnostic approach, a tool, a sequence), name it explicitly.
2. **Biggest mistakes / misses** — wrong assumptions, wasted loops, things done twice, rules violated, time sunk into the wrong layer. For each: *what was the moment it went wrong, and what signal was available that would have caught it earlier?* Include the user's corrections — if Charlie had to redirect, that's a miss worth recording.
3. **Near-misses and surprises** — things that almost bit us, or that only surfaced by luck.
4. **Process verdicts** — for each mistake, decide its disposition:
   - **Lesson** → write it (Phase 2)
   - **Standing-rule candidate** → propose it to Charlie in the wrap-up report (do NOT silently add rules to CLAUDE.md; rules are Charlie's call)
   - **Ticket** → file it in helmsman (bug/feature)
   - **One-off** → say so and move on; not everything needs ceremony

Be candid. A retrospective that only lists wins is worthless.

## Phase 1.5 — Check the KB before writing

Before capturing anything, search open-notebook so you extend what exists rather
than duplicating it:

```bash
kb search "<the problem you solved>" -n lessons -l 5
kb search "<the system you touched>" -n diagnostics -l 5
```

If a lesson already covers it, update that note instead of adding a near-copy —
near-duplicates are how a KB stops being trustworthy.

## Phase 2 — Knowledge capture

- Write/update lesson files for anything lesson-worthy that wasn't already captured mid-session (`Projects/<project>/Lessons/<Title>.md`). The standing rule says capture-when-solved, so this is a sweep for stragglers, not the primary mechanism.
- Post one-line summaries of new lessons to #b3ck (`slack-post-filtered b3ck "..." --priority=low`).
- Push lessons that ALL agents need into the helmsman lessons table (`POST http://localhost:5682/lessons`).
- Update auto-memory: new/changed standing facts → memory files + MEMORY.md index. Correct any memory entries the session proved wrong.
- **Write to open-notebook** (this is where we put things now, and where every
  agent searches):
  ```bash
  # Current project state — one per project touched:
  kb write -n projects -t "<Project> HANDOFF" -f "Projects/<Project>/HANDOFF.md"

  # Lessons worth sharing beyond this session:
  kb write -n lessons -t "<short rule>" --text "<rule + why + how to apply>"

  # A runbook or decision record you created/changed:
  kb write -n runbooks -t "<title>" -f "<path>"
  ```
  `kb write` upserts by title (safe to re-run) and credential-scrubs every body.
  The nightly `seed-open-notebook` re-syncs the bulk corpora, so this is only for
  what THIS session changed.
- **Log session efficiency:** every wrap-up logs one row so `agent_efficiency` has a baseline for the weekly review. Estimate from the session itself — no external tracker exists, so self-report honestly:
  ```bash
  /Users/charlieseay/.local/bin/log-efficiency --agent claude-code \
    --tokens <approx total tokens this session, from context/compaction warnings> \
    --deliverables <count of commits/files/tickets shipped this session> \
    --type <code|docs|analysis|infrastructure> \
    --quality <1.0-5.0, your honest call> \
    --technique "<comma-separated: agent-delegation, strategic-read, etc.>" \
    --notes "<one-line session summary>"
  ```
  This is the only place session-level token/deliverable counts are wired end-to-end — `/checkpoint` runs too often mid-session to double as the caller, and autonomous helmsman-dispatched tasks (nvidia-agent, Bedrock) have their own cost tracking elsewhere. Skip this step only for the lightweight trivial-session path (see Notes below).

## Phase 3 — Notes & state

- Overwrite `## Session State` in the active project note(s): where things stand, what's verified vs pending, exact resume point.
- Update the master project file's `## Last Session` entry (operator, work completed, decisions, issues, next actions).
- Append the session summary to `Projects/AI Handoff.md` ("Pick-up after YYYY-MM-DD session" section) so Gemini/next-session Claude can resume cold.

## Phase 4 — Open-loop sweep

- Anything left undone that the team should own → dispatch to helmsman with a proper brief (or confirm a ticket exists).
- Background monitors/jobs still running → note them in Session State with what they're watching and what to do with the result.
- Unverified deploys → either verify now or record explicitly as UNVERIFIED in Session State (never let "probably fine" be the last word).

## Phase 5 — Checkpoint

Run the `/checkpoint` skill (full multi-repo sweep — it handles commits, pushes, PDFs, container freshness, AI Handoff regeneration). This commits everything Phases 1–4 produced.

## Output — the Wrap-Up Report

End with a compact report to Charlie, in this shape:

```
## Session Wrap-Up — YYYY-MM-DD
**Wins:** (3-5 bullets, each with the repeatable ingredient if any)
**Mistakes & misses:** (honest bullets; each with disposition: lesson / rule-candidate / ticket / one-off)
**Lessons captured:** (links)
**Rule candidates for your call:** (proposals, if any)
**Open loops:** (what's still running/pending and who owns it)
**Resume point:** (one sentence — what next session starts with)
```

## Notes

- Do not auto-trigger wrap-up on token thresholds — that's the checkpoint/handoff/compact protocol's job. Wrap-up is for the *true* end of a session, invoked by Charlie.
- If the session was trivial (a few small edits), say so and run a lightweight version: skip Phase 1 ceremony, do Phases 3 + 5.
- Wins deserve the same processing as mistakes: a repeatable win that never gets named is a lesson lost.
