---
name: "etsy-preview-quality"
description: "Close the visual gap between our Etsy listing images and the ones that actually win a category — pull real competitor comps via the Etsy public search API, LOOK at their hero images, and composite a competitive hero for free with Playwright + PIL (no Fal.ai spend). Use whenever a listing has 0-few views, when Charlie says our products look cheap/Playskool next to competitors, before publishing any new digital product, or when a listing's previews are flat screenshots of document pages. Covers the four specific things winning listings do that flat screenshots do not."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["digital-product-quality-bar", "etsy-hero-image-generation", "etsy-api", "etsy-catalog-triage"]
---

# Etsy Preview Quality

**Fleet-wide. Zero cost.** Playwright + PIL + the Etsy API. No paid image models.

## Why this exists

2026-10-14: Charlie said our Etsy products look "Playschool" while competitors
ship "Mercedes." That was correct and the gap turned out to be purely
presentational — not content, not copy. Our resume bundle had 15 genuinely
ATS-sound templates and a 4,444-char description (longer than the $10.19
category winner's 1,357) and still had 0 views.

## Step 1 — pull REAL comps (the API does this, no scraping)

Etsy blocks scraping (DataDome) but the authenticated **public search** works:

```python
import sys, json, urllib.parse, urllib.request
sys.path.insert(0, "/Volumes/data/projects/listing-bot/src")
from platforms.etsy_oauth import get_valid_access_token
cid = open("/Volumes/data/secrets/etsy-api-key").read().strip()
csec = open("/Volumes/data/secrets/etsy-api-secret").read().strip()
H = {"x-api-key": f"{cid}:{csec}", "Authorization": f"Bearer {get_valid_access_token(cid)}"}
u = "https://openapi.etsy.com/v3/application/listings/active?" + urllib.parse.urlencode(
    {"keywords": "<the buyer's phrase>", "limit": 20, "sort_on": "score"})
d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
# each result carries: listing_id, price, views, num_favorers
```

Then `GET /listings/{id}/images`, download `url_fullxfull`, and **actually Read
the image**. Counting images does not reveal the gap; looking does.

Skip comps with 0 reviews and 0 favorites — those are struggling listings, not
proof of anything.

## Step 2 — the four things winners do

Verified against two independent category winners (4,412 views/119 favs at
$10.19, and 4,039 views/152 favs at $2.99):

1. **A styled backdrop with depth.** Textured wood/stone/linen or a layered
   studio background. The page sits ON a surface, with a drop shadow and a
   slight rotation. It reads as a product photo, not a screenshot.
2. **Previews are FILLED IN with realistic content.** A named person
   ("Caroline Hamilton", "Whitney West"), real companies, real sentences,
   real dates. **Never show `[Your Full Name]` or `[Company Name]` in a
   preview image** — bracketed placeholders make a finished product look like
   an unfinished wireframe. Keep the brackets in the DELIVERABLE, not the photo.
3. **A designed badge or seal.** An embossed/foil "ATS Friendly" circle with
   format icons. The key benefit as a GRAPHIC, not as body text.
4. **A benefit bar.** A dark strip with the counts: layouts, variants, extras.

## Step 3 — build it free

- Fill a COPY of the templates with realistic sample content (regex-replace the
  placeholders). Never modify the shipped deliverable.
- Screenshot with Playwright at `device_scale_factor=3`, then crop to the top
  ~60% — document templates have large empty lower halves that waste the frame.
- Composite with PIL: generated linen/vignette backdrop, rotate each card,
  render a real blurred shadow per card, then title / seal / benefit bar.
- 2000x2000. Verify by READING the rendered PNG before upload — layout bugs
  (title overlapping a card, cards cropping off-canvas) are invisible in code.

## Step 4 — price against the comps

Pull the comps' prices before pricing. Our resume bundle sat at $18.99 while
the entire winning set was $2.99-$10.19 — above every winner, with 0 reviews.
Note the $2.99 listing had MORE favorites than the $10.19 one: these categories
are won on conversion and volume, not on price anchoring.

## Step 5 — upload

```python
from platforms.etsy_shop import EtsyShop
EtsyShop().replace_hero(lid, "hero.png", alt="...")   # uploads rank=1, verifies
```

## Gotchas

- Run with plain `python3`, NOT `python3 -I` (PIL/playwright are in user site-packages).
- `pandoc` strips CSS: HTML->docx variants come out byte-identical. Re-apply
  colors with python-docx and hash-check before packaging.
- Use realistic but clearly fictional sample people. Never a real person's name,
  likeness or employer.

## The generator (added 2026-10-14)

`talos-tools/digital-products/tools/build_hero.py` implements this skill's
section 3 as a reusable tool. Pillow only, zero cost.

```bash
python3 tools/build_hero.py --spec spec.json --pages pages/<listing_id>/ --out hero.png
```

Per-listing config for the live catalogue is in `tools/hero-specs.json`:
```json
{"4582643427": {"title":"52 WEEK","title2":"SAVINGS TRACKER",
  "sub":"Save $1,750 in a Year  ·  Print & Tick",
  "bg":[240,234,240],"band":[66,46,96],"seal_color":[128,88,168],
  "seal_big":"52","seal_mid":"WEEKS","seal_small":"$1,750 GOAL",
  "bar":"WEEKLY AMOUNTS · RUNNING TOTAL · CHECKBOXES"}}
```

Source the `--pages` directory from the LISTING BEING BUILT, via
`EtsyShop().images(lid)` → download `url_fullxfull`. The whole catalogue can be
regenerated in a loop.

### Two layout traps this tool already handles
- **Square sources blow up the centre card.** A 1:1 listing image scales far
  taller than the portrait page screenshots the fan was tuned for, and the
  centre card ends up covering the subtitle. Height is clamped to 760px and
  every card is pushed clear of the title plate (which ends at y=470).
- **Long titles collide.** Title font size steps down by length (126 / 104 /
  84), and the second line steps separately. Check any title over ~17 chars.

### Always LOOK before uploading
Build a 2x2 or 3x2 contact sheet of the rendered heroes and read it. The
square-source bug above was invisible in code and obvious in one glance — the
first batch of 21 shipped with the "25 FONTS" subtitle completely covered.
