<!-- Merged from audit-vault.md on 2026-10-15. Full original text. -->
Audit vault project notes against the actual state of their code repositories. Identifies drift in status, version, test counts, and timestamps.

## Usage
- `/audit-vault` — full scan of all mapped projects
- `/audit-vault <project>` — scan a single project (e.g., `/audit-vault sounding`)

## Project-to-Repo Mapping

| Vault Note | Code Repo | Test Runner | Extra Checks |
|-----------|-----------|-------------|--------------|
| Projects/[project-1]/[project-1].md | /path/to/[project-1] | pytest | version, PyPI |
| Projects/[project-2]/[project-2].md | /path/to/[project-2] | pytest | version, PyPI |
| Projects/[project-3]/[project-3].md | /path/to/[project-3] | swift test | swift build |
| Projects/[project-4]/[project-4].md | /path/to/[project-4] | npm test | version |
| Projects/[project-5]/[project-5].md | /path/to/[project-5] | npm run build | playwright |

## Steps

### 1. Pre-flight

Check which projects to audit:
- If an argument was provided, filter the mapping table to that project only
- If no argument, audit all projects in the table
- Skip any project whose repo path does not exist on disk (report it as "repo missing")

### 2. Read Each Vault Note

For each project, read the vault note and extract:
- **status** from YAML frontmatter
- **updated** date from YAML frontmatter
- **version** mentioned anywhere in the note (look for patterns like `v1.2.3`, `version: 1.2.3`, `## Version`)
- **test count** mentioned in the note (look for patterns like "XX tests", "XX passing", "test count: XX")
- **deployment state** (look for "deployed", "live", "spec only", "in development", etc.)

### 3. Check Each Repo

For each project, gather actual state from the code repo:

**Version (Python projects):**
```bash
grep -m1 'version' /path/to/<repo>/pyproject.toml 2>/dev/null || grep -m1 '__version__' /path/to/<repo>/src/*/__init__.py 2>/dev/null
```

**Version (Swift projects):**
```bash
grep -m1 'version:' /path/to/<repo>/Package.swift 2>/dev/null
```

**Version (Node projects):**
```bash
node -e "console.log(require('/path/to/<repo>/package.json').version)" 2>/dev/null
```

**Tests:**
| Runner | Command | How to count |
|--------|---------|-------------|
| pytest | `cd /path/to/<repo> && python -m pytest --tb=no -q 2>&1` | Parse "X passed" from output |
| swift test | `cd /path/to/<repo> && swift test 2>&1` | Parse "Test Suite ... passed" lines |
| npm test | `cd /path/to/<repo> && npm test 2>&1` | Parse test runner output |
| npm run build | `cd /path/to/<repo> && npm run build 2>&1` | Pass/fail only (no test count) |
| xcodebuild | `cd /path/to/<repo> && xcodebuild -scheme [scheme-name] -destination 'platform=iOS Simulator,name=iPhone 16' build 2>&1 \| tail -5` | Pass/fail only |

Run tests with a 120-second timeout per project. If a test hangs, kill it and report "timeout".

**Last commit date:**
```bash
git -C /path/to/<repo> log -1 --format='%ci' 2>/dev/null
```

**Repo exists and has code:**
```bash
test -d /path/to/<repo>/.git && echo "yes" || echo "no"
```

### 4. Compare and Report

Build a findings table:

```
| Project | Note Status | Actual Status | Tests (Note) | Tests (Actual) | Version (Note) | Version (Actual) | Updated (Note) | Last Commit |
```

Flag drift in any column where the note doesn't match reality:
- **Status drift** — note says "spec only" but repo has passing tests → flag
- **Test count drift** — note claims 42 tests but pytest reports 47 → flag
- **Version drift** — note says v0.2.0 but pyproject.toml says 0.3.1 → flag
- **Staleness** — last commit is >7 days newer than the note's `updated` date → flag

Summarize:
- Total projects scanned
- Projects with drift (list each issue)
- Projects fully in sync
- Projects skipped (repo missing)

### 5. Offer Fixes

For each piece of drift found, offer to fix the vault note:
- Update `updated` frontmatter to today's date
- Update version references to match code
- Update test counts to match actual
- Update status if clearly wrong (e.g., "spec only" → "active" when tests pass)

**Do not auto-fix.** Present the list of proposed changes and wait for confirmation before editing any vault notes.

## Notes

- Run tests in parallel where possible to keep the audit fast
- Python projects: activate venv if one exists (`source .venv/bin/activate`) before running pytest
- Swift tests can be slow on first build — warn if this is the case
- If a project has no tests configured, report "no tests" rather than failing
- The vault path contains spaces — always quote it in commands
- This skill is designed to run weekly but can be run anytime

## Lessons

- **2026-06-16** — `monitoring_doc_drift_false_alarms`: Before declaring a service 'DOWN', check it against REALITY not the CLAUDE.md port table — docs drift. A container 'Up' with an unpublished port is proxy-only (not broken); a missing service may be decommissioned (not down). _(context: Audit flagged Grafana(:3000)+Netdata(:19999) DOWN. Truth: grafana is Up but port unpublished (proxy-accessed); netdata doesn't exist + isn't in current infra notes (retired). Same class as bedrock-router :5700->:5683 drift.)_ [src: session/2026-06-15-trust]
- **2026-06-16** — `status-vocab-drift-3-layers`: When a downstream UI doesn't show items, check status-vocabulary drift across ALL layers: the source DB statuses, the n8n column list, AND the Bridge's KNOWN_STATUSES/JobStatus/column-order. An unknown status gets silently coerced to 'Queued' and disappears. Fix every layer. _(context: 7 'Ready for Delivery' deliverables + Scored/Bid Failed were invisible: n8n STATUS_COLUMNS dropped them AND Bridge KNOWN_STATUSES coerced them to Queued. Fixed all 3 layers.)_ [src: session/2026-06-16-bridge]
- **2026-06-16** — `status-schema-vocab-drift-recurring`: When a UI/dashboard shows nothing or wrong data, the #1 suspect is status/schema-vocabulary drift across layers: source DB statuses vs the query's column list vs the consumer's known-status set. Unknown values get silently coerced (->Queued) or dropped. Check + fix EVERY layer. _(context: Recurred 3x this session: restored endpoints w/o their views; n8n STATUS_COLUMNS vs Bridge KNOWN_STATUSES; centaur statuses vs Bridge JobStatus. Each made real data invisible.)_ [src: session/2026-06-16-meta]
- **2026-09-16** — `general`: When Charlie says "let's make the commits so we're current", that does NOT
include the Obsidian vault. On 2026-09-15 I surveyed repos for uncommitted
work, saw the vault dirty and 3 commits ahead, and tried to push it. The
auto-mode classifier blocked it, and Charlie asked: "Why try to push to the
vault instead of CMDB like you're supposed to." _(context: the vault is HISTORY-ONLY since 2026-08-31 — helmsman + open-notebook
are truth ([[feedback-vault-historical-only]]). Treating it as "just another
repo to sync" skips the real question: does this state belong in the vault at
all? It usually does not, and pushing it makes a second source of truth the
fleet cannot query ([[feedback-cmdb-not-repo-handoffs]]).)_ [src: lesson-2236]
- **2026-10-03** — `general`: 2026-09-12 cost review (ccusage over ~/.claude/projects, 30 days): 17B tokens, 98% cache reads, 40M output. 130 interactive vault sessions = 88% of load at ~324K context tokens per turn because settings.json defaulted to opus[1m]; the 1M window let sessions grow past every compaction threshold. ~2,300 automation sessions (dispatcher, bedrock worker, nvidia-agent) were only 12%. Moving work to OpenRouter/Bedrock would COST more (API-equivalent ~$8k/mo vs flat Max). Fix: default model = opus (200K), [1m] per session only, fresh session per task, status line showing ctx %. Measure with: npx ccusage@latest monthly --breakdown. Stale ANTHROPIC_SMALL_FAST_MODEL=sonnet-4-5 also made background tasks run on Sonnet instead of Haiku. _(context: Auto-applied from continuous processor)_ [src: lesson-2005]
- **2026-10-03** — `Jackel`: Task #2813: agent/task-1000345 was labeled the investigator audit-trail feature, but its actual 76-commit diff (2026-05-22 to 2026-09-01) was unrelated stale OSINT camera/reverse-image-search work (Google Vision, PimEyes, FaceCheck, TinEye, camera sources) with many duplicate repeated commits, a committed secrets/tineye.key placeholder, and a regression removing the /audit route prefix already present on main. The real audit-trail middleware/routes already existed on main untouched. Decision: closed the branch (deleted local+remote, tip 0bcb244) rather than merge. Lesson: branch/task titles can drift far from actual diff content -- always diff vs main before trusting the branch description. _(context: Auto-applied from continuous processor)_ [src: lesson-2024]
- **2026-10-03** — `general`: A CMDB record asserting DELETION is worse than a missing one — it blocks rediscovery _(context: Auto-applied from continuous processor)_ [src: lesson-2063]
- **2026-10-03** — `general`: 9 Slack-visible agent personas (Lighthouse, Salvager, Deckhand, Navigator, Purser, Herald, Scribe, Buoy, Rigger) are confirmed RETIRED, not silently broken. Checked against the CMDB agents registry (http://192.168.68.78:8117/api/agents) and ~/Projects/claude-config/agents/ -- none of the 9 have a definition file, a CMDB entry, or a launchd job. Their Slack channels all stopped receiving Helmsman EXEC dispatch prompts around 2026-05-24 to 2026-06-09 and have been silent since; nothing currently runs them, so there is no live process to fix. Before that stop, every one of them was hitting the same handful of root causes repeatedly: invalid Helmsman owner names (RIGGER, CHARLIE, Infrastructure Team are not in valid_owners), missing/wrong brief_text shape, a shell allowlist that blocked their own instructed commands (n8n API curls, ls/grep), and vault_read calls against paths that never existed (Projects/Enchapter/Enchapter.md, Projects/Lab/Apps/). Per the vault being historical-only now (sources-of-truth rule), any successor automation for this kind of sweep should read CMDB/helmsman/open-notebook, never vault_read. Charlie should archive the 9 corresponding Slack channels manually -- no MCP tool available here can archive a Slack channel. _(context: Auto-applied from continuous processor)_ [src: lesson-2310]
- **2026-10-03** — `general`: Task #224 (D&D artisan folios) .talos/phase1-research.md scratch file was found contaminated again during a later dispatch: a complete, correct #224 execution brief (lines 1-296) was followed by an inline HTML comment claiming an unrelated #223 (Montessori) brief had been removed, but the full #223 brief (lines 309-514) was still physically present below that comment. The removal never actually happened -- either the edit that wrote the comment did not also delete the content, or a subsequent concurrent Phase-1 dispatch for #223 re-appended after the comment was written. Fixed by truncating the file back to just the #224 brief (through its Verification code block) and dropping both the leaked #223 content and the stale comment. This confirms lesson #3123/#3124's root cause (.talos/phase1-research.md is a single shared, non-path-isolated scratch file across concurrent Phase-1 dispatches for DIFFERENT task IDs) is still unfixed at the infra level -- an in-band comment is not a durable fix, only a per-task-run file path (e.g. .talos/phase1-research-<task_id>.md) or truncate-on-write semantics will actually prevent recurrence. _(context: Auto-applied from continuous processor)_ [src: lesson-3127]
- **2026-10-03** — `general`: Recurring failure (3x): EMPTY_MODEL_OUTPUT: worker/model produced no output twice — infrastructure or routing failure; the task itself is untested. Check agent_rout

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-3884]
- **2026-10-03** — `general`: A hook that writes to the thing it just committed is an infinite loop. claude-session-stop committed the vault, THEN appended a boilerplate stanza to Projects/AI Handoff.md - leaving the vault dirty, which the next session-stop committed and appended to again. 4,865 auto-commits resulted; two fired 39 seconds apart on 2026-09-14. It also violated vault-historical-only by writing session state to the vault AND telling the next session to re-read that vault file instead of the CMDB. Fixed 2026-09-14: commit only if genuinely dirty, write the session pointer to the open-notebook handoffs notebook via kb write, never write back into the vault. A no-op session now leaves NO trace, which is correct - 4,865 identical entries are worse than none. Test both directions: 3 fires on a clean vault must produce 0 commits, and 1 fire with a real change must produce exactly 1 commit plus a KB note. _(context: Auto-applied from continuous processor)_ [src: lesson-2053]
- **2026-10-03** — `general`: Second occurrence (first was lesson #2267, product-11): .talos/phase1-research.md and sibling scratch files (cursor-brief.md, phase1-output.md, phase2-execute.md, phase2-output.md) in the vault are a single shared path, not task-isolated. Mid-research on product-item-146, phase1-research.md was found already overwritten with a brief for product-item-157, and the phase2 scratch files still held stale content from the even-older product-11 run. Pipeline needs a per-task-id scratch path or Phase 2 will eventually execute against the wrong tasks plan. _(context: Auto-applied from continuous processor)_ [src: lesson-2277]
- **2026-10-03** — `general`: Task #3383 (Digital Product #8, competitor-research gap-fill sweep) correctly declined: product-8/phase-0/execution-plan.md and phase-1/design-notes.md both confirm it is a retired duplicate dispatch of Strategy item #12 (third blueprint, canonical concept lives under Product #3, itself blocked upstream on Product #4 Phase 2). This is at least the 16th dispatch of work against product-8 since root cause lesson 1691 (blueprint filename collision + missing pre-dispatch GET /tasks dedup check), matching prior declines 1704,1723,1724,1727,1729,1861,1865 -- but this time via a catalog-wide 0/87-products competitor-research sweep rather than a REMEDIATION retry, showing the sweep also does not filter out retired/duplicate products before dispatching. Separately observed: the vault scratch file .talos/phase1-research.md was overwritten mid-task by a concurrent Phase 1 dispatch for a different product (Product #7) before this brief was written -- it is a single shared, non-task-keyed scratch path across concurrent Phase 1 dispatches, a race. Output was written to phase1-output.md instead to avoid clobbering the other task. _(context: Task #3383, Product #8 competitor-research sweep. Root dedup bug: lesson 1691. Product-8 retirement: lesson 1702. Prior decline chain: 1704,1723,1724,1727,1729,1861,1865.)_ [src: lesson-2884]
- **2026-10-03** — `general`: Talos two-phase dispatcher writes concurrent tasks to shared fixed-path scratch files (.talos/phase1-research.md, .talos/cursor-brief.md, .talos/phase2-execute.md, .talos/phase1-output.md, .talos/phase2-output.md in the vault root) instead of per-task paths. Confirmed directly: task #3619 (product-item-171) brief content in .talos/phase1-research.md was overwritten mid-session by a concurrent dispatch for task #3614/#3617-era work on product-item-163, verified via two consecutive Reads of the same file returning different task content, and via /tmp/helmsman-tasks/*.brief timestamps showing tasks 3613-3662 all queued within a 6-minute window. A prior task (#3615, product-146) result claimed this was already logged as "Lesson #2909" -- that lesson ID does not exist in the registry (404), so that claim was a subagent fabrication and should not be trusted; this is the first real log of the pattern. _(context: Task #3619 dispatch (competitor-research evidence for product-item-171). The underlying research goal was already satisfied on disk before this task ran (matches the separate, already-common late-arriving-duplicate-dispatch pattern), so this session did not depend on the shared-file race, but writing a Phase 1 brief into .talos/phase1-research.md would have been silently discarded or would have clobbered a concurrent task's in-flight work.)_ [src: lesson-2915]
- **2026-10-03** — `general`: Talos phase-1 research pipeline: multiple concurrent phase1 dispatches write their brief to the SAME shared scratch file (~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SeaynicNet/.talos/phase1-research.md) instead of a per-task/per-product path. Observed live 2026-09-24: a phase1 run for product-item-147 was mid-write to this file when a concurrent phase1 dispatch for product-item-139 (then another for product-item-138, task #3610) overwrote the top Original-Task-Request section with a different product goal while the in-progress brief text for the prior product remained appended below it -- producing a file whose header says one product and whose body brief discusses a different one. Root cause is a dispatcher/pipeline defect: phase1-research.md is a single global slot, not scoped per task_id/product_id. Fix belongs at the pipeline level (write to a per-task path like .talos/phase1-research-<task_num>.md, or a locking/queueing mechanism so only one phase1 run touches the shared file at a time) -- not something a single phase1 execution can work around. Separately confirmed (again) that product-item-147 itself already had complete, high-quality competitor-research evidence on disk (4 real Etsy comps, notes.md, 14 images) before this task reached execution -- 5th+ instance of the dispatch-lag duplicate pattern seen on 140/171/153/(now 147). _(context: Auto-applied from continuous processor)_ [src: lesson-2909]
- **2026-10-03** — `general`: During task #4140 (Digital Product #146 revision), observed that .talos/phase1-research.md in the SeaynicNet vault is used as a shared scratch path by multiple concurrent Talos Phase 1 (research/brief) dispatches with no per-task scoping. Within a single session, this file was read 3 times with 3 different Original Task Request bodies (product #57, then #164, then a version with #164/#160/#158 briefs stacked under one template header), and between one read and a subsequent append it was reset entirely back to the bare unfilled template (710 lines of stacked content -> 130 lines of empty template) by another concurrent writer -- meaning at least 3 other in-flight Phase 1 briefs (products #158, #160, #164) were silently destroyed, not just overwritten-but-recoverable. Any Phase 2/Cursor process relying on reading .talos/phase1-research.md for the compiled brief has no reliability guarantee which task's content (if any) it will find there. _(context: Auto-applied from continuous processor)_ [src: lesson-3114]
- **2026-10-03** — `general`: Talos Phase-1 scratch file .talos/phase1-research.md (in the SeaynicNet vault, not a repo) is a SHARED path reused across concurrent Phase-1 research tasks, not per-task. Wrote a full execution brief for Digital Product #160 revision (visual-quality feedback: flat vector-only PDF, zero images/illustrations, exercise library page shows only 1-of-30+ claimed exercises) and appended it to the file. On save, discovered the file had been concurrently overwritten/appended by at least two other Phase-1 tasks (Digital Product #164 and #158 revisions) -- the top Original Task Request block now reads #164 even though the #160 brief is still present further down the file. If this file is the real Phase-1-to-Phase-2 handoff channel, a downstream Phase-2/Cursor consumer reading it could pick up the wrong products header while multiple unrelated briefs sit concatenated in one file. Fix: give each Phase-1 task its own scratch path (e.g. per-task-id filename) instead of a single shared .talos/phase1-research.md, or have the orchestrator consume-and-clear immediately after each Phase-1 write. _(context: Auto-applied from continuous processor)_ [src: lesson-3102]
- **2026-10-13** — `general`: Recurring failure (4x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-22615]
- **2026-10-13** — `general`: Recurring failure (4x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-22765]
- **2026-10-13** — `general`: Recurring failure (5x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 5 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-22920]
- **2026-10-13** — `general`: Recurring failure (5x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 5 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-23228]
- **2026-10-13** — `general`: Recurring failure (4x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-23378]
- **2026-10-13** — `general`: Recurring failure (5x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 5 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-23513]
- **2026-10-13** — `general`: Recurring failure (5x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 5 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-23804]
- **2026-10-13** — `general`: Recurring failure (4x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-23948]
- **2026-10-13** — `general`: Recurring failure (4x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-24087]
- **2026-10-13** — `general`: Recurring failure (4x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-24239]
- **2026-10-13** — `general`: Recurring failure (4x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-24387]
- **2026-10-13** — `general`: Recurring failure (3x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-24537]
- **2026-10-13** — `general`: Recurring failure (3x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-24685]
- **2026-10-13** — `general`: Recurring failure (3x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 3 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-24836]
- **2026-10-14** — `general`: Recurring failure (4x): DoD validation failed - see deliverable Deliverable: Setup timed out after 15s (possible iCloud vault I/O stall)

Context: Error occurred 4 times across different tasks _(context: Auto-applied from continuous processor)_ [src: lesson-28895]
