---
name: "digital-product-playbook"
description: "The end-to-end standard for choosing, building, and publishing a digital product (planner, printable, Notion/Canva template, coloring/puzzle book, font or asset bundle) on any storefront -- Etsy first. Use this before starting Phase 0 research on a new product, before writing or approving any listing copy, before generating product images, and before publishing or relisting. Covers what to build (demand + autocomplete + deliverability vs. competition), competitor research (quality, formats, reviews), graphics (Gemini / fal.ai), SEO, the no-AI-slop and fact-check rules, and the pre-publish gate. Platform-specific mechanics live in etsy-api, etsy-catalog-triage, digital-product-quality-bar, and etsy-gumroad-reprice-seo -- this skill decides WHAT and WHETHER; those decide HOW on a given platform."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["digital-product-quality-bar", "etsy-catalog-triage", "etsy-api", "etsy-gumroad-reprice-seo", "product-quality-verify", "charlie-inbox-filing", "talos-brief-authoring"]
---

# Digital Product Playbook

Charlie's standard for every digital product, on every storefront. Etsy is
the first platform; the rules are platform-agnostic.

**Why:** on 2026-09-28 the shop had 35 listings with 3 total views; Charlie
deleted 24 for quality. Most failures traced to process, not effort: products
chosen without demand data, filler copy from a generator, one near-duplicate
preview image, and a price claim nobody checked. Every step below closes one
of those gaps.

## Directory phases vs. playbook steps -- these are two different numbering schemes

**Added 2026-10-01** after confusion over why customer-facing files live in
`phase-3/`, not the highest-numbered directory. Every product directory under
`talos-tools/digital-products/product-item-<N>/` uses a fixed 5-stage
pipeline that does NOT map one-to-one onto this skill's numbered steps above:

| Directory | Contains |
|---|---|
| `phase-0/` | Research: demand/saturation data, competitor research, market analysis |
| `phase-1/` | Design/build: render scripts, design notes, source HTML/CSS |
| `phase-2/` | Generation: raw exports from the build tool (Canva PDFs, rendered images) |
| `phase-3/` | **Packaging: the actual customer-facing deliverable** (`customer-package/` or `customer-package.zip`), preview/marketing images (`preview-mockups/`), and the Etsy listing copy |
| `phase-4/` | QA/submission: the quality-bar audit report and submission checklist, run AFTER phase-3 is packaged |

So `phase-3` is not "the third of five content stages" — it is the specific,
fixed name for "packaged and ready to sell," and `phase-4` is a review gate
on top of it, not a later content stage. A fix to the customer-facing
product always lands in `phase-3/customer-package/`, never a higher-numbered
phase. When editing a live product, locate the real shipped file via this
table rather than assuming the highest phase number holds the newest
customer-facing content.

## 1. Choose what to build -- demand first

Build nothing without both signals:

- **Popular + autocomplete searches.** Real buyer phrasing, not category
  guesses. Pull Etsy's live search suggestions for the seed term. A
  third-party keyword tool (KeywordTool, eRank) is a proxy; label it as one.
- **Saturation.** `findAllListingsActive` count for the exact phrase, plus
  favorites on the top 5 results (pattern in `etsy-catalog-triage`).

Then **prioritize what we can deliver well against what has lower
competition.** A 900-listing niche where the top 5 have ~0 favorites beats a
25,000-listing niche led by a 1,000-favorite competitor, even if the big niche
feels more central. If we can't beat the top result's deliverable, skip it.

## 2. Research competitors -- quality, formats, reviews

For the top 3-5 results in the chosen phrase, record:

- **Quality:** open their preview images (don't just count them). What does
  the buyer actually receive?
- **Formats:** ready-to-use vs. build-it-yourself, file types, page counts,
  sizes (US Letter + A4), app compatibility (GoodNotes, Notability, Canva).
- **Reviews:** shop review count and what buyers praise or complain about
  (`GET /shops/{shop_id}/reviews`). Complaints are the spec for our version.

Our deliverable must match or beat the best competitor on every axis we
charge for. Record the comparison in `phase-0/competitor-research/`.

## 3. Find the differentiation gap -- what do ALL competitors miss?

**Added 2026-10-01, confirmed on the Tent Camping Checklist (product-item-225):**
step 2's competitor pull answers "do we match the market." This step asks a
different question: "what does the ENTIRE top-5 field fail to offer that a
buyer in this niche would genuinely want?" Matching competitors ships a
product that's merely competitive; closing a gap none of them cover ships
one that's structurally better, not just better-executed.

Look across all 3-5 comps pulled in step 2 for a shared absence, not just
individual weaknesses:
- Do none of them include genuinely useful **reference/educational content**
  adjacent to the product's core function? (The camping checklist case: 5
  real competitors, all pure packing-list PDFs, zero instructional content —
  adding a few reference pages on knots, fire-starting, and water safety
  turned a commodity checklist into the only guide-plus-checklist in the
  niche, for near-zero marginal cost since the base pipeline already existed.)
- Do none of them offer real editability (see `digital-product-quality-bar`
  section 1) when the category's buyers clearly want to customize?
- Do none of them segment by use-case/audience when the audience is
  obviously not homogeneous (trip type, skill level, dietary need, etc.)?

If a genuine, low-cost-to-close gap exists across the whole field, closing it
is higher-leverage than polishing copy or images on a me-too product. Record
the gap and the fix in `phase-0/competitor-research/` alongside the
comparison table, and reflect it in the listing copy's differentiation
language (not just a feature bullet — a buyer should understand immediately
why this listing and not the other 20 nearly-identical ones). **Bonus
content must still clear the same visual bar as the rest of the product**
(see `pdf-form-generation`'s "Illustrated themes" section) — a wall of plain
text bolted onto a well-designed product looks like an afterthought and
undercuts the differentiation it's supposed to deliver.

## 4. Build -- graphics

- Functional previews (the real pages in a device or desk context) are
  rendered from the actual product files.
- Illustrative or hero art: **Gemini** or **fal.ai**. fal.ai runs on about
  $20/month of credits -- spend it on hero and lifestyle images, not on
  re-rendering pages that already exist.
- **At least 5 genuinely distinct images**, ideally 8-10: cover/hero, inside
  pages, what's included, device/compatibility, who it's for. Duplicates don't
  count. Check before uploading:
  `md5 -q phase-3/preview-mockups/*.png | sort | uniq -d` must print nothing.
  (2026-09-28: product 181's "4 images" were 2 files saved twice each.)

## 5. Listing copy -- SEO researched, no AI slop, facts checked

- **Title** (140 characters max): buyer phrase first, then audience/format.
- **13 tags** (20 characters each max, no duplicates, no single filler words):
  pulled from real competitor tags and autocomplete, not invented.
- **Description structure:** 1-2 plain sentences on what it is, then
  WHAT YOU GET / WHO IT'S FOR / FILE DETAILS / HOW IT WORKS as bullet lists.
- **No AI slop.** None of: introducing, meticulously, go-to, unlock, elevate,
  seamless, game-changer, journey, effortlessly, must-have, "perfect for anyone
  looking for", "take your X to the next level", keyword lines. listing-bot's
  generator enforces this (`seo/descriptions.py` SLOP_PHRASES); hand-written
  copy must meet the same bar.
- **Every number is recomputed from the deliverable** -- page counts, field
  counts, totals, sizes. Never copy a number from a prior draft, a STATUS.json
  note, or LLM output. (2026-09-28: product 181 claimed a $1,378 total; its own
  grid totals $1,750.06.)

## 6. Pre-publish gate

Run `digital-product-quality-bar` plus these checks. Any failure blocks publish:

- [ ] Demand + saturation evidence is recorded (step 1)
- [ ] Competitor comparison is recorded, and we meet or beat it (step 2)
- [ ] Differentiation gap considered and, if a genuine one exists, closed or
      explicitly deferred with a reason (step 3)
- [ ] 5+ distinct images (md5 check above)
- [ ] Title/tags valid; tags sourced from real buyer terms
- [ ] Description is sectioned, has no banned phrases, and every number is verified
- [ ] No internal identifiers (`Product #item-N`, working-file headings) in
      any customer-facing file, the local listing copy included

## 7. Publish -- throttled, verified, and surfaced correctly

- **Throttle:** 5-10 new listings per week at most, never a same-day batch.
  Etsy's 2026 enforcement flags rapid, similar-styled AI-pipeline uploads.
- **Verify after every write** with a fresh GET. A 200 response is not proof.
- **A content fix to a live product isn't done until the buyer download is replaced.**
  Images and description are only half of it. Attach the rebuilt file with
  `POST .../listings/{id}/files` (it's additive), then delete the old
  `listing_file_id`. (2026-09-29: product 181's download still carried the
  false total after the listing and images were fixed.)
- **Re-pull live listing state before every dispatch or retry** in a long
  session. Charlie deletes listings in other sessions, and stale IDs look
  like pipeline bugs.
- **Don't file tasks for review.** A finished, QA-passed product surfaces in
  Charlie's Inbox on its own (`charlie-inbox-filing` Kind 2). A question with
  options is a strategy item (Kind 3), not a task.

## 8. After launch

Wait 2-3 weeks for organic indexing before judging traffic. Then triage with
`etsy-catalog-triage`. No paid ads until products are proven good (Charlie's
call, 2026-09-28).

## 9. Retrofitting existing catalog products

**Added 2026-10-01.** Steps 1-6 describe building a new product. The same
gate applies to anything already shipped — a product built before step 3
existed, or before `pdf-form-generation`'s illustrated-theme fixes landed,
can still be retrofitted. This is cheap, low-risk work specifically **while
the catalog has no real sales/traffic yet** (zero live customers means zero
risk of confusing existing buyers with a changed deliverable) — do this
audit now rather than after launch pressure makes it harder to prioritize.

For each existing product:
1. Re-pull step 2's competitor comparison fresh (comps and their
   favorites/reviews change over time) and re-run step 3's differentiation
   check against it — a product built before this step existed was never
   checked against "what does the whole field miss."
2. Check visual tier against `pdf-form-generation`'s "Illustrated themes"
   section even if the product predates that section — a flat, color-header-
   only PDF competing against illustrated comps has the same structural gap
   regardless of when it shipped.
3. Prioritize by effort-to-impact, not by product age: a near-zero-cost gap
   close (e.g. 2-3 bonus reference pages reusing an already-built pipeline)
   beats a full visual rebuild of a product that's already visually
   competitive. Use `etsy-catalog-triage`'s data-driven approach to pick
   which products get today's effort if there are many candidates.
4. Still respect the stagger-launch rule for re-publishing updates — don't
   batch-update the whole catalog in one session even if no traffic risk
   exists yet; verify each retrofit fully (per this skill's step 6 gate)
   before moving to the next.
