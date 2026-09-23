---
name: "etsy-gumroad-reprice-seo"
description: "Reprice a batch of Etsy/Gumroad listings (e.g. shifting a catalog toward volume pricing) and/or rewrite their titles and tags for real Etsy buyer search behavior, across both platforms, with mandatory re-fetch verification on every write. Use this whenever Charlie asks to reprice the shop, run a pricing strategy change, fix weak/generic listing titles, or improve Etsy SEO — especially when a catalog has real listings but zero or near-zero views, which usually means discovery (titles/tags), not quality, is the bottleneck."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["etsy-api", "gumroad-api", "talos-product-launch-audit"]
---

# Etsy + Gumroad Repricing & SEO Rewrite

**Fleet-wide skill.** Plain Python against `etsy-api` and `gumroad-api`
(read those two skills first — this one assumes their auth patterns and
gotchas). Any agent capable of HTTP calls can run this.

## Why this exists

On 2026-09-22, a Talos catalog (16 Etsy + 14 Gumroad listings, genuinely
sound products per `talos-product-launch-audit`) had **zero views, zero
favorites, zero sales** across the board despite being live for days. That
signature — real listings, zero traffic — almost always means a discovery
problem, not a quality or pricing problem: nothing is surfacing the
listings in search. Two things were fixed the same session and are worth
doing together whenever this pattern shows up:

1. **Pricing strategy** — Charlie chose to shift from low-volume/high-price
   ($25-90/item) to high-volume/low-price ($2.99 single-item, $4.99
   bundles) as a deliberate bootstrap strategy: a brand-new shop with zero
   reviews needs sales velocity more than per-unit margin, since Etsy's
   organic search ranking rewards recent sales/review activity. This is a
   strategic choice, not a universal rule — confirm it's still the goal
   before reapplying it blindly to a shop that already has traction.
2. **SEO overhaul** — inspecting the actual live tags found roughly half of
   every listing's 13 tag slots filled with **leaked ad-campaign/pipeline
   vocabulary** (`campaign`, `ad group`, `criterion type`, `keyword`,
   `labels`, `build`, `comp-confirmed`) instead of real buyer search terms.
   That's not a "weak tags" problem, it's a "half the search surface is
   garbage" problem — worth a full rewrite, not an incremental swap.

## Step 0 — decide scope before touching anything

Pull current state from both platforms first (per `etsy-api` / `gumroad-api`)
and look at it before planning changes:

```python
# Etsy: GET /shops/{shop_id}/listings?state=active&limit=100
# Gumroad: paginated GET /v2/products (loop on next_page_key)
```

Check whether the catalog has a genuine discovery problem (real products,
zero/near-zero views) before assuming a full repricing/SEO pass is needed —
if a listing already has views/favorites/sales, changing its price or tags
resets its search history and review momentum for no reason. This skill is
for a catalog that isn't getting found at all, not for tuning something
already working.

## Step 1 — repricing (if in scope)

Decide a pricing tier rule appropriate to the actual catalog. The
2026-09-22 precedent: single-item products (one coloring book, one planner,
one print) → $2.99; multi-item bundles/packs (template sets, font packs,
resume bundles) → $4.99. Build an explicit mapping — don't wing it
per-listing — and validate every listing matches before writing anything:

```python
REPRICE = {
    "title_fragment": new_price,
    # ... one entry per product family, matched by substring against
    # both platforms' current titles
}

def match_price(title):
    for frag, price in REPRICE.items():
        if frag.lower() in title.lower():
            return price
    return None
```

**Etsy price updates do NOT go through the plain listing PATCH** — see
`etsy-api`'s "Updating price" section for the exact inventory-endpoint
sequence (GET `/listings/{id}/inventory` → strip disallowed keys → PUT →
re-fetch). This was the single biggest trap in the 2026-09-22 run: every
PATCH-based price write returned HTTP 200 and silently changed nothing.
**Test the correct method on one listing, confirm via independent re-fetch,
before batching across the rest of the catalog.**

Gumroad price updates go through the same `PUT /v2/products/{id}` used for
other fields (`data={"price": cents}}`) — see `gumroad-api` for the
re-fetch-to-verify discipline that applies to every Gumroad write.

## Step 2 — SEO rewrite (if in scope)

### Research real search terms first

Don't guess at buyer search phrases from category knowledge alone — search
for current Etsy SEO guidance (tag composition, long-tail keyword patterns)
before writing tags, since best practices and Etsy's own algorithm behavior
shift over time. As of 2026-09-22 the consensus pattern is: mix 2-3 broad
category tags, 8-10 long-tail (3+ word) buyer-intent phrases, 2-3
niche/descriptive tags — and never repeat words already in the title, since
that wastes search surface Etsy could otherwise be matching on.

### Write and validate before sending anything

Etsy enforces exactly 13 tags per listing, each **≤20 characters**, no
duplicates within a listing, and title ≤140 characters. Validate ALL of
this locally before any API call — a single oversized tag fails the whole
batch PATCH, and the error doesn't always identify which tag:

```python
for lid, r in REWRITES.items():
    assert len(r["tags"]) == 13
    assert len(set(r["tags"])) == 13          # no dupes
    assert all(len(t) <= 20 for t in r["tags"])
    assert len(r["title"]) <= 140
```

Iterate the validator until it passes clean for the whole batch — this
caught multiple over-length tags in the 2026-09-22 run before anything went
live, exactly as designed.

### Write titles/tags via plain PATCH — confirmed working, unlike price

```python
r = requests.patch(
    f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/{listing_id}",
    headers=headers,
    json={"title": new_title, "tags": new_tags},
)
r.raise_for_status()
check = requests.get(f".../listings/{listing_id}", headers=headers).json()
assert check["title"] == new_title and check["tags"] == new_tags
```

### Mirror to Gumroad

Gumroad doesn't have Etsy's tag-based search model, but title still matters
for its own browse/search — match each Gumroad product back to its Etsy
counterpart by fuzzy title match and push the same improved title via
`PUT /v2/products/{id}` with `data={"name": new_title}`, re-fetching to
confirm per `gumroad-api`'s write discipline. Handle any product with no
Etsy equivalent by writing a title directly rather than skipping it
silently.

## Step 3 — verify everything, independently, before reporting done

Every single write in this skill (price, title, tags, on either platform)
has a documented history of reporting success while silently not applying.
The discipline that makes this skill trustworthy is: **test the write
method on one item, confirm via a separate GET, THEN batch the rest — and
verify every item in the batch, not just the first one.** A batch script
that logs "16/16 succeeded" is only meaningful if "succeeded" was defined
as "independently re-fetched and matches the target," not "got HTTP 200."

## What this does not cover

- Actually driving traffic to the repriced/re-tagged listings (Pinterest,
  Etsy Ads, social) — those require account-level setup (a Pinterest
  Business account with API access, enabling Etsy Ads in Shop Manager) that
  has to happen once, manually, before any automation can act on it. A
  clean, well-priced, well-tagged catalog with zero visitors still needs
  something pointing buyers at it; this skill only fixes the "would convert
  if seen" half of the problem.
- Deciding the pricing strategy itself — that's a business judgment call
  (margin vs. volume vs. review-velocity bootstrap) that should come from
  Charlie, not be inferred or defaulted by whichever agent runs this skill.
