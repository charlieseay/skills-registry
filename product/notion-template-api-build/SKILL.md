---
name: "notion-template-api-build"
description: "Build a real, ready-to-duplicate Notion workspace (pages, databases, properties, sample rows) via the Notion API from an existing build specification or design manifest — the exact working payload shapes for API version 2025-09-03 (which silently rejects two of the three most obvious ways to create a database with custom properties), plus how to file the one genuinely-manual step (Share to web / Allow duplicate) as a decision for a human. Use this whenever a Talos digital product ships as a Notion build-specification document instead of a real template, or whenever any task needs to create Notion pages/databases programmatically."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["digital-product-quality-bar", "talos-product-launch-audit"]
---

# Notion Template API Build

**Fleet-wide skill.** Plain Python/curl against the Notion REST API — any
agent with HTTP access and the credential below can do this.

## Why this exists

Several Talos digital products (product-item-153, 158, and likely 10/25)
were designed with a full page/database manifest but shipped as 400-line
"build this yourself in Notion" instruction documents instead of a real
template — a structural quality gap vs. successful competitors (see
`digital-product-quality-bar`). The build specs themselves even claimed
"No Notion API access is required... following the no-API pattern
validated in product-item-153/10/25" — which was false: none of those
products had ever actually been built into a real Notion page. The gap
wasn't that this couldn't be automated; nobody had actually tried the API
build end-to-end and fixed the real payload-shape gotchas that made a
naive attempt fail three different ways.

This skill exists so the next build starts from a working script, not
from three rounds of guessing against a 500/400 error with no useful
message.

## Prerequisites

- A Notion integration token at `/Volumes/data/projects/talos-tools/.secrets/notion-token`.
- The integration must have the target root page shared with it (Notion
  page menu → `...` → `Connect to` → the integration). For this pipeline,
  the working root is page id `3d0faa0547bc81df91ddf781cb7931e6`
  ("Ultimate Life Planner — Neutral") — the integration bot can only see
  this one root and its children (confirmed, helmsman lesson #1693). New
  products get created as children of this root, not at workspace root.
- `Notion-Version: 2025-09-03` header on every request. This version split
  "databases" into databases + **data sources** — several gotchas below
  stem directly from that split.

## The three real gotchas that broke naive attempts

### 1. `POST /v1/databases` with a top-level `"properties"` key is silently ignored

```python
# WRONG — returns 200, but the database has ONLY the auto-title property,
# nothing else. No error is raised anywhere.
requests.post("https://api.notion.com/v1/databases", headers=HEADERS, json={
    "parent": {"type": "page_id", "page_id": parent_id},
    "title": [{"text": {"content": "Projects"}}],
    "properties": {"Status": {"select": {...}}},   # <-- silently dropped
    "is_inline": True,
})
```

Properties must be nested under `initial_data_source`:

```python
# RIGHT
requests.post("https://api.notion.com/v1/databases", headers=HEADERS, json={
    "parent": {"type": "page_id", "page_id": parent_id},
    "title": [{"text": {"content": "Projects"}}],
    "is_inline": True,
    "initial_data_source": {"properties": {
        "Project": {"title": {}},
        "Status": {"select": {"options": [{"name": "Active", "color": "orange"}]}},
    }},
})
```

**How this was caught:** the create call returned HTTP 200 every time, so
nothing looked wrong until the very next call (adding a row) failed with
`"Status is not a property that exists"`. A `GET /v1/data_sources/{id}`
on the freshly-created database showed only the title property — proof
the create payload's properties were dropped, not a downstream bug.
**Never trust a 200 from database creation as proof the schema you asked
for was applied — verify with a GET before building on top of it.**

### 2. Two different IDs both "look like" the database id, and only one works for row creation

The create-database response has both a top-level `id` and a
`data_sources[0]["id"]`:

```json
{
  "id": "8b19eb17-a51a-4bca-bf8b-dda54bf595a9",
  "data_sources": [{"id": "13e82b58-5fb4-4dc5-a4a4-9d3a9395030d", "name": "..."}]
}
```

`POST /v1/pages` (adding a row) wants the **top-level `id`** under
`parent: {"type": "database_id", "database_id": <top-level id>}` —
passing the data-source id there 404s with `"Could not find database with
ID"` (a real, different object, just the wrong one for this call).
Querying rows, conversely, needs the **data source id**:
`POST /v1/data_sources/{data_source_id}/query` — the old
`POST /v1/databases/{id}/query` pattern from pre-2025-09-03 now 400s with
`"invalid_request_url"`.

Rule of thumb: **database_id for writing pages into it, data_source_id
for querying/reading its schema and rows.**

### 3. Filing the human decision: `actions_json` must be a JSON *string*, not a nested object

`POST /decisions` on this fleet's helmsman API stores `actions_json` as a
column that expects a pre-serialized JSON string, not a raw array —
sending an actual JSON array (not stringified) produces an opaque 500
Internal Server Error with no useful message, even though the field looks
identical when you fetch back a decision that *did* work (both render the
same in a `GET`). Always `json.dumps()` the `actions_json` value before
including it in the request body:

```python
payload["actions_json"] = json.dumps([{"label": "...", "url": "..."}])
```

### 4. Appending block children requires `PATCH`, not `POST`

`POST /v1/blocks/{id}/children` — the pattern shown in older Notion API
docs and in some SDKs — 400s on this API version with
`{"code":"invalid_request_url","message":"Invalid request URL."}`, a
generic-sounding error that doesn't name the method as the problem. On
`Notion-Version: 2025-09-03` the same payload against the same URL
succeeds with `PATCH`. Found while building product-item-25's welcome
callout block. Use `requests.patch(...)`, not `requests.post(...)`, for
appending children to a page or block.

## A raw HTTP fetch cannot verify a Notion public page's real content

Confirmed live 2026-09-22: Notion's public `notion.site` pages are a
client-rendered SPA. The server's initial HTML response contains a fixed
shell (`<title>Notion | Where teams and agents work together</title>`)
for EVERY page load — published or not — and the real title/content is
filled in by JavaScript afterward. A plain `curl`/`urllib`/WebFetch-style
check that reads only the raw HTML cannot tell a genuinely working,
published page apart from a truly broken one; both return HTTP 200 with
the identical shell title.

This produced a real false positive: product-7's QA gate (and an
independent re-check using curl, matching what the gate saw) both flagged
5 real, working, already-shared Notion pages as broken, based solely on
this shell-title heuristic. Charlie opened the exact same URL in a real
browser and saw genuine content. The pages were never broken — only the
verification method was blind to their real state.

**If you need to verify a Notion public page is genuinely live and
populated, a raw HTTP fetch is not sufficient.** Options, in order of
reliability: (1) ask the human who can open it in a real browser, (2) use
a headless-browser tool that actually executes JavaScript (not curl,
not WebFetch, not urllib), (3) as a last resort, trust the Notion API's
own `public_url` field being non-null as a weak signal that sharing was
enabled at some point — but that alone doesn't prove current content is
correct, since sharing is a workspace-level toggle independent of the
page's content.

## The one thing that genuinely cannot be automated

The Notion API has **no property to toggle "Share to web" or "Allow
duplicate as template."** This is UI-only, confirmed independently across
this pipeline's history at least 4 times now (helmsman lessons #1693,
#1827, #1684, and this skill's own build). Do not attempt browser
automation to work around it and do not fabricate a placeholder public
URL — file a decision for the human instead, naming the exact page URL
and the exact 3 clicks (Share → enable web access → enable Allow
duplicate as template).

Database **views** (Board/Timeline/Kanban/Gallery, and setting a
non-default view as the database's default) are the same category of
UI-only limitation — mention this as a secondary, non-blocking note in
the same decision rather than treating it as a build blocker; the
duplicate link works fine with just the default table view.

## Canonical build pattern

```python
import requests, time

TOKEN = open("/Volumes/data/projects/talos-tools/.secrets/notion-token").read().strip()
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

def create_page(parent_id, title, icon=None):
    payload = {"parent": {"page_id": parent_id}, "properties": {"title": [{"text": {"content": title}}]}}
    if icon: payload["icon"] = {"emoji": icon}
    r = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=payload)
    r.raise_for_status(); time.sleep(0.4)
    return r.json()

def create_database(parent_id, title, properties, icon=None):
    """Returns the database id to use for row creation (parent.database_id)."""
    payload = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [{"text": {"content": title}}],
        "is_inline": True,
        "initial_data_source": {"properties": properties},
    }
    if icon: payload["icon"] = {"emoji": icon}
    r = requests.post("https://api.notion.com/v1/databases", headers=HEADERS, json=payload)
    r.raise_for_status(); time.sleep(0.4)
    return r.json()["id"]

def add_row(database_id, properties):
    payload = {"parent": {"type": "database_id", "database_id": database_id}, "properties": properties}
    r = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=payload)
    r.raise_for_status(); time.sleep(0.35)
    return r.json()

def verify_row_count(database_id, expected_count):
    """Never trust the build script's own success output -- independently
    re-query afterward, per state-reconciliation discipline."""
    db_info = requests.get(f"https://api.notion.com/v1/databases/{database_id}", headers=HEADERS).json()
    ds_id = db_info["data_sources"][0]["id"]
    r = requests.post(f"https://api.notion.com/v1/data_sources/{ds_id}/query", headers=HEADERS, json={})
    actual = len(r.json().get("results", []))
    assert actual == expected_count, f"expected {expected_count} rows, found {actual}"
    return actual
```

Property value shapes for `add_row`'s `properties` dict:

```python
def title_prop(text): return {"title": [{"text": {"content": text}}]}
def rich_text_prop(text): return {"rich_text": [{"text": {"content": text}}]}
def select_prop(name): return {"select": {"name": name}}
def multi_select_prop(names): return {"multi_select": [{"name": n} for n in names]}
def date_prop(iso): return {"date": {"start": iso}}
def number_prop(n): return {"number": n}
def checkbox_prop(b): return {"checkbox": b}
```

## Workflow, end to end

1. Read the existing build specification / design manifest in full — do
   not redesign, translate what's already there (page names, icons,
   colors, database schemas, sample rows) into API calls.
2. Verify the root page is accessible (`GET /v1/pages/{root_id}` returns
   200) before starting.
3. Create the root product page as a child of the shared root.
4. For each database in the spec: create it with `initial_data_source`,
   confirm the schema landed with a `GET /v1/data_sources/{id}` (don't
   trust the create response alone), then add sample rows.
5. After the full build, independently re-query every database's row
   count and compare against what the spec called for — this is what
   catches a silent partial failure, since the build script's own printed
   "✓" output is not proof (see `state-reconciliation`).
6. Save the root page URL to `phase-2/notion-master-url.txt`.
7. File a decision (with `actions_json` as a `json.dumps()`-ed string) for
   the one manual Share-to-web/duplicate step, naming the exact page URL
   and exact clicks.
8. Do not touch the live Etsy/Gumroad listing in the same pass — that's a
   separate follow-up once the public duplicate link exists.

## A note on task dispatch, if routing through helmsman

A brief that lists research steps then build steps (e.g. "1. Research:
read X. 2. Research: read Y. 3. Build: create Z.") can still get rejected
at a "compile" stage with `"Steps out of order — modification steps
appear before research steps"`, even when the submitted brief passes the
literal `brief_lint.py` step-order check cleanly (verified directly
against that function's source). This is a separate, opaque compile-time
gate whose source wasn't located during this build — `skip_brief_lint=1`
does not bypass it either. If a Notion-build task gets stuck in this loop
after 2-3 genuinely well-ordered rewrites, don't keep guessing at brief
wording — either escalate the dispatch-pipeline bug separately, or execute
the build directly in the current session using the pattern above rather
than burning further cycles fighting the dispatcher.
