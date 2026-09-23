---
name: "gumroad-api"
description: "Query the Seaynic Labs Gumroad shop via the Gumroad v2 API — list all products (published and unpublished), check for duplicate or existing products before publishing anything new, and get the real published state/URL of a product. Use this whenever a task involves Gumroad products, Gumroad publishing, checking what's live on Gumroad, or before any code/agent creates a new Gumroad product. Also use it whenever a local record (STATUS.json, a DB flag, a dashboard) claims something about Gumroad publish state — that claim must be verified against this API, not trusted as-is."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["etsy-api", "talos-product-launch-audit", "state-reconciliation"]
---

# Gumroad API (Seaynic Labs shop)

**This is a fleet-wide skill — usable by any agent (Claude, nvidia-agent,
Gemini, aider, Ollama), not just one tool.** Plain Python against a
documented REST API, no agent-specific runtime dependency.

## The incident this skill prevents

On 2026-09-21 we found **multiple duplicate live Gumroad listings** (identical
title and price, different `short_url`) because nothing checked existing
products before publishing. In the same audit we found a product's
`STATUS.json` claiming a Gumroad URL that Gumroad no longer served (404) —
the local tracking file was simply wrong.

Later the same night, we discovered a critical pagination blindspot:
**`GET /v2/products` defaults to 10 items per page and paginates via `next_page_key`**.
Previous sweeps made a single unpaginated call, assuming it returned the entire shop.
As a result, products sitting on page 2 were invisible to automated checks —
including active duplicate listings and an incomplete product (Product #7) that had
been pulled from Etsy hours earlier but remained live on Gumroad because the unpaginated
search never saw page 2.

**Gumroad's API is the only trustworthy source of "what's actually live" — never
trust a local file, STATUS.json, or dashboard state for Gumroad publish status.
And you MUST always paginate through all pages using `page_key` to see the full catalog.**

**The rule this skill exists to enforce: before creating any new Gumroad
product, always list all existing products across all pages and check for a name match.**

## Credential

Plain access token at `/Volumes/data/secrets/gumroad-access-token`. Used as
a query parameter, **not** a Bearer header:

```
?access_token={token}
```

## Canonical usage pattern (Paginated)

**IMPORTANT: Gumroad ignores `page=N`, `limit=N`, and `per_page=N`.**
It paginates with 10 products per page and provides `next_page_key`. To retrieve
the full catalog, you must loop with `page_key` until `next_page_key` is empty or null.

```python
import requests

token = open("/Volumes/data/secrets/gumroad-access-token").read().strip()

products = []
params = {"access_token": token}

while True:
    r = requests.get(
        "https://api.gumroad.com/v2/products",
        params=params,
    )
    r.raise_for_status()
    data = r.json()

    assert data["success"], data
    products.extend(data.get("products", []))

    page_key = data.get("next_page_key")
    if not page_key:
        break
    params["page_key"] = page_key

for p in products:
    price_dollars = p["price"] / 100  # Gumroad price is in cents
    print(p["id"], "|", p["name"], "|", price_dollars, "|", p["short_url"],
          "|", "published" if p["published"] else "unpublished")
```

This endpoint returns **every** product regardless of published state — use
the `published` boolean to distinguish live listings from drafts. This is
also the endpoint to hit whenever you need ground truth for "is X live on
Gumroad" instead of trusting a cached/local record.

## Pagination details

- `GET /v2/products` defaults to 10 products per page.
- Standard pagination query parameters (`page=1`, `limit=100`, `per_page=50`, `count=100`) are **ignored** by Gumroad.
- The response JSON includes `next_page_key` (and `next_page_url`).
- When more products exist, pass `page_key: <next_page_key>` in subsequent requests.
- Loop until `next_page_key` is `None` or absent. Failure to paginate silently truncates the product list at 10 items.

## Before publishing anything new — the check to always run

1. Pull the full product list from `GET /v2/products`.
2. Compare the candidate name (and ideally price) against existing product
   names — exact or close fuzzy match both count.
3. If a match exists among `published: true` products, do not create a new
   product — treat it as already live.
4. Only create a new product when no matching published product exists.

## Updating price, title, and other fields — success ≠ applied

`PUT /v2/products/{id}` accepts `price` (in cents) and `name` (the title) as
form fields and generally applies them correctly — confirmed working
2026-09-22 across a 14-product repricing + retitling batch. But treat
`{"success": true}` as a claim, not proof, on every write:

```python
r = requests.put(
    f"https://api.gumroad.com/v2/products/{product_id}",
    params={"access_token": token},
    data={"price": 299, "name": "New Title Here"},  # price in cents
)
body = r.json()  # {"success": true} — this alone is NOT confirmation

# ALWAYS re-fetch and compare against the target value:
check = requests.get(
    f"https://api.gumroad.com/v2/products/{product_id}",
    params={"access_token": token},
).json()
confirmed = check["product"]["price"] == 299 and check["product"]["name"] == "New Title Here"
```

This isn't paranoia for its own sake — see the `published` field below,
where this exact PUT pattern has silently no-op'd before. Re-fetching after
every write is cheap insurance against Gumroad's API reporting success on a
field it didn't actually change.

## Unpublishing a product — the PUT no-op trap

On 2026-09-21, a second incident: an agent tried to unpublish a duplicate
product via `PUT /v2/products/{id}` with `published=false` (also tried
`published=0` and a JSON body). **Gumroad returned `success: true` every
time but never actually changed the product's published state** — a silent
no-op, not a real error. The agent then escalated to `DELETE
/v2/products/{id}` to get the product off the storefront, which worked, but
nobody had authorized deletion — only unpublish. That specific case turned
out to be harmless (verified: zero sales existed anywhere on this Gumroad
account, and Gumroad's delete is soft — the record stayed fully fetchable
via `GET /v2/products/{id}` afterward, recoverable via Gumroad support). But
it was luck, not by design.

**The rule this near-miss establishes: `success: true` from Gumroad's API is
not proof the change applied. Always re-fetch the resource after a write and
check the actual field you changed, before concluding the call worked.** If
a PUT/update call reports success but a re-fetch shows the field unchanged,
that is a failure — stop and report it. Do not substitute a more destructive
call (like DELETE) to route around an update that silently didn't take,
unless the human overseeing the task has explicitly authorized deletion as a
fallback. Deletion and unpublishing are not equivalent — deletion may be
recoverable through Gumroad support but is not something Gumroad's API lets
you casually reverse yourself.

If you hit this no-op again, the correct move is: report the exact request
you sent, the response you got, and the re-fetch showing it didn't apply —
then stop and let a human decide whether deletion is acceptable for that
specific product, rather than deciding it yourself.

## Product Cover & Thumbnail Image Automation (Direct Upload Flow)

**Gumroad DOES support full programmatic cover and thumbnail image automation via API**, but **NOT** via `PUT /v2/products/:id` (which silently ignores `covers` and `thumbnail` parameters).

Verified independently on 2026-09-21: this endpoint family accepts EITHER
auth style (`Authorization: Bearer <token>` header or `?access_token=<token>`
query param) — unlike some Gumroad endpoints, it isn't picky. The example
below uses the header form; the rest of this skill's examples use the query
param form. Either works here; pick one and be consistent within your own
script.

**Note this endpoint is additive, not idempotent** — calling `/covers`
again with the same image adds a second cover entry rather than replacing
the first. If you re-run an upload (e.g. retrying after a script failure),
check the product's existing `covers` array first and skip/delete-then-add
rather than blindly re-posting, or you'll accumulate duplicate cover images
on the same product.

The real, working endpoint architecture uses ActiveStorage direct uploads:

### Endpoints
1. `POST https://api.gumroad.com/v2/direct_uploads` — registers the image blob and returns a `signed_id` (`signed_blob_id`) and presigned S3 upload URL.
2. `PUT <direct_upload['url']>` — upload raw image bytes to Gumroad's public S3 storage with the headers provided by step 1.
3. `POST https://api.gumroad.com/v2/products/:id/covers` with `data={'signed_blob_id': signed_id}` (or `data={'url': <public_image_url>}`) — attaches the cover image to the product carousel.
4. `POST https://api.gumroad.com/v2/products/:id/thumbnail` with `data={'signed_blob_id': signed_id}` (or `data={'url': <public_image_url>}`) — sets the product thumbnail (requires a 1:1 square image).
5. `DELETE https://api.gumroad.com/v2/products/:id/covers/:cover_id` — removes a cover.

### Canonical Python Implementation

```python
import base64
import hashlib
from pathlib import Path
import requests

token = open("/Volumes/data/secrets/gumroad-access-token").read().strip()
headers = {"Authorization": f"Bearer {token}"}

def upload_gumroad_cover(product_id: str, image_path: Path):
    data = image_path.read_bytes()
    checksum = base64.b64encode(hashlib.md5(data).digest()).decode("utf-8")

    # 1. Request direct upload blob
    payload = {
        "blob": {
            "filename": image_path.name,
            "byte_size": len(data),
            "checksum": checksum,
            "content_type": "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
        }
    }
    r1 = requests.post(
        "https://api.gumroad.com/v2/direct_uploads",
        headers={**headers, "Content-Type": "application/json"},
        json=payload
    )
    r1.raise_for_status()
    blob = r1.json()
    signed_blob_id = blob["signed_id"]
    direct_upload = blob["direct_upload"]

    # 2. PUT bytes to S3
    r2 = requests.put(
        direct_upload["url"],
        data=data,
        headers=direct_upload["headers"]
    )
    r2.raise_for_status()

    # 3. Attach cover to product
    r3 = requests.post(
        f"https://api.gumroad.com/v2/products/{product_id}/covers",
        headers=headers,
        data={"signed_blob_id": signed_blob_id}
    )
    r3.raise_for_status()
    return r3.json()
```

Alternatively, if an image is already hosted on a public CDN (e.g. Etsy CDN `https://i.etsystatic.com/...`), you can attach it directly by passing `url`:
```python
requests.post(
    f"https://api.gumroad.com/v2/products/{product_id}/covers",
    headers={"Authorization": f"Bearer {token}"},
    data={"url": public_image_url}
)
```

## Reconciling against local tracking files

If a pipeline (e.g. Talos's `listing-bot`) keeps its own record of publish
state (a `STATUS.json`, a DB row, a `platforms.gumroad.url` field), treat
that record as a *claim*, not a fact. To verify it:

1. Pull the live product list from this API.
2. Match by name (URLs can go stale even when the record isn't literally
   wrong — Gumroad permalinks can differ from what was recorded if the
   product was recreated).
3. If the recorded URL doesn't appear in the live list, or the live list
   contains a same-titled product under a different URL, the local record
   is stale — fix the record from the API's answer, not the other way
   around.
