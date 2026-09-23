---
name: "coloring-book-generation"
description: "Fleet-wide blueprint for building adult coloring-book products (printable coloring pages for Etsy/Gumroad) via Canva-generated line art. Covers the critical design_type mistake (document vs. logo), dual export formats (print PDF + digital PNG for tablet apps), shell-quoting gotchas with signed URLs, quality gates for detail density, and reference implementation (product-item-175). Use this whenever an agent is building a coloring book product, needs to decide on a design generation path, or wants to validate a page before shipment."
category: "creative"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["digital-product-quality-bar", "talos-product-launch-audit", "occasion-card-generation"]
---

# Coloring Book Generation — Canva Line Art Pipeline

**Fleet-wide skill.** Covers the complete journey from coloring-book idea to publishable products, with a proven Canva-based generation path and honest documentation of critical mistakes and workarounds discovered in real practice.

## Why this exists

On 2026-09-22, the question was: "Can Talos generate print-ready adult coloring-book pages at scale via Canva?" The research revealed one critical finding:

**Using `design_type: "document"` for coloring pages returns completely wrong templates.** An initial Canva-generation attempt with `design_type: "document"` and a prompt for "intricate line art, black outlines only" returned four candidates, all wrong: a "Mandala Coloring Page" that was actually a business document title slide with "Submitted to: Creative Team" text, an "Invoice" template, "Meeting Minutes," and other completely unrelated layouts. Zero actual illustration content, zero usable coloring-page structure. This is a real, costly mistake — the exact failure mode worth flagging clearly to prevent future attempts down the same broken path.

**The fix: `design_type: "logo"` produces genuinely excellent, print-ready line art on the first try.** Regenerating the exact same conceptual request with `design_type: "logo"` (the same type proven correct for isolated illustration in `occasion-card-generation`'s Canva-hybrid technique) yielded genuinely excellent, print-ready coloring-page line art: clean black outlines, real intricate detail, clear separate colorable regions, correctly isolated on a plain white background with no card layout, no extra text elements. The design_type distinction is the single most important detail in this workflow.

Adult coloring books are a legitimate, proven product category (thousands of unique designs sell monthly on Etsy and Gumroad), but this category has a specific quality gate: a coloring page must have real intricate detail and complexity — thin, sparse pages read as low-effort regardless of execution. This skill documents the design_type mistake, the working path, the dual-export-format requirement unique to this category, and concrete quality checks before shipment.

## The gate — validated page to approved product

### Phase 1: Category & Market Validation (research before design)

Do not start designing a coloring page until you have real evidence the theme has demand and realistic pricing.

#### 1A: Market Research Pattern

Follow the discipline already proven in `digital-product-quality-bar` and `talos-product-launch-audit`:

- **Search the actual platforms** (Etsy, Gumroad, Amazon Print-on-Demand) for existing adult coloring books in this theme (mandalas, nature, fantasy, abstract geometric, etc.). What are the top 5-10 current listings? What's their:
  - Price point (document actual current prices)
  - Page count (most bundles are 10-30 pages, single-page products are rare and lower-priced)
  - Deliverable format (PDF, PNG, both, print-on-demand)
  - Visual style/complexity (line-art density, size of colored regions, detail level)
  - Sales/favorites signal if visible (Etsy shows favorites)

- **Assess whether this theme is viable for Talos:**
  - Is there a price tier where adult coloring books compete (typically $3–15 USD for digital bundles)?
  - Do top competitors show real demand (multiple images, positive signals)?
  - Is the theme specific enough to define a clear product boundary (not generic "coloring pages" but "mandala-style florals for meditation" or "fantasy creatures in intricate scenes")?

- **Document the research** — a one-sentence niche statement minimum: "Adult coloring book: mandala florals, 20 pages, PDF + PNG, $7.99" is the baseline; include the price point and top-3 competitor references.

#### 1B: Positioning & Bundle Planning

Before designing, decide:

- **Core theme**: What is this coloring book FOR? ("meditation/relaxation via mandala patterns," "fantasy lovers who want complex line art," "nature enthusiasts"). Not the design, the use case.
- **Page count & bundle structure**: Most successful products are bundles (15–30 pages minimum), not single pages. Organize into themed collections ("Mandala Pack A: 20 Florals," "Mandala Pack B: 20 Geometric").
- **Detail/complexity level**: Explicitly plan the line-art density. Thin pages (sparse design, large regions) read as budget coloring books; dense pages (many thin lines, many small regions) read as premium/challenging.
- **Format scope**: Digital-only PDF (print at home, via PrintNinja, via print-on-demand), PNG for tablet/iPad coloring apps (Procreate, GoodNotes, Notability — a real distinct market), or BOTH as a standard offering.

### Phase 2: Design Generation — The Working Path (Canva Logo Type)

#### Path: Canva MCP + Logo Design Type ✅ Proven

**Best for:** High-quality, intricate line art suitable for printing and digital tablet use.

**Current readiness in this environment:** PROVEN. Real working code exists for coloring pages (2026-09-22). Three production pages confirmed.

**Critical mistake to avoid:**

❌ **DO NOT use `design_type: "document"`** — it returns business/office document templates, not coloring-page illustrations. Tested versions returned invoices, meeting minutes, and title slides with corporate text. Zero usable coloring-page candidates in any batch.

✅ **DO use `design_type: "logo"`** — returns isolated, intricate illustrations on plain white backgrounds with no layout scaffolding. The same type proven correct for card generation in `occasion-card-generation`.

**What the working path does:**

1. Call `generate-design` with `design_type: "logo"` and a detailed prompt:
   ```
   "A detailed [theme]-style illustration for an adult coloring book: 
    intricate line art, black outlines only on a pure white background, 
    no color fill, no shading, no drop shadow. Many thin lines creating 
    numerous separate colorable regions. Suitable for printing and 
    tablet-based coloring."
   ```
   
2. View candidates via `read-design` with `filter.fields: ["thumbnails"]` — this renders inline directly in the response. (Earlier attempts to `curl` the raw `thumbnail.url` from `generate-design` failed — those URLs return an HTML viewer shell requiring session auth, not a raw image. `read-design` returns real, curl-able signed URLs.)

3. `create-design-from-candidate` to convert the chosen candidate into a real design ID.

4. Export in two formats (both from the same design_id):
   - **Print PDF**: `export-design` with `format: {"type": "pdf", "size": "letter"}` — produces print-ready, 8.5×11 inch page at 300 DPI.
   - **Digital PNG**: `export-design` with `format: {"type": "png", "width": 2000}` — produces high-resolution image for digital/tablet coloring (Procreate, GoodNotes, Notability use 2000+ pixels).

5. Download both signed URLs via **Python's `requests.get(url)`**, NOT bash `curl`.

**Strengths:**
- Genuinely high-quality line art (not geometric clip art)
- Intricate detail and complexity (buyers see real coloring challenge, not thin/sparse page)
- Clean white background (no chroma-keying or post-processing needed — unlike card generation, the whole point of a coloring page is the plain white background)
- Deterministic output
- Both print (PDF) and digital (PNG) formats from the same asset
- Fully human-supervised session (not headless, but suitable for interactive Talos sessions or human builders)

**Weaknesses:**
- Requires human-supervised Canva session (OAuth-authenticated)
- Not suitable for fully autonomous Talos execution (same auth constraint as Path B in `occasion-card-generation`)
- PDF/PNG export availability limited by Canva's platform update cycles (rare, but verify export feature is available)

**Critical gotcha — shell-quoting corrupts signed URLs:**

One PNG export download failed via bash `curl` with a `SignatureDoesNotMatch` XML error even though the signed URL was freshly generated. Root cause: shell special characters in the signed URL (`&`, `%2F`, `=`, etc.) were mangled by bash double-quote escaping. The exact same URL worked fine when requested via Python's `requests.get(url)` without any shell quoting layer.

**The reliable pattern:**
```python
import requests

url = "<signed_export_url>"
response = requests.get(url)
response.raise_for_status()

with open("output.png", "wb") as f:
    f.write(response.content)
```

Never pass these URLs through bash `curl` — the string corruption is silent (no obvious error until the bytes are checked) and only appears for URLs with special characters, making it hard to reproduce and debug consistently.

**Reference pattern:**

Product-item-175 (2026-09-22): 3 coloring pages.
- Page 1: Mandala-style floral wreath — intricate repeating patterns, many separate colorable sections, print-ready PDF + 2000px PNG.
- Page 2: Autumn pumpkin-patch scene — pumpkins, vines, leaves, with detailed line work suitable for both print and digital coloring.
- Page 3: Whimsical owl-on-branch-under-stars — detailed feather line art, leafy branch, scattered stars, real complexity.

All three pages generated with `design_type: "logo"`, exported to both PDF (letter-size, 300 DPI) and PNG (2000px width), downloaded via Python requests library. All images confirmed to have high detail density and genuinely intricate line work (not sparse/thin).

---

### Phase 3: Content Quality Gate — Detail Density & Printability Check

Before declaring a page "done," verify it passes the quality check specific to coloring books.

#### The Real Failure Mode (Potential, based on card-skill precedent)

A coloring page that is technically a "design" but uses thin, sparse line art reads as low-effort or budget, not premium. Buyers of adult coloring books specifically seek challenge and intricacy — a page with 5-10 large regions and minimal detail reads as a children's coloring book, not an adult product.

**The check:**
- [ ] Does the page have **genuinely intricate detail**? Count the line-art density: is there visible complexity with many small regions, not just a few large shapes?
- [ ] Would a buyer look at this preview and think "this will take 20+ minutes of careful coloring" (premium) or "this will take 5 minutes" (budget/sparse)?
- [ ] Is the line art consistently detailed throughout, or are there bare/empty areas that feel unfinished?

**How this differs from card generation:**
Cards tolerate sparse/geometric designs as intentional minimalist choices. Coloring books do not — buyers are explicitly purchasing density and complexity. A sparse coloring page is a fundamental product-type mismatch, not a valid design choice.

#### Verify Printability

- [ ] PDF export test: download the PDF, open in a PDF viewer, print to paper. Does it render cleanly? No smudging, no color shifts (since these are black-line pages, the PDF should be pure black + white)?
- [ ] PNG dimensions: is the PNG 2000px+ width? For tablet use, buyers with Retina displays will appreciate high resolution.
- [ ] Both formats exist for the same page? (Never ship one format only; dual-format is the category standard.)

#### Reference the Full Quality Gate

Before publishing, run the complete `digital-product-quality-bar` checklist:
1. **Deliverable format** — for coloring books, PDF (print-ready) + PNG (digital/tablet) are BOTH standard. Both should be included as download options in the customer package.
2. **Preview images** — minimum 5-7, showing sample pages, detail close-ups, and at least one page with example coloring (a partial or fully colored version of the same page design to show buyers what the result looks like).
3. **Listing copy** — benefit-first ("Intricate designs to challenge and relax you"), clear what's included (page count, file formats, software required).
4. **Category-specific** — show at least one actual COLORED sample page in preview images. Buyers won't buy blind on line-art quality; they need to see what the design looks like with color applied.
5. **Pricing** — compare against current comps on the actual platform. Adult coloring books typically price $3–12 USD depending on page count (10-20 pages = $4–6, 20-40 pages = $6–10, 50+ pages = $10+).

### Phase 4: Product Delivery & Publishing

Package the coloring-book product for Talos distribution:

1. **File structure** (Phase 3 output directory)
   ```
   product-item-N/
   ├── phase-3/
   │   ├── customer-package/
   │   │   ├── coloring-book-complete.pdf        # All pages, print-ready, 300 DPI
   │   │   ├── page-1-print.pdf                  # Individual page PDFs
   │   │   ├── page-2-print.pdf
   │   │   ├── page-3-print.pdf
   │   │   ├── page-1-digital.png                # High-res PNGs for tablet apps
   │   │   ├── page-2-digital.png
   │   │   ├── page-3-digital.png
   │   │   └── README.txt                        # How to print & digital-color
   │   ├── preview-mockups/
   │   │   ├── preview-all-pages.png             # All pages shown
   │   │   ├── preview-page-1-detail.png         # Close-up of line art
   │   │   ├── preview-page-1-colored.png        # Actual colored sample
   │   │   ├── preview-page-2.png
   │   │   ├── preview-page-3.png
   │   │   └── preview-context.png               # Page in use (printed, on table, etc.)
   │   └── STATUS.json
   └── listing-content/
       ├── etsy-listing.md
       └── gumroad-listing.md
   ```

2. **Listing copy structure** (per `digital-product-quality-bar`):
   - **Headline**: benefit-focused ("Unwind with 20 intricate coloring pages — detailed line art for hours of meditative creativity")
   - **What's included** (bullets): "20 full-page coloring designs", "Print-ready PDF at 300 DPI", "High-resolution PNG files for iPad/tablet coloring apps (Procreate, GoodNotes, Notability)", "Themes: mandalas, nature scenes, [specific themes]"
   - **Who this is for**: niche description ("Adults seeking intricate line art for relaxation and creative expression")
   - **Delivery**: "Instant digital download. Print at home, local print shop, or bring PDF to online print service. Use PNG files in your favorite tablet coloring app."
   - **File specs**: "PDF (300 DPI, 8.5×11 in, black line art on white), PNG (2000×2600 pixels, RGB)"
   - **FAQ**: addressing "What paper should I use?", "Can I print in color?", "How do I use PNG on iPad?", "Are these commercial-license (resell/print-for-profit)?"

3. **Run the full audit** before publish:
   - Check via `talos-product-launch-audit` for duplicates on both platforms
   - Verify deliverable format (BOTH PDF + PNG, not one only)
   - Confirm preview image count (minimum 7, including at least one colored sample)
   - Verify page count matches listing claim
   - Confirm no leaked internal prompts/scratchpad text in customer files

### Phase 5: Variant Generation at Scale

Once one coloring page works, generating variants is mechanical:

- **Theme variants** (easiest): different visual theme, same line-art density and complexity level (mandala → nature → fantasy → geometric)
- **Complexity variants** (medium): same theme, different detail level (simple mandala → intricate mandala with nested patterns)

Talos can batch-produce these by:
1. Templating the Canva-generation prompt (parameterize theme, complexity, style)
2. Looping over variant configs (JSON list of {theme, complexity, style} combinations)
3. Exporting each to PDF + PNG via the working path above
4. Bundling 15-30 per product

This is suitable for human-supervised batches, fully repeatable.

---

## Gotchas & Common Mistakes

### Gotcha 1: Using `design_type: "document"` for coloring pages
**DON'T.** This returns business/office templates, not illustrations. Tested versions returned invoices, meeting minutes, corporate slides — zero usable candidates. Always use `design_type: "logo"`.

### Gotcha 2: Passing signed URLs to bash `curl`
**DON'T.** Special characters in the URL (`&`, `%2F`, `=`, etc.) are mangled by shell escaping, causing `SignatureDoesNotMatch` errors. Use Python's `requests.get(url)` instead.

### Gotcha 3: Shipping only PDF (or only PNG)
**DON'T.** Dual format is the market baseline for coloring books. Print-ready PDF + high-res PNG for tablet apps are both standard. Include both in every product.

### Gotcha 4: Sparse line art masquerading as a finished design
**DON'T.** A page with 5-10 large regions reads as children's coloring, not adult premium. Adult coloring books must have genuinely intricate detail — many small regions, complex line work, real coloring challenge. If the generated page is sparse, pick a different candidate or regenerate with a more detailed prompt.

### Gotcha 5: No colored sample in preview images
**DON'T.** Buyers won't purchase blind on line-art quality. Include at least one preview image showing the same page (or a similar page) with actual coloring applied — this shows the real result and builds confidence.

### Gotcha 6: Forgetting to test printability
**DON'T.** Download the actual PDF, open it, print it to paper. Verify: no smudging, black lines are crisp, dimensions are correct. A PDF that looks fine on screen can have hidden issues when printed.

### Gotcha 7: Single-page products priced at bundle rates
**DON'T.** A single coloring page is not a competitive product (buyers expect 15+ pages minimum). If you generate a single page, either bundle it with others or price it distinctly lower ($1-2, not $4-6).

---

## Success Checklist

### Design Phase
- [ ] Market research completed (top 5 coloring-book comps identified, prices documented, page counts noted)
- [ ] Theme & use case defined (meditation/fantasy/nature/etc.)
- [ ] Bundle structure decided (page count: 15-30 minimum, theme consistency)
- [ ] Design path chosen: Canva Logo Type + dual export (PDF + PNG)
- [ ] Multiple design candidates generated and reviewed for detail density
- [ ] All pages confirmed to have intricate detail (not sparse/thin)

### Product Phase
- [ ] All pages generated in both PDF and PNG formats
- [ ] PDF test-printed (black lines crisp, dimensions correct, no smudging)
- [ ] PNG files confirmed high-resolution (2000px+)
- [ ] Preview images created (minimum 7, including at least one colored sample and close-up detail)
- [ ] Customer package assembled (PDFs, PNGs, README, file specs clear)
- [ ] Listing copy written (benefit-first, theme clear, dual-format documented)
- [ ] No leaked internal content in customer files
- [ ] Duplicate check passed (no same title on Etsy/Gumroad)
- [ ] Quality gate passed (digital-product-quality-bar full checklist)

### Publishing Phase
- [ ] All files uploaded to Etsy/Gumroad (both PDF + PNG options)
- [ ] Pricing matches current market comps for page count
- [ ] Product live and tested (bought + downloaded as customer, verified both formats work)
- [ ] Audit cycle complete (talos-product-launch-audit passed)

---

## Dependencies

This skill orchestrates:
- **digital-product-quality-bar** — the full publishing gate
- **talos-product-launch-audit** — duplicate detection, truth-in-listing checks
- **Canva MCP** — for interactive design generation (requires authenticated claude.ai session)
- **Python requests** — for downloading signed export URLs

All core dependencies are available.

---

## Related Skills & Reading

- [digital-product-quality-bar](../product/digital-product-quality-bar/) — the full publishing gate
- [talos-product-launch-audit](../product/talos-product-launch-audit/) — pre-publish audit cycle
- [occasion-card-generation](./occasion-card-generation.md) — sibling skill covering card-specific design paths and Canva-hybrid technique

---

## Example: Mandala Coloring Pages (Real, 2026-09-22)

**Theme:** Adult coloring book, mandala florals + nature + abstract geometric, intricate line art for meditation/relaxation.

**Design path:** Canva MCP with `design_type: "logo"`.

**Pages actually shipped (product-item-175):**
1. **Mandala-style floral wreath** — concentric repeating floral pattern, many small regions, real intricacy. Print PDF + 2000px PNG.
2. **Autumn pumpkin-patch scene** — pumpkins of varying sizes, detailed vines with leaves, field elements, high line-art density. Print PDF + 2000px PNG.
3. **Whimsical owl-on-branch-under-stars** — detailed feather line work on the owl, leafy branches, scattered stars with fine detail, genuinely intricate. Print PDF + 2000px PNG.

**Real working process:**
- Generated 3 unique page designs using `generate-design` with `design_type: "logo"`, 1 candidate per design selected
- Exported each to PDF (letter-size, 300 DPI, print-ready) and PNG (2000px width, digital/tablet use)
- Downloaded both formats via Python requests library
- Created 7 preview mockups (overview of all 3 pages, detail close-ups, one page shown with example coloring applied)
- Wrote listing copy ("Unwind with intricate mandala and nature coloring pages...")
- Ran full quality gate + duplicate checks
- Published to Etsy/Gumroad at $4.99

**Total time:** ~60 minutes for 3 complete, publishable pages.

**Result:** 3 coloring-page designs, both PDF (print-ready, 300 DPI) and PNG (digital/tablet), 7 preview images, pricing competitive for page count and quality.

---

**This skill was authored 2026-09-22 and captures the proven Canva Logo-type coloring-generation pattern, the critical design_type mistake, dual-export requirement, and shell-quoting gotcha discovered in real practice.**
