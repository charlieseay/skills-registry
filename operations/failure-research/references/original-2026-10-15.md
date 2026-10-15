---
name: failure-research
description: Structured root-cause investigation for fleet and infrastructure-level failures — crash loops, model routing/evaluation failures, validator bugs, recurring INFRA_ERROR task failures, stale-data symptoms, or launchd/container lanes that die silently. Use this whenever a task, monitor, or Charlie reports something is failing, crashing, timing out, or behaving unexpectedly across the agent fleet, helmsman, CMDB, containers, or launchd — not for a bug inside a single codebase's tests or logic, which is systematic-debugging's job instead. Triggers on "why is X crashing", "investigate this failure", "X keeps failing", "evaluate model Y for routing", a recurring INFRA_ERROR or worker/transport failure, or any task titled "Research failure: ...".
---

# Failure Research

## Why this exists

Fleet-level failures (a crash-looping container, a launchd lane exiting green
while doing nothing, a model that fails routing evaluation, a validator that
rejects good work) are shaped differently than a bug in one codebase. They
span multiple systems (helmsman, CMDB, Docker, launchd, model routers), the
evidence lives in different places depending on failure type, and — critically
— many of them have already happened before and been diagnosed. The helmsman
`/lessons` log exists specifically to short-circuit re-diagnosing a known
failure from scratch, but it only works if it's checked *first*, not after.

This skill is the fleet-ops counterpart to `systematic-debugging` (which
covers root-causing bugs inside a single codebase's code/tests). Use this one
when the failure is about the *system running the code*, not the code itself.

**Core principle, shared with systematic-debugging:** find the root cause
before proposing a fix. A patched symptom on a fleet-level failure is
especially costly here, because it tends to recur across many tasks rather
than one.

## Step 1: Classify the failure

Naming the shape narrows where to look immediately:

| Shape | Signature | Where the evidence lives |
|---|---|---|
| Crash loop | A container or process repeatedly restarts | `docker logs <container> --tail 200`, `docker ps` restart count |
| Launchd lane failure | A scheduled job "ran" (exit 0) but did nothing, or exits non-zero | **Exit code alone is not a health signal** — check the interpreter's TCC grants, `PATH` inside the launchd environment, the shebang binary, and actual stdout/stderr log files (see `reference_launchd_lane_failure_modes` — 4 known silent-death modes) |
| Model evaluation / routing failure | A model candidate fails an eval gate, or routing picks a bad model | The router's eval output/logs, not just "it seemed to fail" |
| Validator / lint bug | A brief or deliverable is rejected by a validator that shouldn't have rejected it | The validator's own rule definition plus the specific deliverable that tripped it |
| INFRA_ERROR / worker-transport failure | Task fails before being judged at all — e.g. `HTTPConnectionPool(host='localhost...` | The worker process's own logs/health, not the task content — the task never actually ran |
| Stale-data symptom | Something reads as wrong because the data feeding it is old, not because the logic is wrong | The data source's last-updated timestamp vs. when it was actually queried |

If a failure doesn't fit cleanly, say so rather than forcing it into the
nearest category — investigate what actually happened before classifying.

## Step 2: Check `/lessons` before re-diagnosing

```bash
curl -s "http://localhost:5682/lessons?q=<key terms from the failure>&limit=5"
```

or `kb search "<topic>" -n lessons -l 5`. Several of these failure types are
*known recurring* — the session-start invariants already surface some (e.g.
"Recurring failure (9x): INFRA_ERROR: worker/transport failed before the task
was judged"). If this exact or a closely related failure is already logged,
start from that lesson's root cause and confirm it still applies, rather than
re-running the full investigation from zero. If the lesson's fix was applied
before and the failure recurred anyway, that itself is a finding — the fix
didn't address the actual root cause, or something regressed it.

## Step 3: Pull real evidence for *this* occurrence

Don't reason from the failure type in the abstract — get this specific
instance's evidence:

- **Helmsman task:** `curl -s "http://localhost:5682/tasks/<id>"` — read the
  actual error/deliverable field, not just the status.
- **Container:** `docker logs`, `docker inspect` for restart count and exit
  code history.
- **Launchd:** `launchctl list <label>` for load state, plus the lane's actual
  log file (location is job-specific — check the plist's
  `StandardOutPath`/`StandardErrorPath`).
- **Model routing:** the router's own decision/eval log for that specific
  call, not a summary.

A failure-research task that concludes without citing the specific evidence
for *this* occurrence (not just "this is a known issue") hasn't actually
investigated it.

## Step 4: Root-cause, not symptom-patch

Ask: does this explanation account for *why* the failure happens, not just
*that* it happens? "The container keeps crashing" is a symptom. "The
container crashes because it OOMs at ~1.2GB and the compose file caps it at
1GB" is a root cause. If the fix under consideration is a restart, a retry,
or a wider timeout with no explanation of the underlying trigger, that's very
likely a patch, not a fix — go one layer deeper first.

## Step 5: Close the loop — write the lesson back

Once root-caused (and ideally fixed), write it to helmsman so the next
occurrence short-circuits at Step 2 instead of repeating this whole
investigation:

```bash
curl -s -X POST "http://localhost:5682/lessons" \
  -H 'Content-Type: application/json' \
  -d '{"lesson": "<failure type>: <root cause>. Fix: <what resolved it>. Evidence: <how to recognize it next time>."}'
```

Skip this only if the investigation is still open (root cause not yet
confirmed) — a half-diagnosed guess written to `/lessons` pollutes the next
agent's Step 2 lookup worse than no lesson at all.
