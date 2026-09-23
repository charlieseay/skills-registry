---
name: "talos-brief-authoring"
description: "Write a helmsman task brief that passes brief-lint and brief_compiler's gate on the first submission — the exact required sections, the fast-path shape, the negative-control requirement, and a bundled pre-flight script (scripts/verify_brief.py) that tests a brief against the REAL gate locally before you POST it. Use this whenever filing a task via POST /tasks for any owner (CLAUDE, TALOS, etc.), especially for research-then-build work like a Notion template build or any multi-step product fix. Run scripts/verify_brief.py BEFORE every POST /tasks call — a clean POST response is not proof a brief was accepted."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["notion-template-api-build", "digital-product-quality-bar"]
---

# Talos Brief Authoring

**Fleet-wide skill.** Any agent filing a `POST /tasks` brief — not just
Claude — should follow this so the brief clears the gate on the first or
second attempt instead of bouncing through several rounds of opaque
rejections.

## Why this exists

Filing a well-researched, correctly-ordered Notion-template-build task
took 9 submission attempts across two products (#3283, #3284, #3287,
#3288, #3289...) before it cleared, even though the actual task content
was correct from very early on. Most of that churn was avoidable: some
rejections were pointing at a real bug in the gate itself (now fixed,
see below), and some were pointing at real, learnable requirements
(a negative control, a deterministic Verification block) that this
skill states up front instead of discovering by trial and error.

## The gate, in order

A submitted `brief_text` goes through, roughly:

1. **`POST /tasks`'s own field check** — needs `task`, `priority`, `tags`
   (CSV string), `brief_text`, and (unless `skip_brief_requirement=1`) the
   brief itself.
2. **`brief_lint.validate_brief()`** (in `helmsman-db/brief_lint.py`,
   running inside the `helmsman-db` container) — checked at `POST /tasks`
   time, returns a 400 with `violations` if it fails. This is the one you
   see synchronously in the API response.
3. **`brief_compiler.gate()`** (in `claude-config/bin/lib/brief_compiler.py`,
   imported by both `worker-dispatcher.py` and `agent-executor.py`, run
   asynchronously after the task is accepted) — this is the "compile
   attempt N/2" step. It calls the standalone `claude-config/bin/brief-lint`
   bash script (7 checks) plus its own `has_negative_control()` check.
   A failure here shows up later as `status: failed` with
   `last_failure_output` starting `BRIEF: compile attempt...` — not as an
   immediate POST rejection, so don't assume `status: pending` on the
   initial response means the brief is actually accepted.

**Practical implication: always poll the task a few seconds after filing
and check its `status` and `last_failure_output` — a clean POST response
is not proof the brief passed stage 3.** This isn't hypothetical: task
#3297 got a clean `dispatched: true` POST response and was silently
cancelled by the compile gate two seconds later — nobody noticed until
asked to check on it.

```bash
curl -s -X POST "http://localhost:5682/tasks" -H 'Content-Type: application/json' --data @brief.json
sleep 5
curl -s "http://localhost:5682/tasks/<num>" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['status'], d.get('last_failure_output',''))"
```

## Verify BEFORE filing, not after (scripts/verify_brief.py)

Don't wait for the poll-after-filing step above to discover a rejection —
this skill bundles a script that runs the exact same `brief_compiler.lint()`
gate locally, instantly, before you ever call `POST /tasks`:

```bash
python3 /Volumes/data/skills/product/talos-brief-authoring/scripts/verify_brief.py your_task.json
# or without a JSON file:
python3 .../scripts/verify_brief.py --task "Task title" --brief brief.md --owner TALOS --priority 3
```

Exit 0 means the brief will pass; exit 1 prints the exact rejection
reason. Make this step 1 of filing any task, not a debugging tool you
reach for after a rejection — it's the same amount of work either way,
just before the wasted round-trip instead of after it.

## Required shape (fast path)

```markdown
## Goal
One or two sentences: what changes, for what reason.

## Context
Background, prior art already found (see feedback_research_before_every_brief),
credentials/paths involved, known constraints. Reference absolute paths
using the SAME path convention the executing owner's sandbox allows (see
"Owner path conventions" below) — a path that looks fine to you can be a
forbidden_paths violation for a restricted owner like TALOS.

## Steps
Numbered list. Research steps (read/fetch/curl/cat/grep/find/search/investigate)
before the first modification step (write/edit/create/modify/update/deploy/build/commit).
Only the FIRST step's classification matters for step-ordering — a later
verification step is free to use words like "confirm" or "find" without
being misread as out-of-order research (see "Known false-positive history" below).

## Verification
A fenced ```bash block with an ACTUAL pass/fail check (test, ||, &&, or an
exit code), PLUS a genuine negative control — a check that is expected to
FAIL, proving the positive check isn't vacuously true. The literal phrase
"negative control" doesn't have to appear for brief_compiler's check to
pass as of the current has_negative_control() implementation, but including
it explicitly is cheap insurance since that function does a literal
case-insensitive text search for it.

## Expected Output
Name exact file paths, exact JSON fields, or exact HTTP status codes that
will be true when the task is done — vague language here ("things should
work") is rejected.
```

If the tier classifies as `standard` or `full` (touches secrets, a
datastore, or customer-facing material — `brief_compiler.classify_tier()`
decides this automatically from your Context/Steps text), the compiled
brief will also require `## Dependencies`, and `full` tier adds
`## Rollback`, `## Security Review`, `## Recovery`, `## QA Checklist` —
these get auto-populated by the compiler if you don't supply them, so
don't preemptively write them unless you have something specific to say.

## Owner path conventions — the trap that isn't about brief quality at all

A brief can be perfectly well-formed and still get rejected with
`SECURITY: Owner <X> cannot access forbidden path` or `must reference an
allowed repository` — this is a completely separate check
(`OWNER_PERMISSIONS` in `helmsman-db/server.py`), not a brief-lint issue,
and no amount of rewording the Steps section fixes it.

- **TALOS** is restricted to a specific allowlist (`~/Projects/talos-tools`,
  `~/Projects/vault-mcp`, `~/.claude/skills`, `/Volumes/data/skills`, a
  few others) and explicitly forbidden from `/Volumes/data/secrets`,
  `~/Library/Mobile Documents`, and any literal `charlieseay/` path
  segment.
- This repo has **two mount points for the same content**:
  `/Volumes/data/projects/talos-tools` and `~/Projects/talos-tools` (the
  real, home-relative one TALOS's allowlist actually names). Always use
  the `~/Projects/...` tilde form in a brief destined for TALOS, never the
  `/Volumes/data/projects/...` form, even though both resolve to real
  files you can read directly in your own session.
- Avoid writing out `/Users/charlieseay/...` literally anywhere in a
  TALOS-owned brief — `charlieseay/` is on the forbidden-path substring
  list, so a fully-expanded home path (even one that would otherwise be
  fine) gets blocked. Use `~/` instead.
- A brief mentioning an unrelated file by bare filename in prose (e.g.
  "documented in `product-10/DUPLICATE-NOTE.md`") has been observed to
  get parsed by the compile stage as if it were a literal input-path
  argument and rejected as "Input file path '/DUPLICATE-NOTE.md' does not
  exist." If you need to reference a tangential file that the task itself
  doesn't read or write, say it in plain prose without a path-shaped
  token, or leave it out of the brief and mention it separately.

## `check_single_phase` — regex heuristics replaced with an LLM check (2026-09-22)

The "Steps mix research (read) and modification (write)" check used to be
a regex heuristic and hit FOUR independent false-positive sources in one
debug session filing task #3297 (a deliberately research-only brief for
TALOS): negation blindness ("do not build X yet" read as a build step),
compound-identifier substrings ("notion-template-api-build" the skill
name read as the verb "build"), noun-vs-verb ambiguity ("build
feasibility" read as an imperative), and list-conjunction misparsing
("...would be), and build feasibility..." read as a new clause). Each
regex fix solved its own case and broke on the next.

**As of `469dda4`, this check is an LLM judgment call** (`ask_llm`, free
tier, ~1s), not a regex — the same kind of ambiguous natural-language
judgment a human reviewer would make, which regex heuristics are
structurally bad at. It fails CLOSED: if the model call is unreachable or
returns something unparseable, the check reports "mixes" (rejects the
brief) rather than silently waving it through.

**Practical implication**: you generally don't need to work around
phrasing anymore — "do not build X yet", a hyphenated skill name, "build
feasibility" as a phrase, and list-conjunction "and" are all handled
correctly now. If this exact class of false positive reappears, the
model call itself is the thing to debug (check `ask_llm --health`, check
the prompt in `_llm_check_phase_mixing()` in `claude-config/bin/brief-lint`),
not another regex patch.

## Known false-positive history in `check_step_ordering` (fixed 2026-09-22)

`claude-config/bin/brief-lint`'s step 7 check used to compare the *first*
modification-keyword line against the *last* research-keyword line
anywhere in the Steps section. A correctly-ordered brief with a
post-build verification step like "independently re-query every database
and **confirm** each has the expected row count" tripped this every time,
because "find"/"search" are on the research-keyword list and a
verification step legitimately uses them. Fixed to only flag a brief
whose first step is itself a modification with no research step before
it anywhere — matching the check's own stated intent. If you hit this
exact error again after the fix, the bug has regressed; don't just
reword your Steps section blind — check
`claude-config/bin/brief-lint`'s `check_step_ordering()` function
directly against your actual submitted text, and check whether the
long-running `worker-dispatcher.py`/`agent-executor.py` processes need a
restart to pick up a code change (see below).

## If a brief keeps failing for reasons that don't match its actual content

1. Test directly against the real gate before assuming your wording is
   wrong:
   ```bash
   python3 -c "
   import sys; sys.path.insert(0, '~/Projects/claude-config/bin/lib')
   import brief_compiler, json
   task = {'task': '...', 'brief_text': open('your_brief.md').read(), 'project': None}
   brief, meta = brief_compiler.compile_brief(task, allow_llm=False)
   ok, errors = brief_compiler.lint(brief)
   print(ok, errors)
   "
   ```
   If this reports `True, []` but the live dispatcher still rejects the
   identical content, the problem is a stale running process, not your
   brief.
2. `worker-dispatcher.py` (launchd: `com.seayniclabs.worker-dispatcher`)
   and `agent-executor.py` (spawned by `worker-pool-manager.py`, not
   launchd-managed directly — check for orphaned PPID-1 processes) both
   import `brief_compiler` once at startup. A code fix to `brief-lint` (a
   subprocess call, re-read from disk every time) should apply
   immediately without a restart; a fix to `brief_compiler.py` itself
   requires restarting whichever process runs it.
   ```bash
   launchctl kickstart -k gui/$(id -u)/com.seayniclabs.worker-dispatcher
   ps aux | grep agent-executor   # check for stale PPID-1 orphans, kill + let worker-pool-manager.py respawn
   ```
3. Don't keep resubmitting the same brief with cosmetic rewording more
   than 2-3 times — if it's still failing identically, the content isn't
   the variable. Trace the actual gate code per step 1 above before
   burning further submission attempts.

## Filing checklist

- [ ] `## Goal`, `## Context`, `## Steps`, `## Verification`, `## Expected Output` all present, in that order.
- [ ] Steps: research (read/fetch/find/etc.) before the first build/write/create step.
- [ ] Verification: a fenced bash block with a real pass/fail check AND a negative control.
- [ ] Expected Output: exact paths/fields/codes, not vague language.
- [ ] Every path uses the owner's allowed convention (tilde-relative for TALOS, no literal `charlieseay/` segments, no `/Volumes/data/secrets`).
- [ ] No bare filename references to unrelated files in prose.
- [ ] After filing, poll the task's `status` a few seconds later — don't trust the initial POST response alone.
