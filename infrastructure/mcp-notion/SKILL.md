---
name: mcp-notion
description: Query and modify Notion pages, databases, and blocks via the `notion` MCP server. Use when a task needs to read Notion page content, create/update database rows, search pages, or manage page structure. This is for general Notion access via MCP; for building new Notion templates from scratch with full schema creation, use the separate notion-template-api-build skill instead.
---

# Notion MCP Server

The `notion` MCP server (proxy name `notion`, stdio via
`/Users/charlieseay/.local/bin/notion-mcp`) wraps the official Notion MCP
implementation (`@notionhq/notion-mcp-server`). The wrapper injects the
authentication token automatically from
`/Volumes/data/secrets/notion-token-talos`.

**Auth setup:** Token is already configured in the wrapper script. No
additional credentials needed — the MCP proxy handles auth transparently.

## Tool catalog (24 tools, confirmed live 2026-09-30)

Query `tools/list` via the MCP proxy if this skill feels stale — Notion's MCP
server can gain/lose tools on updates. This list is a snapshot from
2026-09-30, tested via `npx @notionhq/notion-mcp-server`.

### Page operations

- `API-post-page` — Create a new page as a child of another page or database
- `API-retrieve-a-page` — Get page metadata (title, properties, archived state,
  cover, icon)
- `API-patch-page` — Update page properties (title, cover, icon, archived state)
- `API-move-page` — Move a page to a different parent (page or database)
- `API-retrieve-a-page-property` — Get a single page property's value (e.g.
  Status select, person assignment)

### Database & data source operations

- `API-retrieve-a-database` — Get database metadata and schema
- `API-retrieve-a-data-source` — Get data source details (internal to the
  Notion API v2025-09-03 split between databases and data sources)
- `API-query-data-source` — Query rows in a database (filter, sort, paginate)
- `API-create-a-data-source` — Create a new database with schema
- `API-update-a-data-source` — Update database schema (add/remove/modify
  properties)
- `API-list-data-source-templates` — List built-in database templates

### Block operations

- `API-retrieve-a-block` — Get block metadata (type, created/updated times)
- `API-get-block-children` — List child blocks (pages, paragraphs, lists,
  callouts, images, etc.)
- `API-patch-block-children` — Update block children (supports append, replace,
  delete within a parent block)
- `API-update-a-block` — Update block content (e.g. paragraph text, heading
  level, toggle state)
- `API-delete-a-block` — Remove a block

### Search & navigation

- `API-post-search` — Search Notion pages and databases by title, content, or
  property values

### Comments

- `API-create-a-comment` — Add a comment to a page or block
- `API-retrieve-a-comment` — Get comment details
- `API-get-users` — List workspace users

### User

- `API-get-self` — Get the authenticated user's profile (the integration bot)
- `API-get-user` — Get a specific user's profile by ID

### Markdown export

- `API-retrieve-page-markdown` — Export a page and its children as Markdown
- `API-update-page-markdown` — Update page content via Markdown (beta feature)

## Key gotchas and differences from the raw API

### 1. Database ID vs. Data Source ID (v2025-09-03 split)

Notion's API split database operations into two concepts in September 2025:

- **Database ID** (`database_id`): Use for `API-post-page` to create rows in a
  database, and for the `parent` field when creating new child pages.
- **Data Source ID** (`data_source_id`): Use for `API-query-data-source` to
  read rows and for `API-update-a-data-source` to modify schema.

**Which to use:** If the task is to add a row to a database, use the database
ID from `API-retrieve-a-database`'s top-level `id`. If querying rows, get the
data source ID from `data_sources[0]["id"]` in the same response. Mixing them
produces 404 errors.

### 2. Pagination is built into query responses

`API-query-data-source` returns a `next_cursor` if more results exist. Always
check for it; if present, pass it in the next call's `start_cursor` parameter
to continue. Notion does NOT return all rows in one call by default.

### 3. Properties in `API-patch-page` must match database schema exactly

When updating a page in a database, property names and types must match what
the database defines. Typos or wrong property types produce validation errors.
Always query `API-retrieve-a-database` first if unsure of the exact schema.

### 4. Rich text and block content require nested structures

Text content is not a plain string. Every text field uses a structure like:

```json
{
  "title": [{"text": {"content": "Page title"}}],
  "rich_text": [{"text": {"content": "Body text"}}],
  "paragraph": {"rich_text": [{"text": {"content": "Content"}}]}
}
```

This is verbose but allows Notion to track formatting, links, mentions, etc.
Copy the exact pattern from the tool's documentation when constructing text
payloads.

### 5. `API-post-search` is limited and may not find recent changes

Search is eventually consistent — newly created pages or recently updated
content may not appear in search results for up to a few seconds. If you just
created a page and need to find it immediately, use `API-retrieve-a-page`
directly with its ID instead.

### 6. Markdown export/import is a beta feature

`API-retrieve-page-markdown` and `API-update-page-markdown` are newer features
and may not work on all page types. If a page fails to export as Markdown,
fall back to querying its blocks directly with `API-get-block-children`.

### 7. Sharing and public URLs cannot be set via API

The Notion API has no endpoint to enable "Share to web" or "Allow duplicate as
template" — these are UI-only toggles. If a task needs to create a public
duplicate link, file a decision for the human with the exact page URL and the
clicks needed.

## Workflow pattern for common tasks

### Read a page's content

```
1. API-retrieve-a-page {page_id}
   → Returns title, properties, icon, cover, archived state
2. API-get-block-children {page_id}
   → Returns paragraphs, lists, headings, images, etc.
3. For each block type, parse its content (text, images, nested blocks)
```

### Query a database

```
1. API-retrieve-a-database {database_id}
   → Get data_source_id from response
2. API-query-data-source {data_source_id}
   → Returns rows (pages in the database) with all properties
3. Check for next_cursor; if present, query again with start_cursor
```

### Create a new page in a database

```
1. API-retrieve-a-database {database_id}
   → Confirm schema (properties, types)
2. API-post-page {database_id, properties}
   → Properties must match schema exactly
3. If the page needs blocks (body content), API-patch-block-children after creation
```

### Update a database row

```
1. API-patch-page {page_id, properties}
   → Pass only the properties you want to change
   → Must match database schema
```

### Search for pages

```
API-post-search {query}
→ Returns matching pages (may not include very recent additions)
→ Use results to get page IDs, then fetch full content with API-retrieve-a-page
```

## Known environment facts

- Token source: `/Volumes/data/secrets/notion-token-talos` (injected by wrapper,
  never visible to agents)
- Root page for products: `3d0faa0547bc81df91ddf781cb7931e6` ("Ultimate Life
  Planner — Neutral")
- New product pages are created as children of the root, not at workspace root
  (API access is scoped to this subtree only)
- Notion API version in use: `2025-09-03`

## Quick self-check for this skill

```bash
# Verify Notion MCP is reachable via the proxy
python3 -c "
import json
config = json.load(open('/Users/charlieseay/.config/mcp-proxy/config.json'))
notion_cfg = config['mcpServers']['notion']
print(f\"Command: {notion_cfg['command']} {' '.join(notion_cfg['args'])}\")
"

# Verify the wrapper script has the token
cat /Users/charlieseay/.local/bin/notion-mcp
# Should show: export NOTION_TOKEN=$(cat /Volumes/data/secrets/notion-token-talos)

# If this skill feels stale, list live tools from Notion MCP:
# (Requires Notion token in env; done automatically via MCP proxy)
npx -y @notionhq/notion-mcp-server <<'EOF'
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
EOF
```

## When NOT to use this skill

- **Building a full new Notion template from scratch:** Use
  `notion-template-api-build` instead — that skill handles the full workflow
  including schema creation, initial data sources, and all the payload gotchas.
- **Sharing pages to the web or enabling duplicates:** The API does not support
  these UI-only features; file a decision for manual action instead.
- **Querying workspaces you don't have access to:** Token scope is limited to
  the root page subtree; other workspaces/spaces are unreachable.

---

**Last Updated:** 2026-09-30  
**Token tested:** 2026-09-30 (24 tools confirmed live)
