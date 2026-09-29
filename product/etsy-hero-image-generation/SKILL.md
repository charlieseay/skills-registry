---
name: "etsy-hero-image-generation"
description: "Produce styled Etsy listing images for a digital product (hero/title card, \"what's included\" infographic, icon badges) and swap them onto a LIVE listing so the new hero is what buyers see first. Uses one cheap Fal.ai generation per product for a text-free styled backdrop, then composites the real product pages, exact title text and badges deterministically with PIL, so nothing is misspelled and the hero shows the actual deliverable. Use this whenever a listing's preview images are flat screenshots, a competitor audit says our hero lacks a title/badges/infographic, a product is about to publish and needs its image set, or you need to replace/reorder the first image on an Etsy listing. Do not ask an image model to render the product name or claims, and do not upload a hero without reading the rank/tie quirks below."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["digital-product-quality-bar", "etsy-api", "etsy-catalog-triage", "talos-product-launch-audit", "product-quality-verify"]
---

# Etsy Hero Image Generation

**Fleet-wide skill.** Plain Python + two REST APIs (Fal.ai, Etsy v3). Every
step writes a file you can look at, or makes an API call you then verify
with a re-fetch. No step depends on a specific agent runtime.

## Why this exists

On 2026-09-29 a competitor audit of all 11 live listings found the same
structural gap on every one of them: our preview images were flat
screenshots of the PDF pages, with no title card, no "what's included"
image, no Fillable/Instant Download/Print-Ready badges and no styling.
Competitors in the same searches lead with a designed hero (branded
background, big product name, tagline, page-count badge) and only then show
the pages. A buyer scrolling search results sees one thumbnail. If that
thumbnail is a gray screenshot with no product name on it, the listing loses
before copy or price matter. (Per-listing evidence is in
`talos-tools/digital-products/<product>/phase-3/competitor-audit-2026-09-29.md`.)

`digital-product-quality-bar` states the requirement (5-10 images, a styled
hero, an infographic, badges, 2000px minimum). Before this skill nothing
said how to produce those images or how to get them onto a live listing in
the right order. This skill covers the how.

## Cost: know it before you generate (observed 2026-09-29)

Budget context: Charlie has roughly **$20/month of Fal.ai credit**. Treat it
as tight.

Live prices from Fal's own pricing API (`GET https://api.fal.ai/v1/models/pricing?endpoint_id=<model>`,
same `Authorization: Key` header). **Re-query before a batch; don't trust this table blindly:**

| Model | Unit price | 1536x1536 (2.36MP) | Use |
|---|---|---|---|
| `fal-ai/flux/schnell` | $0.003 / MP | **$0.007** | drafts, prompt checks |
| `fal-ai/flux/dev` | $0.025 / MP | **$0.059** | **default for backdrops** |
| `fal-ai/flux-pro/v1.1` | $0.04 / MP | $0.094 | only if dev clearly fails |
| `fal-ai/ideogram/v3` | $0.03 / image | $0.03 | text-in-image (we don't need it, see below) |
| `fal-ai/recraft/v3/text-to-image` | $0.04 / image | $0.04 | vector/illustration styles |

**Actual 2026-09-29 batch:** 3 products → 3 flux/dev generations at
1536x1536 = **$0.177 total** ($0.059 each), 0 retries. All three backdrops were
usable on the first try with the prompt pattern below. One backdrop served both
the hero and the infographic for its product, so the batch needed 3 generations,
not 6.

**Budget rules:**
- **One generation per product.** Reuse the backdrop for hero + infographic
  (that also gives you the consistent palette the quality bar requires).
- **Always `--dry-run` first.** `fal_generate.py` prints the live price and the
  estimated cost and exits without spending anything.
- `--max-cost` (default $0.10) makes the script refuse any single call above the cap.
- Never loop regenerate-until-good. If a backdrop fails, fix the prompt once
  (usually a prop landing in the center), regenerate once, and stop there.
  A 3-product batch should never cost more than ~$0.40.
- Every paid call is appended to `~/.local/share/fal-spend.jsonl` (model,
  size, est_cost, seed, prompt, output path), so a batch can be audited later.

## The architecture: AI paints the room, code places the product

Diffusion models misspell text and invent product details. The quality bar
also requires the hero to show **the actual product**. So we split the job:

1. **Fal.ai generates only a text-free styled backdrop**: a flat-lay
   surface in the product's palette, with props at the edges and an empty
   center.
2. **`compose_listing_image.py` composites on top of it:** the real rendered
   product pages (from the deliverable PDFs/PNGs), the product title, the
   tagline, badge pills and a round count seal, all set in real fonts, so the
   spelling and the numbers are exactly what we typed.

This is also why no text-capable model (ideogram/recraft) is needed:
anything a buyer reads is typeset, never generated.

**About `claude-config/bin/composite-service` (port 3601):** it does **not**
call Fal.ai. It is a small logo-overlay HTTP service: it takes an
already-generated `image_url` plus a `logo_url` and pastes the logo in a
corner. It has **no badge or text capability**, so badges live in
`compose_listing_image.py` instead. The working Fal.ai call pattern in this
codebase actually comes from the n8n "Content Image Generator" workflow
(`/Volumes/data/containers/n8n/backups/workflows/Content_Image_Generator__*.json`):
`POST https://fal.run/<model>`, header `Authorization: Key <key>`.
`fal_generate.py` uses exactly that. The CMDB service entry is `fal-ai`
(host `fal.run`).

## Scripts (in `scripts/`)

| Script | Does |
|---|---|
| `fal_generate.py` | live price check → cost cap → `POST https://fal.run/<model>` → downloads the PNG → logs spend |
| `compose_listing_image.py spec.json` | builds a 3000x3000 JPG hero (`layout: hero`) or infographic (`layout: grid`) from a JSON spec |
| `etsy_images.py list/upload/delete/hero` | Etsy image operations, each followed by a re-fetch; `hero` = safe hero replacement |

Key: `/Volumes/data/secrets/content_studio_fal_api_key` (the same key is also in
`n8n_fal_api_key`). Etsy auth reuses listing-bot's OAuth module per `etsy-api`.
Fonts: macOS `Avenir Next.ttc` (Heavy for titles, Demi for badges, Medium for body).

## Step-by-step for one product

### 0. Read before you make anything
- The product's `phase-3/competitor-audit-*.md`, if one exists. It says what
  the comps lead with.
- **Pull the listing's live state now**, not from a snapshot:
  `etsy_images.py list <listing_id>` plus `GET /listings/<id>`. On 2026-09-29
  two of three titles had already been changed by hand since the audit.
- **Verify every claim you plan to put on an image against the deliverable
  files, not the listing copy or README.** Page count and field count come
  from `pypdf` (`len(reader.pages)`, `len(reader.get_fields())`); page size
  comes from the PDF mediabox. The 2026-09-29 batch caught a README saying
  "letter-size (8.5x11)" for PDFs that are actually 1500x1500pt squares.
  That claim was kept off the image.

### 1. Render the real product pages
```python
import fitz  # PyMuPDF
doc = fitz.open("customer-package/print-pack/Binder-US-Letter.pdf")
for i, page in enumerate(doc):
    page.get_pixmap(dpi=160).save(f"preview-mockups/_pages/letter-{i+1:02d}.png")
```
For a fillable product, fill a **copy** with example data before rendering
(`w.field_value = ...; w.update()` on `page.widgets()`). A partly-filled page
sells the product better than a blank one. Check the widget types first: the
52-week tracker's "checkboxes" are actually Text fields, so they take `"X"`,
not a checkbox on-state.

### 2. Backdrop prompt pattern (the only paid step)
```
Overhead flat lay product photography backdrop. A <surface in palette color>
fills the frame. Props only along the outer edges and corners: <3-5 props that
signal the niche, each with a position: "in the top-left corner", "at the right
edge", "partly out of frame bottom-right">. The entire center of the frame is
empty bare <surface>. <light: soft diffused window light | warm golden afternoon
light>, gentle shadows, <mood>, <3-4 palette colors> palette, professional Etsy
product photography, sharp focus. No paper, no documents, no text, no letters,
no numbers, no labels, no logos.
```
Why each clause is there:
- **"Props only along the outer edges" + "entire center empty"**: the pages
  and the title panel cover the center and the top ~30%. Props in the middle
  get buried or collide with the pages.
- **"No paper, no documents"**: otherwise the model draws its own fake planner
  pages, which then compete with the real product.
- **"No text / letters / labels / logos"**: flux still sometimes adds gibberish
  text on props (the 2026-09-29 wine backdrop put garbled text on a cork).
  Keep text-bearing props (corks, bottles, books) in the top band, where the
  title panel covers them, or leave them out.
- Palette words matter more than props. Match the product's existing brand
  colors, or the niche's visual language from the comp audit: pastel
  sage/blush for savings trackers, cream/navy/brick-red for emergency prep,
  terracotta/burgundy/olive for wine and travel.

Worked prompts that succeeded first try are logged in `~/.local/share/fal-spend.jsonl`.

```bash
S=/Volumes/data/skills/product/etsy-hero-image-generation/scripts
python3 $S/fal_generate.py --dry-run --prompt "..." --out preview-mockups/bg-fal-hero.png
python3 $S/fal_generate.py --prompt "..." --out preview-mockups/bg-fal-hero.png
```
Then **open the PNG and look at it** before compositing.

### 3. Hero (title card) spec
The pattern every winning comp shared in the 2026-09-29 audits: product name
in big type on image 1, a one-line benefit tagline, a count badge, and a spec
line or badge row, all in front of the actual pages.

```json
{"out": "hero-styled-01.jpg", "background": "bg-fal-hero.png", "layout": "hero",
 "palette": {"primary": "#1f3a5f", "accent": "#b8412e", "ink": "#1c2430", "panel": "#fdf9f1"},
 "title": ["FAMILY EMERGENCY", "BINDER"],
 "tagline": "Contacts, medical info and evacuation plans in one grab-and-go binder",
 "pages": ["_pages/letter-04.png", "_pages/letter-05.png", "_pages/letter-01.png",
           "_pages/letter-07.png", "_pages/letter-12.png"],
 "page_mode": "fan", "spread": 1500, "fan_angle": 22,
 "badges": ["FILLABLE + PRINTABLE", "US LETTER + A4", "INSTANT DOWNLOAD"],
 "seal": ["16", "PAGES", "290 FIELDS"], "seal_pos": [2600, 1290]}
```
- `title`: 1-2 lines. The last line is drawn larger in `primary`. Use the
  buyer's search phrase ("52 WEEK / SAVINGS CHALLENGE"), not an instruction
  ("FILL IT IN ON YOUR TABLET" was our old hero, which never named the product).
- `page_mode`: `single` for a 1-page product (add `"angle": -3` for a casual
  tilt), `fan` for 3-5 pages. Comps use a fan to show volume at a glance.
  `page_border: 30` adds a white paper edge to art that runs to the page edge
  (coloring pages).
- `seal`: the single most repeated comp element was a page/field-count badge.
  Use the biggest *true* number: "16 PAGES", "54 FILLABLE FIELDS", "6 DESIGNS".
- `panel_margin`: widen the title panel (default 150; use 70) to cover a
  text-bearing prop at the top edge.
- **Seal placement:** keep `seal_pos` y at least ~300px below the panel
  bottom, or it covers the end of the tagline (happened on the first
  2026-09-29 render). Always look at the output.

### 4. "What's included" infographic spec (`layout: grid`)
Same backdrop, frosted over so dense text stays readable. Cards in a grid,
each with a colored header band, a real page thumbnail and bullets:
```json
{"out": "whats-inside-styled-02.jpg", "background": "bg-fal-hero.png", "layout": "grid", "cols": 3,
 "title": ["WHAT'S INSIDE"], "tagline": "16 binder pages in 5 sections, plus print extras",
 "cards": [{"title": "MEDICAL", "color": "#c0392b", "thumb": "_pages/letter-05.png",
            "items": ["Medical info per person", "Allergies + medications"], "thumb_ratio": 0.46}],
 "footer": "290 fillable fields  |  US Letter + A4 print PDFs  |  Instant download"}
```
- For a multi-section product, group the pages into 4-6 **color-coded
  categories**. The best emergency-binder comp did exactly this, and it reads
  as "organized system". Keep the claim honest: say "5 sections", not
  "color-coded pages", unless the PDF itself is color-coded.
- For a design pack (coloring pages, clipart), use one card per design with
  `thumb` + `caption` and no header band, then put formats in the footer.
- With 4 bullets and a thumbnail, use `thumb_ratio` ~0.46 or the last bullet
  overflows the card (another first-render bug from 2026-09-29).
- Skip the infographic if the listing already has a good one. The 52-week
  tracker's existing "WHAT YOU GET" card was better than any comp's, so we
  kept it and spent nothing.

### 5. Badges
Badges are the `badges` pill row and the `seal` in the hero spec. There is no
separate overlay step. Standard vocabulary, **only when true for this product**:
`FILLABLE PDF`, `PRINTABLE`, `FILLABLE + PRINTABLE`, `INSTANT DOWNLOAD`,
`PRINT-READY`, `US LETTER + A4`, `PNG FOR TABLETS`, `GOODNOTES READY`.
Use 3 pills. More than 3 shrinks the type below thumbnail legibility.

### 6. Check the output against the quality bar before uploading
- [ ] 3000x3000 (the compositor always outputs this; the Etsy minimum is 2000, 3000 is preferred), JPEG under 3MB, no watermark
- [ ] Every number/claim on the image matches the deliverable (step 0)
- [ ] Nothing overlaps: seal vs tagline, bullets vs card edge, pages vs badges
- [ ] Downscale to 570px (the search-thumbnail size) and confirm the title still reads
- [ ] Hero and infographic share the palette/fonts with each other

## Putting it on the live listing (read `etsy-api` first)

```bash
S=/Volumes/data/skills/product/etsy-hero-image-generation/scripts
# find a local copy of the CURRENT hero first, so it can be kept, not lost
python3 $S/etsy_images.py hero <listing_id> hero-styled-01.jpg \
    --keep-old-as-last <local copy of current hero> --alt "<buyer-readable description>"
python3 $S/etsy_images.py upload <listing_id> whats-included-styled-02.jpg --rank 2 --alt "..."
python3 $S/etsy_images.py list <listing_id>
```
`hero` does: record the current rank-1 id → upload the new image with
`rank=1` → confirm it appears in `GET /listings/{id}/images` → `DELETE
/shops/{shop_id}/listings/{id}/images/{old_id}` (204) → re-fetch and assert
the new id is first → optionally re-upload the old hero at the explicit last
rank, so its content isn't lost. It exits non-zero at the first step that
doesn't verify.

To find the local file behind a live image: download its `url_570xN` and
compare it against the candidates in `phase-3/preview-mockups/` with a
128x128 grayscale mean-difference. Under 2 is a match. (All three 2026-09-29
heroes matched a local file at 0.3-1.5.)

### Etsy image-order quirks confirmed live 2026-09-29
These extend `etsy-api`'s "Replacing the hero" section:
1. **`rank` on `POST .../images` is honored, and it defaults to 1.** An upload
   *without* an explicit rank lands at rank 1 and ties with the hero. This is
   the real cause of the "old and new both show rank 1" behavior `etsy-api`
   describes. Always pass `rank` explicitly: `1` for a new hero,
   `len(images)+1` for "append at end".
2. **A mid-list rank ties rather than inserting.** Uploading at `rank=2`
   produced two images at rank 2. Nothing below it shifted.
3. **Ties are served in ascending `listing_image_id` order** (checked via
   `GET /listings/{id}?includes=Images`, which is the order buyers get). A newly
   uploaded image does not always get a higher id than older ones, so after
   any tie, check the served order. To force a new image into slot N: delete
   the current slot-N image and re-upload it at the end with an explicit rank.
4. **More than 10 images is accepted.** A listing went to 12 images without
   error (comps show up to 19-20). The 10-image number in older notes is not
   Etsy's current limit.
5. `DELETE /shops/{shop_id}/listings/{listing_id}/images/{listing_image_id}`
   returns 204 and the delete applies. The re-fetch confirmed it every time.

### Verification: what counts as done
- `GET /listings/{id}?includes=Images`: the first image is the new id at
  3000x3000, the old hero id is absent, and the count is what you expect.
- Download the first image's `url_570xN` and **look at it**. That is the
  thumbnail a buyer sees in search.
- For any tag/title change made at the same time: re-GET the listing and
  compare it to the target list. A 200 on the PATCH doesn't prove the change
  landed (see `etsy-api`'s price incident). Save the old values to
  `phase-3/tag_backup_<date>.json` before patching.

## 2026-09-29 batch (first use), for reference

| Product | Listing | Generated | Live result |
|---|---|---|---|
| 52 Week Savings Tracker (181) | 4582643427 | hero (single filled page, sage/blush, 54-field seal) | 6 images, new hero first; old tablet hero kept at rank 6 |
| Family Emergency Binder (221) | 4584396043 | hero (5-page fan, 16-page/290-field seal) + color-coded 6-card "What's inside" | 12 images: hero, infographic, rest; old flat hero moved to 11 |
| Travel & Wine Coloring (177) | 4581333085 | hero (3-page fan, 6-designs seal) + 6-design "What's included" | 9 images: hero, infographic, rest; old cellar hero kept at 9 |

Fal spend: $0.177 total. Specs and outputs are in each product's
`phase-3/preview-mockups/` (`bg-fal-hero.png`, `hero-spec.json`,
`hero-styled-01.jpg`, `*-spec.json`, `*-styled-02.jpg`). Copy a spec as the
starting point for the next product in the same category.
