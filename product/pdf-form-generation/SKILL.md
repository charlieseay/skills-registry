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

## Scaling to a real product batch

`scripts/add_form_fields.py` is now generalized (as of 2026-09-24, first
proven on the Monthly Budget Planner product): it reads a multi-page
`pdf-form-fields.json` (`{"pages": [{"name", "pdf_path", "page_w_in",
"page_h_in", "margin_in", "rects"}, ...]}`), namespaces every field as
`<page_name>__<field_name>` to avoid collisions across pages, and infers
text vs. checkbox by a `TEXT_FIELD_HINTS` substring list instead of a fixed
2-name allowlist — extend that list (or add a real `/Btn` branch back) for a
product with checkboxes. Call it as `add_form_fields.py <input_dir>
<output_path>`.

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
