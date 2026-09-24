---
name: "etsy-api"
description: "Query or manage the Seaynic Labs Etsy shop via the Etsy Open API v3 — list active/inactive listings, check for duplicate or existing listings before publishing anything new, look up a single listing, or deactivate/update one. Use this whenever a task involves Etsy listings, Etsy publishing, Etsy pricing, checking what's live on Etsy, or before any code/agent creates a new Etsy listing. Also use it to investigate Etsy OAuth/token errors, 403s mentioning \"shared secret\", or listing-fee cost questions. Do not hand-roll Etsy OAuth or guess at API headers — this skill has the exact working pattern and known gotchas."
category: "product"
metadata:
  version: "1.1.0"
  agents: ["any"]
  related_skills: ["gumroad-api", "talos-product-launch-audit", "state-reconciliation"]
---

# Etsy API (Seaynic Labs shop)

Talos's `listing-bot` already holds a working OAuth setup for this shop. This
skill exists so nobody re-derives that setup, mis-guesses the auth header, or
skips the "does this already exist?" check that caused a real incident.

**This is a fleet-wide skill — usable by any agent (Claude, nvidia-agent,
Gemini, aider, Ollama), not just one tool. Nothing here depends on any
specific agent's runtime; it's plain Python against a documented REST API.**

## The incident this skill prevents

On 2026-09-21 we found **23 duplicate active listings** on this shop — 7
products each posted up to 4 times, 1 posted 3 times, all identical
title/price. `listing-bot` had re-run its publish step against products it
had *already* published, with nothing checking Etsy for an existing listing
first. Each active listing costs **$0.20 per 4 months**, billed regardless of
duplication, so this was pure waste that recurs every renewal cycle until the
duplicates are deactivated.

**The rule this skill exists to enforce: before creating any new Etsy
listing, always list current active listings and check for a title match.**
Never trust a local file (STATUS.json, a DB row, a "published" flag) as proof
of what's live on Etsy — query Etsy directly.

## Credentials and where the token lives

- App key/secret (not usable alone — this is the OAuth *app* identity, not a
  bearer token): `/Volumes/data/secrets/etsy-api-key` and
  `/Volumes/data/secrets/etsy-api-secret`
- A working OAuth access+refresh token pair already exists at
  `~/.config/listing-bot/etsy_tokens.json` (includes `shop_id`). It's managed
  by `listing-bot`'s own module:
  `/Volumes/data/projects/listing-bot/src/platforms/etsy_oauth.py`

**Reuse `etsy_oauth.get_valid_access_token(client_id)` from that module
rather than re-implementing the OAuth refresh flow.** It reads the token
file, refreshes if the access token is stale, and writes the refreshed token
back to disk. If `~/.config/listing-bot/etsy_tokens.json` doesn't exist or
the refresh token itself is dead, that's a real blocker — surface it, don't
try to run a fresh OAuth authorization flow yourself (it needs a browser
redirect Etsy approved for `listing-bot`'s registered redirect URI).

## The header gotcha that produces a misleading error

Etsy's `x-api-key` header is **not** just the client_id. It must be:

```
x-api-key: {client_id}:{client_secret}
```

(keystring and shared secret joined with a colon.) Sending just the
client_id passes Etsy's basic auth check but fails deeper in, returning:

```json
{"error":"Shared secret is required in x-api-key header."}
```

with HTTP 403. This looks like a missing/invalid key problem — it's actually
a malformed header. Always build `x-api-key` as `f"{client_id}:{client_secret}"`.

## Canonical usage pattern

```python
import sys, json, os, requests

sys.path.insert(0, "/Volumes/data/projects/listing-bot/src")
from platforms.etsy_oauth import get_valid_access_token

client_id = open("/Volumes/data/secrets/etsy-api-key").read().strip()
client_secret = open("/Volumes/data/secrets/etsy-api-secret").read().strip()

access_token = get_valid_access_token(client_id)

tokens = json.loads(
    open(os.path.expanduser("~/.config/listing-bot/etsy_tokens.json")).read()
)
shop_id = tokens["shop_id"]

headers = {
    "Authorization": f"Bearer {access_token}",
    "x-api-key": f"{client_id}:{client_secret}",
}

# List active listings — ALWAYS do this before creating a new one.
r = requests.get(
    f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings",
    headers=headers,
    params={"state": "active", "limit": 100},
)
r.raise_for_status()
data = r.json()

for listing in data["results"]:
    price = listing["price"]
    amount = price["amount"] / price["divisor"]  # Etsy price is cents-style int + divisor
    print(listing["listing_id"], listing["title"], amount, listing["state"])
```

If the shop has more than 100 active listings, paginate with `offset`.

## Key endpoints

Base URL: `https://openapi.etsy.com/v3/application`

| Purpose | Method + path |
|---|---|
| List listings (any state) | `GET /shops/{shop_id}/listings?state=active\|inactive\|draft&limit=100&offset=N` |
| Get one listing | `GET /listings/{listing_id}` — **listing-scoped, no shop_id.** The shop-scoped `GET /shops/{shop_id}/listings/{listing_id}` 404s for a draft listing that demonstrably still exists in the shop's own listing search (confirmed 2026-09-23) — use the listing-scoped path for a definitive single-listing check. |
| Update title/description/tags/state | `PATCH /shops/{shop_id}/listings/{listing_id}` |
| Update price/quantity | `PUT /listings/{listing_id}/inventory` — see below, NOT the plain PATCH |
| Create a new listing | `POST /shops/{shop_id}/listings` |
| Delete a listing | `DELETE /listings/{listing_id}` — **listing-scoped, no shop_id.** `DELETE /shops/{shop_id}/listings/{listing_id}` 404s (same shop-vs-listing-scoped trap as GET above), confirmed 2026-09-23 deleting 6 dead duplicate drafts. |

`state=active` is the one that matters for duplicate-checking and for "what's
actually live" questions — `inactive`/`draft` listings aren't costing listing
fees and aren't visible to buyers.

**The shop-scoped listing list (`GET /shops/{shop_id}/listings?state=...`) is
eventually consistent and can lag well behind reality** — confirmed
2026-09-23: 6 listings individually DELETEd (each got a clean `204`) still
appeared in a `state=draft` list query moments later, while an individual
`GET /listings/{id}` on each correctly returned `404`. When you need a
definitive single-listing answer (did my write actually take?), always
GET that one listing_id directly — never trust the list endpoint's absence
or presence of an entry as proof, in either direction.

## Digital file size limit — 20MB per file, 5 files per listing

Etsy's `POST /shops/{shop_id}/listings/{listing_id}/files` returns
`400 {"error": "This file exceeds the maximum file size"}` for any single
file over roughly 20MB, with zero indication of the actual limit or that
splitting is the fix. Confirmed 2026-09-23 after this exact error produced
**6 dead duplicate draft listings** across two products (a brief-compiler
bug repeatedly retried the same oversized upload, see
`talos-product-launch-audit`) — Etsy's own docs confirm: 20MB max per
file, up to 5 files per listing, 100MB total.

A single zip bundling both print-PDF and digital-PNG exports for a
multi-page product (a coloring book, a gamebook with many illustrated
pages) routinely exceeds this once a product has more than ~4-5 pages at
real print/tablet resolution — don't assume a "reasonable" zip is safe;
check its size before upload.

**The fix, already implemented in `listing-bot/src/platforms/etsy.py`
(`_split_zip_under_limit` / `_upload_digital_deliverable`, added
2026-09-23):** if the deliverable zip exceeds ~19MB (1MB margin under
Etsy's cap), repack its contents into multiple sub-19MB zips via
largest-first bin packing, and upload each as a separate digital file
(Etsy's 5-file-per-listing allowance covers this for any product this
pipeline currently produces). `publish()`'s call site already uses this;
`update_digital_file()` (the *replace an existing listing's file* path,
not initial publish) does **not** yet — it will hit the same 400 if ever
asked to replace a file over the limit. Extend the same split logic there
if that path is needed for an oversized replacement.

If you hit "exceeds the maximum file size" anywhere else in this codebase
(or a different publisher entirely), this is the fix pattern — don't
re-diagnose from scratch.

## Price format

Etsy returns price as `{"amount": 5555, "divisor": 100, "currency_code": "USD"}`,
not a plain decimal. Always compute `amount / divisor` — don't treat `amount`
as dollars.

## Updating price — the plain PATCH silently no-ops, confirmed 2026-09-22

`PATCH /shops/{shop_id}/listings/{listing_id}` with `{"price": 2.99}` returns
HTTP 200 with a full listing object — but the price field in that response,
and in every subsequent GET, stays at the OLD value. No error, no warning.
This bit a 16-listing repricing batch: every single PATCH "succeeded" and
every single one silently failed to change the price, caught only because
each write was re-fetched and compared against the target.

**Why:** price lives on the listing's inventory/offerings, not on the
top-level listing resource, for any listing that has (or could have)
variations. The plain listing PATCH only touches title/description/tags/state
— price has its own endpoint.

**The fix — go through `/listings/{listing_id}/inventory` instead:**

```python
# 1. GET the current inventory structure
inv = requests.get(
    f"https://openapi.etsy.com/v3/application/listings/{listing_id}/inventory",
    headers=headers,
).json()

# 2. Rebuild products/offerings with ONLY the fields Etsy's PUT accepts.
#    The GET response includes product_id, offering_id, is_deleted,
#    readiness_state_id — sending those back on PUT gets a 400:
#    "Array contains invalid keys: product_id,is_deleted". Strip them.
clean_products = []
for product in inv["products"]:
    clean_offerings = [
        {"price": 2.99, "quantity": o["quantity"], "is_enabled": o["is_enabled"]}
        for o in product["offerings"]
    ]
    clean_products.append({
        "sku": product.get("sku", ""),
        "property_values": product.get("property_values", []),
        "offerings": clean_offerings,
    })

# 3. PUT the cleaned structure back — note `price` here is a plain decimal,
#    not the {amount, divisor} struct the GET returns it as.
r = requests.put(
    f"https://openapi.etsy.com/v3/application/listings/{listing_id}/inventory",
    headers=headers,
    json={"products": clean_products},
)
r.raise_for_status()

# 4. ALWAYS re-fetch and compare — this exact call silently no-op'd via the
#    wrong endpoint, so trust nothing here without independent verification.
check = requests.get(
    f"https://openapi.etsy.com/v3/application/listings/{listing_id}/inventory",
    headers=headers,
).json()
confirmed = check["products"][0]["offerings"][0]["price"]
assert confirmed["amount"] / confirmed["divisor"] == 2.99
```

Test on one listing before batching a price change across many — this
sequence (GET inventory → strip disallowed keys → PUT → re-fetch to verify)
is exactly what caught and fixed the 2026-09-22 incident, and the 400 on the
first PUT attempt (before stripping keys) is expected, not a sign something
deeper is wrong.

**The inventory endpoint is listing-scoped, not shop-scoped — no `shop_id`
in the URL at all.** `PUT /shops/{shop_id}/listings/{listing_id}/inventory`
404s outright. The correct path (confirmed 2026-09-22 for both GET and PUT)
is `PUT https://openapi.etsy.com/v3/application/listings/{listing_id}/inventory`
— same base pattern as the image endpoints below, which also drop the
shop_id segment. If a 404 shows up on an inventory call specifically, check
the URL for a stray `/shops/{shop_id}/` before assuming the listing_id or
auth is wrong.

## Updating title and tags — plain PATCH works fine here

Unlike price, `title` and `tags` are top-level listing fields and the plain
PATCH applies them correctly:

```python
r = requests.patch(
    f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/{listing_id}",
    headers=headers,
    json={"title": new_title, "tags": new_tags},
)
r.raise_for_status()
# Still re-fetch and compare — cheap insurance, and price taught us not to
# assume any write endpoint behaves the way it looks like it should.
```

**Tag constraints (enforced by Etsy, confirmed 2026-09-22):** exactly up to
13 tags, each **20 characters or fewer**, no duplicates within a listing.
Validate every tag's length locally before sending — Etsy will reject the
whole PATCH if any tag is too long, and the error doesn't always name which
one. Use real long-tail buyer search phrases, not title repeats and not
internal pipeline vocabulary (see the tag-quality note below).

**Tag-quality trap found 2026-09-22:** if the listing-generation pipeline
ever writes ad-campaign or automation metadata into the tags field (words
like `campaign`, `ad group`, `criterion type`, `keyword`, `labels`, `build`,
`comp-confirmed`), those tags are wasted search surface — real buyers never
search those words. Check a sample of live tags for this pattern before
trusting that a product's SEO is sound; it's a strong signal the same
leaked-artifact problem `talos-product-launch-audit` looks for elsewhere in
the pipeline is also present in tag generation.

## Digital file size limit — 20MB per file, 5 files max

Confirmed live 2026-09-22: uploading a deliverable zip over ~20MB fails
with `{"error": "This file exceeds the maximum file size"}` on
`POST .../listings/{id}/files`. Etsy's documented limit is 20MB per file,
up to 5 files per listing (100MB aggregate) — a single large zip (e.g. an
audio/video bundle) needs to be split into multiple smaller zips, each
under 20MB, uploaded as separate files (up to 5) rather than compressed
or re-encoded to a lossy format that would break a format promise made in
the listing copy (e.g. "16-bit WAV").

When splitting, group logically (e.g. by category/genre) so each part is
self-contained and customers know what's in which file — update the
listing description to explicitly say "N ZIP files, download all of
them" so buyers don't think they only received part of the product.

## Uploading listing images

```python
r = requests.post(
    f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/{listing_id}/images",
    headers=headers,
    files={"image": (image_path.name, open(image_path, "rb"), "image/png")},
)
r.raise_for_status()
```

This is a multipart file upload (`files=`, not `data=` or `json=`) — do not
send an image as a URL or base64 string, Etsy's image endpoint wants raw
bytes. Etsy assigns a new `listing_image_id` per successful call; re-running
this adds another image rather than replacing one, same as Gumroad's covers
endpoint — check existing image count first if you're worried about
duplicates from a retried script.

After uploading, `GET /shops/{shop_id}/listings/{listing_id}/images` (not
under `/shops/{shop_id}/...` — this specific endpoint is
`/v3/application/listings/{listing_id}/images`, no shop_id segment) returns
the current image list; use this to verify a batch of uploads actually
attached, per the "never trust success alone" discipline. This same
verification call is known to occasionally return an empty/zero-count
result immediately after a rapid burst of Etsy API calls (rate-limiting
manifesting as a false negative, not a real absence of images) — if a
verification check unexpectedly shows 0 images right after upload, wait a
moment and re-check once before concluding the upload failed.

## Replacing the hero/first image — there is no working reorder endpoint

Uploading a new image via `POST .../images` always appends it — it never
replaces or reorders anything, and the `GET .../images` response's `rank`
field is misleading: right after a fresh upload, both the old and new
image can show `rank: 1` simultaneously in the results array, with the
OLD one still listed first. Do not assume the most recently uploaded
image is the one shoppers actually see first.

**There is no working `PUT`/reorder endpoint for this.** A `PUT
.../listings/{listing_id}/images/{listing_image_id}` with `{"rank": 1}`
404s outright (confirmed 2026-09-22). Some third-party docs describe a
`POST .../images` with `rank` + `overwrite=1` form fields as a documented
workaround, but treat that as unverified — it was not confirmed working
in this shop.

**The confirmed-working fix**: upload the new image first (it lands
somewhere in the list, order unreliable), then `DELETE
.../listings/{listing_id}/images/{old_hero_image_id}` — deleting the
current rank-1 image promotes whatever is next in the array to rank 1.
If the newly-uploaded image was already next in line, this correctly
makes it the new hero. Always re-fetch `GET .../images` after the delete
to confirm the order landed the way you expect — don't assume from the
delete call's 204 alone.

## A documented Etsy quirk: activation response, not a follow-up GET, is the real confirmation

After `PATCH .../listings/{listing_id}` with `{"state": "active"}`, a
follow-up `GET` on that same listing can return 404 for a few moments even
though the listing genuinely did go active — this is a known Etsy API
timing quirk (their `open-api` GitHub discussion #1063), not a bug in your
code and not evidence the activation failed. The PATCH/activation response
itself already contains the full updated listing object (`state`, `url`,
etc.) — treat that response as the verification, rather than chaining an
immediate GET that may spuriously 404.

## Before publishing anything new — the check to always run

1. Pull all `state=active` listings for the shop.
2. Compare the candidate title (and ideally price) against existing titles —
   exact match or close fuzzy match both count; a bot that reformats the
   title slightly is still a duplicate.
3. If a match exists, do not create a new listing — either skip, or treat it
   as an update to the existing one.
4. Only create a new listing when no matching active listing exists.

This one check is what was missing on 2026-09-21 and is the entire reason
this skill exists.
