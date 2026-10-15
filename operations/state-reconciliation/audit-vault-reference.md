# Vault Audit Deep-Dive Reference

This reference documents detailed vault auditing procedures for state reconciliation. This is the vault-notes-specific version of the broader `state-reconciliation` skill.

## Audit Vault Project Notes vs Repos

Scan vault project notes against actual code repository state and identify drift in status, version, test counts, and timestamps.

### Usage

- `/audit-vault` — full scan of all mapped projects
- `/audit-vault <project>` — scan a single project (e.g., `/audit-vault sounding`)

This is the vault-notes-only specialization. For everything else (CMDB, containers, launchd, deployments, credentials), use the broader `state-reconciliation` skill.

### Project-to-Repo Mapping Template

| Vault Note | Code Repo | Test Runner | Extra Checks |
|-----------|-----------|-------------|--------------|
| Projects/[project]/[project].md | ~/Projects/[project] | pytest | version, PyPI |
| Projects/[project]/[project].md | ~/Projects/[project] | swift test | swift build |
| Projects/[project]/[project].md | ~/Projects/[project] | npm test | version |
| Projects/[project]/[project].md | ~/Projects/[project] | npm run build | playwright |

### Audit Procedure

#### 1. Pre-flight

Check which projects to audit:
- If an argument was provided, filter to that project only
- If no argument, audit all projects in the mapping
- Skip any project whose repo path does not exist on disk (report as "repo missing")

#### 2. Read Each Vault Note

Extract from frontmatter and body:
- **status** — project state (active, paused, decommissioned, retired, superseded)
- **updated** date — when the note was last touched
- **version** — look for patterns like `v1.2.3`, `version: 1.2.3`, `## Version`
- **test count** — look for patterns like "XX tests", "XX passing", "test count: XX"
- **deployment state** — look for "deployed", "live", "spec only", "in development"

#### 3. Check Each Repo

Gather actual state from the code repo:

**Version (Python):**
```bash
grep -m1 'version' /path/to/<repo>/pyproject.toml 2>/dev/null || \
grep -m1 '__version__' /path/to/<repo>/src/*/__init__.py 2>/dev/null
```

**Version (Swift):**
```bash
grep -m1 'version:' /path/to/<repo>/Package.swift 2>/dev/null
```

**Version (Node):**
```bash
node -e "console.log(require('/path/to/<repo>/package.json').version)" 2>/dev/null
```

**Tests:**

| Runner | Command | How to count |
|--------|---------|-------------|
| pytest | `cd /path/to/<repo> && python -m pytest --tb=no -q 2>&1` | Parse "X passed" from output |
| swift test | `cd /path/to/<repo> && swift test 2>&1` | Parse "Test Suite ... passed" |
| npm test | `cd /path/to/<repo> && npm test 2>&1` | Parse from test runner output |
| npm run build | `cd /path/to/<repo> && npm run build 2>&1` | Pass/fail only (no count) |
| xcodebuild | `cd /path/to/<repo> && xcodebuild -scheme <name> -destination 'platform=iOS Simulator,name=iPhone 16' build` | Pass/fail only |

**Last commit:**
```bash
git -C /path/to/<repo> log -1 --format='%ci' 2>/dev/null
```

**Repo health:**
```bash
test -d /path/to/<repo>/.git && echo "yes" || echo "no"
```

#### 4. Compare and Report

Build a findings table:

```
| Project | Note Status | Actual Status | Tests (Note) | Tests (Actual) | Version (Note) | Version (Actual) | Updated (Note) | Last Commit |
```

Flag drift:
- **Status drift** — note says "spec only" but repo has passing tests → flag
- **Test count drift** — note claims 42 tests but pytest reports 47 → flag  
- **Version drift** — note says v0.2.0 but pyproject.toml says 0.3.1 → flag
- **Staleness** — last commit >7 days newer than note's `updated` date → flag

Summarize findings:
- Total projects scanned
- Projects with drift (list each issue)
- Projects fully in sync
- Projects skipped (repo missing)

#### 5. Offer Fixes (Do Not Auto-Fix)

For each drift found, propose changes:
- Update `updated` frontmatter to today's date
- Update version references to match code
- Update test counts to match actual
- Update status if clearly wrong

**Do not auto-fix.** Present proposed changes and wait for confirmation before editing.

### Lessons

- **`monitoring_doc_drift_false_alarms`** — Before declaring a service 'DOWN', check against REALITY not the CLAUDE.md port table. A container 'Up' with an unpublished port is proxy-only (not broken); a missing service may be decommissioned (not down).
- **`status-vocab-drift-3-layers`** — When data disappears from a UI, check status-vocabulary drift across ALL layers: source DB statuses, n8n columns, AND Bridge's KNOWN_STATUSES. Unknown statuses get silently coerced to 'Queued'.
- **`status-schema-vocab-drift-recurring`** — The #1 suspect when a UI shows nothing or wrong data is status/schema-vocabulary drift across layers. Check + fix EVERY layer, not just the one that looks wrong.

### Implementation Notes

- Run tests in parallel where possible to keep audits fast
- Python: activate venv if present (`source .venv/bin/activate`) before pytest
- Swift tests can be slow on first build — warn users
- If no tests configured, report "no tests" rather than failing
- Vault paths contain spaces — always quote them in commands
- Designed to run weekly but works anytime
