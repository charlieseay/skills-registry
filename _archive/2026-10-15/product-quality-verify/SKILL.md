---
name: "product-quality-verify"
description: "Verify a claim about a digital product's actual content — a file/asset count, a \"unique\" or \"distinct\" claim, whether a deliverable matches its listing copy, whether a linked resource (Notion template, Google Doc, etc.) actually works for a customer — by inspecting the real files/URLs, never by trusting filenames, a prior audit's conclusion, or an AI-written quality report. Use this before accepting any \"below bar,\" \"mismatched count,\" \"not actually unique,\" or \"broken link\" verdict about a Talos/digital-product deliverable, and before repricing, reworking, or relisting a product based on such a claim. This is the digital-product-specific sibling of state-reconciliation — reach for that skill for infra/deployment claims, this one for \"is this product actually what its listing says it is.\""
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["talos-product-launch-audit", "fix-listing-content-violations", "state-reconciliation"]
---

# Product Quality Verification

**Fleet-wide skill** — this is a verification discipline (open the files,
check the claim), not a tool-specific procedure. Any agent with file/URL
access can apply it.

## Why this exists

On 2026-09-21, a quality-gate audit assessed 25 Talos digital products and
flagged two as `BELOW_BAR` for fabricated headline counts. One of those two
verdicts was itself wrong: the audit claimed a font bundle shipped "35 of 44
claimed characters, no numerals at all." Direct inspection of the actual
delivered files found all 44 characters present, including all 10 numerals,
with a file count that exactly matched the listing's own stated math. The
audit had drawn a specific, confident, wrong conclusion — the kind of finding
that would have triggered real rework on a product that was already correct.

In the same session, a separate agent reported "20 of 33 published listings
have no matching pipeline product" — a 61% orphan rate presented as a data
quality finding. The real cause was comparing live listing titles against
the wrong field (a generic placeholder like "Strategy Item #139" instead of
the actual product name, which was one directory-level deeper in a listing
copy file). The true orphan rate was near zero.

On 2026-09-22, a fresh full-catalog audit (27 products) reported one product
as "ERROR — no local directory exists (orphaned)." Direct inspection found
the directory did exist, containing a `DUPLICATE-NOTE.md` explaining it was
an intentionally-abandoned duplicate of a different, already-canonical
product folder. The rest of that same 27-product report held up under
independent spot-checking of 5 more "CLEAN" verdicts (zip contents matched
category expectations in every case) — the point isn't that agent audits
are usually wrong, it's that *specific checkable claims* need checking
regardless of how well-evidenced the surrounding report reads.

**The pattern in all these cases: an agent inferred something about content
from metadata, file names, or one field, when the real answer required
opening the actual files.** This skill exists so that inference gap gets
closed before anyone acts on it — reworking a fine product wastes time;
shipping one that's actually broken loses a customer.

## Core principle

A quality or content claim about a product ("N unique items," "ships X
format," "the link works," "meets the count in the title," "this directory
doesn't exist") is a hypothesis until someone has opened the actual
deliverable and checked. A confident, well-structured audit report is not
evidence — it's a claim with the same verification burden as anything else.

## When to use this

- Before accepting a "below bar," "fails the count," "not actually distinct,"
  "mismatched," or "orphaned/missing" verdict from any quality gate, AI
  review, or audit — automated or agent-generated.
- Before reworking, relisting, retitling, or repricing a product based on
  such a verdict.
- Before trusting a claim that compares two things without opening both (e.g.
  "the title says 480, the files suggest 96" — did anyone look at the images,
  or infer from filenames alone?).
- Before trusting any "X% match rate" or "N items orphaned/missing" figure
  that came from comparing against one specific field — check whether that
  field is actually authoritative or just a placeholder.
- Before telling a customer or listing platform anything about a product's
  contents that traces back to an unverified audit.

## How to verify, by claim type

### "N items/characters/assets are missing" or "count doesn't match"

Don't count filenames matching a pattern and stop there — a naming
convention can undercount or overcount depending on how it's structured
(size variants, format variants, and base items can all live in the same
directory). Instead:

1. Find the actual claim's unit of measurement precisely (e.g. "44
   characters per font" — a character, not a file; each character may exist
   in multiple sizes/formats, which is not the same as 44 files).
2. Extract the real distinct set directly: strip known variant suffixes
   (size, format, color/tier) and count what's left, then sanity-check the
   total file count against the stated formula (e.g. `5 fonts × 44 chars × 3
   sizes × 2 formats = 1320` — if the actual file count matches this
   arithmetic, the components are very likely all present; if the arithmetic
   doesn't match the claimed shortfall either, the shortfall claim is
   suspect).
3. List the specific missing items by name, don't just report a smaller
   total. "35 not 44" without naming which 9 are missing is not verified —
   it's an assumption dressed as a finding.

### "These aren't actually unique / distinct" (recolors, resizes, near-duplicates)

Filenames and byte-hashes cannot answer this — a resized or recolored image
has a different hash and a plausible-looking distinct filename while being
the same design. This requires actually looking at the rendered content:

1. Use the Read tool (or equivalent) to view the actual image files, not
   just list them.
2. Pick a sample the claim itself would predict as duplicates (e.g. rarity
   tiers of "the same" icon) and visually compare: same silhouette/shape
   with only a color change (supports the claim), or genuinely different
   composition (refutes it).
3. Also sample a set the claim says should be distinct from each other, as a
   negative control — if those also turn out identical, the whole product
   has a problem; if they're clearly different, the base library itself is
   fine even if variant-counting inflated the total.
4. State plainly what you saw, not just a verdict — "tier 2 and tier 3 of
   the sword icon are pixel-identical except for a palette swap" is
   checkable by someone else; "not unique" is not.

### "This link/deliverable is broken" (dead Notion share, expired URL, wrong file)

1. Find where the actual customer-facing link/file lives (README, delivery
   instructions, listing copy) — don't assume it's the same as an internal
   draft link found elsewhere in the pipeline.
2. Actually fetch it (WebFetch, curl, or equivalent) and read what comes
   back — a login wall, a 404, a generic marketing page, and a working
   duplicatable template all look superficially similar in a one-line
   summary; describe the actual page content/title/visible affordances
   (e.g. "a Notion 'Duplicate' button is present" vs. "shows the unpublished
   app shell") so the finding is falsifiable.
3. Check each instance independently if a claim covers multiple products —
   don't assume they all fail the same way just because they're grouped in
   one audit finding.

### "N% orphaned / no match found" (cross-referencing two records)

1. Confirm the field being matched against is actually authoritative for
   that comparison. A generic placeholder, a truncated title, or a
   differently-cased string will produce false non-matches.
2. Before accepting a high non-match rate, spot check 2-3 of the "orphaned"
   items by searching more broadly (other files in the same
   record/directory, not just the one field originally compared) — if the
   real data is one directory level away, the whole "orphan" rate is an
   artifact, not a finding.
3. A suspiciously clean 100%-match result after a correction pass deserves
   the same scrutiny as a suspiciously bad one — spot check the correction,
   don't just trust that "fixed" means "now correct." (On 2026-09-21, a
   "0 orphaned, 100% matched" follow-up still contained two wrong
   assignments — verified by checking a row against data already
   independently confirmed earlier in the same session.)

### "This directory/product doesn't exist" or "is an error/orphan"

1. Actually list the directory before concluding it's missing — a `find` or
   `ls` that returns nothing because of a typo'd path or wrong working
   directory looks identical, from a summary, to a genuinely absent folder.
2. If it exists but looks abandoned or incomplete, check for its own
   explanation before flagging it as broken — a `DUPLICATE-NOTE.md`,
   `INVESTIGATION-*.md`, or similar file often documents that the folder
   was intentionally superseded by a different one. That's a resolved,
   correctly-handled situation, not an error needing action.

## Reconcile, don't just report

- If the original claim holds up: say so and move on — confirming a real
  defect is exactly what the check is for.
- If the original claim is wrong: say so plainly, don't soften it into
  "partially accurate." A hallucinated defect is a different failure mode
  from a real one and should be named as such so the pattern (which
  agent/prompt/model produced it) can be tracked.
- If verifying requires a capability you don't have in the current context
  (e.g. rendering an image you can't open, hitting a rate-limited API),
  say that explicitly rather than letting the unverified claim stand by
  default. An unverified claim should never silently convert into an
  accepted one just because nobody got around to checking it.
