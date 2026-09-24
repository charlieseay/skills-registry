---
name: "apify-web-research"
description: "Run an Apify actor to pull structured competitor/market data (product listings, prices, ratings, review counts) from a site that doesn't have a clean API of its own -- a free-lane alternative to a plain web search when the task needs real structured comps, not search-result snippets. Use this whenever a competitor-benchmarking step (per digital-product-quality-bar's Step 0, or any product research task) targets a marketplace/site that isn't already covered by a dedicated API skill (etsy-api, gumroad-api) -- Amazon, Fiverr, Upwork, Indeed, YouTube, Facebook reviews, itch.io, or a generic Etsy/Gumroad search this account doesn't already have a clean API path for. Do not reach for this when etsy-api or gumroad-api already gives clean structured data directly through their own documented endpoints -- this skill is for the gap those don't cover."
category: "research"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["etsy-api", "gumroad-api", "talos-product-launch-audit", "digital-product-quality-bar"]
---

# Apify Web Research

**Fleet-wide skill.** Any agent needing structured data from a site with no
clean API of its own should use this rather than scraping HTML by hand or
trusting a plain web search's snippet text — a search result gives you a
sentence about a listing; an actor run gives you the actual price, rating,
and review count as real fields you can put in a comp table.

## When to reach for this vs. something else

- **Etsy or Gumroad data** → use `etsy-api` / `gumroad-api` first. Both
  platforms have clean, already-working OAuth/API access on this account
  with documented gotchas. Only fall back to an Apify Etsy/Gumroad actor
  (both exist on this account — see below) if the official API genuinely
  can't answer the question (e.g. bulk cross-shop competitor search, which
  Etsy's own API doesn't expose the way a scraper can).
- **A site with no API worth the trouble** (Amazon, Fiverr, Upwork,
  Indeed, generic marketplaces, YouTube transcripts, Facebook reviews) →
  this skill. A general web search gives you a search-result snippet, not
  a clean `{title, price, rating, review_count}` record you can drop into
  a comp table.
- **A one-off "what's out there" question with no need for structured
  fields** → a plain web search is faster and free-er than spinning up an
  actor run. Reach for Apify when the task specifically needs comparable
  structured data across several results, not a general sense of the
  landscape.

## Auth — reuse the existing token, don't create a new one

The account already has a working Apify token at
`/Volumes/data/secrets/n8n_apify_token`. Read it the same way
`cost-monitor.py` does (`~/Projects/claude-config/bin/cost-monitor.py`,
`collect_apify()`) — don't request a new API key or credential.

```python
token = open("/Volumes/data/secrets/n8n_apify_token").read().strip()
headers = {"Authorization": f"Bearer {token}"}
```

## Actors already available on this account

Check `GET https://api.apify.com/v2/acts` before assuming you need to find
or build a new actor — this account already has 9 actors set up and
previously run, several directly relevant to product/market research:

| Actor name | Actor ID | Use for |
|---|---|---|
| `etsy-product-search-scraper` | `7uBnuXg56t3U0h5Nl` | Bulk Etsy competitor search across shops — broader than etsy-api's per-shop listing calls |
| `etsy-listings-scraper` | `6xoTiGfCmvG8ZKmtn` | Deep-dive on specific known Etsy listings |
| `gumroad-product-scraper` | `6PrFwxetNSUJUjLA7` | Gumroad competitor search |
| `fiverr-scraper` | `wjFmOagR5iZ30b4Kf` | Service-gig market research (freelance/consulting product ideas) |
| `upwork-jobs-scraper` | `GGKOD4wJ69c6yZjCF` | Job-market demand signals for a skill/service idea |
| `indeed-scraper` | `BIeK7ZcYUrdxDgOEQ` | Same, broader job-board coverage |
| `itch-io-game-assets-scraper` | `fpXieM8APdlnuHeMR` | Game-asset/interactive-content market (relevant to branching-narrative-pdf-style products) |
| `youtube-transcript-scraper` | `faVsWy9VTSNVIhWpR` | Pull transcript content for research/summarization, not product comps |
| `facebook-reviews-scraper` | `dX3d80hsNMilEwjXG` | Review-sentiment research on a specific page/product |

This list can go stale — always confirm with a live `GET /v2/acts` call
rather than trusting this table blindly if it's been a while since it was
last updated (see date on this skill's last edit).

## Running an actor and getting results — verified pattern

Apify's actor-run flow is async: start a run, poll until it finishes (or
use the `run-sync-get-dataset-items` convenience endpoint for a single
blocking call), then read the dataset it produced.

```python
import time
import requests

token = open("/Volumes/data/secrets/n8n_apify_token").read().strip()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

actor_id = "7uBnuXg56t3U0h5Nl"  # etsy-product-search-scraper

# Simplest path for a bounded, one-shot research pull: run synchronously
# and get the dataset items back directly, capped by maxItems so you never
# accidentally scrape more than you need.
run_input = {
    "search": "engineering coloring page adult",
    "maxItems": 10,
}
resp = requests.post(
    f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items",
    headers=headers,
    json=run_input,
    params={"timeout": 120},  # seconds Apify waits before giving up and returning what it has
)
resp.raise_for_status()
items = resp.json()  # list of dicts -- exact fields depend on the actor, see below

for item in items[:5]:
    print(item.get("title"), item.get("price"), item.get("shop_average_rating"), item.get("shop_total_rating_count"))
```

If a run needs more than the sync endpoint's timeout allows (large scrapes,
slow sites), start it async and poll instead:

```python
run = requests.post(
    f"https://api.apify.com/v2/acts/{actor_id}/runs",
    headers=headers,
    json=run_input,
).json()["data"]
run_id = run["id"]

# Poll until terminal status -- SUCCEEDED, FAILED, ABORTED, or TIMED-OUT
while True:
    status = requests.get(
        f"https://api.apify.com/v2/actor-runs/{run_id}",
        headers=headers,
    ).json()["data"]
    if status["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
        break
    time.sleep(5)

if status["status"] != "SUCCEEDED":
    raise RuntimeError(f"Actor run {run_id} ended {status['status']}")

dataset_id = status["defaultDatasetId"]
items = requests.get(
    f"https://api.apify.com/v2/datasets/{dataset_id}/items",
    headers=headers,
    params={"limit": 20},
).json()
```

**Real confirmed output shape** (from `etsy-product-search-scraper`, a
past successful run, 2026-09-02): each item is a flat dict with `title`,
`price`, `currency_code`, `url`, `shop_average_rating`,
`shop_total_rating_count`, `image_urls` (a list) — directly usable as a
comp-table row per `digital-product-quality-bar`'s Step 0 format. Field
names vary by actor; always inspect a real item from the dataset before
assuming a field exists, the same discipline `etsy-api` already teaches
for that platform's own API responses.

## Cost awareness — real ceiling, and a verified false-confidence trap

Apify billing is metered per compute-unit and per-paid-actor-event, not a
flat subscription. The account's plan is STARTER: `monthlyUsageCreditsUsd:
29, maxMonthlyUsageUsd: 29` — a genuine hard $29/month credit pool, not
just a policy number. This pipeline's own standing rule
(`feedback_apify_cost_ceiling` in memory) self-enforces a lower **$27**
warning line so there's margin before the real cap bites.

**Checking `GET /v2/users/me/usage/monthly`'s top-level
`monthlyServiceUsage.ACTOR_COMPUTE_UNITS.amountAfterVolumeDiscountUsd`
field alone is a trap — confirmed live 2026-09-23.** That field only
covers compute-unit cost, one of several billed service types. The real
total credits consumed for the cycle is
`data.totalUsageCreditsUsdAfterVolumeDiscount` at the top level of the
response, not nested under any one service. Checking only the
`ACTOR_COMPUTE_UNITS` line showed `$0.07` — looking safe — while the real
total was `$29.82`, already over the $29 cap, driven almost entirely by
`PAID_ACTORS_PER_EVENT` charges (several of the actors on this account are
paid, ~$5/day in the first half of this cycle). Acting on the
compute-units-only figure led directly to an actual live 403
`platform-feature-disabled: Monthly usage hard limit exceeded` on the very
next run attempt.

**Always read the top-level total, not a single service line:**

```python
resp = requests.get(
    "https://api.apify.com/v2/users/me/usage/monthly",
    headers=headers,
)
data = resp.json()["data"]
spent_this_cycle = data["totalUsageCreditsUsdAfterVolumeDiscount"]  # NOT a nested per-service field
cycle_end = data["usageCycle"]["endAt"]
if spent_this_cycle > 20:  # well under the $27 self-enforced ceiling, leaves room to notice before it's tight
    print(f"WARNING: ${spent_this_cycle:.2f} spent this cycle (resets {cycle_end}) -- do not run more actors")
```

If the account is at or past the cap, actor runs fail outright (403) —
there is no graceful degradation. Check this BEFORE attempting a run, not
after a failure, and if the cycle is exhausted, fall back to a plain web
search or wait for the next cycle (`usageCycle.endAt`) rather than
retrying against a hard limit.

Set `maxItems` conservatively on every run (10-20 is usually plenty for a
comp table of 3-5 real competitors) rather than pulling a full dataset —
cost scales with pages/items scraped and per-actor-event charges, and a
comp table needs a handful of real, representative results, not
exhaustive coverage. Several actors on this account are **paid actors**
(flagged by the `PAID_ACTORS_PER_EVENT` line item) — these cost real money
per run regardless of item count, so prefer a free/community actor for a
routine research pass and reserve a paid one for when its specific
capability is genuinely needed.

## What this is NOT for

- Not a replacement for `etsy-api`/`gumroad-api` when those already give
  clean structured data directly — check those skills first for anything
  Etsy/Gumroad-native.
- Not for tasks that just need a general sense of a market (a plain web
  search is faster and free) — reach for this when the task specifically
  needs comparable structured fields (price, rating, review count) across
  multiple real results to build a comp table.
- Not for anything requiring login-gated or paywalled content the actor
  can't legitimately access — Apify actors here scrape public listing
  pages, not authenticated account data.
