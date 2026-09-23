---
name: "lifestyle-niche-coloring"
description: "Blueprint for lifestyle-themed coloring-page products (travel, wine/vineyard, food, beer, bourbon) for Etsy/Gumroad. Documents a real market split: illustrated coloring books are a proven bestseller mechanism for travel/lifestyle themes (reuses the coloring-book-generation pipeline directly), while wine/bourbon/beer 'tasting tracker' products are a real but SEPARATE, commoditized, form-based niche needing a different, not-yet-built PDF-form pipeline. Use this whenever asked to build food/travel/beverage-themed products, or to decide whether a lifestyle idea fits the illustration pipeline or needs a new one."
category: "creative"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["coloring-book-generation", "technical-diagram-coloring", "digital-product-quality-bar", "talos-product-launch-audit"]
---

# Lifestyle Niche Coloring — Travel, Wine, and the Tasting-Tracker Trap

**Fleet-wide skill.** A thin, theme-specific layer on top of `coloring-book-generation` — read that skill first for the actual generation mechanics. This skill exists to document a mechanism decision: "food, travel, beer, bourbon, wine" sounds like one category, but two independent research passes found it's actually two separate markets with two separate product mechanisms, only one of which this shop can build today.

## Why this exists

On 2026-09-22, Charlie's brief was "Food, travel, beer, bourbon and wine. Lots of ideas." A first research pass under-evidenced its recommendation (leaned on "competitors show..." without citing real listings) and got sent back. A second, sharper pass with real Etsy searches found a clear split:

**Wine/bourbon/beer "tasting tracker" products are real but a different, commoditized niche.** Confirmed real listings: "Wine Tasting Notes Journal PDF Printable" ($2.50–4.00, 2–9 pages), "Printable Beer Tasting Journal" (10 pages), "Bourbon Tasting Scorecard" (flavor wheel + trivia). All of these are **form-based PDF worksheets** — structured fields, rating scales, checkboxes — not illustrated line art. Pricing floors around $2.50–5 because the category is crowded and low-effort to produce with a template tool. Building this well would need a genuinely different pipeline (Python + a PDF form-layout library like `reportlab` or `weasyprint`, precise field placement) that has never been proven anywhere in this shop — the closest existing skill, `notion-template-api-build`, builds Notion workspaces via API, not printable PDF forms, and doesn't transfer.

**Illustrated travel/lifestyle coloring books are a proven bestseller mechanism, and it's the shop's already-proven pipeline.** Confirmed real listing: "Travel Coloring Pages," 60 pages, $5.94, carrying Etsy's bestseller tag. This is the exact same Canva `design_type: "logo"` line-art pipeline already shipped twice in this shop (`coloring-book-generation`, `technical-diagram-coloring`).

**The decision this skill documents:** given real bestseller evidence exists for illustrated lifestyle coloring pages, and the tasting-tracker niche would require standing up a brand-new, unproven PDF-form pipeline for a $2.50-floor commodity market — the right first validation bet is illustrated coloring pages themed around travel and wine regions (vineyards, wine-country villages, tasting rooms, travel landmarks), not a tasting tracker. This is a build-cost/evidence tradeoff, not a claim that tasting trackers can never work — if that niche is worth pursuing later, it needs its own pipeline and its own research pass, not a forced fit into the coloring-page mechanism.

## What NOT to build under this skill

Do not attempt a wine/bourbon/beer tasting-notes tracker as a coloring-page product — it is not one. A tasting tracker needs actual fillable structure (lines to write on, rating boxes, flavor wheels with labeled sectors) that Canva's `generate-design` illustration pipeline cannot produce; forcing it would ship a page that looks like a form but has no usable field structure, which is worse than not building it. If a tasting-tracker product is wanted, that's new-pipeline work: flag it as a distinct task requiring PDF form-layout tooling, not an extension of this skill.

**This niche is worth a dedicated follow-up, not a dismissal.** A deeper pass (with real listing URLs, not just search snippets) found the wine-tasting-scorecard niche has substantially deeper proven demand than a first look suggests — specific real listings (e.g. Etsy listing 648605371, "Wine Tasting Score Card (6 Wines)") carry **4,983 reviews at 5.0 stars**, and a sibling listing carries 4,982 — this is sustained, high-volume repeat demand, not a thin niche. The dominant format is a **party-use blind-tasting scorecard** (single page or small bundle, reprinted per wine-night event, which drives repeat purchases) rather than a long-term personal journal. A 25-page "4-in-1 kit" bundle (scorecards + placemats + wine tags + host guide) with a Star Seller badge was also confirmed. Recommended entry point for whoever picks this up: a single 1-page, 6-wine blind-tasting scorecard at ~$4.99 first (matching the proven high-review format exactly, not a redesign), with a bundle/kit variant (~$8.99, 8-12 pages: scorecard + host guide + vocabulary reference + reveal page) only after the single card validates. This needs the PDF-form pipeline called out above — do not force it through Canva's illustration path.

## The validated mechanism for this theme

Identical to `coloring-book-generation` and `technical-diagram-coloring`: `generate-design` with `design_type: "logo"` (never `"document"` — confirmed to produce wrong business-template content), view via `read-design` with `filter.fields:["thumbnails"]`, dual export (`{"type":"pdf","size":"letter"}` + `{"type":"png","width":2000}`), download via Python `requests.get()` (never bash `curl` — mangles signed URL special characters).

Theme-specific prompt guidance: ask for genuine scenes with real detail density — vineyard landscapes with rolling hills and grapevine rows, rustic wine-tasting-room interiors, European wine-country village streets, wine bottle/glass still-life with grape clusters, travel-postcard-style landmark illustrations (style generically — avoid rendering a specific trademarked logo or exact real building likeness), wine-cellar/barrel-room scenes. Same detail-density quality gate as the base skill applies: sparse/thin line art is a real failure mode, not an acceptable minimalist choice, for this product type.

## Validation product pattern

Same taste-test discipline as the prior two categories: 5-6 pages covering distinct sub-themes, priced $4.99-5.99, explicitly scoped as a taste-test in STATUS.json rather than committing to a full 40-60 page bundle (the market-leading comp, "Travel Coloring Pages," is 60 pages at $5.94 — scale toward that only if the taste-test proves the theme).

## Everything else

Generation mechanics, the `document`-vs-`logo` gotcha, the curl-vs-`requests.get()` download gotcha, detail-density quality gate, and the full publishing checklist are identical to `coloring-book-generation` — read that skill directly. This file's only job is the theme-specific market call: illustrated coloring pages for travel/wine, not a tasting-tracker form product.

---

**This skill was authored 2026-09-22, after two research passes converged on a real bestseller (60-page "Travel Coloring Pages," $5.94) supporting the illustration mechanism, while confirming wine/bourbon/beer tasting trackers are a real but separate, unbuilt, form-based niche. See `coloring-book-generation` for the shared pipeline this reuses.**
