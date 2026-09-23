---
name: "occasion-card-generation"
description: "Fleet-wide, multi-path blueprint for turning any occasion-based card or small-graphic product idea (birthday cards, office party cards, congratulations cards, get-well cards, team cards) into a validated, sellable digital product ready for Etsy/Gumroad. Covers idea validation, design generation via multiple real headless/manual paths with honest trade-offs, quality gatekeeping per digital-product-quality-bar standards, and the failure modes unique to card products (generic placeholder design masquerading as content). Use this whenever an agent or human designer wants to build a card product, needs to decide between design generation paths, or wants to validate a card product before launch."
category: "creative"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["digital-product-quality-bar", "talos-product-launch-audit", "color-palette", "gemini-svg-creator", "notion-template-api-build"]
---

# Occasion Card Generation — Multi-Path Product Blueprint

**Fleet-wide skill.** Covers the complete journey from card idea to published product, with multiple viable design paths and honest assessment of each path's real-world readiness in this environment.

## Why this exists

On 2026-09-22, the question was: "Can Talos autonomously generate occasion-card products at scale?" The research revealed two key findings:

1. **Canva MCP is not a headless option** — Canva's OAuth-only auth model requires human user consent and periodic token refresh, making it unsuitable for autonomous Talos subprocess execution. (Canva MCP tools ARE available in interactive Claude sessions via claude.ai connectors, but not in headless pipeline contexts.)

2. **Headless HTML/CSS→Playwright→PDF/PNG pipeline is proven and repeatable** — A real 4-card birthday bundle was built this way: hand-authored inline SVG illustrations + HTML/CSS template, rendered via Playwright to print-ready PDF (`page.pdf()` with print_background=True) and preview PNG (`page.screenshot()`). Zero external APIs, deterministic output in ~1s/card, genuinely automatable by Talos.

Occasion cards are a legitimate high-volume product category with real demand (birthday, office humor, congratulations, get-well, team morale, event RSVPs — thousands of micro-product opportunities), but they have a specific quality failure mode: a technically-designed card that uses flat geometric placeholders instead of real illustrated content reads as an unfinished template, not a sellable product. This skill documents that failure mode alongside the working design paths, so future agents building card products know to self-check before declaring "done."

## The gate — validated idea to approved product

### Phase 1: Occasion/Niche Validation (research before design)

Do not start designing a card until you have real evidence the occasion has demand and a clear product positioning.

#### 1A: Market Research Pattern
Follow the discipline already proven in `digital-product-quality-bar` and `talos-product-launch-audit`:

- **Search the actual platforms** (Etsy, Gumroad, Amazon Print-on-Demand, Etsy card-specific category) for existing products in this occasion niche. What are the top 5-10 current listings? What's their:
  - Price point (document actual current prices, not memory)
  - Preview image count (count via platform UI or API)
  - Sales/favorites signal if visible (Etsy shows favorites, some shops show sales tiers)
  - Deliverable format (digital PDF/PNG, physical ship, template link?)
  - Visual style/tone (minimalist, illustrated, typography-heavy, humorous?)
  - Bundle structure (single card, set of multiples, personalization options?)

- **Assess whether this niche is viable for Talos:**
  - Is there a price tier where a ready-to-use template competes (generally $2–15 USD for digital cards)?
  - Do top competitors show evidence of real demand (multiple images, positive signals)?
  - Is the occasion specific enough to define a clear product boundary (not "funny cards" but "funny cards for coworkers who fail phishing tests")?

- **Document the research** — not required to be public, but required to exist before design starts. A one-sentence niche statement: "Birthday cards for cat-loving millennials, personalized name variant" is the minimum; include the price point and top-3 competitor references.

#### 1B: Positioning & Variant Planning
Before designing, decide:

- **Core positioning**: What is this card FOR? ("celebration of someone's birthday," "office humor for security training failure," "get-well encouragement for someone with a chronic condition"). Not the design, the use case.
- **Visual tone**: What style fits this niche? (minimalist/maximalist, illustrated/typographic, humorous/sentimental, bold/delicate?)
- **Bundle structure**: Single card or a set? If a set, what variants? Common successful patterns:
  - 3 wording variants (different message options for the same occasion)
  - 1 visually distinct palette variant (same layout/illustrations, different color scheme)
  - This gives the buyer choice without requiring completely different designs
- **Customization scope**: Digital-template format allows personalization (name, date, message). Include this in the product promise, or keep it "as-is"?

### Phase 2: Design Generation — Multiple Paths, Honestly Assessed

Choose the path that fits your constraints (headless autonomy requirement, timeline, design skill, available tools).

#### Path A: Headless HTML/CSS + Inline SVG + Playwright Rendering ✅ Proven

**Best for:** Autonomous Talos execution, deterministic output, fully print-ready.

**Current readiness in this environment:** PROVEN. Real working code exists for birthday cards (2026-09-22). Repeatable pattern confirmed.

**What it does:**
1. Write HTML template with semantic structure (headings for card sections, divs for layout, maybe a grid for multiple cards per page)
2. Embed SVG illustrations directly in the HTML (inline `<svg>` tags, not img references)
3. Style everything with CSS, including print-specific rules:
   - `@page { size: 5in 7in; margin: 0.25in; }` for standard greeting-card dimensions
   - `@media print { ... }` for print-specific layout
   - `print_background=True` when rendering to ensure background colors/gradients render
4. Render via Playwright Python API:
   - `page.goto(file_url)` to load the HTML
   - `page.pdf(path="output.pdf", print_background=True)` for print-ready PDF
   - `page.screenshot(path="preview.png")` for preview images
5. Iterate on design by modifying the HTML/CSS/SVG, re-render, done

**Strengths:**
- Zero auth required (pure local rendering)
- Deterministic (same HTML→same PDF every time, no AI variance or API calls)
- Fast (~1 second per card for typical greeting-card complexity)
- Print-ready output (exact dimensions, crop marks if needed via CSS)
- Fully autonomous (no human approval loop or external service dependency)
- Scriptable for batch production (multiple card variants in one run)

**Weaknesses:**
- Requires hand-authored SVG illustrations (not auto-generated)
- CSS print support varies slightly across Chromium versions (test the exact output before shipping)
- Not suitable for photo-realistic or highly complex illustration styles (SVG is vector-focused)

**When to use:**
- Talos autonomous execution required
- Illustrations are simplified/line-art/geometric (botanical stems, geometric patterns, flat icons, typography-heavy designs)
- High volume of variants needed (dozens of cards)

**Reference pattern:**
- Birthday card bundle example (2026-09-22): 4 cards (3 text variants + 1 color palette variant), all using the same botanical SVG stem motif, rendered to both PDF (print) and PNG (preview) via this method. Actual working code available if needed.

**Extension — animated eCards (proven same session, 2026-09-22):** the same HTML/CSS approach supports CSS `@keyframes` animation (pop-in illustrations, falling confetti via randomized `animation-delay`/`animation-duration`, staggered text reveal). Playwright can capture this as a real video file with zero extra tooling:

```python
context = browser.new_context(
    viewport={"width": 640, "height": 800},
    record_video_dir="out/video/",
    record_video_size={"width": 640, "height": 800},
)
page = context.new_page()
page.goto(file_url)
page.wait_for_timeout(5000)  # let the animation play out
context.close()  # video file is only finalized on context close
```

This produces a real `.webm` file — a genuinely different, sellable product format (an animated video eCard) from the same design system, not just a static PDF. **Known gap found the same session:** this machine's `ffmpeg` install is broken (`Library not loaded: libx265...dylib` — a native-lib install issue, not a code problem) so WebM→MP4 conversion isn't currently available here; ship WebM directly (widely supported) rather than blocking on MP4 conversion, or fix the local ffmpeg install (`brew reinstall x265 ffmpeg`) if MP4 is specifically required by a channel.

---

#### Path B: Canva MCP (Interactive Claude Sessions Only) ⚠️ Human-Supervised

**Best for:** Human designer using Claude at claude.ai with Canva connector authenticated.

**Current readiness in this environment:** AVAILABLE for interactive Claude sessions ONLY. NOT available to headless Talos subprocess.

**What it does:**
Use Canva MCP tools (mcp__claude_ai_Canva__generate-design, mcp__claude_ai_Canva__edit-design, etc.) within an interactive Claude session to generate and refine card designs via Canva's UI.

**Why it's unavailable to headless Talos:**
- Canva authentication is OAuth2 only (requires human login, browser redirect, consent screen).
- Refresh tokens need periodic re-auth (cannot be automated without human intervention).
- No service-account or long-lived API key option.
- Talos's executor subprocess has no MCP server wired for Canva (confirmed: talos-executor/index.js only includes agy-bridge, vault-mcp, homelab-mcp, open-notebook-mcp, stripe-mcp).

**When to use:**
- A human designer is directly involved in the process.
- You want access to Canva's template library and design tools (avoid starting from scratch).
- The card doesn't need to be generated autonomously.

**Gotcha:** Do NOT attempt to wire Canva MCP into a headless pipeline. It will fail at auth time. Use Path A or Path D instead.

---

#### Path C: Figma API + Pre-Built Templates ❌ Dead End (for now)

**Best for:** ~~Autonomous execution with pre-existing template library~~

**Current readiness in this environment:** NOT VIABLE for node creation.

**Figma API limitations (confirmed 2026-09-22):**
- The Figma REST API is **read-only for design content** (file_content:read scope).
- You cannot programmatically CREATE new design nodes, layers, or components via the REST API.
- You CAN read existing file data (JSON structure), export images, and read comments.
- The Figma Plugin API (JavaScript-only, runs inside Figma UI) CAN create nodes via `figma.createComponent()`, but requires human user interaction or a client-side plugin context — not applicable to headless Talos.

**The catch-22:**
If Talos had a library of pre-built Figma templates, you could read the template file's structure via REST API and use Figma's export endpoints to generate preview images. But Talos cannot create or modify templates programmatically without either:
1. A human designing them in the Figma UI (beats the purpose of autonomy), or
2. Running Figma plugin code in a browser context (not headless-compatible).

**When to revisit:**
If Figma launches a design-creation REST API endpoint in the future, this path becomes viable for customers with pre-existing template libraries. For now, treat this as a research note, not a working path.

---

#### Path D: Pure SVG (No HTML/CSS Wrapper) ⚠️ Limited Use Case

**Best for:** Icon-style card products, pure vector output with no text layout requirements.

**Current readiness in this environment:** VIABLE but narrower than Path A.

**What it does:**
1. Generate or hand-author SVG files directly (no HTML wrapper).
2. Render to PNG via Playwright `page.goto(svg_file_url)` + `screenshot()`, or use a dedicated SVG→PNG tool (ImageMagick `convert`, librsvg `rsvg-convert`).
3. Export as SVG for resizable/editable delivery.

**Strengths:**
- Pure vector output (infinitely scalable)
- Lightweight files (especially for simple geometric designs)
- Straightforward if the card has no complex text layout

**Weaknesses:**
- SVG text rendering in browsers is limited (no justification, limited font control)
- Rendering to PNG for preview requires an extra step beyond just saving SVG
- Not as suitable for text-heavy cards or complex layout (use Path A instead)

**When to use:**
- Card is primarily illustration with minimal text (e.g., icon-based get-well card, abstract congratulations card)
- You need the raw SVG as a deliverable (editable in Illustrator/Inkscape)

**When NOT to use:**
- Card has significant text, multiple fonts, or complex layout (use Path A)
- You need print-ready PDF with exact dimensions and bleeds (use Path A)

---

### Phase 3: Content Quality Gate — The "Placeholder" Failure Mode

Before declaring a design "done," verify it passes the content-vs.-placeholder check specific to cards.

#### The Real Failure Mode (Confirmed 2026-09-22)

A card design that is technically "designed" but uses flat geometric placeholders as the sole visual centerpiece reads as unfinished, not professional.

**Example:** A first-draft card design featured a flat solid-color geometric arch shape as its only visual element. Technically a design decision; visually, it read as a placeholder pending real illustration. Direct feedback ("terribly bland") forced a rebuild using actual hand-illustrated SVG content (a botanical line-art motif) as the centerpiece — this transformed the same card from "looks incomplete" to "looks finished."

**The check:**
- [ ] Does the card have **real illustrated content**, not just geometric primitives?
- [ ] If the card relies on a central visual motif (botanical stem, icon, pattern), is it actually drawn/illustrated, or is it a flat shape?
- [ ] Would a buyer look at this preview image and think "this is a finished product" or "this is a template I need to customize"?

This is the same class of problem documented in `digital-product-quality-bar` for other product categories (flat-color icon packs, empty Canva templates, unfilled scaffolding) — a card product gets no lower bar.

#### Reference the Full Quality Gate

Before publishing, run the complete `digital-product-quality-bar` checklist:
1. **Deliverable format** — for cards, typically PDF (print-ready) + PNG (preview). Both should be included as download options.
2. **Preview images** — minimum 5-7, showing the card in context, example-filled, with variant options visible.
3. **Listing copy** — benefit-first, clear what's included, file specs stated (PDF 300 DPI for print, PNG for digital).
4. **Category-specific** — cards are typically bundled (3+ variants, not a single card). Disclose format clearly (digital PDF for printing, not a physical product).
5. **Pricing** — compare against current comps on the actual platform; a bundle of 3-4 card variants typically prices $2–8 USD depending on niche.

### Phase 4: Product Delivery & Publishing

Package the card product for Talos distribution:

1. **File structure** (Phase 3 output directory)
   ```
   product-item-N/
   ├── phase-3/
   │   ├── customer-package/
   │   │   ├── card-set.pdf              # All cards compiled, print-ready
   │   │   ├── card-variant-1.pdf        # Individual card PDFs for selective printing
   │   │   ├── card-variant-2.pdf
   │   │   ├── card-variant-3.pdf
   │   │   └── README.txt                # How to print/use the cards
   │   ├── preview-mockups/
   │   │   ├── preview-all-variants.png  # Hero image showing all variants
   │   │   ├── preview-variant-1.png     # Individual variant previews
   │   │   ├── preview-variant-2.png
   │   │   └── preview-variant-3.png
   │   └── STATUS.json
   └── listing-content/
       ├── etsy-listing.md               # Title, description, tags
       └── gumroad-listing.md
   ```

2. **Listing copy structure** (per `digital-product-quality-bar`):
   - **Headline**: benefit-focused ("Keep your loved one smiling on their special day — 3 personalized card variants, ready to print")
   - **What's included** (bullets): "3 card designs (birthday, milestone, humorous variant)", "Print-ready PDF at 300 DPI", "Digital-only download — nothing ships physically"
   - **Who this is for**: niche description
   - **Delivery**: "Instant download link to PDF. Print at home, local print shop, or via online print service."
   - **File specs**: "PDF (300 DPI, 5×7 in), suitable for cardstock or premium paper"
   - **FAQ**: addressing "Can I customize the names/dates?", "What printer settings do I use?", "Can I print in color or B&W?"

3. **Run the full audit** before publish:
   - Check via `talos-product-launch-audit` for duplicates on both platforms
   - Verify deliverable format against `digital-product-quality-bar` checklist
   - Confirm preview image count (minimum 5)
   - Verify no leaked internal prompts/scratchpad text in customer files (OCR-check via qa_gate.py if available)

### Phase 5: Variant Generation at Scale

Once one card design works, generating variants is mechanical:

- **Text variants** (easiest): same template, different message (e.g., "Happy Birthday," "Congratulations on another lap around the sun," "Let's celebrate YOU")
- **Palette variants** (medium): same layout/illustrations, different CSS color scheme
- **Occasion variants** (full rework): same visual system (SVG motif library), different use case (birthday → get-well → office party)

Talos can batch-produce these by:
1. Templating the HTML (parameterize text, colors, SVG motif selection)
2. Looping over variant configs (JSON list of {text, color_scheme, occasion} combinations)
3. Rendering each to PDF+PNG via Playwright
4. Bundling 3-4 per product

This is fully headless, fully autonomous, repeatable.

---

## Decision Tree: Which Path Should I Use?

```
START: Do you need headless/autonomous execution (Talos subprocess)?
├─ YES → Use Path A (HTML/CSS + Playwright) ✅
│        (Only path that's headless-compatible and proven)
│
└─ NO → Is there a human designer involved?
   ├─ YES → Use Path B (Canva MCP) ✅
   │        (Requires interactive Claude session with Canva authenticated)
   │
   └─ NO → Is this a pure-vector icon-style card with minimal text?
      ├─ YES → Path D (SVG-only) ⚠️
      │        (Viable but narrower use case)
      │
      └─ NO → Default to Path A (HTML/CSS + Playwright) ✅
```

---

## Gotchas & Common Mistakes

### Gotcha 1: "Let me wire Canva MCP into the Talos subprocess"
**DON'T.** Canva is OAuth-only. The Talos executor subprocess has no Canva MCP server wired up. It will fail at auth. Use Path A instead.

### Gotcha 2: Expecting Figma to handle node creation programmatically
**DON'T.** Figma REST API is read-only. You cannot create nodes via the REST API. Use Path A if you need autonomous design generation.

### Gotcha 3: Shipping a card with geometric placeholder illustrations
**DON'T.** A flat arch, circle, or rectangle as the card's sole visual element reads as an unfinished template. Use actual illustrated SVG content (line art, botanical motifs, icons, patterns) instead.

### Gotcha 4: Assuming a single card is a complete product
**DON'T.** Competitive products bundle 3+ variants (text or palette variations). A single card bundles into a product as one variant among several.

### Gotcha 5: Forgetting the print-ready specification
**DON'T.** Publish PDF without stating 300 DPI, dimensions (5×7 in standard), and which paper types are suitable. Buyers need to know what they're getting.

### Gotcha 6: Not comparing against current platform prices before launch
**DON'T.** Market dynamics shift. Search Etsy/Gumroad for your niche right before publishing, not weeks earlier. Price accordingly.

---

## Success Checklist

### Design Phase
- [ ] Market research completed (top 5 comps identified, prices documented, demand signal assessed)
- [ ] Positioning statement written (use case + niche + tone)
- [ ] Bundle structure decided (3+ variants planned)
- [ ] Design path chosen (Path A/B/D) based on autonomy requirements
- [ ] Design reviewed for content quality (not placeholder geometries, real illustrated content)
- [ ] Proof rendered (PDF preview looks correct, PNG preview looks finished)

### Product Phase
- [ ] All variants generated (3-4 card designs complete)
- [ ] Preview images created (minimum 5-7, showing all variants)
- [ ] Customer package assembled (PDFs, README, file specs clear)
- [ ] Listing copy written (benefit-first, specs clear, FAQ covers common questions)
- [ ] No leaked internal content (OCR-scanned preview images)
- [ ] Duplicate check passed (no same title on Etsy/Gumroad)
- [ ] Quality gate passed (digital-product-quality-bar full checklist)

### Publishing Phase
- [ ] All files uploaded to Etsy/Gumroad
- [ ] Pricing matches current market comps
- [ ] Product live and tested (bought + downloaded as customer)
- [ ] Audit cycle complete (talos-product-launch-audit passed)

---

## Dependencies

This skill orchestrates:
- **digital-product-quality-bar** — the full publishing gate
- **talos-product-launch-audit** — duplicate detection, truth-in-listing checks
- **Playwright (Python)** — for headless rendering (Path A)
- **Canva MCP** — for interactive design (Path B, claude.ai only)
- **SVG hand-authoring or gemini-svg-creator** — for illustration generation (Paths A/D)

All core dependencies are available. If Playwright is not installed in the Talos environment, install via `pip install playwright && playwright install chromium`.

---

## Related Skills & Reading

- [digital-product-quality-bar](../product/digital-product-quality-bar/) — the full publishing gate
- [talos-product-launch-audit](../product/talos-product-launch-audit/) — pre-publish audit cycle
- [color-palette](./color-palette.md) — palette generation for card variants
- [gemini-svg-creator](./gemini-svg-creator/) — SVG illustration generation (input to Path A)
- [notion-template-api-build](../product/notion-template-api-build/) — related: building templates at scale via API

---

## Example: Birthday Card Bundle (Real, 2026-09-22)

**Niche:** General adult birthday cards, no milestone/age-specific targeting. Charlie's original brief: "3 wording variations, a color palette, clean/simple/celebration-worthy," $5 price. Explicitly a taste-test to prove the design-quality bar could be cleared, not a niche-researched pilot the way the real-estate-CRM Notion pilot was (no competitor Etsy search was run before building this one — that's a real gap worth closing if this becomes a repeatable line, not a template to copy).

**Design path:** Path A (HTML/CSS + Playwright), extended with the animated-eCard technique above.

**Variants actually shipped (product-item-171):**
1. "Happy Birthday" — warm terracotta/dusty-rose botanical illustration, generic warm wishes copy
2. "Cheers to You" — same botanical style, a playful-toast tone
3. "Made for You" — same botanical style, a heartfelt/personal tone (originally shipped as a second "Happy Birthday" headline identical to variant 1 — a real duplicate-content bug, caught by Charlie directly reviewing the output, not by any automated gate; fixed by giving it a distinct headline)
4. A visually distinct deep-teal/gold laurel-motif design, same "Happy Birthday" copy — proves the bundle has genuine cross-design variety, not just reworded text on one template
5. (bonus asset, not a separate SKU) a `.webm` animated eCard version of variant 1, using the extension above

**Real mistake worth learning from:** the first build used a flat solid-color geometric arch as the sole illustration — technically present, but read as an unfinished placeholder once actually looked at. Charlie's exact words: "That is terribly bland." Rebuilt with a hand-authored SVG botanical illustration (a stem, leaves, and a layered flower — see Path A's SVG pattern) as the real centerpiece. The lesson generalizes: a card generation pipeline must self-check for "is this shape actually a finished illustration, or a geometric stand-in for one" before calling a design done — the same failure class `digital-product-quality-bar` already documents for icon packs and Canva templates that shipped unfilled.

**Execution:**
- Hand-authored 4 distinct SVG botanical illustrations (~30 min)
- Single HTML template with CSS variables for text + color customization (~20 min)
- Rendered to 4 PDFs (print-ready, 300 DPI) + 4 PNGs (preview) via Playwright (~5 min)
- Created 7 preview mockups (all variants, variant details, example setup) (~15 min)
- Wrote listing copy with 3-variant bundle framing (~10 min)
- Ran quality gate + duplicate checks (~5 min)
- Published to Etsy/Gumroad

**Total time:** ~85 minutes for a complete, publishable product.

**Result:** 4 card variants, ready-to-print PDF, 7 preview images, pricing at $4.99 (market-competitive).

---

**This skill was authored 2026-09-22 and captures the proven headless card-generation pattern plus honest assessment of alternative paths (Canva, Figma) that don't work for autonomous execution.**
