---
name: "etsy-catalog-triage"
description: "Decide which 1-3 listings in a multi-product Etsy catalog deserve fix/ad-spend effort right now, using real Etsy traffic data and real competitor saturation counts instead of guessing. Use this whenever Charlie asks to review/audit a whole catalog against competitors, wants products generating traffic or revenue 'today' or 'fast', asks which products to fix first, or before spending on Etsy Ads or a rework pass on more than one listing. Also use it before assuming a batch of same-day-published listings is safe to promote further — it includes the suppression-risk check. This is the missing prioritization layer above digital-product-quality-bar (is a product good) and etsy-gumroad-reprice-seo (fix pricing/tags once in scope) — neither of those decides which listings are worth the effort or whether it's currently safe to add visibility."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["etsy-api", "digital-product-quality-bar", "etsy-gumroad-reprice-seo", "product-quality-verify", "digital-product-playbook"]
---

# Etsy Catalog Triage

**Fleet-wide skill.** Answers one question with real data instead of a guess:
*of everything live in the shop, which 1-3 listings should get fix/ad-spend
effort right now, and is it currently safe to promote them further?*

## Why this exists

On 2026-09-28, asked to audit a 35-listing catalog and get 1-3 products
producing revenue "today," the natural approach was to jump straight to
picking familiar-looking products and fixing images/copy. That would have
wasted the effort: real data (pulled via `etsy-api`) showed the catalog had
3 total views and 0 favorites across all 35 listings — there was no
traffic to triage into "converts poorly" vs. "doesn't convert," because
almost nothing had been seen at all. Separately, 21 of the 35 listings had
been published in a single same-day batch, which is a documented Etsy 2026
enforcement trigger for AI-pipeline shops — a fact that would not surface
from reading STATUS.json, only from checking listing creation timestamps
directly against the live API.

Neither `digital-product-quality-bar` (checks whether a product meets the
bar) nor `etsy-gumroad-reprice-seo` (fixes pricing/tags once you know the
scope, and explicitly disclaims deciding what's in scope) answers "which
listings, out of many, are worth today's effort." This skill is that layer.

## The sequence

### 1. Pull real per-listing traffic — never guess or infer from STATUS.json

```python
import sys, requests
sys.path.insert(0, "/Volumes/data/projects/listing-bot/src")
from platforms.etsy_oauth import get_valid_access_token

client_id = open("/Volumes/data/secrets/etsy-api-key").read().strip()
client_secret = open("/Volumes/data/secrets/etsy-api-secret").read().strip()
token = get_valid_access_token(client_id)
headers = {"x-api-key": f"{client_id}:{client_secret}", "Authorization": f"Bearer {token}"}
# shop_id from ~/.config/listing-bot/etsy_tokens.json

all_listings, offset = [], 0
while True:
    r = requests.get(f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/active",
        headers=headers, params={"limit": 100, "offset": offset})
    batch = r.json().get("results", [])
    all_listings.extend(batch)
    if len(batch) < 100: break
    offset += 100
```

Each result includes `views`, `num_favorers`, and `creation_timestamp` —
this alone answers whether the catalog has any real traffic yet.

### 1a. Re-pull immediately before EVERY dispatch, not once per session

A listing_id list built once and reused across a multi-hour session goes
stale the moment real-world state changes underneath it — Charlie deleting
listings for quality reasons, another session publishing/pulling products,
or anything else external. Confirmed 2026-09-28 (helmsman lesson_id 3788):
a 10-product audit batch was built once early in a session, then dispatched
4+ times over several hours against the same fixed listing_id list. Three
of the ten had gone genuinely 404 by later attempts — Charlie had deleted
them from Etsy, and the shop's real active count dropped from 35 to 11
during that same session window. Every retry against that stale batch was
doomed regardless of brief wording, timeout budget, or output-format
constraints, because the actual defect was upstream of the brief entirely:
wrong inputs, not a broken pipeline. The failures looked exactly like
agent/pipeline defects (truncated output, a worker corrupting its own
script) and consumed several real debugging cycles before the actual cause
(stale listing_ids) was found by walking the brief manually.

**The rule this establishes: re-run the live listing pull (1) immediately
before dispatching, and again before EACH retry** — not once when the
batch was first identified. If a task keeps failing for reasons that don't
obviously repeat (different symptom each time), check whether every
external ID it names is still real and live before assuming the task
content or pipeline is broken.

### 2. Check the batch-upload / suppression risk before promoting anything

Group `creation_timestamp` by day. **A large fraction of the catalog
published on the same day is a real risk signal**, independent of content
quality — Etsy's 2026 enforcement flags rapid, similar-styled AI-pipeline
uploads for shop-level suppression (search it if this needs re-confirming;
policy changes). The live API has no field for "shadow suppressed" — check
what's checkable (shop `is_vacation`, all listings still `state: active`,
zero inactive/taken-down listings, no policy-flag lessons in helmsman) and
be explicit that this does NOT prove the shop is clean. Etsy Shop Manager's
dashboard and the account owner's email are the only sources that can
confirm or rule out an actual suppression notice — say so, don't imply the
API check is conclusive.

If traffic is near-zero AND the shop/listings are only days old, near-zero
views is the normal cold-start case (Etsy's index takes roughly 2-3 weeks),
not automatically evidence of suppression — don't over-read a young shop's
silence as a crisis, but don't ignore a real same-day batch pattern either.

### 3. Pull real competitor saturation per category — `findAllListingsActive`

```python
r = requests.get("https://openapi.etsy.com/v3/application/listings/active",
    headers=headers, params={"keywords": "family emergency binder printable",
    "limit": 5, "sort_on": "score"})
d = r.json()
# d["count"] = total active competing listings across ALL of Etsy for this term
# d["results"][i]["num_favorers"] = top competitors' actual traction
```

Free, no scraper, 10,000 requests/day — see `etsy-api` for the full pattern.
Run this once per category actually represented in the catalog (don't
guess categories from titles alone; pull the real query).

### 4. Rank candidates: traffic potential vs. effort, not familiarity

Build one table: category, competing-listing count, top-competitor
favorites, our own listing's current views/images/tags. Prefer categories
where:
- Competing listings are in the low thousands, not tens of thousands
  (25,000+ active competitors for one phrase means outcompeting a
  784-favorite competitor, not a fast win)
- Top 5 competitor results themselves have low/zero favorites (nobody has
  won the niche yet — a real opening, not just "less crowded")
- Our own listing is close to the bar already (7+ images, real tags) —
  cheap to finish beats expensive to rebuild

A listing in a 900-count category with 0-favorite top competitors beats a
listing in a 30,000-count category with a 1,000-favorite leader, even if
the saturated category "feels" more central to the business.

### 5. State the realistic timeline, don't imply "today" means organic traffic today

Organic Etsy indexing lag is roughly 2-3 weeks even after a listing is
fixed — that is normal, not a failure. The only lever that produces a
same-day traffic *signal* is paid Etsy Ads ($1-2/day) on the specific
listings just fixed. Say this plainly rather than letting "generate
revenue today" quietly become a claim about organic search.

## Quick reference

| Question | Where the real answer lives | Do NOT trust |
|---|---|---|
| Is this listing getting traffic? | `views`/`num_favorers` on the live listing object | STATUS.json, "should be ranking by now" |
| How saturated is this category? | `findAllListingsActive` count for the real search phrase | Gut feel about the niche |
| Did we just batch-publish unsafely? | `creation_timestamp` grouped by day | Nothing — this has no local record |
| Is the shop actually suppressed? | Etsy Shop Manager dashboard / email (not API-checkable) | Treating "no red flags in the API" as proof |
| Autocomplete/live search suggestions | A live Etsy search-box session | A third-party keyword-tool's estimate presented as literal autocomplete |

## Common mistakes

- **Reusing a listing_id batch across multiple dispatch attempts without re-pulling live state first** — real-world state changes mid-session (deletions, new publishes), and retrying a stale batch produces symptoms that look like agent/pipeline bugs but are actually just wrong inputs. Re-verify before every dispatch, not once.
- **Picking listings to fix by familiarity or "this seems like our best product"** instead of pulling real view/favorite/saturation numbers first — the whole point of this skill is that intuition about a 35+ listing catalog is usually wrong.
- **Treating zero views as proof of a quality problem** on a shop/listing under ~2-3 weeks old — check age before diagnosing.
- **Treating "no suppression evidence in the API" as "confirmed not suppressed"** — the API cannot see policy-review state; say what you actually checked and what remains unverifiable without the human's own dashboard/email access.
- **Presenting a third-party keyword tool's suggestions as Etsy's live autocomplete dropdown** — note the real source; they're a useful proxy, not the same thing.
- **Skipping the batch-upload timestamp check** because nothing in STATUS.json flags it — this is exactly the kind of risk that's invisible unless you deliberately pull and group `creation_timestamp`.
