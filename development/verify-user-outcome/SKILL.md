---
name: verify-user-outcome
description: Before calling anything done, tested, shipped, fixed or live, check the outcome the way its user would actually see it, not the signal underneath (a passing test, an HTTP 200, a success message, a status field, a file that exists). Use when tests pass, a deploy finished, a listing or product was published, a skill/config/lane was changed, a script reported success, or right before telling Charlie something works. Triggers on "tests pass", "done", "shipped", "it's live", "deployed", "fixed", "published", "verified".
---

# Verify the User's Outcome

Every piece of work has someone it's for: a buyer opening a download, a person
clicking a button, an agent loading a skill, Charlie reading a report. "Done"
means that person sees the right result. Everything short of that (a green test,
a 200, a script's "0 errors", status=shipped, a file that exists) is a signal
that usually correlates with the outcome. It isn't the outcome.

## The check (before saying done)

1. **Name the user and the moment.** Who consumes this, and where do they look?
   The public URL, not localhost. The live listing, not the upload response. The
   skill list an agent actually sees, not the registry row. The PDF opened in a
   real viewer, not the script that generated it.
2. **Look there, the way they would.** Open it, click it, read it, run the exact
   command shown to them. For anything visual, look at the pixels. For anything
   with a count or claim ("15 templates", "fixed", "7 personas"), count or test it.
3. **Compare to the claim.** Does what you see match what you're about to report?
   Quote the evidence: what you opened and what it showed.
4. **Check what could undo it.** Could the result be reverted, overwritten,
   hidden or never reached? A process that didn't reload new code, a retry that
   rewrites reviewed files, a cache in front of the change, a config the running
   service ignores, an item that reappears from another view.
5. **Report the evidence, not the signal.** "Live listing shows 6 images, hero
   is the new one" beats "upload succeeded".

## Signals that are not outcomes

| Signal | What it misses | Check instead |
|---|---|---|
| Tests pass | Tests may assert the contract (API returned 200) but not the visible result | Would the suite still pass if the re-render, propagation or final step broke? If yes, it isn't testing the outcome |
| HTTP 200 / health ok | The page renders while everything behind it is dead | Exercise the real function (a real request, the real integration) |
| Script reports success | It reports what it attempted, not what landed | Inspect the side effect directly (live API, file contents, readlink) |
| Status = shipped / QA pass | The producing agent's own check can pass on wrong output | Open the deliverable; check it's the right product, complete, not placeholder |
| File exists, right size | Could be a stub, a duplicate, or the wrong product | Open it; compare against the claim |
| Pushed / committed | The running process still has old code | Restart, confirm a fresh PID, re-test the original symptom |
| Config changed | The service may ignore unknown values or fall back silently | Confirm from the service's own log or behavior which value it used |

## UI state changes

For toggles, moves between lists, deferrals and status transitions, the outcome
is where the item ends up. Trace click → API → state → re-render → what's
visible, and test to the last step. Full guidance and the incident behind it:
`references/ui-state-change-tests.md`.
