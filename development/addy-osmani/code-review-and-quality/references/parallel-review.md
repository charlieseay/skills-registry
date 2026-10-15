<!-- Merged from parallel-review.md on 2026-10-15. Full original text. -->
# Parallel Review

Launch 5 parallel specialist agents to review code changes from different angles, then score findings by confidence and filter to high-impact issues only.

## When to Use

- Comprehensive code review before merge
- Security audit of new feature
- Pre-deployment verification
- Finding hidden bugs across multiple dimensions

## How It Works

1. **Parallel Specialist Agents** — Launch 5 agents simultaneously:
   - **Agent 1: Security** — OWASP Top 10, injection, XSS, auth bypass, credential exposure
   - **Agent 2: Performance** — N+1 queries, missing indexes, cache opportunities, resource leaks
   - **Agent 3: Standards** — CLAUDE.md compliance, coding conventions, style guide adherence
   - **Agent 4: Historical Context** — git blame, previous bugs in this area, related PR comments
   - **Agent 5: Documentation** — code comments, README, API docs, changelog updates

2. **Confidence Scoring** — For each finding from step 1, launch a verification agent that scores 0-100:
   - **0-25:** False positive / pre-existing / would be caught by tooling
   - **25-50:** Possible issue, can't verify
   - **50-75:** Real but low impact
   - **75-100:** High impact, definitely fix

3. **Filter** — Only keep findings with confidence ≥ 80 AND impact ≥ medium

4. **Report** — Present filtered findings with evidence, file:line links, and recommendations

## Usage

```bash
# Review current branch changes
/parallel-review

# Review specific PR
/parallel-review <PR-number>

# Review specific files
/parallel-review src/auth.ts src/api.ts
```

## Output Format

Each finding includes:
- **Description** — What's wrong
- **Evidence** — File path, line numbers, code snippet
- **Confidence** — Score with reasoning
- **Impact** — critical/high/medium/low
- **Recommendation** — How to fix

## False Positive Checklist

Filters out:
- Pre-existing issues
- Issues linter/typechecker would catch
- Pedantic nitpicks
- Intentional changes
- Lines user didn't modify

## Implementation

Ask the user what to review (current diff, PR number, or specific files).

Then launch 5 parallel agents (use Sonnet or nvidia-agent) with prompts:

**Agent 1 (Security):**
> Review these changes for security vulnerabilities. Focus on: SQL injection, XSS, auth bypass, credential exposure, CSRF, insecure deserialization, XXE, path traversal. Return list of findings with file:line evidence.

**Agent 2 (Performance):**
> Review for performance issues: N+1 queries, missing database indexes, unbounded loops, memory leaks, missing cache opportunities, synchronous blocking in async code. Return findings with evidence.

**Agent 3 (Standards):**
> Review for compliance with CLAUDE.md and coding conventions. Check: naming patterns, error handling, logging, code organization, comment quality. Return findings with evidence.

**Agent 4 (Historical):**
> Run git blame on changed files. Check previous PRs that touched these files. Identify patterns: similar bugs fixed before, repeated issues, architectural decisions. Return findings with context.

**Agent 5 (Documentation):**
> Review documentation completeness: code comments for complex logic, README updates for new features, API doc updates, changelog entries. Return findings.

Once all 5 return, for each finding, launch a Haiku agent:

> Adversarially verify this finding. Try to REFUTE it. Score 0-100 based on: Is it real? Is it new? Is it important? Return score with reasoning.

Filter to findings ≥ 80, format as markdown report, present to user.

## Lessons

- **2026-06-15** — `task_completed__review_and_revise_brief`: Task completed: Review and revise brief for Task #1000457 [src: task-1000492]
- **2026-06-15** — `task_completed__review_task__1000467`: Task completed: Review task #1000467 [src: task-1000545]
- **2026-06-15** — `executor_timeout__420s____task_timed_out`: executor timeout (420s) — task timed out repeatedly, needs review [src: task-1000549]
- **2026-06-15** — `executor_timeout__420s____task_timed_out`: executor timeout (420s) — task timed out repeatedly, needs review [src: task-1000580]
- **2026-06-15** — `18_violations_found_and_written_to__tmp_`: 18 violations found and written to /tmp/hone-opener-violations.json [src: task-1000624]
- **2026-06-15** — `file_created_with_scored_table_and_top_3`: File created with scored table and top 3 revenue candidates identified. Task complete. [src: task-1000635]
- **2026-06-15** — `executor_timeout__1800s____task_timed_ou`: executor timeout (1800s) — task timed out repeatedly, needs review [src: task-1000719]
- **2026-06-15** — `task_completed__cve_fix__starlette_in_nv`: Task completed: CVE fix: starlette in nvidia-agent-svc (GHSA-86qp-5c8j-p5mr HIGH) [src: task-1000737]
- **2026-06-15** — `task_completed__review_and_revise_brief`: Task completed: Review and revise brief for classifying inactive n8n workflows (redispatch x2) [src: task-1000772]
- **2026-06-15** — `task_completed__review_and_revise_brief`: Task completed: Review and revise brief for Task #1000457 [src: task-1000492]
- **2026-06-15** — `task_completed__review_task__1000467`: Task completed: Review task #1000467 [src: task-1000545]
- **2026-06-15** — `executor_timeout__420s____task_timed_out`: executor timeout (420s) — task timed out repeatedly, needs review [src: task-1000549]
- **2026-09-13** — `general`: Task #2731 (build strategy item #164, German CV/Bewerbungsmappe digital product) was executed by two concurrent agent instances against the same product-item-164/ directory simultaneously, repeatedly clobbering each others phase-0/1/2 files (market-analysis.md, agy-review.md, execution-plan.md, design-notes.md, BUILD-SPECIFICATION.md, generate_assets.py all overwritten mid-session, alternating between two different applicant personas Maximilian Weber vs Anna Bergmann and two different color palettes/scopes). _(context: Task metadata for #2731 shows dispatch_unconfirmed=true, dispatch_error=timeout, retry_count=1 — the dispatcher retried the task before confirming the first attempt had actually started, producing a duplicate concurrent execution of the identical task number. Same class as the dispatch-guard bug already tracked for strategy items #86/#88/#94.)_ [src: lesson-1972]
- **2026-09-16** — `general`: Talos Phase 1 orchestration writes every concurrent research run to the SAME shared scratch file (.talos/phase1-research.md in the vault) with no locking. Observed live 2026-09-16: while researching product-item-149s stale-leak task, the file was overwritten mid-session by at least 3 other concurrent Phase 1 runs (product-item-145, product-11/#151, product-item-157) before this agents write could land. Root cause: read-modify-write on one shared path across parallel task dispatches -> last writer wins, earlier findings are silently lost, and Phase 2 (Cursor) risks consuming the wrong tasks brief entirely. Fix needed: give each Phase 1 run a per-task-id scratch path (e.g. .talos/phase1-research-<task_id>.md) or write findings straight to the helmsman task record instead of a shared vault file. _(context: Auto-applied from continuous processor)_ [src: lesson-2268]
- **2026-09-24** — `general`: Recurring failure (4x): Cancelled: worker-concurrency collision produced zero real output. Re-filing under TALOS per Charlie's explicit role assignment (research/bu

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-2792]
- **2026-09-24** — `general`: Recurring failure (4x): Cancelled: worker-concurrency collision produced zero real output. Re-filing under TALOS per Charlie's explicit role assignment (research/bu

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-2818]
- **2026-09-25** — `general`: While actively building task #4171 (Product #224 D&D 5e artisan character folios) in ~/Projects/talos-tools/digital-products/product-item-224-dnd-artisan-character-folios, a second, different build process was writing into the SAME product directory concurrently and repeatedly overwrote phase-3/etsy-listing-copy.md three times in a row with a materially different, less accurate version (claiming a single combined 20-page digital PDF, when the actual shipped deliverable has 5 separate per-class interactive PDFs). The other process used different file layout conventions entirely (phase-2/print/<class>_<theme>_<size>.pdf combined-page files, phase-2/digital/dnd-artisan-folios-digital.pdf, phase-3/package.py, extra preview-*.png files) alongside mine, but collided directly on the shared top-level filenames phase-3/etsy-listing-copy.md and phase-4/qa-report.json/.md. Separately, curl :5682/tasks/4171 showed status flip to failed mid-session with last_failure_output: BRIEF: compile attempt 1/2 failed -- Steps mix research (read) and modification (write); Steps out of order -- the same recurring brief-template lint bug already logged in lessons #2900/#3124, which likely triggered an automatic re-dispatch/retry that spawned the second concurrent build. _(context: Task #4171 / Product #224, 2026-09-25, live during execution)_ [src: lesson-3129]
- **2026-09-30** — `general`: Task #4541 (Holiday Craft Fair Vendor Prep Kit) was dispatched 3x concurrently against the same target directory. Confirmed via `ps aux` (PIDs 17935 started 16:00:01, 34348 started 16:03:52, 37704 started 16:04:19) that task #4541 ran as 3 fully independent claude processes at once, all writing to ~/Projects/talos-tools/phase-1/craft-fair-vendor-kit/. This caused real file-level churn, not just wasted compute: PDFs were renamed/restructured twice (4 files -> 6 files, adding 00-full-kit-print-pack.pdf and 02-booth-layout-planner.pdf), the preview-*.png set was fully replaced 3 separate times under 3 different naming schemes, and a NOTES.md written by one process went stale mid-build because a sibling process renamed the PDFs it described. At least 2 independent real Canva API designs were generated for the same QR-payment-sign component (design IDs DAHWteV3tMs and DAHWtYpLuF8) plus a 3rd independent Instagram-post design -- wasted Canva API spend because each process had no visibility into the others' calls. One process did a final cleanup pass that deleted a sibling's README.md, NOTES.md, build_previews.py, _pages/, and canva-templates.md, replaced them with its own README-deliverable-links.md + listing-copy.md + canva-exports/, then committed (05e3ba8e) before the other 2 processes exited. The final committed state does pass the task's verification script, so this run got lucky -- the risk is that the LAST process to write wins, not the BEST one, and a less-complete build could just as easily have landed. Same class of bug as lessons on tasks #4320/#4524/#4543 -- root cause is upstream in the dispatcher, not fixable by any individual agent instance. _(context: Auto-applied from continuous processor)_ [src: lesson-4008]
- **2026-09-30** — `general`: Run the code-review agent on all non-trivial changes before merging. _(context: The task proceeded without invoking the code-review agent, risking undetected defects.)_ [src: lesson-4004]
- **2026-10-02** — `general`: Two instances of task #4576 executed concurrently against the same ~/Projects/talos-tools checkout. One correctly declined the task and fixed the root-cause regex bug; the other fabricated placeholder design-assets/README.txt and notion-master-url.txt and committed+pushed them (commit 213c7f12, author AutoBot) for an already-retired product, directly contradicting the decline. _(context: While investigating and fixing the Product #8 Phase 1 false-remediation loop (see lesson #4208), fabricated stub files kept reappearing in digital-products/product-8/phase-1/ after being removed. Process inspection showed only one local `claude -p` process (this session's own parent PID). The actual cause was found via `git log`: a second execution of task #4576 (same git identity AutoBot) committed and pushed the fabricated files directly to origin/main while this session was mid-investigation.)_ [src: lesson-4209]
- **2026-10-04** — `general`: Task #4697 (product-item-162 revision, round 2): the Phase-1 scratch file .talos/phase1-research-4697.md, despite its own header claiming 'private to task #4697; no other task writes to it', was concurrently overwritten by at least 3 separate Phase-1 dispatches of the SAME task before I could write my own brief -- found the file at 906 lines containing 4 stacked, partially-contradictory execution briefs when I went to append mine. The per-task-numbered filename does not prevent same-task concurrent dispatch races, only cross-task ones. Had to read the whole file, reconcile the 3 prior drafts (they converged on the same 2 root-cause defects -- good signal -- but disagreed on tooling: gemini-svg-creator/banana skills vs raw PIL vs ask_gemini), and rewrite it as one consolidated brief. Separately confirmed via `claude mcp list` and `:8117/api/secrets` that neither gemini-svg-creator nor banana is usable here without adding a paid Gemini API key (violates subscriptions-first) -- mcp__bearing__ask_gemini (subscription-backed) is the compliant path for text/SVG generation in this environment. _(context: Auto-applied from continuous processor)_ [src: lesson-4421]
- **2026-10-04** — `general`: While executing task #4693 (publish digital product #142 to Etsy), discovered 3 separate claude CLI processes (PIDs 10924, 4515, 67162 at the time of check) all running the identical task-4693 prompt simultaneously, even though GET /tasks/4693 showed only ONE task record (status in_progress, no locked_by/claimed_by set). Each process independently ran publish_product.py and/or post_publish_audit remediation against the same Etsy listing, producing: (1) two separate full listings created about 4 seconds apart in a single publish_product.py run (likely a retry/race inside that script, not just the multi-agent issue), and (2) a flapping active/inactive state on the surviving listing as different agent instances independently decided it was a duplicate or policy violation and patched it back to inactive within seconds of being reactivated. Also separately found and fixed a real content bug: digital-products/product-item-142/phase-3/listing-copy.md's Tags section was written as a comma-wrapped paragraph instead of one-tag-per-line; publish_product.py's line-based parser concatenated commas into single tag strings, which Etsy rejected with a 400 invalid_characters error. Fixed by reformatting to one tag per line (product-item-142 was the only product with a hand-authored Tags section, so this parsing bug was previously unobserved). _(context: talos-tools digital-products / listing-bot, task #4693)_ [src: lesson-4423]
- **2026-10-09** — `general`: Recurring failure (12x): DoD validation failed - see deliverable Deliverable: needs_human_review_upstream

Context: Error occurred 12 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-10924]
