---
name: "technical-diagram-coloring"
description: "Blueprint for engineering/technical-themed coloring-page products (circuit boards, computer/PCB layouts, mechanical/gear patterns) for Etsy/Gumroad. Documents why 'technical diagram puzzles' (circuit mazes, PCB spot-the-difference, schematic word searches) have NO real market evidence, and the honest pivot to engineering-themed coloring pages instead — reusing the proven coloring-book-generation pipeline with a new theme, not a new mechanism. Use this whenever asked to build electrical/circuit/computer/engineering diagram products, or to evaluate whether a 'diagram puzzle' idea is viable."
category: "creative"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["coloring-book-generation", "digital-product-quality-bar", "talos-product-launch-audit"]
---

# Technical Diagram Coloring — Engineering-Themed Line Art

**Fleet-wide skill.** A thin, theme-specific layer on top of `coloring-book-generation` — read that skill first for the actual generation mechanics (Canva `design_type`, dual PDF/PNG export, download gotchas, quality gates). This skill exists only to document a market-research finding that changes what gets *built* under this theme, not how it's built.

## Why this exists

On 2026-09-22, Charlie's brief was "Electrical diagrams for the engineering inspired. Computer and IT related pictures and diagrams that could be puzzles." Before designing anything, real market research was run against Etsy, Gumroad, and general web search for existing "technical diagram puzzle" products.

**Finding: there is no real market for solvable technical puzzles in this theme.** No circuit-diagram mazes, no PCB spot-the-difference sets, no schematic-styled word searches were found with any competitor presence or sales signal on either platform. Standalone solvable-puzzle categories (mazes, word searches, spot-the-difference) exist as their own genres with their own pricing, but none of them are built around engineering/circuit/PCB visual themes.

**What DOES have real market evidence:** engineering/tech-themed coloring PAGES — e.g. "Circuit Boards! A Coloring Book For Electrical Engineers" and a "Technology Coloring Book — 40 Computer Science Designs" on Etsy. These are line art to color, not solvable puzzles. Digital bundle pricing in this space runs $4–7 for 40–50 pages, consistent with the general adult-coloring-book market documented in `coloring-book-generation`.

**The honest pivot this skill documents:** treat "engineering diagram puzzle" as a coloring-page theme, not a new product mechanism. Position it as "engineering-inspired aesthetic line art for tech enthusiasts and makers" — explicitly not claiming functionally accurate circuit diagrams. If a real puzzle mechanism is wanted later (an actual maze, an actual spot-the-difference), that is a distinct, unvalidated product idea and should get its own market research pass before building — don't assume this skill covers it.

## Why not a real puzzle mechanism

A genuine "find the component" or maze-through-a-circuit puzzle needs an underlying solvable structure (a real path, a real pair of images with N deliberate differences) that a text-to-image generator like Canva's `generate-design` cannot reliably produce — it can only generate a plausible-looking single image, not a verified-solvable puzzle pair or path. Building an actual solvable puzzle in this theme would need a different, non-Canva pipeline (e.g. procedural maze generation with tech-styled skinning, or a scripted diff-pair generator) — worth a distinct research pass if the market ever justifies it, but not assumed by default.

## Canva feasibility for this theme

Same `design_type: "logo"` pipeline as `coloring-book-generation`, with a theme-specific ceiling to plan around:

- **Realistic**: clean geometric circuit symbols, isometric motherboard/PCB layouts, stylized wire traces, retro-computer/terminal illustrations, gear/mechanical patterns, network/server-rack diagrams, CPU cross-sections rendered as line art.
- **Not realistic**: functionally accurate schematics with correct component values, precise PCB trace routing, or anything a real engineer would read as technically correct. Canva produces visually plausible technical-looking line art, not engineering-correct diagrams.

Prompt accordingly — ask for "engineering-inspired," "blueprint-style," or "technical aesthetic" line art, never "an accurate schematic of X."

## Validation product pattern

Same taste-test discipline as `coloring-book-generation`'s product-item-175: build a small spread (5-6 pages) covering distinct sub-themes before committing to a full 20+ page bundle. Sub-themes with real prompt variety: isometric motherboard/PCB, circuit-trace geometric pattern, retro computer/terminal, network/server rack, mechanical gear pattern, CPU chip cross-section.

Price a taste-test set like product-item-175's ($4.99–5.99), not the full-bundle tier ($5.99–7 for 20 pages) — scale to a full bundle only if the taste test proves the theme sells.

## Everything else

Generation mechanics, dual PDF+PNG export requirement, the `document`-vs-`logo` design_type gotcha, the curl-vs-`requests.get()` download gotcha, detail-density quality gate, and the full publishing checklist are identical to `coloring-book-generation` — read that skill directly rather than duplicating it here. This file's only job is the theme-specific market call: coloring pages yes, solvable puzzles not yet.

---

**This skill was authored 2026-09-22, following market research that found zero competitor evidence for "technical diagram puzzles" as a distinct product mechanism, and recommending the coloring-page reframe instead. See `coloring-book-generation` for the shared pipeline this reuses.**
