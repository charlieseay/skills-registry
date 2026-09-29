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

## 3. Build -- graphics

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

## 4. Listing copy -- SEO researched, no AI slop, facts checked

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

## 5. Pre-publish gate

Run `digital-product-quality-bar` plus these checks. Any failure blocks publish:

- [ ] Demand + saturation evidence is recorded (step 1)
- [ ] Competitor comparison is recorded, and we meet or beat it (step 2)
- [ ] 5+ distinct images (md5 check above)
- [ ] Title/tags valid; tags sourced from real buyer terms
- [ ] Description is sectioned, has no banned phrases, and every number is verified
- [ ] No internal identifiers (`Product #item-N`, working-file headings) in
      any customer-facing file, the local listing copy included

## 6. Publish -- throttled, verified, and surfaced correctly

- **Throttle:** 5-10 new listings per week at most, never a same-day batch.
  Etsy's 2026 enforcement flags rapid, similar-styled AI-pipeline uploads.
- **Verify after every write** with a fresh GET. A 200 response is not proof.
- **Re-pull live listing state before every dispatch or retry** in a long
  session. Charlie deletes listings in other sessions, and stale IDs look
  like pipeline bugs.
- **Don't file tasks for review.** A finished, QA-passed product surfaces in
  Charlie's Inbox on its own (`charlie-inbox-filing` Kind 2). A question with
  options is a strategy item (Kind 3), not a task.

## 7. After launch

Wait 2-3 weeks for organic indexing before judging traffic. Then triage with
`etsy-catalog-triage`. No paid ads until products are proven good (Charlie's
call, 2026-09-28).
