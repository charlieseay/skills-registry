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
