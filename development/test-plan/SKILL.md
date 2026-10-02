---
name: test-plan
description: 'Author a comprehensive end-to-end test plan for a product, service, API, MCP server, dashboard, or digital download. Covers five perspectives (admin, customer, technical, non-technical, voice/language) across eight lifecycle stages (discovery → install → first use → thorough use → edge cases → failure modes → support → exit). Use whenever the user asks to "write a test plan", "how do we test X", "QA plan", "acceptance criteria", "verify this is ready to ship", or before any product launch. Also use to REVIEW an existing test plan for completeness — it carries a coverage gate that fails inadequate plans.'
---

# Test Plan

Write test plans that catch what actually ships broken: hollow products whose README promises files the zip doesn't contain, dashboards showing stale data, services that pass an API check and fail in a browser, and copy that reads like a language model wrote it.

A test plan is not a list of features with "verify it works" beside each one. It is a set of executable assertions with observable results, written from five different chairs, across the whole customer lifetime.

## Step 1 — Decompose into surfaces

Every product ships across five surface layers. Enumerate them before writing a single test case.

| Layer | What lives here |
|---|---|
| **Acquisition** | Landing page, pricing, checkout, webhook, receipt email |
| **Distribution** | The bytes the customer receives: zip, npm package, Docker image, git repo, PDF |
| **Interface** | HTTP endpoints, CLI commands, MCP tools, UI routes |
| **Execution** | State: database, cache, worker queues, filesystem, browser storage |
| **Operational** | Logs, metrics, health probes, config, cost tracking |

To decompose:

1. **Inventory every claim.** Extract every filename, command, flag, and capability promised in the README, sales copy, and API docs into a checklist. Each becomes a test case. This one step catches hollow products.
2. **Map the delivered artifacts.** List every byte the customer receives.
3. **Map the entry points.** Every endpoint, command, tool, route.
4. **Identify state boundaries.** Every database, file path, `localStorage` key, queue.
5. **Identify operational controls.** Every log stream, health endpoint, env var.

## Step 2 — The five perspectives

Each perspective sits in a different chair and sees different failures. A plan missing any one of them is incomplete.

| Perspective | Sits as | Hunts for | Verifies by |
|---|---|---|---|
| **ADMIN** (`ADM`) | The operator running this | Silent failures, unmonitored cost burn, missing logs, no recovery path, zombie processes | Process inspection, `launchctl`/`docker` probes, log validation, cost counters, simulated crash + restart |
| **CUSTOMER** (`CUS`) | A paying stranger | Broken downloads, missing promised files, useless errors, dropped webhooks, stuck subscriptions | Clean-room execution as an unprivileged user, real download + unzip, Stripe test-mode checkout |
| **TECHNICAL** (`TEC`) | An engineer evaluating | Undocumented 500s, injection, race conditions, type mismatches, CORS, auth boundaries | Status code checks, schema validation, concurrent hammering, malformed payloads |
| **NON-TECHNICAL** (`NON`) | Someone who doesn't code | Raw stack traces in the UI, jargon errors, no visual confirmation, unclear value | Layout checks, plain-language error audit, DOM text inspection, "could my mother do this?" |
| **VOICE** (`VOI`) | The brand auditor | AI-slop phrasing, question openers, passive voice, hedging, marketing fluff | Automated string extraction + lint against the voice rules (see `writing-rules` skill) |

**Never collapse perspectives.** An API test is not a customer test. Admin credentials are not customer credentials.

## Step 3 — The eight lifecycle stages

Cover all eight. Skipping the back half is how you ship a product nobody can uninstall.

1. **DISCOVERY** — Landing page, pricing, docs. Do the claims match the backend? Do the links resolve?
2. **INSTALL / ONBOARD** — Clean environment, no pre-cached deps. Permissions, layout, zero implicit globals.
3. **FIRST USE** — Time to first value. Must reach an observable win in under 5 minutes with zero warnings.
4. **THOROUGH USE** — Real workloads. Data written in step A is queryable in step B, survives restart, appears in UI without a manual refresh.
5. **EDGE CASES** — Empty input, 10MB payloads, Unicode/emoji/RTL/null bytes, zero quantities, rapid repeats, rate limits.
6. **FAILURE MODES** — Cut the network, pass a bad token, make the DB read-only, kill a dependency. Errors must be structured and actionable, never a hang or a silent success.
7. **SUPPORT** — `--help` on every subcommand. Errors state the root cause AND the fix command. Logs redact secrets.
8. **EXIT** — Uninstall, revoke, export, delete. Zero orphaned lockfiles, daemons, or credentials.

## Step 4 — Write executable test cases

A test case is executable only when an agent can run it deterministically and get an unambiguous PASS/FAIL.

**Rules:**

- **Concrete preconditions.** Not "system running" — `PORT=8080 npm start &` then `curl -sf localhost:8080/health`.
- **Deterministic steps.** Exact command or exact DOM selector. Numbered.
- **Observable assertions.** Exact exit code, stdout regex, HTTP status, response key/value, or DOM selector text. Never "verify it works."
- **A falsification check.** State how the assertion goes RED. If the check passes against a deliberately broken build, the check is worthless — this is the single highest-value rule here.

Use this template verbatim:

```markdown
### [TP-{SURFACE}-{PERSPECTIVE}-{NNN}] {Imperative title}

- **Perspective**: ADMIN | CUSTOMER | TECHNICAL | NON-TECHNICAL | VOICE
- **Lifecycle Stage**: DISCOVERY | INSTALL | FIRST_USE | THOROUGH_USE | EDGE_CASES | FAILURE_MODES | SUPPORT | EXIT
- **Severity on Failure**: P0 | P1 | P2 | P3
- **Preconditions**:
  - {exact directory, env vars, service state}
- **Steps**:
  1. `{exact command}`
  2. `{exact command}`
- **Expected Result (Observable)**:
  - {exact exit code / HTTP status / stdout match / DOM text}
- **Falsification Check (Red Probe)**:
  - {how to make this assertion fail — proves the check has teeth}
- **Actual Result**: `[PENDING]`
- **Status**: `[NOT RUN | PASS | FAIL | BLOCKED | SKIPPED]`
- **Proof**: `[receipt path, terminal output, or screenshot]`
```

## Step 5 — Classify severity

- **P0 — Blocker.** Promised files missing from the deliverable. Service won't start. Silent failure (error occurs, exit code 0 or UI says success). Credential leak.
- **P1 — Critical.** Primary workflow fails with no workaround. Data corruption. Payment webhook drops entitlement. Unhandled 500 with a stack trace.
- **P2 — Major.** Feature fails but an obvious workaround exists. Dashboard stale until manual refresh. Error message missing context.
- **P3 — Polish.** Voice violation. Minor layout glitch. Log missing a correlation ID.

## Step 6 — Run the coverage gate

A plan that fails any box below is not finished. Include this filled-in gate at the bottom of every plan.

```markdown
## Coverage Gate

### Parity
- [ ] 100% of files named in README/docs asserted to exist with non-zero size
- [ ] 100% of CLI commands and flags have an executable case
- [ ] 100% of API endpoints have status + payload assertions
- [ ] 100% of pricing/sales claims validated against actual backend behavior

### Perspectives
- [ ] ADMIN ≥2 cases (monitoring, log inspection, recovery)
- [ ] CUSTOMER ≥3 cases (acquisition, clean install, refund/exit)
- [ ] TECHNICAL ≥4 cases (validation, error schemas, auth boundaries)
- [ ] NON-TECHNICAL ≥2 cases (visual clarity, plain-English copy)
- [ ] VOICE ≥2 cases (all user-facing strings audited)

### Lifecycle
- [ ] All 8 stages represented
- [ ] ≥1 clean-room test in an isolated environment
- [ ] ≥1 test asserting time-to-first-value under 5 minutes

### Rigor
- [ ] Zero vague assertions ("verify it works", "check output", "ensure success")
- [ ] Every assertion names an exact code, status, selector, or regex
- [ ] Every case has a falsification check
- [ ] Dashboard/report tests assert live values, not fixtures

### Isolation
- [ ] Customer cases run WITHOUT admin credentials
- [ ] Browser cases run with cleared cache and fresh storage
```

## Step 7 — Avoid the seven anti-patterns

Read `references/anti-patterns.md` for the good/bad case pairs. Summary:

1. **Testing the API instead of the user flow.** The endpoint returns 200; the React component throws and the user sees white. Drive the browser.
2. **Happy path only.** Valid input works; `--tier invalid` produces a traceback and exit code 0.
3. **Tautological checks.** `test -f backup.sql` passes on a 0-byte file. Write a canary value and read it back.
4. **Browser cache masking failures.** Your cached JWT hides the redirect loop a new visitor hits. Ephemeral context, cache disabled.
5. **Admin privilege leak.** Master token passes; the customer role lacks the scope. Provision a real customer token.
6. **Hollow ship.** `pytest` passes in the source tree; the build omits `templates/` from the zip. Test the artifact, not the repo.
7. **Verification that fails when it passes.** `grep -c` exits 1 on zero matches; under `errexit` an absence check fails at the moment it succeeds. Capture counts with `|| true`, then `test` the value.
8. **Voice drift.** "Seamless, game-changing solution." Extract every string and lint it.

## Step 8 — Store the plan

Test plans belong in open-notebook so every agent can find them:

```bash
kb write -n qa-kb -t "<Product> Test Plan" -f <path-to-plan.md>
```

`kb write` upserts by title, so re-running updates rather than duplicating. Also commit the plan to the project repo under `docs/test-plans/` so it versions with the code.

## Output contract

One markdown file per service or product. Named `<service-slug>-test-plan.md`. Contains: a surface decomposition table, the test cases grouped by perspective, and the filled coverage gate. Every case uses the template. No case says "verify it works."
