# Test Plan Anti-Patterns

Seven ways a test plan looks thorough and isn't. Each shows the bad case, why it passes on broken software, and the replacement.

---

## 1. Testing the API instead of the user flow

The endpoint returns 200. The user sees a white screen.

**BAD**
```markdown
- Steps: `curl -s http://localhost:3000/api/projects`
- Expected: 200 with `[{"id":1,"name":"Talos"}]`
```
Passes while the React component throws on a null status icon and renders nothing.

**GOOD**
```markdown
- Steps:
  1. Launch Playwright, navigate to http://localhost:3000/projects
  2. Collect console errors via page.on('console')
  3. Wait for [data-testid="project-card-1"]
- Expected:
  - page.errors() length is 0
  - [data-testid="project-card-1"] visible within 2000ms
  - .project-name text equals "Talos"
```

---

## 2. Happy path only

**BAD**
```markdown
- Steps: `seaynic-cli create --name my-project --tier pro`
- Expected: Project created successfully.
```
Never exercises `--tier invalid`, which produces a traceback and exits 0.

**GOOD**
```markdown
- Steps:
  1. `seaynic-cli create --name my-project --tier invalid-tier`
  2. Capture stdout, stderr, exit code
- Expected:
  - Exit code 1
  - stderr contains "Error: Invalid tier 'invalid-tier'. Allowed: starter, pro, enterprise."
  - stdout contains zero occurrences of "Traceback (most recent call last)"
- Falsification: same command with `--tier pro` must exit 0
```

---

## 3. Tautological checks

An assertion that passes on broken software is not an assertion.

**BAD**
```markdown
- Steps: `./backup-db.sh`
- Expected: exit 0 and /backups/db.sql exists
```
`sqlite3 .dump > file` creates a 0-byte file and exits 0 when the source path is wrong. Test passes; data is gone.

**GOOD**
```markdown
- Steps:
  1. `sqlite3 ./app.db "INSERT INTO canary (val) VALUES ('canary-999');"`
  2. `./backup-db.sh`
  3. `test -s /backups/db.sql`
  4. `grep -q canary-999 /backups/db.sql`
  5. `sqlite3 /tmp/restore.db < /backups/db.sql`
  6. `sqlite3 /tmp/restore.db "SELECT val FROM canary WHERE val='canary-999';"`
- Expected: step 3 exit 0, step 4 exit 0, step 6 stdout equals "canary-999"
- Falsification: step 4 against an empty file must exit 1
```

---

## 4. Browser cache masking failures

**BAD**
```markdown
- Steps: Navigate to /dashboard in the existing Chrome profile
- Expected: Dashboard loads
```
Your cached JWT and stale JS chunks hide the infinite redirect loop a first-time visitor hits.

**GOOD**
```markdown
- Steps:
  1. Launch a fresh Playwright context: incognito, no cookies, cache disabled
  2. Navigate to http://localhost:3000/dashboard
- Expected:
  - Redirect to /login?redirect=%2Fdashboard
  - Initial navigation status 302 or 307
  - input[name="email"] is focused
```

When using Chrome DevTools MCP, pass `ignoreCache: true` on reload — this is a standing rule, not a suggestion.

---

## 5. Admin privilege leak

**BAD**
```markdown
- Steps: `curl /v1/exports/123 -H "Authorization: Bearer $MASTER_ADMIN_KEY"`
- Expected: export payload returned
```
The customer role lacks the `exports:read` scope. Nobody finds out until a customer complains.

**GOOD**
```markdown
- Steps:
  1. `customer_token=$(./bin/create-test-token --role customer --tier basic)`
  2. `curl -s -w "\n%{http_code}" /v1/exports/123 -H "Authorization: Bearer $customer_token"`
- Expected:
  - status 200
  - body contains only customer-owned records
- Falsification: expired customer token must return 401
```

---

## 6. Hollow ship / ghost artifacts

The single most expensive failure in this shop. Tests pass in the source tree; the customer downloads a zip with no product in it.

**BAD**
```markdown
- Steps: `pytest tests/`
- Expected: 10 passed
```
The build script omits `templates/` from the zip. Every test passes. Every customer refunds.

**GOOD**
```markdown
- Steps:
  1. `./build-release.sh`  → dist/starter-kit.zip
  2. `unzip dist/starter-kit.zip -d /tmp/sterile-install`
  3. For every filename referenced in README.md, assert it exists in the extracted tree:
     `for f in $(grep -oE '\`[A-Za-z0-9_./-]+\.[a-z]+\`' README.md | tr -d '\`'); do
        test -s "/tmp/sterile-install/$f" || echo "MISSING: $f"; done`
- Expected: step 3 output is empty
- Falsification: delete one referenced file from the zip; step 3 must name it
```

Run this against every digital product before it goes on sale.

---

## 7. Verification that fails when it passes

`grep -c` exits **1** when it finds zero matches. Under `set -o errexit` — which
autonomous runners use — a "prove this string is absent" check therefore fails
the task at the moment it succeeds.

Cost a real task: 2026-08-26, #1689 unlisted a product correctly (HTTP 302, zero
checkout strings) and was marked `needs_human_review` because the verification
block exited 1 on the passing case.

**BAD**
```bash
curl -s -o /dev/null -w '%{http_code}\n' https://store.example.com/products/x
curl -s https://store.example.com/products/x | grep -ci checkout
```
Exits 1 exactly when the product is correctly unlisted.

**GOOD**
```bash
code=$(curl -s -o /dev/null -w '%{http_code}' https://store.example.com/products/x)
hits=$(curl -s https://store.example.com/products/x | grep -ci checkout || true)
echo "status=$code checkout_hits=$hits"
test "$code" != "200" && test "$hits" -eq 0 && echo "PASS: unlisted"
```

Rules for any absence assertion:
- Capture counts into a variable with `|| true`, then `test` the value
- Never let a bare `grep -c`, `grep -q`, or `test -f` be the last command in an
  `errexit` block when zero/absent is the PASS condition
- Echo the observed values before asserting — a receipt showing `status=302
  checkout_hits=0` explains itself; a bare exit code does not

## 8. Asserting a layout instead of the requirement

A verification that hardcodes where a file lives fails correct work that put it
somewhere equally valid. The requirement is "12 dashboards exist", not "12 files
match `dashboards/*.json`".

Cost a real task twice on 2026-08-26: #1691 shipped 12 Grafana dashboards under
`grafana/dashboards/`; the brief globbed `dashboards/*.json`, counted 0, and the
task was sent to `needs_human_review` with the work complete on disk.

**BAD**
```bash
ls *.json dashboards/*.json 2>/dev/null | wc -l    # 0 — wrong directory
test -x deploy.sh                                   # fails on a valid non-exec file
```

**GOOD**
```bash
n=$(find . -name '*.json' -path '*dashboard*' | wc -l | tr -d ' ')
echo "dashboards=$n"
test "$n" -ge 12 && echo PASS
```

Rules:
- Search with `find` for the property, don't glob an assumed path
- Assert a threshold (`-ge 12`), not an exact tree shape
- Echo the observed value so the receipt shows *why* it passed or failed
- If the layout genuinely matters, say so in the brief's Expected Output — then
  the verification is testing a stated requirement, not a guess

## 9. Voice drift / AI-slop copy

**BAD**
```markdown
- Steps: Read the landing page
- Expected: Page looks good and explains the product
```
Ships "In today's fast-paced environment, leverage our seamless, game-changing solution."

**GOOD**
```markdown
- Steps:
  1. `node ./scripts/extract-strings.js > /tmp/ui-strings.txt`
  2. `grep -icE "seamless|leverage|game-chang|robust|dive deep|supercharge|elevate|revolutioniz|empower|delve|in today's|unlock the power" /tmp/ui-strings.txt`
  3. `grep -icE "^[[:space:]]*(Are you|Want to|Need to|Looking for|Ready to|Tired of)" /tmp/ui-strings.txt`
  4. `grep -icE "\b(most|many|some) (developers|users|teams|people)\b" /tmp/ui-strings.txt`
- Expected: steps 2, 3, and 4 each output 0
- Falsification: inject "seamless" into one string; step 2 must output ≥1
```

Full rule set lives in the `writing-rules` skill. The lint above covers the mechanically checkable subset; a human or model still reads for the rest.
