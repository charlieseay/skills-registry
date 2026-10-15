---
name: mcp-miniflux
description: RSS feed aggregation & article management via Miniflux API. List feeds (w/ unread counts), get unread articles, search articles, read full article content, mark articles as read. API key from /Volumes/data/secrets/miniflux_api_key; connects to http://localhost:8107.
---

# Miniflux RSS MCP

The `miniflux` MCP server (proxy name `miniflux`, Python FastMCP launcher at
`/Users/charlieseay/Projects/miniflux-mcp/.venv/bin/miniflux-mcp`) exposes
**Miniflux RSS reader** API operations as MCP tools. It connects to a local
Miniflux instance (http://localhost:8107) and provides feed/article management,
unread filtering, keyword search, and full-content retrieval.

**Auth:** API key is read from `/Volumes/data/secrets/miniflux_api_key` (preferred)
or environment variable `MINIFLUX_API_KEY` (fallback). The key is injected into
the `X-Auth-Token` header on every request.

**Use cases:** Query RSS backlogs, find articles by keyword, mark feeds as read,
retrieve unread article summaries for briefing workflows (e.g., daily digest).

## Tool catalog (5 tools, tested live 2026-09-30 against /Users/charlieseay/Projects/miniflux-mcp/src/miniflux_mcp/server.py:34-199)

**Browse feeds:**
- `feeds_list()` → str
  - List all subscribed RSS feeds with unread counts.
  - **Parameters:** none
  - **Returns:** Newline-separated text; each line is:
    ```
    Feed Title (N unread) — https://feed.example.com/rss
    ```
  - **Example output:**
    ```
    Hacker News (47 unread) — https://news.ycombinator.com/rss
    TechCrunch (12 unread) — https://feeds.techcrunch.com/feed
    ```

**Get unread articles:**
- `entries_unread(limit=20, feed_id=0)` → str
  - Retrieve unread articles, optionally filtered by a specific feed.
  - **Parameters:**
    - `limit` (int, default 20) — max articles to return (Miniflux caps this server-side)
    - `feed_id` (int, default 0) — feed ID to filter on. 0 means all feeds.
  - **Returns:** Newline-separated text; each article is:
    ```
    • Article Title
      Feed Name | https://article.url
      2026-09-30T14:22:00Z
    ```
  - **Example output:**
    ```
    • "New Rust async runtime released"
      Rust Blog | https://blog.rust-lang.org/2026/09/30/async.html
      2026-09-30T14:22:00Z
    
    • "Kubernetes 1.30 launch notes"
      K8s Weekly | https://kubernetes.io/blog/2026/09/30/release.md
      2026-09-30T12:00:00Z
    ```

**Search articles:**
- `entries_search(query, limit=10)` → str
  - Search articles across all feeds by keyword.
  - **Parameters:**
    - `query` (string, required) — search keyword(s) (e.g., "Rust async", "Python 3.13")
    - `limit` (int, default 10) — max results
  - **Returns:** Newline-separated text; format same as `entries_unread()`
  - **Example:**
    ```
    entries_search(query="rust", limit=5)
    
    → "Zero-cost Rust abstractions"
      Rust Blog | https://blog.rust-lang.org/2026/...
      2026-09-28T10:15:00Z
    
    → ...
    ```
  - **Behavior:** Miniflux searches title + content; results are the first N matches.

**Read full article:**
- `entry_read(entry_id)` → str
  - Fetch the full content of a single article by ID.
  - **Parameters:**
    - `entry_id` (int, required) — article ID (from entries_unread or entries_search)
  - **Returns:** Formatted text with:
    ```
    Title: Article Title
    Feed: Feed Name
    Author: Author Name (if present)
    Published: 2026-09-30T14:22:00Z (if present)
    URL: https://article.url
    
    Content:
    [full article body with HTML stripped]
    ```
  - **Example:**
    ```
    Title: Why Rust is winning
    Feed: Rust Blog
    Author: Jane Doe
    Published: 2026-09-30T14:22:00Z
    URL: https://blog.rust-lang.org/2026/why-rust.html
    
    Content:
    Rust has been growing in adoption across... [full text]
    ```
  - **HTML stripping:** The tool strips all HTML tags from article content, leaving plain text.

**Mark articles as read:**
- `entries_mark_read(entry_ids)` → str
  - Mark one or more articles as read in bulk.
  - **Parameters:**
    - `entry_ids` (list[int], required) — list of article IDs to mark read
  - **Returns:** `"Marked N entries as read."`
  - **Example:**
    ```
    entries_mark_read([123, 456, 789])
    → "Marked 3 entries as read."
    ```
  - **Behavior:** Updates Miniflux's internal unread count for the affected feeds.

## Miniflux API specifics

**Base URL:** http://localhost:8107 (configured in server.py:9, customizable)

**API version:** /v1/ (Miniflux API versioning)

**Key endpoints used:**
- `GET /v1/feeds` → list all feeds
- `GET /v1/entries?status=unread&limit=N` → unread articles
- `GET /v1/entries?search=<query>&limit=N` → search articles
- `GET /v1/entries/<entry_id>` → fetch single article
- `PUT /v1/entries` (with `status` and `entry_ids`) → mark entries as read

**Auth header:** `X-Auth-Token: <API_KEY>`

## Known issues & workarounds (tested 2026-09-30)

**1. API key must exist at `/Volumes/data/secrets/miniflux_api_key`**
- If the file doesn't exist and `MINIFLUX_API_KEY` env var is not set, the tool
  returns empty string and API calls fail with HTTP 401 Unauthorized.
- **Fix:** Create the secrets file or set the env var before starting the MCP server.
  ```bash
  echo "your_miniflux_api_key_here" > /Volumes/data/secrets/miniflux_api_key
  chmod 600 /Volumes/data/secrets/miniflux_api_key
  ```

**2. Miniflux service must be running at http://localhost:8107**
- If Miniflux is stopped or on a different port, all tool calls timeout or fail.
- **Fix:** Start Miniflux (Docker, systemd, or binary). Confirm with:
  ```bash
  curl -s http://localhost:8107 | head -20
  ```

**3. Feed IDs are numeric; you must know the ID to filter by feed**
- `entries_unread(feed_id=42)` returns unread from feed #42 only.
- To find a feed's ID, call `feeds_list()` first and infer from the context
  (or check Miniflux dashboard for ID).
- **Workaround:** Call `feeds_list()` without filtering (feed_id=0) to get all
  feeds + all articles; then filter client-side.

**4. Search is basic keyword matching; not full-text index**
- Miniflux search (via `/v1/entries?search=`) is a **LIKE** query, not fuzzy matching.
- `entries_search(query="rust")` matches articles with "rust" in title or content.
- Typos, synonyms, and abbreviations won't match (e.g., "Rust" vs "rs" won't match).

**5. Entry IDs are **only** valid for the current feed/instance**
- An `entry_id` from one Miniflux instance is meaningless on another.
- If you store article IDs in notes and swap Miniflux instances, IDs become stale.

**6. Article content is HTML-stripped; formatting is lost**
- `entry_read()` uses `re.sub(r"<[^>]+>", "", content)` to strip tags.
- **Result:** All formatting (bold, italics, links, code blocks) is removed.
- **Consequence:** Article is readable as plain text, but layout is flat.
- **Workaround:** Use the `url` field from `entry_read()` to open the original
  article in a browser if formatting matters.

**7. Published date may be missing or incorrect**
- Some feeds omit `published_at` or use non-standard date formats.
- The tool returns `"Unknown date"` if missing; Miniflux parsed it differently.
- **Fix:** Trust the Miniflux dashboard's date view for authoritatively.

**8. Bulk marking read doesn't return status per article**
- `entries_mark_read([123, 456])` marks both or neither; no per-article status.
- If one ID is invalid, the entire call may fail or partially succeed
  (behavior depends on Miniflux version).

## Real-world example: Daily digest workflow

```
1. entries_unread(limit=50)
   → Get first 50 unread articles from all feeds

2. entries_search(query="kubernetes", limit=10)
   → Find K8s-related articles from unread

3. entry_read(entry_id=789)
   → Get full content of a specific article

4. entries_mark_read([123, 456, 789])
   → Mark those 3 articles as read in Miniflux
```

## Quick self-check

**Confirm Miniflux is running and reachable:**
```bash
curl -s http://localhost:8107/v1/feeds -H "X-Auth-Token: $(cat /Volumes/data/secrets/miniflux_api_key)" | head -20
```

Should return a JSON array of feeds. If it times out or returns 401, either
Miniflux is down or the API key is invalid.

**Confirm API key is readable:**
```bash
cat /Volumes/data/secrets/miniflux_api_key
```

Should print a non-empty string (your Miniflux API key).
