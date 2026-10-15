<!-- Merged from session-check.md on 2026-10-15. Full original text. -->
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

## Lessons

- **2026-09-13** — `general`: A verification that cannot fail proves nothing — always include a negative control. Three times in one session (2026-09-12) a check passed while testing nothing: (1) Caddy on srv2 returned HTTP 200 for authentik/n8n/grafana/portainer Host headers, so I concluded the services were alive behind a proxy; it returns 200 with an empty body for bogus.invalid too — it is a catch-all. docker ps over SSH showed srv2 runs NONE of them. (2) I tested a stale-JSON fallback by stopping the helmsman container; a watchdog-spawned NATIVE server still answered :5682, so the fallback branch never executed and I reported it verified. Proof required pointing the client at a dead port. (3) sqlite3 VACUUM on a 0-byte file exits 0, which is how two launchd jobs faked maintenance for months. HOW TO APPLY: before trusting a green check, ask what result a BROKEN system would give. If it is the same green, the check is worthless. Add a control that must fail (a bogus hostname, a dead port, a known-absent row) and confirm it does. _(context: Auto-applied from continuous processor)_ [src: lesson-1989]
- **2026-09-13** — `general`: When agent process exits, immediately check git status before declaring success. Agent workers (cursor-worker, nvidia-agent) may complete work without committing. Pattern: (1) ps shows process gone, (2) git status to see uncommitted changes, (3) verify build, (4) commit manually if needed. Do not assume process exit = committed work. _(context: Auto-applied from continuous processor)_ [src: lesson-1913]
- **2026-09-13** — `general`: Do not report a live-service change as "done" until the state you are describing has actually been re-verified against current reality, not the state at the time you made the change. 2026-09-10: after fixing Bridge, reported a clean summary including a claim about a DNS propagation state that had not been re-checked since the fix was applied -- Charlie had to correct directly ("the bridge needs to be rebuilt and deployed... i cannot answer correctly") because the question asked assumed a state the agent had not confirmed. Fix: before any "all done" or status-summary message about a live system, re-query that systems actual current state in the same turn, not rely on the state from when the change was made minutes/turns earlier -- especially across container redeploys, DNS changes, or anything with real propagation/settling time. _(context: Auto-applied from continuous processor)_ [src: lesson-1937]
- **2026-09-15** — `general`: Corrected 2026-09-14: I wrote a full session handoff to
`~/Projects/m5-agents/HANDOFF.md`. Charlie: *"handoff.md? we should be using
the cmdb (helmsman and open-notebook)"*. _(context: a handoff committed in a repo is a second source of truth. It drifts
the moment anyone updates the CMDB, and the agent fleet cannot query it — the
M5 agents read open-notebook, not files in a repo on another host. This is the
same drift that `[[feedback_cmdb_drift_recurrence]]` and
`[[feedback_vault_historical_only]]` are about; a repo file is just a third
copy alongside the vault.)_ [src: lesson-2091]
- **2026-09-15** — `general`: An agent reporting confident numbers with tools_used=0 is not lying by choice — check whether its MODEL is dead. nvidia/llama-3.3-nemotron-super-49b-v1 was retired 2026-08-26 and returned HTTP 410 on every call for 3 weeks; the service stayed 'up', /health returned ok, and the only symptom was Bosun posting invented container counts to Slack. Probe the pinned model with a 1-token request before debugging the agent's honesty. _(context: Auto-applied from continuous processor)_ [src: lesson-2110]
- **2026-09-16** — `general`: Lesson #858 ('a provider 200 proves the ENDPOINT is up, not that the MODEL exists') was written 2026-08-18, eight days before the 2026-08-26 NVIDIA EOL that then went unnoticed for three weeks. A correct lesson nobody ENFORCES prevents nothing. The gap: nvidia-probe-weekly validated models in ask_nvidia's lane table but could not see a model pinned in a service's own source (slack-chat-svc TOOL_CAPABLE_MODEL). Closed by claude-config bin/pinned-model-guard.sh, Sundays 03:00, which probes every hardcoded model constant and treats only 404/410 as death (429/503/timeout are transient). HOW TO APPLY: when writing a lesson about a class of failure, ask what SCHEDULED CHECK catches the next instance. If the answer is 'someone remembering', write the check. _(context: Auto-applied from continuous processor)_ [src: lesson-2132]
- **2026-09-16** — `general`: Lesson #858 ('a provider 200 proves the endpoint is up, not that the model exists') was written 2026-08-18, EIGHT DAYS BEFORE the 2026-08-26 NVIDIA EOL — and the retirement still went unnoticed for three weeks. A correct lesson nobody ENFORCES prevents nothing. The gap: nvidia-probe-weekly validated models in ask_nvidia's LANE TABLE but could not see a model pinned in a service's own source (slack-chat-svc's TOOL_CAPABLE_MODEL). Closed by bin/pinned-model-guard.sh (Sundays 03:00), which greps every hardcoded model constant and probes it, treating only 404/410 as death (429/503/timeouts are transient). HOW TO APPLY: when writing a lesson about a class of failure, ask what SCHEDULED CHECK would catch the next instance — and if the answer is 'someone remembering', write the check. _(context: Auto-applied from continuous processor)_ [src: lesson-2128]
- **2026-09-17** — `general`: Created a synthetic helmsman task with owner=CLAUDE, status=pending (intending to PATCH it to approved next) to test an approval-triggered publish flow. Before I could PATCH it, a live autonomous QA/dispatch pipeline claimed the task, completely rewrote its brief_text and metadata into an unrelated generic task (a test-script-creation brief), and the product_num field I needed for my test was gone. My subsequent PATCH to approved then raced that dispatchers own write and got silently clobbered. This is the exact same failure class as the 2026-09-05 test-contamination lesson (a real worker claims a task within milliseconds of a status change), but the earlier lesson only covered TEST FILES with a live-dispatch opt-in env var -- it did not cover ad-hoc manual test tasks created directly via curl during an interactive session, which have no such gate available. RULE: never create a helmsman task with an owner/status combination that any live dispatcher could claim (owner=CLAUDE + status=pending/approved is claimable) purely for interactive testing. Either (a) test the underlying function directly in Python without touching helmsman at all -- this is what worked cleanly for the rest of the session once I switched to it, or (b) if a real task-lifecycle test is unavoidable, use a status/owner combination no fleet component polls for, and verify that by grepping active dispatcher/watcher source for the status value first. _(context: 2026-09-18 session: testing the watch_approvals.py listing-bot integration against real helmsman tasks. Directly extends the existing gate-live-dispatch-tests-behind-explicit-opt-in lesson (2026-09-05) -- same root cause, new surface.)_ [src: lesson-2457]
- **2026-09-21** — `Helmsman`: Own test/smoke-test tasks are not inert: a cancelled synthetic task can still be picked up by a background automation lane (nhr-triage retried #3261 and spawned a failed child #3263) before the cancel is fully processed or if a cancel is missed. Fix: after any test dispatch, re-query the task list by project/status at the end of the session -- never trust memory of what you created. This is the state-reconciliation failure mode applied to your own test cleanup, not just to relayed claims from others. _(context: Auto-applied from continuous processor)_ [src: lesson-2633]
- **2026-09-24** — `general`: 2026-09-24 session, visual-design redesign pass on 40 digital products: Charlie caught by eye that all 40 products were functionally correct but visually bland -- market-evidence research was done, but the VISUAL half of digital-product-quality-bar Step 0 (pull real competitor preview images, not just review counts) was skipped entirely. Built a shared CSS design system directly from real Etsy comp images, validated on 2 products (table layout + checklist layout) before rolling out to the other 38 via 4 parallel subagents. Found and independently fixed 3 real defect classes across the batch, none caught by the agents own self-reports: (1) the same never-ran-final-overlay-step bug from earlier tonight recurred across ~20 products -- render-v2 intermediates were genuinely regenerated with new styling but shipped customer-package files were untouched; (2) one agent redesigned the WRONG duplicate implementation of product #199 (192 fields/4 pages) and overwrote the correct 858-field/28-page version -- caught by checking field counts against known-correct baselines, restored from an intact backup path; (3) a class-name mismatch bug (markup used class=week-theme, CSS defined .theme) on product #184 caused the pink badge styling to silently not apply despite the shared CSS loading correctly -- only caught via direct Playwright getComputedStyle() query after a misleading low-DPI screenshot read gave a false negative. Lesson: after ANY subagent claims a visual/styling fix, verify with (a) git log on the EXACT shipped file path, not just that some file changed, (b) field/page counts against a known baseline, and (c) a real render at sufficient DPI or a getComputedStyle() query, not just eyeballing a small screenshot -- low-DPI screenshots can look unstyled even when the CSS is genuinely correct, producing false-positive bug reports that waste debugging time. _(context: Auto-applied from continuous processor)_ [src: lesson-2785]
- **2026-09-25** — `general`: Recurring failure (4x): INFRA_ERROR: worker/transport failed before the task was judged - see deliverable Deliverable: Error: 500 Server Error: Internal Server Erro

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-2999]
- **2026-09-25** — `general`: Dispatched to task-4164.brief (nominally Task #222 wall art) but live helmsman state for #4164 already showed status=failed and had been recycled to an unrelated task (#223 Montessori) by the time the session started -- the on-disk /tmp/helmsman-tasks/*.brief files are not reliably in sync with live helmsman task state; always re-check `curl :5682/tasks/<num>` before trusting a dispatched .brief file's content. Separately, Task #4163 (the real Product #222 task) failed at brief-compile with 'Steps mix research (read) and modification (write)' -- the exact same root cause already documented in lesson #2900 (2026-09-24, task #3387/#3347) -- recurring a 3rd+ time, meaning the upstream product-build brief template still hasn't been fixed to avoid interleaving research and modification verbs across its Steps list. Despite the failed status, real work had already started on disk (digital-products/product-item-222-mid-century-bauhaus-wall-art/phase-0/market-analysis.md and phase-1/design-notes.md existed), consistent with lesson #3116's pattern that a brief-compiler failure does not mean no work happened -- check disk/git before redoing anything. Also found: .talos/phase1-research.md is a SHARED scratch file that multiple concurrent Phase-1 dispatches append to rather than each getting their own file -- it contained duplicated/stale execution briefs for Task #224 (written twice) stacked with the current #222 brief, a collision risk matching the already-known concurrent-dispatch lesson pattern (tasks #4140, #4146). Did not write further to that file to avoid clobbering the in-progress concurrent build. _(context: Auto-applied from continuous processor)_ [src: lesson-3124]
- **2026-09-26** — `general`: This task's target problem was already resolved by concurrent task #4190 before execution; verify live state before running any brief whose Context section wasn't generated in the last few minutes. _(context: Auto-applied from continuous processor)_ [src: lesson-3218]
- **2026-09-27** — `general`: Recurring failure (4x): Verification service returned HTTP 404 - could not verify deliverable

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-3550]
- **2026-10-01** — `general`: Recurring failure (3x): ## Verification block exited 0 but has NO negative control (a check that must fail). A pass that a broken system would also return proves no

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4098]
- **2026-10-04** — `general`: Drift items 1-2 were already fixed in prior sessions; only ETSY_DUPLICATE_TITLE (intentional draft 4588091961) remains. CMDB and store.db are in sync with live Etsy. _(context: Auto-applied from continuous processor)_ [src: lesson-4396]
- **2026-10-06** — `general`: Recurring failure (5x): BRIEF: cancelled after 2 compile attempts — compiled brief still fails lint: Missing executable verification commands in ## Verification sec

Context: Error occurred 5 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4644]
- **2026-10-06** — `general`: Recurring failure (6x): ORPHANED: swept 2026-10-06 -- nothing's blocked_by references this research task (superseded by a later split of the same root, or its root 

Context: Error occurred 6 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4755]
- **2026-10-07** — `general`: Recurring failure (3x): DoD validation failed - see deliverable Deliverable: Model finished with no output

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4911]
- **2026-10-07** — `general`: Recurring failure (6x): Closed 2026-10-07 by Claude: underlying fault cleared (trust-canary all PASS, kb search returns results); no work left.

Context: Error occurred 6 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4910]
- **2026-10-07** — `general`: Recurring failure (10x): DoD validation failed - see deliverable Deliverable: Task completed (no task_complete called)

Context: Error occurred 10 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4895]
- **2026-10-07** — `general`: Recurring failure (3x): CANCELLED 2026-10-06 (STALE_PREMISE): alert was transient. helmsman-queue-audit, verify-shipped, deadman-ping, loop-deadman are all exit 0 a

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4850]
- **2026-10-07** — `general`: Recurring failure (6x): CANCELLED 2026-10-06: stale auto-generated research task; brief cites nonexistent paths / lacks negative control. Charlie approved cancellin

Context: Error occurred 6 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4841]
- **2026-10-07** — `general`: Recurring failure (3x): CANCELLED: Charlie decision 2026-10-06 killed the digital product #165 Etsy publish; this task is part of that chain.

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4867]
- **2026-10-07** — `general`: Recurring failure (6x): Closed 2026-10-07 by Claude: underlying fault cleared (trust-canary all PASS, kb search returns results); no work left.

Context: Error occurred 6 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4939]
- **2026-10-07** — `general`: Recurring failure (3x): Closed 2026-10-07: boot noise / sonique stale login item stopped; services verified up.

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-4942]
- **2026-10-08** — `general`: Recurring failure (3x): DoD validation failed - see deliverable Deliverable: Model finished with no output

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-5026]
- **2026-10-08** — `general`: Recurring failure (6x): Closed 2026-10-07 by Claude: underlying fault cleared (trust-canary all PASS, kb search returns results); no work left.

Context: Error occurred 6 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-5024]
- **2026-10-08** — `general`: Recurring failure (10x): DoD validation failed - see deliverable Deliverable: Task completed (no task_complete called)

Context: Error occurred 10 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-5019]
- **2026-10-08** — `general`: Recurring failure (6x): Closed 2026-10-07 by Claude: underlying fault cleared (trust-canary all PASS, kb search returns results); no work left.

Context: Error occurred 6 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-5171]
- **2026-10-08** — `general`: Recurring failure (3x): DoD validation failed - see deliverable Deliverable: Model finished with no output

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-5173]
- **2026-10-08** — `general`: Recurring failure (3x): Closed 2026-10-07: boot noise / sonique stale login item stopped; services verified up.

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-5329]
- **2026-10-08** — `general`: Recurring failure (3x): DoD validation failed - see deliverable Deliverable: Model finished with no output

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-5328]
- **2026-10-08** — `general`: Recurring failure (6x): Closed 2026-10-07 by Claude: underlying fault cleared (trust-canary all PASS, kb search returns results); no work left.

Context: Error occurred 6 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-5478]
- **2026-10-08** — `general`: Recurring failure (3x): Closed 2026-10-07: boot noise / sonique stale login item stopped; services verified up.

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-5481]
- **2026-10-08** — `general`: Recurring failure (22x): ## Verification commands FAILED on execution (LLM verdict was FAIL). The commands are the authority.

Context: Error occurred 22 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-7583]
- **2026-10-11** — `general`: Recurring failure (4x): EXECUTOR (claude exited 1): You've hit your session limit · resets 10am (America/Chicago)

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-15479]
- **2026-10-11** — `general`: Recurring failure (29x): EXECUTOR (claude exited 1): You've hit your session limit · resets 3pm (America/Chicago)

Context: Error occurred 29 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-15473]
- **2026-10-14** — `general`: Recurring failure (4x): Cancelled 2026-10-14: orphaned research task — parent #5805 is cancelled, so this research has no consumer.

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-28751]
- **2026-10-14** — `general`: Recurring failure (4x): Cancelled 2026-10-14: orphaned research task — parent #5805 is cancelled, so this research has no consumer.

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-28894]
- **2026-10-15** — `general`: Recurring failure (99x): Cancelled 2026-10-14: stale leftover from the Oct 5-12 runaway window. Status was non-terminal but nothing had advanced it in days -- redisp

Context: Error occurred 99 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-29966]
- **2026-10-15** — `general`: Recurring failure (99x): Cancelled 2026-10-14: stale leftover from the Oct 5-12 runaway window. Status was non-terminal but nothing had advanced it in days -- redisp

Context: Error occurred 99 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-30406]
