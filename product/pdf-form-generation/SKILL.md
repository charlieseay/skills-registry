---
name: "pdf-form-generation"
description: "Generate a genuinely fillable PDF (real AcroForm checkboxes/text fields, not flattened-to-image visuals) for planner/tracker/journal-style digital products, using only local/free tools already in this pipeline (Playwright + pypdf, no reportlab/weasyprint/wkhtmltopdf). Use this whenever a product needs a fillable form — habit trackers, budget planners, checklists, logbooks — anything with checkboxes or text fields a buyer fills in digitally (GoodNotes/Procreate/Acrobat), not just a static printable. This closes the exact capability gap flagged in decision #288/#289 (40-item planner/tracker idea list) — the shop had no fillable-form pipeline before 2026-09-24."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["coloring-book-generation", "branching-narrative-pdf", "digital-product-quality-bar"]
---

# PDF Form Generation

**Fleet-wide skill.** Any agent building a planner/tracker/journal product
with fillable fields should use this pattern rather than shipping a
static-only PDF (which undersells the category — buyers filling out a
digital planner in GoodNotes/Procreate expect real tappable fields, not a
flat image of a checkbox) or reaching for a new paid dependency.

## Why this exists, and why it's two tools, not one

Confirmed empirically 2026-09-23 (task #3338, proof receipt
`task_3338_1790211586`, 30/30 real fields verified) — this is a **hybrid
pipeline**, because neither tool alone can do the job:

- **Playwright's `page.pdf()` cannot create real fillable fields.** It
  renders via Chromium's print pipeline, which rasterizes HTML
  `<input>`/`<div>` elements into their static visual appearance only. An
  HTML checkbox printed to PDF becomes ink that *looks* like a checkbox —
  no AcroForm `/Widget` annotation exists behind it, so `pypdf.get_fields()`
  (or Acrobat, or any real PDF viewer's form mode) sees nothing. Confirmed
  by trying the visual-only path first: `get_fields()` returned `None`.
- **pypdf can create real AcroForm fields but has no page-layout engine** —
  no HTML/CSS, no text flow, no tables. It only manipulates existing PDF
  objects (rects, streams, dictionaries).

So: **Playwright renders the visual design and records exact DOM
coordinates of every fillable element; pypdf overlays real `/Widget`
annotations on top of those exact coordinates.**

**Ruled out, don't re-litigate:** reportlab (not installed, would be a new
dependency this category doesn't yet justify), weasyprint (installed but
missing system libs — Pango/cairo/GDK-Pixbuf — `import weasyprint` fails
outright on this host, a Homebrew library chase not a code fix), wkhtmltopdf
(not installed, abandoned upstream since 2020, known CVEs).

## The pipeline — two scripts, run in order

`scripts/render_layout.py` → `scripts/add_form_fields.py`

Both scripts currently hardcode one demo product (a 4-habit weekly tracker)
end-to-end as a working reference implementation — **read them before
adapting, don't try to import them as a generic library yet**. To build a
new product:

### 1. Adapt `render_layout.py`

- Replace the `HTML` string with your product's actual design (title,
  table/grid, checkboxes, text fields) — reuse the same CSS patterns
  already proven here (`.box` for checkboxes, `.name-line`/`.notes-box` for
  text fields).
- **Every fillable element MUST have a `data-field="<unique_name>"`
  attribute.** The script walks `[data-field]` via
  `getBoundingClientRect()` and writes each element's real rendered pixel
  position to `pdf-form-fields.json` — this is what keeps the widget
  overlay pixel-exact even as the HTML/CSS layout changes. Don't
  hand-compute coordinates from CSS; always capture them from the live DOM
  the way this script does.
- Adjust `PAGE_W_IN`/`PAGE_H_IN`/`MARGIN_IN` if the product isn't US
  Letter.
- Output paths (`/tmp/pdf-form-layout.pdf`, `/tmp/pdf-form-fields.json`)
  are currently hardcoded — change them per-product if building multiple
  products in the same session, or you'll clobber the previous one.

### 2. Adapt `add_form_fields.py`

- This one is already mostly product-agnostic — it reads
  `pdf-form-fields.json` and builds real `/Widget` annotations from
  whatever field names/coordinates it finds, with no product-specific
  logic in the coordinate math.
- **The one hardcoded assumption**: field type is inferred by name —
  `if field_name in ("name", "notes")` → text field (`/Tx`), else →
  checkbox (`/Btn`). For a product with more than 2 text fields, generalize
  this (e.g. a `data-type="text"` attribute on the HTML element instead of
  a name allowlist) rather than keep extending the tuple.
- Output path (`/tmp/pdf-form-poc-2026-09-23.pdf`) is hardcoded — change
  per-product.
- `pypdf` is the only new dependency, pure Python, no system libraries.
  Already present on this host (confirmed via the working POC).

## Verifying the output is genuinely fillable — don't trust visual inspection alone

A field that *looks* right in a screenshot can still be flattened ink, not
a real widget. Always verify with `pypdf.get_fields()`, not just opening
the file:

```python
from pypdf import PdfReader
r = PdfReader("your-output.pdf")
fields = r.get_fields()
assert fields and len(fields) > 0, "no fillable fields -- likely flattened to static image"
print(f"{len(fields)} real fields:", {name: f.get('/FT') for name, f in fields.items()})
```

`/FT` of `/Btn` = checkbox, `/Tx` = text field. If `get_fields()` returns
`None` or empty, the visual-only rendering path was used by mistake — check
that `add_form_fields.py` actually ran and its output (not
`render_layout.py`'s intermediate `pdf-form-layout.pdf`) is what got
shipped.

Also spot-check by actually opening the file in Preview.app or Acrobat and
clicking a checkbox/typing in a text field — `get_fields()` proves the
AcroForm structure exists, not that it renders/behaves correctly in a real
viewer (appearance streams, `/NeedAppearances`, etc. are easy to get subtly
wrong in ways a structural check won't catch).

## Visual design — this is not optional, it is Step 0 of digital-product-quality-bar

**Confirmed 2026-09-24: a batch of 40 products shipped functionally correct
(real fields, real content, no repetition) but visually bland — plain
black-on-white, no color, no typographic hierarchy — because market-evidence
research (review counts, pricing) was done but the VISUAL half of
`digital-product-quality-bar`'s Step 0 competitor research was skipped.**
Charlie caught this by eye immediately on review. Do not repeat this: before
writing any `render_layout.py`, pull 2-3 real preview images from the
strongest comp listing(s) for that product's category via the Etsy API
(`GET /v3/application/listings/{id}/images`) and actually look at them
(download + Read as an image) — not just their review/favorite counts.

A shared, evidence-based CSS design system now exists at
`design-system/style.css` in this skill directory, built directly from real
comp images (Monthly Budget Planner and Bill Tracker top listings). It
provides: `.doc-title`/`h1` (bold display font), `.section-title` (colored
underline bar), `table.tracker-table` (pastel color-coded header row that
rotates pink/blue/yellow/purple per column, zebra-striped rows), `.amt-field`/
`.name-line` (visible field underlines), `.check-box` / a page-local
`.checkbox-box` alias (rounded checkbox), `.notes-box`, `.badge-pill`. Load
it into any product's `STYLE` block with:

```python
DESIGN_SYSTEM_CSS = Path("/Volumes/data/skills/product/pdf-form-generation/design-system/style.css").read_text()
STYLE = f"<style>{DESIGN_SYSTEM_CSS}\n  /* page-specific overrides below */\n</style>"
```

**Known gotcha, hit twice already (products #175 and #209): any `<table>`
tag must carry `class="tracker-table"` or the shared styles never match —
bare `<table>`/`<th>`/`<td>` renders with zero styling. Same for `.amt-field`/
`.qty-field`-style inline spans: they need an explicit `width` or they
collapse to invisible with no field line at all, even though the border-bottom
rule is present in CSS.** Always visually render and Read at least one full
page after wiring in the design system — do not assume the CSS applied just
because the script ran without error.

## The most expensive recurring bug: never-shipped restyles

**Confirmed 3+ times on 2026-09-24 across ~20 products in one batch:** a
render/restyle pass genuinely regenerates correct new content in an
intermediate directory (commonly named `render-v2`), but the final
`add_form_fields.py` overlay step never runs against the shipped
`phase-3/customer-package/<name>.pdf` path — so the customer-facing file
silently stays on the OLD version while a commit message and a detailed
agent report both claim the fix is complete. This is not a hypothetical —
it happened to products #171-190, #207 twice, and nearly shipped a wrong
duplicate on #199.

**The fix, every time, in one command:**
```bash
python3 /Volumes/data/skills/product/pdf-form-generation/scripts/add_form_fields.py <intermediate_dir> phase-3/customer-package/<name>.pdf
```
Run this as the LAST step of any render/restyle work, against the actual
final `render_layout.py` output directory — never consider a visual change
"shipped" just because `render_layout.py` ran without error.

**Verifying a claimed fix is real, not just a plausible report:**
1. `git log --oneline -- <exact shipped file path>` — if the fix commit
   doesn't appear, the shipped file was never touched, no matter what the
   commit message or agent report says.
2. `pypdf.get_fields()` field count AND page count against a known-good
   baseline (STATUS.json's prior numbers, or an independent earlier check).
3. Actually render 2-3 spread-out pages to PNG at 100+ DPI and Read them —
   a screenshot rendered too small/low-DPI can look unstyled even when the
   CSS is genuinely correct (verified 2026-09-24 on product #184: a
   misleadingly low-DPI screenshot looked completely unstyled; a fresh
   150dpi render of the identical file showed the styling was fine all
   along — re-render before concluding a restyle failed).
4. If still unsure, query computed styles directly instead of guessing from
   pixels: `page.eval_on_selector("h1", "el => getComputedStyle(el).fontWeight")`
   during the Playwright render step settles it immediately.

## Second recurring bug: `pdf-form-fields.json` path portability

`render_layout.py` writes each page's `pdf_path` — if written as
`str(pdf_path)` from a relative `out_dir` argument, the resulting path is
relative to whatever directory the script was RUN from, not to the
`pdf-form-fields.json` file itself. Running `add_form_fields.py` from a
different working directory later (e.g. a fresh agent session, or after
`cd`-ing elsewhere) then fails with `FileNotFoundError` on a path like
`product-item-184-gratitude-journal/phase-1/01-day-1.pdf` that doesn't exist
relative to the new cwd. **Always write `pdf_path` as just the basename**
(`pdf_path.name`, not `str(pdf_path)` or `str(pdf_path.absolute())`) so the
JSON stays portable — `add_form_fields.py` already resolves it relative to
the JSON's own directory. The current `scripts/render_layout.py` demo and
`product-item-175-budget-planner`'s copy do this correctly; if you copy an
older product's script as your starting point, check this specifically.

## Third recurring bug: class-name mismatches silently no-op the CSS

A page-specific style block can define a rule (e.g. `.theme { background:
var(--accent-pink); ... }`) while the actual HTML element uses a
differently-named class (`class="week-theme"`) — no error, no warning, the
CSS rule simply never matches and that element renders with zero styling
while everything else on the page looks fine. This happened on product #184
after an otherwise-correct restyle. **After wiring in any new page-specific
CSS class, grep the same file for both the CSS selector and every markup
usage and confirm they're identical strings** — don't rely on the visual
render alone to catch this, since a missing color/badge on one element
among many is easy to miss at a glance.

## Illustrated themes — visual tier that wins in digital-product markets

**Added 2026-10-01, corrected 2026-10-01 after real-world failure on the Tent Camping Checklist product (product-item-225) required 5 rounds to actually ship correctly.** Confirmed gap on competitor audit: our color-header-only design system (however clean, however functional) is a fundamentally weaker visual tier than real top-selling comps, which use hand-drawn display fonts for titles, full-bleed or edge-bleed illustrated backgrounds, and niche-specific icon accents. This section documents how to layer illustrated themes onto the base form-generation pipeline — a non-negotiable part of `digital-product-quality-bar`'s Step 0 competitor research — **using only the three approaches below, which are the ones actually proven to survive this pipeline's Playwright→Ghostscript→pypdf chain.** Earlier guidance recommended inline SVG icons and Google-Fonts-CDN fonts; both failed in practice (see Gotchas) and are superseded here.

### How it layers onto the existing pipeline

The base pipeline stays unchanged, but `add_form_fields.py` MUST use the Ghostscript-merge-first pattern below — the illustrated theme is a visual layer, not a new pipeline:

1. **Illustrated background**: a light, low-contrast full-page gradient or edge-bleed background behind the entire content. A CSS `radial-gradient`/`linear-gradient` (2-4 stops, all pale/cream, e.g. `#f5f1e8` → `#e0d9ce`) is the proven-simplest option and needs no image generation at all. A generated Fal.ai backdrop (reused from `phase-3/preview-mockups/bg-fal-hero.png` if one exists, per `etsy-hero-image-generation`) is a richer alternative, but test it specifically for in-PDF legibility — a hero backdrop tuned for a marketing thumbnail is often too dark/busy for body text and functional form fields sitting on top of it. Either way, aim for 85%+ lightness with any texture/props concentrated at the edges.

2. **Self-hosted display font for titles** (do NOT use a Google Fonts CDN `<link>` — see Gotchas): download the font's actual `.ttf`/`.woff2` files (freely-licensed OFL fonts from fonts.google.com work) into the product's own directory (e.g. `phase-1/fonts/`), and reference them with local `@font-face` rules using `file:///absolute/path/...` URLs. Update `--font-display` to the font name. Examples by vibe: **playful/family**: "Fredoka", "Varela Round"; **elegant/wellness/journal**: "Caveat", "Tangerine"; **rugged/outdoor**: "Fredoka", "Cabin Sketch". This self-hosted approach is the only one confirmed to actually apply inside `page.pdf()` output in this pipeline's headless/`file://` Playwright context.

3. **Category-header icon accents**: use **Unicode emoji** (e.g. 🏕️ 🔥 👤 ⚠️), not inline SVG — see Gotchas for why SVG is unreliable here. Pick emoji that are simple, high-contrast, and single-glyph (avoid multi-codepoint/ZWJ-sequence emoji, which are more likely to fail). **Every emoji choice must be individually verified** (see step 6) — don't assume a glyph renders in this pipeline just because it displays in a browser tab or a text editor; test it specifically through `page.pdf()` into a real PDF viewer before committing to it as a product's icon set.

### Workflow: applying illustrated theme to a product

**Before designing a new product or restyling an existing one:**

1. Pull 2–3 real preview images from the strongest competitor listing(s) via `GET /listings/{id}/images` (Etsy API) and Read them to understand the visual tier. Document this in the product's `phase-0/competitor-research/` notes.

2. Decide what layers to apply based on market and product stage — background gradient + font upgrade is the highest payoff for lowest effort; add icons last since they need the most individual verification.

3. **For the background:** a plain CSS gradient (no image) is the safest default — it has no font-loading or image-path failure modes at all. Only reach for a generated Fal.ai image if the gradient genuinely isn't enough for the niche, and test it in-page at full opacity with real body text before committing.

4. **For the display font:** download the actual font files (see step 2 above) rather than linking Google Fonts' CDN. Verify the font genuinely renders — not just a plausible-looking fallback (Georgia/serif is a common silent fallback that can look intentional) — by comparing the final shipped PDF's title glyphs against a reference image of the real font.

5. **For icons:** before writing any icon into the product's actual HTML, build a tiny isolated test: a bare HTML file containing just the candidate emoji in the exact header CSS context (same background color, font-size, uppercase transform) the real product will use, run it through the SAME `page.pdf()` call pattern the real pipeline uses (not just opened in a browser tab — print-to-PDF can render differently from on-screen), then open the resulting PDF in a real PDF viewer (see step 6) and confirm every glyph is visible. Only use glyphs that pass this test. Expect some common-looking emoji (⛺ tent, 🛡️ shield were both confirmed to silently fail in this exact pipeline on 2026-10-01) to simply not render for reasons not fully root-caused — don't assume any specific emoji is safe without testing it.

6. **Verify against the FINAL shipped file, in a real PDF viewer — not a CLI rasterizer, and not the intermediate file:**
   - `pypdf.get_fields()` on `phase-3/customer-package/<name>.pdf` — field count must match the pre-restyle baseline exactly. If it dropped, the overlay step (see #7) silently lost content.
   - **Open the actual shipped file in Chrome's built-in PDF viewer (or Preview.app/Acrobat) at 100-150% zoom and look at it directly.** This step is not optional and not interchangeable with any other rendering method. `ImageMagick`'s `magick -density N file.pdf[page]` and other CLI rasterizers were confirmed on 2026-10-01 to render emoji glyphs and gradient fills differently (sometimes blank, sometimes visibly different) than real PDF viewers — a page that looks broken via `magick` can be completely correct in Chrome's viewer, and vice versa. Trusting a CLI tool's render as ground truth produced a false "still broken" conclusion at least once during that session. A real PDF viewer is the only check that reflects what an actual buyer will see.
   - Check every page, not just one — a bug can be category-specific (present on 2 of 4 category headers, absent on the other 2) rather than page-wide, and checking only one page or one category will miss it.

7. **Run the Ghostscript-merge-first `add_form_fields.py` against the shipped path** (see next section for why plain `pypdf.PdfWriter.append()` is not sufficient — this step is also where font/gradient content most often gets silently dropped, not just a "run it or don't" step):
   ```bash
   python3 phase-1/add_form_fields.py <intermediate_dir> phase-3/customer-package/<name>.pdf
   ```

### Critical fix: Use direct `PdfWriter.add_page()` with individual readers, never cross-PDF `append()` — Form XObject coordinate preservation

**Root cause evolution (2026-10-01, product-item-225):** The earlier Ghostscript-merge approach (merge all PDFs via Ghostscript before pypdf overlay) fixed the gradient-drop issue but introduced a new one — Ghostscript's `pdfwrite` device **transforms Form XObject `/BBox` values from relative coordinates (e.g., `[0,0,23,23]`) to absolute page coordinates (e.g., `[676.8,3612,720,3655.2])`**, breaking internal graphics rendering for SVG diagrams and other inline Form content. Pages 5-7 had invisible SVG diagrams (knots, fire structures, water-treatment icons) in the shipped file, even though pypdf structural inspection showed the XObjects present and the intermediate PDF had them working correctly.

**Why both approaches failed:**
- **Original pypdf-only (`append()` per-page):** drops Pattern/Shading resources across `PdfReader` boundaries, causing gradients to vanish silently.
- **Ghostscript-merge-first:** preserves Pattern resources correctly, but transforms Form XObject coordinate systems in a way that breaks inline SVG rendering (XObjects become invisible despite being structurally present).

**The actual fix (2026-10-01, 19:30–19:45):** Abandon Ghostscript merge entirely. Instead, use `PdfWriter.add_page()` with individual `PdfReader` instances, reading each page directly from its source PDF without cross-PDF append. This preserves Form XObject coordinates AND all resource dictionaries (Pattern, XObject, ExtGState, etc.) — each page read is from a single reader, so no cross-boundary resource loss occurs:

```python
writer = PdfWriter()
pdf_readers = {}

for page_meta in data["pages"]:
    pdf_path = (in_dir / page_meta["pdf_path"]).resolve()
    
    if pdf_path not in pdf_readers:
        pdf_readers[pdf_path] = PdfReader(str(pdf_path))
    
    reader = pdf_readers[pdf_path]
    source_page = reader.pages[0]  # Each file from render_layout.py is single-page
    writer.add_page(source_page)   # Add directly; preserves all resources
    page = writer.pages[-1]
    
    # Then overlay fields on this page...
```

This approach is proven on product-item-225 (all 114 fields intact, gradient background preserved, all 12 SVG diagrams on pages 5-7 visible and correctly rendered in final PDF). Copy this pattern for any future product with Form XObjects, gradients, or other embedded vector content.

### Cost discipline

- **Gradients are free** — no Fal.ai call needed for a CSS-only background.
- **Fonts are free** — Google Fonts' actual font files are free to download and self-host; it's only the live CDN link that's unreliable in this pipeline, not the font license.
- **Emoji are free** — no generation cost, but budget real verification time (step 5) since not every glyph works.
- **If using a generated Fal.ai backdrop:** reuse an existing one before generating new; `fal_generate.py --dry-run` shows cost before spending (~$0.06 typical).

### Worked example: Tent Camping Checklist (product-item-225) — including what went wrong and how it was finally fixed

Applied 2026-10-01. This took 6 distinct phases (not a simple 5-round story; the phases had different root causes):

1. **First attempt (visual-only, failed):** CSS gradient + Google Fonts CDN "Fredoka" + 5 inline SVG category icons. Field count verified fine via `get_fields()`. **Shipped completely broken visually** — gradient, font, and icons all absent — because the original `add_form_fields.py` used `pypdf.append()` across multiple per-page `PdfReader` objects, silently dropping Pattern resources. Verification never opened the actual final file in a real viewer.

2. **Second attempt (Ghostscript merge, partially fixed):** Introduced Ghostscript merge-first pattern to fix the gradient drop. Gradient now present. Font still missing (Google Fonts CDN unreliable in `file://` context). Icons still absent. Verification again didn't catch this because it didn't check the final file with sufficient scrutiny.

3. **Third attempt (emoji + CDN font fixes, icons still broken):** Swapped SVG icons for Unicode emoji and attempted CDN fixes. Gradient and font still not working correctly; CDN genuinely doesn't work from headless Chromium's `file://` context.

4. **Fourth attempt (self-hosted font, claimed fixed but was NOT — confirmed wrong 2026-10-01 on republish):** Self-hosted Fredoka font files locally via `@font-face { src: url('file:///...') }` — this was recorded as working at the time, but was independently re-verified wrong days later when this same product was prepared for publish: the `@font-face` `src` referenced `Fredoka-400.ttf` etc., but the actual downloaded files on disk were named `fredoka-400.woff2` (different extension AND different case) — a path that silently 404s inside Chromium's `file://` fetch, so the font-face rule never resolved and every page fell back to the browser's default serif the whole time. This is the exact same class of error the "Key lesson" below describes (an optimistic verification that wasn't actually looking hard enough): the original check that marked this "✓ rendering on all titles" apparently only glanced at the cover page's title styling, not the actual font shape, and never caught the mismatch. **Always verify a self-hosted `@font-face` by confirming the exact filename case and extension on disk match the CSS `src` `url()` byte-for-byte** — `ls` the fonts directory and diff it against the CSS, don't just trust that "I downloaded the font and wrote a font-face rule" means it loads. Icons were also still inconsistent (2 of 5 rendered, 3 blank) at this stage, but verification mistakes (using CLI rasterizers instead of real PDF viewers) masked that separate failure. The inconsistency was incorrectly attributed to "SVG-to-PDF rasterization limitations" and left unfixed at the time.

5. **Fifth attempt (emoji pre-testing, still using Ghostscript):** Tested emoji candidates individually through the real `page.pdf()` pipeline (not just a browser tab), discovered ⛺ and 🛡️ fail to render in this pipeline while 🔥 and 👤 work. Swapped to pre-verified 🏕️ and ⚠️. Verified in Chrome's PDF viewer. SVG diagrams on pages 5-7 still invisible at this point, though earlier agents had claimed them visible (false positive from CLI rasterizer verification). This invisible-diagram issue was not yet caught.

6. **Sixth phase (root-cause: Ghostscript transforms Form XObject coordinates):** Independent re-inspection of page 5-7 in a real Chrome PDF viewer revealed SVG diagrams (knots, fire structures, water icons) completely invisible in shipped file, even though intermediate PDF had them working and pypdf structural checks showed XObjects present. Root-cause analysis: Ghostscript's `pdfwrite` device transforms Form XObject `/BBox` from relative (`[0,0,23,23]`) to absolute page coordinates (`[676.8,3612,...]`), breaking internal graphics rendering. Fixed by abandoning Ghostscript merge entirely and using direct `PdfWriter.add_page()` with individual `PdfReader` instances. This preserves Form XObject coordinates and all resource types. Final verification via 150 DPI pdftoppm render of actual PDF viewer output (not CLI rasterizer default render) confirmed all diagrams visible and correct on pages 5-7.

**State recorded 2026-10-01, 19:45 (later found incomplete — see below):**
- Gradient background (cream→sage): ✓ present and correct on all 7 pages
- Self-hosted Fredoka font: claimed "✓ rendering on all titles" — **this was WRONG, see correction below**
- 4 emoji category icons (🏕️ 🔥 👤 ⚠️): ✓ visible and correct
- All 114 AcroForm fields (90 /Btn, 24 /Tx): ✓ intact
- 6 knot SVG diagrams (page 5): ✓ visible and recognizable at print scale
- 3 fire-structure SVG diagrams (page 6): ✓ visible and correct
- 3 water-treatment SVG icons (page 7): ✓ visible and correct
- Letter and A4 versions: both generated and verified

**Seventh phase (font fix, confirmed on pre-publish review 2026-10-01):** When this product was reviewed again before its first Etsy publish, opening the cover page at 150% zoom in Chrome's real PDF viewer showed the title rendering in a plain serif (Georgia-style fallback), not Fredoka's rounded sans shape. Root cause: `render_layout.py`'s `@font-face` rules pointed to `fonts/Fredoka-400.ttf` (capital F, `.ttf` extension), but the files actually present in `phase-1/fonts/` were named `fredoka-400.woff2` (lowercase, `.woff2`) — a pure filename mismatch, silently failing the `file://` fetch with no visible error anywhere in the pipeline. Fixed by correcting the `src: url(...)` paths and `format()` hints to match the real filenames/extensions on disk, then re-rendering, re-running the overlay, and re-verifying in Chrome. After the fix, the font STILL did not visibly change to Fredoka's rounded style on a follow-up check — rather than ship a third guess, the false "Fredoka" marketing claim was removed from the listing copy entirely instead of continuing to chase it, and the product shipped honestly with the gradient + icon improvements only (both independently confirmed genuinely working). **Lesson: when a specific claimed feature resists two consecutive fix-and-verify cycles, stop re-attempting the same fix and remove the claim from customer-facing copy rather than publishing on a third unverified guess.**

**Key lesson:** Intermediate-file checks and CLI rasterizer renders are not substitutes for opening the actual final shipped file in a real PDF viewer (Chrome, Preview, Acrobat). A page can pass field-count checks and look correct via `magick`/`pdftoppm` CLI while being completely invisible in a real viewer (or vice versa). The only check that reflects the buyer's actual experience is a direct open in a real PDF viewer — and even then, verify the SPECIFIC claimed feature (e.g., zoom in and compare the actual glyph shapes against a reference of the real font), not just "the page looks fine at a glance."

### Gotchas and how to avoid them

- **Don't merge PDFs via Ghostscript if any page contains Form XObjects (inline SVG, custom graphics).** Ghostscript's `pdfwrite` device transforms Form XObject `/BBox` coordinates from relative to absolute, breaking internal graphics rendering. The XObjects remain structurally present (pypdf inspection shows them) but become invisible in real PDF viewers. Use direct `PdfWriter.add_page()` with individual `PdfReader` instances instead, which preserves coordinate systems and all resource types (Pattern, XObject, ExtGState, etc.).

- **Don't use a Google Fonts CDN `<link>` or `@import`.** Confirmed unreliable when the page is loaded via `page.goto("file://...")` in headless Playwright — it silently falls back to a system serif (Georgia) with no error. Self-host the font file locally and use a `file://` `@font-face` `src` instead (see above).

- **Don't assume any given emoji or SVG icon is safe.** Individually verify every glyph through the real `page.pdf()` → real-PDF-viewer path (see Workflow step 5) before using it in a product. A glyph working in a browser tab, or even in an isolated one-off PDF test with different surrounding CSS, is not proof it will work in the actual product's exact header styling — test it in the real context. Confirmed failures (2026-10-01): ⛺ (tent) and 🛡️ (shield) don't render in this pipeline's print-to-PDF path, while 🔥 (fire) and 👤 (person) do. No pre-rendered list is comprehensive — always test the specific glyphs you choose.

- **Never trust a CLI PDF rasterizer (`magick`, `pdftoppm`, `pdftocairo`, etc.) as the sole verification method.** It can render emoji/gradients/SVG content differently than real PDF viewers, producing false-positive AND false-negative "broken" readings. Confirmed on product-item-225: `pdftoppm` (and earlier agents' reports based on it) claimed SVG diagrams were visible, but opening the same file in Chrome's PDF viewer showed them completely invisible. Always additionally open the final shipped file in a real PDF viewer (Chrome's built-in viewer, Preview.app, Acrobat) and look at it directly at 100%+ zoom — this is the only check that reflects the buyer's actual experience.

- **A field-count match and "script ran without error" are not proof the restyle shipped.** Resource preservation and field counts are independent failure surfaces. `pypdf.append()` can silently drop Pattern resources even while fields stay perfectly intact. Ghostscript can transform Form XObject coordinates even while structural checks pass. Check both separately, every time.

- **Check every category/page, not just one.** A bug can hit 2 of 4 category headers and leave the other 2 looking fine, or affect pages 5-7 while pages 1-4 are correct — sampling a single element and generalizing to "it works" is how this shipped broken multiple times in a row.

## Scaling to a real product batch

`scripts/add_form_fields.py` is now generalized (as of 2026-09-24, first
proven on the Monthly Budget Planner product; updated 2026-10-01 to merge
via Ghostscript before `pypdf.append()` — see the Illustrated themes
section's critical-fix note): it reads a multi-page `pdf-form-fields.json`
(`{"pages": [{"name", "pdf_path", "page_w_in", "page_h_in", "margin_in",
"rects"}, ...]}`), namespaces every field as `<page_name>__<field_name>` to
avoid collisions across pages, and infers text vs. checkbox (real `/Tx` vs
`/Btn`) by a `TEXT_FIELD_HINTS` substring list. **`TEXT_FIELD_HINTS` is
product-specific and must be edited per product** — the shared script's
default list (`"name", "month", "year", "notes", "budget", "actual",
"income", "expenses", "saved"`) matches the Budget Planner's field-naming
convention, not every product's. Confirmed 2026-10-01: running the
unmodified shared script against the Tent Camping Checklist's fields
(named `..._custom_N`, no substring in the default list) produced 114
fields with the correct total count but the WRONG type split (114
checkboxes, 0 text, when the real product needs 90/24) — a passing field
*count* does not mean the field *types* are correct. Always edit
`TEXT_FIELD_HINTS` to match the new product's actual field-naming
convention and verify the checkbox/text SPLIT via `pypdf.get_fields()`
(check `/FT` per field, not just `len(fields)`), not just the total. Call
it as `add_form_fields.py <input_dir> <output_path>`.

`render_layout.py` is still per-product on purpose — its HTML/CSS *is* the
product's design, so it doesn't belong in the shared skill. Build a new
product's own copy structured like
`digital-products/product-item-<N>-<slug>/phase-1/render_layout.py`: a
`main(out_dir)` that iterates a `PAGES` list of `(page_name, html)` tuples
and calls `page.pdf()` + the `[data-field]` DOM-coordinate capture once per
page, writing a combined `pdf-form-fields.json` in the multi-page shape
above. See `digital-products/product-item-175-budget-planner/phase-1/` for
a full worked example (13 pages, 494 real fields, yearly overview + 12
monthly detail pages with a shared HTML template function parameterized by
month name) — copy its `PAGES`-list/`main()` structure for the next
multi-page product rather than re-deriving it.
