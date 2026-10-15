---
name: verify-user-outcome
description: Before calling a feature "tested" or "done," verify it from the user's actual vantage point — the visible outcome they'd see — not just the API/data contract underneath it. Use this after writing tests for any feature with a UI or user-visible behavior, before claiming a passing test suite means the feature works, and especially for state-change features (toggles, defers, moves-between-buckets) where the API can succeed while the visible result is wrong. Triggers on "tests pass", "I tested this", "e2e passing", or right before marking a feature done off test results alone.
---

# Verify User Outcome, Not Just the Contract

## Why this exists

A Bridge defer-note feature shipped with 6 E2E tests and 25 unit tests, all
passing, and still had a real UX-breaking bug surface hours later: the
tests confirmed the API contract (a defer call succeeds, returns the right
shape) but never checked the actual visible outcome the feature exists to
produce — does the row actually move to the deferred bucket after a real
defer call, from the same place a user would look?

This isn't a missing-test-coverage problem in the usual sense (more tests
of the same kind wouldn't have caught it) — it's a **vantage-point**
problem. Every one of those 31 tests was asking "did the API do the right
thing," and none were asking "does the thing the user is looking at now
look right." Those are different questions, and a feature can pass every
instance of the first while failing the second.

## The check

Before treating a state-change feature as verified, name the answer to two
different questions and confirm both are covered:

1. **Contract question:** did the API/function call succeed and return the
   expected shape? (Usually what unit/integration tests already check.)
2. **Outcome question:** after this action, does the thing the user would
   actually be looking at reflect the change? Not "did the endpoint return
   200" — did the row move, did the badge update, did the item disappear
   from the list it's supposed to leave and appear in the one it's supposed
   to join?

A test suite that only answers question 1 is not incomplete in volume — it's
answering a different question than "does this feature work." Adding more
tests of the same kind (more contract assertions) doesn't close this gap;
only a test that inspects the same view/state a real user would inspect
does.

## Where this bites hardest: state-change features

Toggles, defers, moves-between-buckets, status transitions — anything where
the "correct" outcome is defined by *where something ends up*, not just
*whether a call succeeded*. For these specifically:

- Trace the full path a real user action takes: click → API call → state
  update → re-render → what's now visible. Test needs to reach the last
  step, not stop at the API call.
- If the test asserts on the API response body rather than the resulting
  UI/list state, that's the tell that it's answering the contract question
  only.
- Ask: "if I broke the re-render step but left the API untouched, would
  this test suite still pass?" If yes, it isn't testing the outcome.

## Relationship to test-plan

This isn't a replacement for the `test-plan` skill — that skill's "verify
from the user's actual vantage point" principle is the general version of
this. This skill exists as a sharper, narrower trigger specifically for
"I already wrote tests and they pass, am I actually done" — the moment
where it's easiest to stop one question short.
