---
name: failure-research
description: Root-cause investigation for fleet and infrastructure failures — crash loops, jobs that run but do nothing, services that report healthy but don't work, quota or rate-limit failures, runaway task generation, cost spikes, model or provider failures, stale data. Use whenever something across the agent fleet, helmsman, CMDB, containers, launchd or providers is failing, timing out, or behaving unexpectedly — not for a bug inside one codebase's logic (that's systematic-debugging). Triggers on "why is X failing", "X keeps failing", "investigate this", "it says healthy but", a cost alert, a recurring INFRA_ERROR, or any task titled "Research failure: ...".
---

# Failure Research

Fleet failures span systems, and the obvious signal (exit 0, /health ok, a
count of 0, a successful POST) is usually the thing that's lying. Find the
cause before fixing anything, and prove it with evidence from this occurrence.

## The method

1. **State the symptom precisely,** separating what was observed from what was
   reported. "Users get no reports" and "/health says ok" are both facts; only
   one is the user's outcome.
2. **Distrust the green signal.** Ask what the passing signal actually checks.
   Exercise the real function: make a real request, read the real output,
   inspect per-component results.
3. **Walk the usual suspects** (below) before inventing anything exotic. Most
   fleet failures here have been one of them.
4. **Find what changed,** and when. Line the onset up against deploys,
   retirements, quota resets, model deprecations and config edits.
5. **Find the generator.** For floods (duplicate tasks, runaway calls, cost
   spikes) find what is creating the work, and stop it before cleaning up.
6. **Root cause, then fix.** A retry, restart, wider timeout or lower cap
   without an explanation is a patch. Say why it failed, fix that, and confirm
   the original symptom is gone.
7. **Check the blast radius.** What else shares the dependency, quota or bug?
   Fix or flag those too.
8. **Record it.** Check helmsman `/lessons` for prior occurrences first
   (`curl -s "http://localhost:5682/lessons?q=<terms>&limit=5"`); once the
   cause is confirmed, write the lesson back. Never record a guess.

## Usual suspects in this fleet

| Pattern | Tell | Check |
|---|---|---|
| Liveness passes, function dead | ping, container Up, HTTP 200 or /health ok while users get nothing | Probe what the service does: a real call, name resolution, per-component results |
| Upstream model or provider gone | Works for months, then every call fails or falls back | Check each model against the provider's live catalog; look for 404/410, 402 payment-required, retired providers |
| Shared quota exhausted | 429s across unrelated callers; one heavy job starves the fleet | Read the error body (per-minute vs per-day limit); find which workload consumed it |
| Partial view treated as complete | Dedup misses, cleanups "converge" while rows remain, counts read 0 | Is the API returning a capped page? Count with a method that covers every row |
| Self-feeding generator | Task or call counts explode; titles nest | Find the producer and its guard; stop it, then clean up with a verified count |
| Unenforced limit | Spend or volume far past a configured cap | Find where the cap is supposed to be enforced; it often isn't |
| Ran but did nothing | Exit 0, scheduled, silent | Read the job's real side effects and dependencies (credentials, providers, PATH, TCC) |
| Old code still running | Fix is pushed but the symptom continues | Process start time vs commit time; restart and confirm a fresh PID |
| Misleading name | A component's name suggests a role it doesn't have | Read what it actually does before acting on it |
| Wrong signal feeding automation | An automated job acts on a metric that doesn't mean what it says | Verify what the metric counts before trusting the action |

## Evidence sources

helmsman task records (`/tasks/<num>`; read the error and failure output, not
just status), service and launchd logs (`StandardErrorPath` in the plist),
`docker logs` / `docker inspect`, provider error bodies and rate-limit headers,
router call logs, CMDB records compared against live state. Cite the specific
evidence for this occurrence in the conclusion.

The previous version of this skill, with the per-shape evidence table:
`references/original-2026-10-15.md`.
