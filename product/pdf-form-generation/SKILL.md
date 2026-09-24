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

## Scaling to a real product batch

For a genuine multi-item product (not a single demo page), generalize
`render_layout.py` to accept the HTML/CSS as a parameter (a template
function, not a hardcoded string) and loop it per page, and
`add_form_fields.py` to accept input/output paths as parameters instead of
hardcoded `/tmp/...` paths — neither script does this yet as of
2026-09-24. Whoever builds the first real multi-page product with this
pipeline should do that generalization as part of the build, and update
this skill's scripts/ with the parameterized versions rather than leaving
per-product copies scattered in /tmp.
