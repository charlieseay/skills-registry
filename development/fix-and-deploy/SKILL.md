---
name: fix-and-deploy
description: Fix a bug in a running service, verify the fix against the ORIGINAL failing symptom (not a proxy for it), deploy, then re-verify against the live deployed target before calling it done. Use whenever a fix is going out to something already running — a service, a container, a site, a Cloudflare-fronted app — not just committed to a branch. Triggers on "fix and deploy", "push the fix", "ship this fix", "restart the service", or any two-part ask that couples a code change with getting it live. Especially load this before writing "fixed" or "deployed" for a production target.
---

# Fix and Deploy

## Why this exists

Two dispatched fixes went out today with a verification step that looked
complete but wasn't:

- A Cloudflare-fronted bug was "fixed and verified" — against
  `localhost:8101`, a local test copy, never against the actual public
  target the bug was reported against. It happened to also be true this
  time, which is worse than being caught, because it teaches that the
  shortcut works.
- Two "fix it" dispatches to running services (nvidia-agent-svc, Bridge)
  worked out, but were verified with "restart the service and curl /health"
  — which proves the service came back up, not that the reported bug is
  gone. Health-check-green and bug-fixed are different claims.

Both share one root cause: verifying against a *proxy* for the real target
(a local copy, a generic health check) instead of the *actual* failing
symptom on the *actual* target. This skill makes that distinction the
default check instead of something re-derived per incident.

## The sequence

### 1. Reproduce the original symptom first — don't skip to writing a fix

Before touching code, confirm you can see the actual reported failure: the
specific error, the specific broken behavior, on the specific target it was
reported on. If you can't reproduce it, you don't yet know what "fixed"
means for this bug.

### 2. Fix it

Standard debugging applies here — see `failure-research` (fleet/infra
scope) or `systematic-debugging` (codebase scope) if the root cause isn't
obvious yet. Don't start this skill's later steps until the fix addresses
a root cause, not a symptom.

### 3. Verify against the ORIGINAL symptom, on the REAL target — not a proxy

This is the step that failed twice today. Ask explicitly: what target does
the bug report describe, and am I checking that exact target?

| If the bug was reported against... | Verify against... | NOT this |
|---|---|---|
| A public/Cloudflare-fronted URL | That public URL, from outside the local network if the bug could be routing/DNS/CDN-related | `localhost` or a local dev copy |
| A specific error a user saw | Reproducing that exact error path | A generic smoke test that happens to pass |
| A reported bug in behavior X | Testing behavior X specifically | `curl /health` or "the service restarted cleanly" |
| A specific input/data shape | That exact input | A simplified or synthetic substitute |

"It's public, so the proof must be public too" — if the target is reachable
by the outside world, your verification needs to reach it the same way,
not through a local shortcut that happens to correlate most of the time.

### 4. Deploy

Follow the project's actual deploy path — Mac builds, other hosts run (see
CLAUDE.md's deployment targets table). Don't skip this distinction: a fix
that's correct locally but never reaches the real running target isn't
deployed, whatever the commit log says.

### 5. Re-verify live, against the original symptom, a second time

After deploy, repeat step 3's exact check against the now-deployed target.
This is not redundant with step 3 — step 3 proved the fix works where you
made it; this step proves it actually reached where the bug was. A fix that
passes step 3 but was never actually deployed (a push that silently didn't
land, a container that didn't restart, a CDN cache serving the old version)
will fail this step and only this step.

### 6. Close the loop

If this was a recurring or fleet-level failure, write the resolution back to
`/lessons` per `failure-research`'s step 5, so the next occurrence
short-circuits instead of re-diagnosing from scratch.

## The rule in one line

**If the target is public, the proof must be public too.** Every other
mistake in this skill collapses to some version of verifying against a
stand-in instead of the real thing.
