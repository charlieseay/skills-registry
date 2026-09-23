---
name: "talos-product-launch-audit"
description: "Run the audit-and-launch cycle for Talos-generated digital products before or after they go live on Etsy/Gumroad — quality verification, duplicate detection, pricing sanity check, listing-content validation, and inventory reconciliation. Also wired as an automated event-driven post-publish hook in listing-bot (helmsman/watch_approvals.py calling src/workers/post_publish_audit.py) that runs scoped per-product checks and immediately auto-deactivates defects on the spot. Use this whenever Talos has produced a new batch of products, whenever Charlie asks to \"get products ready to publish,\" \"clean up the shop,\" \"check for duplicates/false advertising,\" or on any recurring cadence (weekly/monthly) as Talos keeps shipping."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["etsy-api", "gumroad-api", "product-quality-verify", "fix-listing-content-violations", "state-reconciliation"]
---

# Talos Product Launch Audit — the recurring cycle

## Why this exists

On 2026-09-21, a single audit pass on ~25 Talos products found: 30 duplicate
Etsy listings, 6 duplicate Gumroad listings, 4 products advertising a
finished template while shipping a build-specification document instead
(confirmed live, zero sales — pure luck), 1 product with completely
corrupted deliverable files, 1 product shipping admittedly-incomplete
content, 1 product with a totally mismatched deliverable (font files sold
as a Notion planner), and at least one live listing with **leaked LLM
prompt/scratchpad text** visible to customers. Every one of these was
caught only by direct, repeated, skeptical verification against live
platform APIs — never by trusting a single audit pass, a STATUS.json field,
or a subagent's self-report.

**Talos will keep producing products for months.** This exact cycle will
recur. This skill exists so the next agent running it — whichever agent
that is — doesn't have to reconstruct the sequence, the verification
discipline, or the hard lessons from scratch — and so the fixes converge
into durable skills instead of being re-solved as one-off conversation work
each time. **This is a fleet-wide skill: any agent capable of making HTTP
calls and reading files can run this cycle, not just one specific tool.**

## The five sub-skills this orchestrates

Read each one when you reach its step — don't try to hold all of them in
context at once. All five live alongside this one under the shared
`product` skill category:

1. **`etsy-api`** — auth pattern, dedup-check-before-publish rule, listing
   fee economics, price-update inventory-endpoint gotcha.
2. **`gumroad-api`** — auth pattern, the `PUT published=false` silent no-op
   trap, dedup-check-before-publish rule.
3. **`product-quality-verify`** — how to check a content/count/uniqueness
   claim against the actual files, not filenames or a prior audit's
   conclusion.
4. **`fix-listing-content-violations`** — how to diagnose and fix a
   "Content validation failed" block by re-running the real validator
   against current files, never trusting the cached error string.
5. **`state-reconciliation`** (general fleet skill, not product-specific) —
   the underlying discipline that every step below depends on: a claim
   (from a file, a subagent, a prior "done" report) is a hypothesis until
   checked against the live source, in this session, right now.

## The cycle, in order

### Phase 1 — Ground truth on both platforms

Pull the FULL current state from both platforms directly (per `etsy-api`
and `gumroad-api`) before looking at any local file. Do not start from
STATUS.json, the Bridge dashboard, or any cached inventory — all three have
been proven wrong on the same night this skill was written.

- Etsy: `GET /shops/{shop_id}/listings?state=active&limit=100`
- Gumroad: `GET /v2/products`

Check for duplicate titles on each platform (exact match, and close fuzzy
match — a bot that reformats a title slightly is still a duplicate). This
is usually the fastest, highest-value first pass: duplicates cost real
listing fees on Etsy and confuse buyers on both platforms, and they are
mechanically checkable with zero ambiguity.

### Phase 2 — Truth-in-listing sweep (highest severity, do this before pricing/imagery)

For every live listing, cross-reference the promise in the title/description
against the actual delivered files. Watch for these specific patterns,
found repeatedly on 2026-09-21:

- **Spec-sold-as-product**: description promises "ready-to-use," "duplicate
  this template," "a comprehensive system" etc., but the deliverable zip
  contains a file named like `*BUILD-SPECIFICATION*.md` or
  `*build-specification*.md` — instructions to build the thing, not the
  thing itself. Grep every live product's zip for this filename pattern as
  a fast first signal, then confirm by reading the file. **This is not
  automatically a violation** — several products legitimately sell a build
  specification and disclose it prominently in the listing copy (e.g. "This
  is a step-by-step build specification, not a pre-built template — you
  build it yourself in ~35-40 minutes"). Check whether the listing discloses
  this before flagging it; an undisclosed build-spec is the violation, a
  disclosed one is a legitimate product category.
- **Content mismatch**: the deliverable doesn't match the category at all
  (e.g. font files shipped for a listing that describes a Notion planner).
  This tends to trace back to a build-artifact cross-contamination between
  two different pipeline products — check the product's own STATUS.json
  history for a prior QA note about files being mixed up; if one exists,
  the listing copy was very likely never updated to match the corrected
  package.
- **Corrupted deliverable**: don't just count files — open a sample file's
  actual internal structure. A `.dst` embroidery file, for instance, can
  have the right filename and a plausible byte size while its stitch header
  shows a zero bounding box and 1-4 total stitches (meaningless output).
  Apply this "open the actual content, not just the filename/count"
  standard per `product-quality-verify`.
- **Leaked generation artifacts**: read the FULL live description text at
  least once per product, not just a summary. A raw LLM reasoning
  scratchpad ("We need to produce a product description... let's count
  manually...") can end up as the literal live customer-facing text if a
  generation step's intermediate output gets published instead of its
  final output. This is easy to miss if you only check for known bad
  keywords — read for coherence, not just absence of red-flag phrases.
- **Leaked pipeline vocabulary in tags** (found 2026-09-22): a listing's
  13 Etsy tags can end up populated with ad-campaign/automation jargon
  (`campaign`, `ad group`, `criterion type`, `keyword`, `labels`, `build`,
  `comp-confirmed`) instead of real buyer search terms. This isn't
  customer-facing risk the way leaked scratchpad text is, but it silently
  destroys discoverability — check a sample of live tags across the
  catalog for this pattern, especially on any shop with real listings but
  zero/near-zero views.
- **Leaked internal IDs rendered INTO images, not just text** (found
  2026-09-22, 3 independent occurrences: product-item-22, 153, 164): the
  phrase "Strategy item #N" (or "Strategy Item #N") can get burned
  directly into a cover/preview PNG's visible subtitle text — e.g. "2026
  Ultimate Digital Life Planner — All-in-One Notion Planner • Strategy
  Item #153" rendered as a literal line of text on the cover graphic
  itself. This happened because the building agent had "Strategy item
  #{id}: {title}" in its own task-brief context (from
  `pipeline-orchestrator.py`'s Phase-0 brief template) and echoed that
  exact phrasing into the image-generation code it wrote
  (`phase-2/generate_assets.py` or `phase-2/build_pdf.py` in each case) —
  three separate agents made the identical mistake independently, so
  treat this as a systemic risk on every product with a generated cover
  image, not a one-off typo.

  **No existing text-based validator can catch this.**
  `validate_listing_content()` and similar checks scan listing copy
  strings — they cannot see text baked into a PNG's pixels. The only way
  to catch it is to actually look at the rendered image (open it, or run
  OCR on it) — filename, byte size, and even a text-content check on the
  *surrounding* listing copy will all pass clean while the image itself
  leaks. When auditing any product with a generated (not photographed)
  cover/preview image, visually inspect it — don't assume a passing
  content-validator run means the images are clean too.

Any confirmed hit in this phase (undisclosed spec-as-product, content
mismatch, corruption, or leaked scratchpad text) gets pulled from sale
immediately (both platforms), before moving to Phase 3. See "Pulling a
listing" below for the exact mechanics and the standing authorization
boundaries. A disclosed build-spec or a leaked-tags problem does not need
pulling — fix in place (rewrite tags, no listing downtime required).

### Phase 3 — Content-validation blockers

For every product that's blocked from publishing (STATUS.json shows a
cached "Content validation failed" error, or it's simply never made it
live despite being marked ready), run `fix-listing-content-violations`.
**Do not trust the cached error text — it goes stale the moment the file
changes and nobody re-validates.** Several products on 2026-09-21 had a
cached error describing a completely different violation than what the
current file actually contained; one had zero real violations at all.

### Phase 4 — Quality gate

Apply `product-quality-verify`'s discipline to any product not already
covered by Phase 2's truth-in-listing sweep: does the deliverable actually
match its category's competitive bar (real preview images, genuine
distinct assets, accurate counts)? This phase is lower urgency than 2/3 —
it affects conversion rate, not customer-facing risk — so it's fine to
batch this across a wider set of products less frequently than the other
phases.

### Phase 5 — Pricing and SEO sanity check

**Pricing:** compare current price against real competitor listings (web
search for actual live comps in the same category — don't estimate from
memory). Flag anything more than roughly 2x off a comparable product's
price in either direction as worth a second look, not an automatic change
— a premium price can be justified by genuinely more content, and this
needs a human or careful agent judgment call, not a mechanical rule.

**Volume-pricing strategy note (added 2026-09-22):** Charlie has explicitly
chosen, for this catalog, to favor high-volume/low-price over
low-volume/high-price (e.g. $2.99-4.99 for single-item products and simple
bundles, rather than $25-90). This is a deliberate bet that fast sales
velocity and review accumulation matter more than per-unit margin for a
brand-new shop with zero sales history — don't "correct" a low price back
upward without checking whether this strategy is still in effect; ask
before assuming margin-per-unit is the goal here.

**Etsy SEO check:** pull each listing's title and all 13 tags. A title like
"Digital Product: All Fonts Pack" or a tag set dominated by pipeline
vocabulary (see Phase 2's leaked-tags note) is a strong signal the listing
was never optimized for real Etsy search behavior. Etsy buyers search
specific long-tail phrases (3+ words describing exactly what they want);
titles and tags should reflect that, not generic category labels. Verify
every tag is ≤20 characters and there are no duplicate tags before writing
— Etsy rejects the whole batch on either violation, per `etsy-api`.

### Phase 6 — Inventory reconciliation

Update the `published_listings` table (in whatever repo currently owns it
— check `state-reconciliation`-style before assuming a schema exists,
since this project has had this table built in the wrong repo once
already) to reflect the CURRENT, POST-FIX state of both platforms. Match
each live listing back to its pipeline `product-item-N` identifier by
searching the actual listing-copy files for a title match — **do not**
match against STATUS.json's `product_name` field alone, since it is
frequently a generic placeholder like `"Strategy Item #142"` rather than
the real product name, and matching against it alone produces a false
high "orphan rate."

**A local product directory being "missing" is not automatically an
error** (found 2026-09-22): a product-item-N folder can be a documented,
intentionally-abandoned duplicate of a different strategy item (check for
a `DUPLICATE-NOTE.md` or similar file inside it before reporting it as
orphaned/erroring — the canonical build may simply live under a different
product-item-N folder).

## Pulling a listing — mechanics and authorization boundary

**Etsy**: `PATCH /shops/{shop_id}/listings/{listing_id}` with
`{"state": "inactive"}`. Always re-fetch afterward and confirm `state` in
the response — don't trust a 200 status code alone.

**Gumroad**: attempt `PUT /v2/products/{id}` with `published=false` FIRST.
Then **always re-fetch** — Gumroad's API has returned `success: true` on
this exact call while leaving the product `published: true`, repeatedly,
confirmed on 2026-09-21. If the re-fetch shows the unpublish did not apply:

- Check for any completed sales on the product (`GET /v2/sales`, filter or
  scan for the product). If sales exist, STOP — this needs a human decision
  about customer outreach, not an automated pull.
- If confirmed zero sales anywhere on the account AND unpublish has
  genuinely failed, `DELETE /v2/products/{id}` is an acceptable fallback
  **only when the person you're working for has explicitly authorized
  deletion for this class of situation** (Charlie gave this exact standing
  authorization repeatedly on 2026-09-21 for confirmed-problem products
  with zero sales exposure — but a new session should not assume that
  authorization carries forward silently; confirm it applies to the current
  situation, especially if sales are not confirmed zero). Never default to
  DELETE as a matter of convenience when unpublish merely seems slow — only
  when it has been re-fetch-confirmed to have failed.
- Gumroad's delete is soft — a deleted product's full record stays
  retrievable via `GET /v2/products/{id}` and is recoverable through Gumroad
  support. This makes the downside of an authorized delete low, but it does
  not make deletion casual or a first resort.

## Dispatching this work — verification always outlives the dispatch

This whole cycle is designed to run through whichever agent the fleet
routes it to (a delegated subagent, the `agy-bridge` delegate tool, or
fleet workers per the routing rules), with the orchestrating session doing
verification, not first-pass work. Concretely:

- Batch related fixes into one delegated task (e.g. "run
  `fix-listing-content-violations` against these 10 products") rather than
  one dispatch per product — this cuts overhead and lets the agent work
  through a checklist systematically.
- **Every claim a dispatched agent returns is a hypothesis, not a fact,
  until you re-check it against the live platform yourself** — this
  applies even to well-evidenced, confidently-written reports with
  specific before/after tables and re-fetch quotes. On 2026-09-21, two
  separate agent reports falsely claimed the exact same listing was
  "already deactivated / 404" when it was demonstrably still active —
  caught only by an independent direct fetch, not by the quality of the
  report's prose. On 2026-09-22, a full-catalog audit report was
  independently spot-checked and one specific claim ("no local directory
  exists — orphaned") was found false on direct inspection — the directory
  existed and was a documented, already-resolved duplicate. The rest of
  that same report held up under spot-checking, which is the point: verify
  specific checkable claims rather than accepting or rejecting a whole
  report on vibes.
- When verifying a batch of N claims (e.g. N corrected titles), write one
  script that checks all N against the live API in one pass rather than
  checking them one at a time by hand — faster, and harder to accidentally
  skip one.

## Closing a cycle

At the end of a pass, do ONE more completely fresh full-catalog sweep of
both platforms (Phase 1 again) before declaring the catalog clean. On
2026-09-21, a genuinely fresh re-sweep found new, previously-undiscovered
duplicates and false-advertising listings **four separate times in a row**
— each after the prior sweep had already been declared complete. Only stop
when a fresh sweep finds nothing new.

## Automated Post-Publish Hook (Event-Driven Pipeline Gate)

As of 2026-09-21, this audit cycle is wired directly into `listing-bot`'s
event-driven publishing pipeline rather than relying solely on periodic manual
or scheduled runs:

- **Trigger**: In `/Volumes/data/projects/listing-bot/helmsman/watch_approvals.py`,
  immediately after any platform publish succeeds in `publish_main()`,
  `run_post_publish_audit(product_num, results, task_num)` is invoked.
- **Implementation**: `/Volumes/data/projects/listing-bot/src/workers/post_publish_audit.py`
  runs synchronously inline (<2s execution) scoped **strictly to the newly-published product**
  (avoiding wasteful full-catalog resweeps on every publish).
- **Checks Enforced**:
  1. **Duplicate Detection**: Queries live active Etsy listings and paginated Gumroad products
     to ensure no duplicate title exists on the same platform (excluding its own ID).
  2. **Truth-in-Listing Deliverable Sweep**: Inspects `customer-package.zip` directly —
     flags any `*BUILD-SPECIFICATION*.md` sold as a finished product, checks zip validity/non-empty
     files, and checks category consistency (e.g. font files not sold as a Notion planner).
  3. **Prompt/Generation Artifacts**: Scans live title and description text for leaked scratchpad
     patterns (`we need to produce`, `let's count manually`, `AGY`, `phase-X`, `execution-plan`).
  4. **Content Validation**: Executes `validate_listing_content()` from `validators.py`.
- **Auto-Deactivation on Failure**:
  If any check fails, the product is **automatically deactivated on the spot**:
  - **Etsy**: `PATCH /shops/{shop_id}/listings/{listing_id}` with `{"state": "inactive"}` + verified response.
  - **Gumroad**: `PUT /v2/products/{id}` with `{"published": false}` + verified re-fetch. If the PUT
    silent no-op is detected AND confirmed 0 sales exist, escalates to soft `DELETE /v2/products/{id}`.
  - **Remediation & Escalation**: Updates product `STATUS.json` (`published: false`, audit failure
    details), blocks `mark_shipped()` on the source task, and automatically files a P5 task in Helmsman
    (`owner: CLAUDE`) with the failure evidence and platform receipts.
- **Manual/Periodic Invocations**:
  The full multi-product cycle documented in Phases 1–6 remains authoritative for broad batch sweeps,
  catalog cleanup, pricing sanity checks, and multi-product inventory reconciliation.

## What this cycle does not cover

- Building actual preview/mockup images for products that lack them — that
  is real, category-specific production work (PDF page renders, font
  specimen sheets, Notion screenshots, audio cover art), not a fixed
  checklist step. It benefits from the `visual-qa` skill's tooling
  (`pdftoppm`/PIL, never PyMuPDF — AGPL licensing) and its render-validation
  functions, but needs its own task framing per product category.
  **Uploading** the finished images IS covered by the platform skills once
  they're rendered: Etsy via the multipart image-upload pattern in
  `etsy-api`, Gumroad via the `/direct_uploads` → `/covers` → `/thumbnail`
  flow in `gumroad-api` (proven working 2026-09-21 — the earlier belief
  that Gumroad had no image-upload API was itself wrong, caused by testing
  the wrong endpoint; don't re-conclude "not possible" without checking
  that skill first).
- Driving actual traffic to a clean, well-priced, well-tagged catalog —
  a catalog can pass every check in this cycle and still get zero views if
  nothing points buyers at it. That's a distinct problem (see any
  traffic-generation skill for Etsy Ads / Pinterest / social) — this cycle
  only ensures the catalog is sound and discoverable, not that anyone is
  looking at it yet.
- Root-causing *why* a defect happened in the generation pipeline itself
  (e.g. why a font bundle and a Notion planner's files got cross-contaminated,
  or why ad-campaign vocabulary ends up in the tags field). This audit
  catches and stops the bleeding on individual products; fixing the
  generator so it stops happening is separate, deeper engineering work —
  but if the same leaked-artifact pattern shows up more than once, flag it
  as a pipeline bug worth root-causing, not just a per-product fix.
