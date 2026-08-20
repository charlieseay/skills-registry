---
name: audit-project
description: Safe project audit & auto-fix pipeline with regression prevention
tags: [security, code-review, testing]
---

# Audit Project

**Purpose:** Audit a project for code quality, security, and bugs, then auto-dispatch fixes one-at-a-time with regression detection.

**Safety:** Establishes baseline behavior FIRST, tests after EVERY fix, rolls back on regression.

---

## Usage

```bash
/audit-project [project-path]
```

**Example:**
```bash
/audit-project ~/Projects/enchapter-api
```

---

## What It Does

### Phase 1: Baseline Establishment (15-30 min)

1. **Snapshot current behavior**
   - API projects: hit all endpoints, save responses to `baseline/api-outputs/`
   - Frontend projects: screenshot key pages to `baseline/screenshots/`
   - Libraries: run existing tests, save outputs to `baseline/test-outputs/`

2. **Generate integration test suite** (if none exists)
   - API: curl commands for all endpoints
   - Frontend: Playwright smoke tests for critical paths
   - Library: unit tests for public API surface

3. **Git checkpoint**
   - Commit baseline/ directory
   - Tag: `audit-baseline-YYYY-MM-DD`

**Output:** `baseline/` directory with golden outputs for regression detection

---

### Phase 2: Audit (Read-Only, 30-60 min)

Run in parallel (no code changes):

1. **Code Review Agent**
   ```bash
   /code-review --level=high --focus=bugs,correctness
   ```
   - Correctness bugs (logic errors, edge cases)
   - Security vulnerabilities
   - Code quality issues

2. **Security Audit**
   - Check against `Standards/API Security Checklist.md` (12 requirements)
   - Run security scanners:
     - Python: `bandit -r .`
     - Node.js: `npm audit`
     - Docker: `docker scan <image>` (if applicable)

3. **Dependency Audit**
   ```bash
   npm audit --audit-level=moderate  # Node projects
   pip-audit  # Python projects
   ```

4. **Syntax Validation**
   - Run linters/type checkers
   - Validate all config files (JSON, YAML, Docker Compose)

**Output:** 
- All findings → helmsman.db tickets (tagged `audit-YYYY-MM-DD`)
- Priority-sorted by severity: Critical → High → Medium → Low
- Each ticket includes: file, line, issue, fix suggestion, verification steps

---

### Phase 3: Incremental Fix (Hours to Days, Depends on Finding Count)

**Loop (one fix at a time):**

1. **Pick highest-priority unfixed ticket**

2. **Dispatch fix brief** to appropriate worker (nvidia-agent, CURSOR, etc.)
   - Brief includes:
     - Issue description
     - Suggested fix
     - **Regression test:** `diff -r baseline/ current/ || exit 1`
     - **Functional test:** re-run integration suite

3. **Worker executes fix**

4. **Automated regression check:**
   ```bash
   # Re-run integration tests
   ./baseline/run-integration-tests.sh > current/test-outputs.txt
   
   # Compare outputs
   diff baseline/test-outputs.txt current/test-outputs.txt
   
   # API projects: compare responses
   for endpoint in baseline/api-outputs/*.json; do
     curl ... > current/$(basename $endpoint)
     diff <(jq -S . baseline/$(basename $endpoint)) \
          <(jq -S . current/$(basename $endpoint)) || echo "REGRESSION: $endpoint"
   done
   ```

5. **Decision point:**
   - **IF regression detected:**
     - `git reset --hard HEAD~1` (rollback)
     - Mark ticket as NHR (Needs Human Review)
     - Capture lesson: "Fix for X broke Y"
     - Alert Charlie via Slack
   - **IF clean (no regression):**
     - Commit fix: `git commit -m "audit-fix: <issue>"`
     - Update baseline if behavior intentionally changed
     - Mark ticket complete
     - Continue to next ticket

6. **Repeat until all tickets processed**

---

## Project-Specific Configurations

### API Projects (enchapter-api, reactpro, etc.)

**Baseline:**
- `baseline/api-catalog.json` — all endpoints
- `baseline/api-outputs/*.json` — response for each endpoint
- `baseline/openapi.json` — API schema (if exists)

**Integration tests:**
```bash
# baseline/run-integration-tests.sh
set -e
for endpoint in $(jq -r '.endpoints[]' baseline/api-catalog.json); do
  curl -sf "http://localhost:PORT$endpoint" > current/$(echo $endpoint | tr '/' '_').json
done
```

**Regression check:**
```bash
# Compare response schemas (allow new fields, block removed/changed fields)
for f in baseline/api-outputs/*.json; do
  diff <(jq -S 'keys' "$f") <(jq -S 'keys' "current/$(basename $f)") \
    || echo "REGRESSION: Schema changed in $(basename $f)"
done
```

### Frontend Projects (enchapter, hone, charlieseay.com)

**Baseline:**
- `baseline/screenshots/*.png` — key pages
- `baseline/lighthouse-scores.json` — performance/a11y
- `baseline/dom-snapshots/*.html` — critical page structure

**Integration tests:**
```typescript
// baseline/smoke-tests.spec.ts (Playwright)
test('homepage renders', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toBeVisible();
  await page.screenshot({ path: 'current/screenshots/homepage.png' });
});

test('navigation works', async ({ page }) => {
  await page.goto('/');
  await page.click('a[href="/about"]');
  await expect(page).toHaveURL(/.*about/);
});
```

**Regression check:**
```bash
# Visual regression (allow small differences, flag major layout changes)
compare baseline/screenshots/homepage.png current/screenshots/homepage.png \
  -metric RMSE diff.png 2>&1 | awk '{if ($1 > 0.05) exit 1}'
```

### Library Projects (stripe-mcp, vault-mcp, etc.)

**Baseline:**
- `baseline/test-outputs.txt` — all tests passing
- `baseline/public-api.json` — exported functions/classes

**Integration tests:**
```bash
# Re-run existing test suite
npm test > current/test-outputs.txt
pytest > current/test-outputs.txt
```

**Regression check:**
```bash
# Ensure test count doesn't decrease
BASELINE_COUNT=$(grep -c "✓" baseline/test-outputs.txt)
CURRENT_COUNT=$(grep -c "✓" current/test-outputs.txt)
[ "$CURRENT_COUNT" -ge "$BASELINE_COUNT" ] || exit 1
```

---

## Enforcement & Monitoring

### Bridge Dashboard Tile (Optional)

**Audit Progress**
- Project: enchapter-api
- Started: 2026-07-08
- Phase: Fixing (12/45 tickets complete)
- Last fix: CORS whitelist (no regression)
- Next: Rate limiting on /api/generate

### Slack Notifications

**Priority: low** (silent) — routine fix completed
**Priority: question** — regression detected, needs review
**Priority: error** — worker failed to execute fix

---

## Example: Enchapter API Audit Flow

### Phase 1: Baseline (enchapter-api)

```bash
cd ~/Projects/enchapter-api

# Start local server
npm run dev &
sleep 5

# Snapshot all endpoints
mkdir -p baseline/api-outputs
curl http://localhost:3033/api/books > baseline/api-outputs/books.json
curl http://localhost:3033/api/catalog > baseline/api-outputs/catalog.json
curl http://localhost:3033/api/books/the-gift-of-fear > baseline/api-outputs/book-detail.json

# Generate API catalog
cat > baseline/api-catalog.json <<EOF
{
  "endpoints": [
    "/api/books",
    "/api/catalog",
    "/api/books/:slug"
  ],
  "captured": "2026-07-08T18:00:00Z"
}
EOF

# Git checkpoint
git add baseline/
git commit -m "audit: establish baseline for regression detection"
git tag audit-baseline-2026-07-08
```

### Phase 2: Audit (enchapter-api)

Run `/code-review --level=high --focus=security,bugs`

**Findings dispatched to helmsman.db:**
1. #2401 [CRITICAL] SQL injection risk in book search (enchapter-api/routes/search.ts:42)
2. #2402 [HIGH] No rate limiting on /api/generate endpoint
3. #2403 [HIGH] CORS allows all origins in production
4. #2404 [MEDIUM] hasContent logic inconsistent (uses chapter_count vs actual chapters)
5. #2405 [LOW] Missing input validation on book slug parameter

### Phase 3: Fix #2401 (SQL Injection)

**Brief dispatched to CURSOR:**

```markdown
## Goal
Eliminate SQL injection risk in book search by using parameterized query

## Context
File: enchapter-api/routes/search.ts:42
Current: `db.query(\`SELECT * FROM books WHERE title LIKE '%\${query}%'\`)`
Risk: User input concatenated directly into SQL

## Steps
1. Read current implementation
2. Replace with parameterized query: `db.query('SELECT * FROM books WHERE title LIKE ?', [\`%\${query}%\`])`
3. Run syntax check: `tsc --noEmit`
4. Run integration tests
5. Compare API outputs vs baseline

## Verification
\`\`\`bash
# Syntax check
tsc --noEmit || exit 1

# Integration test (try SQL injection)
curl 'http://localhost:3033/api/search?q=test%27%20OR%201=1--' | jq .
# Should return empty results, not all books

# Regression check
curl http://localhost:3033/api/books > current/books.json
diff <(jq -S . baseline/api-outputs/books.json) <(jq -S . current/books.json) || exit 1
\`\`\`

## Success
- SQL injection attempt returns empty results (not all books)
- Legitimate search still works
- API contract unchanged (regression check passes)
```

**CURSOR executes:**
- Fix applied
- Syntax check: ✅
- Functional test: ✅ (injection blocked, search works)
- Regression check: ✅ (API outputs match baseline)

**Outcome:**
- Commit: `audit-fix: eliminate SQL injection in book search`
- Ticket #2401 → shipped
- Continue to ticket #2402

---

## Rollback Example (Regression Detected)

**Scenario:** Fixing #2404 (hasContent logic) breaks iOS app

```bash
# Worker applies fix, runs regression check
curl http://localhost:3033/api/books > current/books.json
diff baseline/api-outputs/books.json current/books.json

# Output:
# < "hasContent": true
# > "hasContent": false
# REGRESSION DETECTED: hasContent field changed for book with chapters
```

**Automated rollback:**
```bash
git reset --hard HEAD~1  # Undo commit
# OR (if not committed yet)
git checkout -- routes/books.ts
```

**Ticket #2404 marked NHR:**
```json
{
  "num": 2404,
  "status": "nhr",
  "nhr_reason": "Regression: fixing hasContent broke API contract (changed true→false for books with chapters)",
  "lesson_captured": "hasContent field used by iOS app for UI state; any change requires coordinated iOS+API deploy"
}
```

**Slack alert (priority: question):**
> 🚨 **Regression detected in enchapter-api**
> Ticket #2404 (hasContent fix) broke API contract
> Rolled back automatically
> Charlie: this needs coordinated iOS+API deploy

---

## Related Standards

- [API Security Checklist](Standards/API Security Checklist.md) — 12 security requirements
- [Code Validation Standard](Standards/Code Validation Standard.md) — Syntax checks before done
- [Brief and Delivery Standard](Standards/Brief and Delivery Standard.md) — QA requirements

---

## Tags

`#audit #security #regression-testing #code-review #incremental-fix`
