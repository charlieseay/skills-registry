---
name: state-reconciliation
description: Verify a claimed state — a HANDOFF note, CMDB record, task status, "this was deleted/deployed/migrated," or any assertion about the current state of a system — against what is actually true right now, then close the gap. Use this whenever you are about to relay, report, or act on a status claim you haven't personally checked against a live source this session: "is X still running", "confirm Y was deleted", "did the migration finish", "what's the current state of Z", before writing anything into a HANDOFF or CMDB record, or before telling Charlie something is "done". Also use it proactively when a claim smells stale — a note that hasn't been touched in weeks but reads as current, or a "completed" status with no verification evidence attached. This is the general-purpose version of audit-vault (vault-notes-only) and branch-drift-sweep (git-only) — reach for this one for everything else: CMDB, containers, launchd, deployments, credentials, datastores.
---

# State Reconciliation

## Why this exists

The same failure has recurred independently across at least five different
projects: a record says one thing, reality says another, and the gap goes
unnoticed until it costs real time. A HANDOFF claimed "63 remaining" when the
actual count was 209. A note looked current while describing state that was
five weeks stale. A leaked credential was documented as "expired" while it was
still live and usable. A datastore migration was declared "actually complete"
three separate times, because each declaration was based on believing the last
one rather than checking the running system. A service was told to shut down
and nobody confirmed it actually had.

None of these were caused by carelessness in the moment — they were caused by
treating a *written claim* as equivalent to a *verified fact*. This skill is
the fix: a repeatable way to close that gap instead of re-discovering it every
time.

**Core principle:** A claim about system state is a hypothesis until it has
been checked against a live source in this session. Yesterday's verification
does not carry forward — state changes.

## When to use this

- Before writing "done," "deployed," "deleted," "migrated," or any status word
  into a HANDOFF, CMDB record, or reply to Charlie.
- Before relaying a claim you read in a note, a prior session's summary, or
  another agent's report — including a subagent's hand-back. A subagent's
  status claim is an input, not a fact.
- Whenever you notice a note or record that looks current but hasn't been
  touched recently — staleness hides in plain sight because well-formatted
  notes look authoritative regardless of age.
- Whenever a "delete," "shut down," or "retire" instruction was given — the
  record of the action is not the action.

**Every dispatched-agent completion is a mandatory trigger, not a judgment
call.** When you fan work out to subagents (Agent tool, Workflow, anything
async) and one reports back "done," "pushed," "fixed," "clean" — run it
through this skill before relaying it, every time, not only when something
smells off. 2026-09-21: a subagent claimed a 95-commit branch was "pushed to
main" after cleaning a leaked secret from its history; the actual push step
had silently never happened (main was still 160 commits behind). A second
subagent's own write-up contradicted itself in the same paragraph (one line
said "resolved to main's version," the next said "accepted branch's
pattern") and would have gone unnoticed without a line-by-line re-read. Both
were caught only by re-running `git log origin/main..HEAD --oneline | wc -l`
myself — the exact step 2 this skill already prescribes. Do that check by
default for every "done," not just the ones that read strangely; a
well-written, internally-consistent false claim is possible and the report's
prose quality is not evidence of anything.

## The four steps

### 1. Identify the claim and its source

State plainly what is being claimed and where it came from: a HANDOFF.md
line, a CMDB field, a task's `status`, a prior session's summary, another
agent's report. Vague claims ("things are running fine") aren't
reconcilable — narrow to a specific, checkable assertion first ("the
Centaur container is up," "the Hetzner open-query service is stopped," "PAT
`ghp_...` is revoked").

### 2. Query the live source of truth — never assume, never reuse a stale check

Match the claim to where the real answer lives. Do not substitute a proxy for
this — a CMDB record *asserting* deletion is worse than a missing one, because
it actively blocks re-discovery.

| Claim about | Live source | NOT this |
|---|---|---|
| A task's status | `curl -s http://localhost:5682/tasks/<id>` | The vault, a HANDOFF, memory of what it was last time |
| A CMDB record (host/service/product) | `curl -s http://192.168.68.78:8117/api/<resource>` | An older CMDB snapshot, a vault note describing the CMDB |
| A container running/stopped | `docker ps`, `docker compose ps` on the actual host | A monitor dashboard that hasn't polled recently |
| A launchd lane's health | `launchctl list <label>` **and** its actual log output — exit code alone is not a health signal (see `reference_launchd_lane_failure_modes`: TCC grants, PATH, interpreter shebang, env formatting can all cause a "healthy" exit 0 on a lane doing nothing) | Trusting a green dashboard tile |
| A service on a remote host stopped/deleted | SSH in and check the process list / provider console directly | Believing the shutdown script ran without exit-checking it |
| A credential's live/revoked state | The provider's own console or API (GitHub tokens API, cloud IAM) | A note saying "rotated" or "expired" |
| A git branch/PR state | `gh pr view`, `git log`/`git reflog` on the actual remote | A stale local checkout |

The vault (`Documents/SeaynicNet`) is historical record only — never treat
vault content as the live source for anything it merely narrates.

### 3. Compare claim vs. reality, field by field

Don't eyeball it — list the specific fields the claim makes (count, status,
timestamp, boolean up/down) and check each one against what step 2 returned.
Partial matches are still drift: "mostly deployed" is not "deployed."

### 4. Reconcile — don't just report

This is the step most likely to get skipped under time pressure, and skipping
it is what let three of the five cases above happen more than once.

- **If they match:** say so plainly and move on — a verified match is a
  legitimate, useful outcome, not a wasted check.
- **If they diverge and the fix is in scope:** patch the record (HANDOFF,
  CMDB, task status) **in this same session**, not as a follow-up. A drift
  finding that doesn't get patched immediately becomes the next session's
  rediscovery of the same drift.
- **If the divergence needs a decision only Charlie can make** (e.g., which
  value is actually correct, or whether to roll back): file one helmsman
  decision showing both the claimed value and the verified value side by
  side, rather than silently picking one.
- **If the claim was actively fabricated** (not just stale, but describing
  something that was never true) — flag this distinctly, it's a different and
  more serious failure mode than drift.

## Negative control — the check must be able to fail

If this skill reports "verified, no drift" every single time it runs, treat
that as a signal the check itself is broken, not that the system is healthy —
a verification that cannot fail proves nothing. Periodically sanity-check by
deliberately tracing a claim you have strong reason to doubt (an old note, a
"completed" task with no evidence attached) rather than only checking claims
that are likely to already be fine.

## Worked example

**Claim:** HANDOFF.md says "Hetzner Talos services fully shut down, migration
to Mac Mini complete."

1. Source: `Projects/Talos/HANDOFF.md`, dated 2026-08-26.
2. Live check: SSH to the Hetzner host and check for `talos-kb-service.py` in
   the process list (this exact gap was previously found unresolved — the
   shutdown script's SSH connection failed mid-run and nobody re-verified).
3. Compare: HANDOFF says "stopped." Process list may still show it running.
4. Reconcile: if still running, kill it, verify with a second process check,
   then patch HANDOFF.md in this same session to reflect the confirmed state
   — not "should be stopped" but "confirmed stopped as of <timestamp>, verified
   via `ps` on <host>."

## Worked example — subagent hand-back

**Claim:** A dispatched agent reports "Pushed branch to main. Final state:
main is up to date with origin/main, merge is aborted, working tree is
clean." (Actual wording from a real report — note it does NOT plainly say
"merge succeeded"; it describes an *aborted* merge in the same breath as
declaring success, which a fast read skips past.)

1. Source: the agent's own final message, not independently verified this
   session.
2. Live check: `git log origin/main..<branch> --oneline | wc -l` on the real
   repo. Also `git fetch origin main` first — a stale local `main` will
   under-report divergence.
3. Compare: the count was 160, not 0. The merge had not happened; only a
   history-rewrite-and-force-push of the *branch* had. "Main is up to date"
   was true and irrelevant — it was up to date because nothing had been
   merged into it yet.
4. Reconcile: this needed a real merge with conflict resolution — genuinely
   more work, not a rubber-stamp. Dispatched a follow-up, then re-verified
   the same way (`git log origin/main..HEAD --oneline | wc -l` == 0, no
   `<<<<<<<` markers anywhere in the tree, gitleaks clean) before reporting
   it done.
