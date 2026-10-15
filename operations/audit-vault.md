---
description: Scan vault project notes against actual repo state and fix drift
---

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
