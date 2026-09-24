---
name: "digital-product-quality-bar"
description: "Concrete, checkable quality gate for Talos digital products (Notion templates, Canva packs, planners, coloring books, font/icon bundles) before they publish to Etsy/Gumroad — preview image count and content, listing copy structure, and whether the deliverable format itself (build-spec vs. ready-to-use) meets the real market bar. Use this whenever a product is approve-ready and about to publish, when a listing has real search traffic but converts poorly, or when comparing a listing against a successful competitor to find the actual gap."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["talos-product-launch-audit", "product-quality-verify", "etsy-gumroad-reprice-seo", "etsy-api"]
---

# Digital Product Quality Bar

**Fleet-wide skill.** Every check here is mechanically verifiable via the
Etsy/Gumroad APIs or by reading the listing copy file — no subjective
judgment calls needed to run the gate, only to decide whether a borderline
case is worth the rework.

## Why this exists

On 2026-09-22, Charlie pointed at a real competitor listing
("Second Brain Notion Template: PARA") and said the quiet part: our
catalog isn't just under-discovered or mispriced, it's **structurally
lower quality** than what's actually winning in these categories. Direct
comparison confirmed it immediately:

| | Our product-158 | Competitor (same search space) |
|---|---|---|
| Preview images | **1** | **10** |
| Deliverable | Build-it-yourself Notion spec (45-60 min) | Ready-to-duplicate Notion workspace |
| Views/favorites | 0 / 0 | 6,383 / 261 |
| Price | $2.99 (after volume repricing) | ~$40 USD |

The gap isn't a marketing problem to paper over with better SEO — it's a
build-and-QA standards problem. This skill turns that research into an
enforceable gate so it doesn't stay a one-time realization.

## The gate — run before any product goes live

### 0. Pull real competitor comps first — every category, not just Notion

The Notion comparison in "Why this exists" wasn't a one-time realization —
it's the method. Before judging a product against this skill's checklist,
pull 3-5 real, currently-live listings in the exact same search space and
compare structured attributes directly. Skipping this step and going
straight to the checklist below risks passing a product that clears every
box here while still being structurally uncompetitive, because the boxes
were written from a fixed snapshot of the market, not the category this
specific product is entering.

**How to pull comps (mechanical, not subjective):**

1. Search the primary keyword phrase on Etsy (or Gumroad, if that's the
   product's real competitive set) the way a buyer would — not a title
   fragment, the actual phrase from the listing's Title field.
2. Take the top 3-5 non-ad results with real review/favorite counts (skip
   anything with 0 reviews and 0 favorites — that's not a proven comp,
   it's another struggling listing like the one you're checking).
3. **Fetch and actually look at 2-3 of the comp's real preview images**
   (`GET /v3/application/listings/{id}/images` on Etsy, download the URLs,
   Read them as images) — do not stop at recording the image count as a
   number. Confirmed 2026-09-24: a full batch of 40 products was built with
   correct market-evidence numbers (reviews, favorites, pricing) but zero
   competitor images actually viewed, and shipped visually bland (plain
   black-on-white, no color, no typography) compared to what real winning
   listings look like. The numeric comp table alone does not catch a visual
   quality gap — only looking at the images does. Record, per comp: preview
   image count, price, deliverable format (ready-to-use vs. build-spec vs.
   bundle), review count, and one sentence on what the listing photos/copy
   emphasize that ours doesn't (palette, typography, layout density,
   mockup/prop styling, badge callouts).
4. Compare against the product under review using that table, not memory
   or a general sense of "the market." A gap of 1 image vs. 10, or
   $40 vs. $2.99, is not a pricing problem to fix with SEO — it's the
   signal that something in sections 1-4 below needs to change first.

**This step has no per-category checklist yet for anything outside
Notion/Canva** (coloring books, gamebooks, font bundles, etc. only have
the thin category-specific bullets in section 4) — if you run this
comparison for one of those categories and find a structural gap the way
the original Notion comparison did, add a category table here the same
way, rather than treating the finding as a one-off for that single
product. The gap in this skill right now is real: it has a philosophy
("compare against comps") but only one worked example (Notion). Building
out concrete comp tables per category as they get audited is exactly how
this section should grow.

### 1. Deliverable format (the single biggest lever)

**Ready-to-use is the market baseline for Notion and Canva products as of
2026 — not a nice-to-have.** A build-specification/instruction-sheet
product is a fundamentally different, lower-value category, even when
honestly disclosed (disclosure avoids false-advertising risk, it does not
close the quality gap).

- [ ] **Notion**: deliverable is a link to a page with "Allow duplicate as
      template" turned ON — buyer clicks, it copies into their workspace,
      done. Not a markdown build-spec, not raw export files requiring
      manual reconstruction.
- [ ] **Canva**: deliverable is a Canva **template link** (creates a clean
      editable copy in the buyer's account) — not a raw file share, not an
      instruction sheet to rebuild in a personal account.
- [ ] If a product genuinely cannot ship ready-to-use yet (a real
      capability gap, not a shortcut), it must be **repositioned as a
      different, lower-priced product type** ("DIY build guide" /
      "specification"), not sold at template-tier pricing in the same
      category as ready-to-use competitors. See "What to do about existing
      build-spec products" below.

### 2. Preview images (mechanically checkable via API)

```python
# Etsy: GET /v3/application/listings/{listing_id}/images
# count the results array length
```

- [ ] **Minimum 5 images, target 7-10** (Etsy allows up to 10 + 1 video).
      A listing at 1-2 images is competing at a structural disadvantage
      regardless of copy or SEO quality — this was our exact situation.
- [ ] Image 1 (hero) shows the **actual product** — a real, styled
      screenshot/render in context — never an abstract cover graphic or
      text-only card.
- [ ] At least 1 image shows the product **filled in with example data**,
      not an empty template — buyers need to visualize using it, not
      building it.
- [ ] At least 1 image states what's included (file format, count, access
      method) visually.
- [ ] All images share consistent fonts/palette/visual weight — mixed
      styles read as unprofessional even if each image is individually
      fine.
- [ ] 2000×2000px minimum resolution, 3000×3000px preferred; no
      watermarks obscuring the actual product.
- [ ] A short looping video (screen recording of the product in use)
      measurably outperforms listings without one — add when feasible.

### 3. Listing copy structure

- [ ] **Opens with a benefit/transformation statement**, not a format
      description. "Stop losing track of X — this gives you Y in Z
      minutes," not "This is a [product type] for [category]."
- [ ] "What's included" as **bullets**, not paragraphs.
- [ ] "Who this is for" section present (helps the right buyer self-select
      in, reduces mismatched-expectation refunds).
- [ ] Access/delivery steps spelled out, 3 steps max.
- [ ] File specs stated explicitly: format, count, DPI (if print),
      software required.
- [ ] "Digital download — nothing physical ships" stated explicitly
      (reduces confusion-driven support/refunds).
- [ ] FAQ section answering 3+ real purchase objections (compatibility,
      access issues, sharing/licensing).
- [ ] No unbacked superlatives ("ultimate," "best," "perfect") — replace
      with the specific, checkable claim they're standing in for.

### 4. Category-specific checks

**Notion**: contains example/demo data (not blank pages) · setup time
under 5 minutes from duplication to first use · cover image set (not
Notion's default gray) · consistent icon/color system throughout.

**Canva**: every font used is available on the free Canva plan (or
alternatives are listed) · all elements are actually editable, no
unexplained locked layers · a brief "how to edit" note lives inside the
design itself, not just in the listing copy.

**Planners/printables**: 300 DPI, print-ready · explicitly states
printable vs. digital-only (iPad/GoodNotes) vs. both.

**Coloring books**: at least one preview image shows an actual finished
sample page — buyers won't buy blind on art quality.

First real comp table for this category (pulled 2026-09-23, "engineering
coloring page adult" search, Etsy Open API, top proven results filtered
to nonzero reviews/favorites):

| | Our product-176 | Comp: "Engineering Coloring Pages for Kids & Adults" | Comp: "Engineering Coloring Book for Adults" |
|---|---|---|---|
| Preview images | 4 | 7 | 4 |
| Price | $4.99 | $55.00 | $1.99 |
| Favorites | 0 (new) | 4 | 4 |
| Pages | 6 | unconfirmed | unconfirmed |

Takeaway: our image count (4) sits between the two comps, not a
structural gap the way the Notion case was — the $55 outlier is priced
for a bundle/poster-set positioning, not a like-for-like comp on page
count. The real lever for this category based on this pull is favorites
count at zero (expected for a same-day listing, re-check after it's had
time to accumulate) rather than a deliverable-format or image-count gap.
This is the category's first real data point, not a final verdict — run
this search again and update the table once there's real sales/view data
on our own listing to compare against.

**Font bundles**: preview shows a full alphabet specimen (upper, lower,
numerals, punctuation) plus 2-3 realistic use-case mockups · license terms
(personal vs. commercial vs. extended) stated plainly.

**Icon/clipart packs**: preview shows individual icons at usable size,
color variants if any, and one in-context use example.

### 5. Pricing sanity check

- [ ] A build-spec/instruction product is not priced at ready-to-use
      template rates. If the deliverable format doesn't meet section 1's
      bar, its price tier should reflect that (this is a separate axis
      from the general volume-pricing strategy in `etsy-gumroad-reprice-seo`
      — a $2.99 build-spec and a $2.99 ready-to-use template are not
      equivalent products even at the same price).
- [ ] Search the primary keyword on the live platform and compare against
      real current comps, not memory — confirm positioning is sane given
      what similar ready-to-use products are actually priced at.

### 6. Claimed "N variations/templates" must be genuinely distinct — check, don't assume

**Confirmed 3 times in one session (2026-09-24): a "build N variations of
template X" instruction gets satisfied by generating 1-2 genuinely
different designs and then recoloring/re-theming those into the remaining
count** — a batch of journal products first (same 5 prompts repeated
30-100 times), then two Instagram-template products (12 "variations" per
master where only ~2 are content-distinct, the rest are pixel-identical
color swaps of one of those 2). Each time this passed the build agent's
own field-count/file-count check (the files genuinely exist, pypdf
genuinely reports real fields) — file existence is not the same as content
distinctness, and neither is a "field count matches" check.

**The check this section requires:** for ANY deliverable claiming N
variations of a template, actually render and visually compare at least 3
spread-out variations (e.g. #1, the middle, and the last) — not just the
first one. If two variations are pixel-identical except for a color swap,
that is NOT a second variation for the purpose of an "N templates" or "N
posts" marketing claim — a buyer reading "141+ unique posts" reasonably
expects 141+ different pieces of content, not a smaller set of designs
recolored to hit a number. Either make the variations genuinely
content-distinct (different copy, different layout emphasis, different
example/data — not just palette), or state the real distinct-design count
honestly in the listing copy instead of the inflated total.

## What to do about existing build-spec products

Several already-published products (e.g. product-item-153, 158, 164) are
honestly-disclosed build-specifications, not false advertising — they
don't need pulling from sale under `talos-product-launch-audit`'s Phase 2.
But they don't clear this quality bar either. Options, roughly in order of
effort:

1. **Best**: rebuild the deliverable as genuinely ready-to-use (a real
   Notion template with sharing enabled, a real Canva template link) —
   this closes the actual gap, not just the disclosure gap.
2. **Acceptable interim**: re-tier the price down and re-title/re-tag to
   honestly signal "build guide" positioning rather than competing
   head-to-head with ready-to-use templates in the same search terms.
3. **Not acceptable**: leave a build-spec product priced and positioned as
   if it were a ready-to-use template just because the disclosure
   technically prevents a false-advertising violation. Disclosure is the
   floor, not the target.

## A second payoff of fixing Notion products: Notion's own Marketplace

Once a Notion product is rebuilt as a genuine "Duplicate as template"
page (option 1 above), it becomes eligible for a distribution channel we
don't currently use at all: **Notion's own template Marketplace**
(notion.com/templates), confirmed researched 2026-09-22.

- Submission is free. Notion's own submission requirement is literally
  "Publish templates as Notion Sites with 'Duplicate as template'
  enabled" — the exact same bar this skill already mandates, so there's
  no extra build work beyond what's already required for Etsy/Gumroad
  quality.
- Payment has two paths: Notion's native Stripe checkout (8% + $0.40/txn,
  but requires a creator approval that "may take a few months") **or**
  linking the listing's checkout to an existing external shop (our
  Gumroad) — no extra approval wait for that path, since we already have
  a working Gumroad shop.
- Templates go through a Notion team content review before listing, and
  screenshots/video (up to 60s) must accurately represent the product —
  same "real content, not placeholder" discipline as the image-quality
  section above.
- There's also a distinct "AI Skills" template category on Notion's
  marketplace (reusable Notion AI instruction packages, not related to
  our own internal skills system despite the name collision) — a
  genuinely different product type worth a separate look once the core
  Notion-template fix lands, not the same work as fixing existing
  products.

**Sequencing**: don't submit to Notion Marketplace before a product
passes this skill's deliverable-format check — a build-spec product
would likely fail Notion's own review for the same reason it fails ours.
Fix the product first; the Marketplace submission is a near-zero-cost
add-on once it's genuinely ready-to-use.

## The wrong-file-uploaded trap — confirmed 2026-09-22, a distinct failure from "no good asset exists"

A second-opinion review (a different model family, via AGY) looked at all
26 live thumbnails on this shop and called nearly every one unprofessional
— raw exports, screenshots, flat gradients. That triggered a real
overreaction risk: assuming every flagged product has a genuine content
problem and needs to be rebuilt or pulled.

**Checking the actual files first caught the AI reviewer being wrong in a
specific, important way.** product-item-145 (a pixel-art icon pack) had a
broken/placeholder gray-dot image live as its Etsy thumbnail — the review
correctly said "this doesn't look like real pixel art" and concluded the
underlying asset-generation skill must be weak. But the product's own
`phase-3/customer-package/atlases/*.png` files (dense contact-sheet
collages of the actual icons) were genuinely good, professional-looking
pixel art that never got uploaded anywhere. The bug was 100% in image
selection during publish, not in content generation.

This means a reviewer (human or AI) grading only the live storefront image
can produce a **false content-quality verdict** — it's actually grading
the publish pipeline's file-picking logic. Distinguishing the two matters
enormously: one is a five-minute image swap, the other is "don't sell this
category at all."

**Before accepting any "this product's content is bad" verdict from a
thumbnail alone:**
1. List every image file under the product's `phase-3/` tree (check
   `preview-mockups/`, `customer-package/`, and any `atlases/`,
   `contact-sheet`, or `-preview` named subfolder — these are the most
   likely locations for a curated hero image that never got uploaded).
2. Open the best 2-3 candidates and actually look at them.
3. Only conclude "real content gap" if nothing in phase-1/phase-2/phase-3
   represents the product well — not just because the currently-live
   thumbnail looks bad. On 2026-09-22, roughly half of the products a
   second-opinion review called "programmer-art" or "placeholder" turned
   out to have a real, good asset sitting unused a few folders away; the
   other half (a music-loop bundle with only 1 image ever generated, a
   character-template pack whose entire deliverable actually is stick-figure
   scaffolding, a crochet pattern set with zero garment photos anywhere)
   were confirmed genuine gaps and got pulled from sale rather than relisted
   with a better photo of the same weak content.
4. When a real, good asset is found unused, the fix is purely mechanical:
   update the publish step to select it (or manually re-upload it) —
   no regeneration, no new skill needed, just fixing what the pipeline
   already had.

## Rapid audit sequence for an existing catalog

1. Pull image count for every live listing via the Etsy images endpoint —
   this is the fastest, purely mechanical first signal (see `etsy-api`
   for the endpoint pattern). Anything under 5 is an immediate flag.
2. For each product, check `talos-tools/digital-products/product-item-N/`
   for whether the deliverable is a real template/link or a build-spec
   document — grep for `BUILD-SPECIFICATION` per `talos-product-launch-audit`'s
   Phase 2 pattern, cross-referenced against this skill's section 1.
3. Prioritize rework by traffic (views), not sales — a listing with real
   views and zero conversions is telling you something specific is wrong
   (usually images or deliverable format); a listing with zero views has
   a discovery problem this skill doesn't address (see
   `etsy-gumroad-reprice-seo` for that half of the problem).
