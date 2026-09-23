---
name: "fix-listing-content-violations"
description: "Diagnose and fix exactly why a Talos digital product is blocked from publishing with a \"Content validation failed - internal/leaked content detected\" error, by running the real validator function against the actual current listing-copy file instead of trusting the (often stale) error string cached in STATUS.json. Use this whenever a product's STATUS.json shows a content-validation error for Etsy or Gumroad, before republishing anything, or whenever \"Strategy Item #N\" / \"Product #N\" placeholder-title problems come up."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["talos-product-launch-audit", "product-quality-verify"]
---

# Fix Listing-Content Validation Violations

**Fleet-wide skill** — the fix here is reading a Python file and calling one
function; any agent capable of running Python can do this, not just one tool.

## Why this exists

On 2026-09-21, two products (product-item-142, product-item-35) were blocked
from publishing with the exact same cached error text in STATUS.json:
`"Content validation failed - internal/leaked content detected: Internal
product number in body text..."`. Both looked identical from that error
string alone. Running the real validator against each product's *current*
listing-copy file showed the actual violations were completely different
per product and, for one of them, **not what the cached error said at all**:

- product-item-35: a literal leftover line `Reference: Strategy item #35.`
  at the top of the listing copy — a stray internal note, one-line fix.
- product-item-142: **not** a "Product #N" violation despite the cached
  error text saying so. The real, current violations were three internal
  `phase-N/...` file-path references leaked into customer-facing body text
  (a price citation and an "internal — not for listing" scope note that a
  publish step was apparently including anyway).

**The lesson: STATUS.json's cached validation error is a snapshot from
whenever it last ran, not a live diagnosis.** The listing copy may have been
edited since, or the error may have come from a different code path than
current validation logic. Never guess at the fix from the error string alone
— always re-run the actual validator against the current file.

## Step 1 — find the real validator and its exact patterns

The validator lives in `listing-bot`'s own codebase:

```
/Volumes/data/projects/listing-bot/src/validators.py
```

Read it. As of 2026-09-21 it has (at minimum) two pattern families:

- `PLACEHOLDER_TITLE_PATTERNS` — matches when the **entire title** is just
  `Product #N` or `Strategy Item #N` (anchored with `^...$`).
- `INTERNAL_NUMBERING_IN_BODY` — matches `Product #N` / `Strategy Item #N`
  (and lowercase variants) appearing **mid-text** anywhere in the
  description.

Check the file for any additional pattern families before assuming the list
above is complete — this file gets extended over time and this skill's
summary can go stale exactly the way STATUS.json's cached error did. Also
check for a phase-path leak check (matching literal `phase-0`, `phase-1`,
etc. in body text) — this is what actually blocked product-item-142.

## Step 2 — run the real function against the current file, don't pattern-match by eye

Import and call the actual validator directly. This is authoritative; eyeballing
the text for "Product #" is not, because you don't know every pattern family
without reading the file first, and grep alone won't tell you which specific
violation type fired.

```python
import sys
sys.path.insert(0, "/Volumes/data/projects/listing-bot/src")
from validators import validate_listing_content

# Read whatever file is actually used as description at publish time —
# check the product's phase-3 directory for etsy-listing-copy.md or
# listing-copy.md (naming is inconsistent across products; find the one
# publish_product.py actually reads for this product).
title = "..."       # the actual listing title
description = open("path/to/listing-copy.md").read()

violations = validate_listing_content(title, description)
print(violations)   # empty list == clean, ready to publish
```

An empty list is the only thing that means "fixed" — don't declare a product
unblocked because the error you found *looks* addressed; re-run the function
and confirm zero violations.

## Step 3 — fix precisely, don't rewrite wholesale

Once you know the exact violating pattern and which line(s) trip it:

- **A stray internal reference line** (like `Reference: Strategy item #35.`):
  delete the line. Don't touch anything else in the file.
- **A file-path citation in body text** (like `` `phase-0/market-analysis.md` ``):
  reword to describe the same fact without the internal path — e.g. "anchored
  to a comparable listing with 2,655 sales and a 4.88★ rating" instead of
  citing the internal research file by path.
- **A whole section explicitly marked "internal — not for listing"** that is
  nonetheless getting included in what's sent to the platform: this is a
  **pipeline bug**, not just a copy problem. Two possible fixes: (a) the
  section should be moved to a separate file that publish_product.py never
  reads, or (b) whatever code assembles the description needs to stop
  reading past the internal-marker heading. Flag this as a root-cause issue
  worth fixing in the pipeline itself if you see it more than once — a
  human writing "not for listing" and having it ship anyway is a process
  failure, not a one-off typo.

Re-run Step 2's validator call after editing. Confirm the returned list is
empty before considering the fix complete.

## Step 4 — this only clears local validation, not live-platform state

A clean `validate_listing_content()` result means the copy is *safe to
attempt publishing* — it does not mean the product is live. After fixing the
copy:

- If the product has never been published, it still needs to go through
  the normal publish flow (which itself should now succeed since the
  content gate will pass).
- If a stale STATUS.json shows `published: false` but the product might
  actually already be live under old copy (a real pattern found the same
  night — see `product-quality-verify` and the Etsy/Gumroad API skills),
  check the live platform directly before assuming this is a fresh
  publish rather than a listing that needs its live copy updated.

## Step 5 — update STATUS.json's cached error, don't leave it stale

Once the fix is verified (empty violations list), update the product's
STATUS.json to remove or correct the stale error message. Leaving the old,
now-inaccurate error text in place is exactly what caused the confusion this
skill exists to prevent — the next agent to look at this product should see
truth, not last week's diagnosis.
