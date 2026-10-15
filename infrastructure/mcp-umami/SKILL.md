---
name: mcp-umami
description: Web analytics via Umami self-hosted instance. Query website stats (pageviews/visitors/sessions), time-series pageview data, top pages. Connects to http://localhost:3010; admin password from /Volumes/data/secrets/umami_admin_password. Real-time analytics dashboarding.
---

# Umami Analytics MCP

The `umami` MCP server (proxy name `umami`, Python FastMCP launcher at
`/Users/charlieseay/Projects/umami-mcp/.venv/bin/umami-mcp`) exposes the
**Umami analytics** self-hosted instance (http://localhost:3010) as MCP tools.
Umami is a privacy-friendly, open-source alternative to Google Analytics. This
MCP provides website statistics, pageview trends, referrer data, and visitor
insights for sites tracked by your Umami instance.

**Auth:** Uses admin username ("admin") + password from
`/Volumes/data/secrets/umami_admin_password`. The server logs in once and
reuses the session token for subsequent requests. Token is cached in memory
(global `_token`); if it expires, the next request detects 401 and refreshes.

**Use cases:** Real-time dashboards, analytics briefings, traffic audits, event
tracking queries for websites running under your Umami instance.

## Tool catalog (6 tools, tested live 2026-09-30 against /Users/charlieseay/Projects/umami-mcp/src/umami_mcp/server.py:45-117)

**Browse websites:**
- `websites_list()` → str
  - List all websites tracked in your Umami instance.
  - **Parameters:** none
  - **Returns:** Newline-separated text; each line is:
    ```
    • Website Name (id=<ID>, domain=example.com)
    ```
  - **Example output:**
    ```
    • My Blog (id=1, domain=blog.example.com)
    • Product Landing (id=2, domain=product.example.com)
    • Internal Docs (id=3, domain=docs.internal.local)
    ```
  - **Usage:** Call this first to get website IDs for other tools.

**Get summary statistics:**
- `website_stats(website_id, start_at=0, end_at=0)` → str
  - Summary stats for a website over a time range.
  - **Parameters:**
    - `website_id` (string, required) — website ID from `websites_list()`
    - `start_at` (int, default 0) — Unix timestamp in milliseconds. 0 = 7 days ago.
    - `end_at` (int, default 0) — Unix timestamp in milliseconds. 0 = now.
  - **Returns:** Single line with summary metrics:
    ```
    Pageviews: 1523, Visitors: 487, Sessions: 612, Bounce rate: 0.34
    ```
  - **Example:**
    ```
    website_stats(website_id="1")
    → "Pageviews: 1523, Visitors: 487, Sessions: 612, Bounce rate: 0.34"
    ```
  - **Time range note:** Defaults to last 7 days if start/end are 0. Pass Unix
    milliseconds for custom ranges (e.g., `end_at=int(time.time()*1000)` for now).

**Get pageview time series:**
- `website_pageviews(website_id, days=7, unit="day")` → str
  - Pageview trends over time (hourly, daily, weekly, or monthly).
  - **Parameters:**
    - `website_id` (string, required) — website ID
    - `days` (int, default 7) — lookback period in days
    - `unit` (string, default "day") — time granularity: "hour", "day", "week", "month"
  - **Returns:** Markdown table:
    ```
    Date | Pageviews | Sessions
    ---|---|---
    2026-09-30 | 250 | 120
    2026-09-29 | 310 | 145
    ...
    ```
  - **Example:**
    ```
    website_pageviews(website_id="1", days=7, unit="day")
    → Markdown table with 7 rows (one per day)
    ```
  - **Granularity options:**
    - `unit="hour"` → hourly breakdown (24+ rows for 7 days)
    - `unit="day"` → daily (7 rows)
    - `unit="week"` → weekly (1 row per week)
    - `unit="month"` → monthly (1 row per month)

**Get top pages (aggregate pageviews):**
- `website_top_pages(website_id, days=7, limit=10)` → str
  - Total pageviews over a period.
  - **Parameters:**
    - `website_id` (string, required)
    - `days` (int, default 7) — lookback period
    - `limit` (int, default 10) — max pages (currently ignored; returns aggregate only)
  - **Returns:** Single line with total:
    ```
    Total pageviews over 7 days: 8491 (per-page breakdown requires Umami metrics API)
    ```
  - **Limitation:** The tool does **not** return per-page breakdown (that requires
    Umami's metrics/details endpoint, which is not implemented). Use this for
    total pageview count only; check the Umami web UI for top pages.

**Get referrers:**
- `website_referrers(website_id, days=7, limit=10)` → str
  - Top traffic sources / referrers for a website.
  - **Parameters:**
    - `website_id` (string, required)
    - `days` (int, default 7)
    - `limit` (int, default 10)
  - **Returns:** Static message:
    ```
    Referrer data requires Umami metrics endpoint (currently unavailable). Check the Umami dashboard directly.
    ```
  - **Status:** This tool is **not implemented**. Referrer data requires Umami's
    metrics API, which is not exposed by this MCP. Use the web UI instead.

**Placeholder (unused in this test):**
- No additional tools detected.

## Umami API specifics

**Base URL:** http://localhost:3010 (configured in server.py:10)

**Key endpoints used:**
- `POST /api/auth/login` → authenticate (returns Bearer token)
- `GET /api/websites` → list all tracked websites
- `GET /api/websites/<id>/stats?startAt=X&endAt=Y` → summary stats
- `GET /api/websites/<id>/pageviews?startAt=X&endAt=Y&unit=day` → pageview time series

**Auth flow:**
1. POST to `/api/auth/login` with username="admin" and password from `/Volumes/data/secrets/umami_admin_password`
2. Response includes `token` (Bearer token)
3. All subsequent requests use `Authorization: Bearer <token>` header

**Token refresh:**
- If a request returns 401 Unauthorized, the cached token is cleared (`_token = None`)
- Next request attempts login again automatically

## Known issues & workarounds (tested 2026-09-30)

**1. Admin password must exist at `/Volumes/data/secrets/umami_admin_password`**
- If the file doesn't exist, startup fails with FileNotFoundError.
- **Fix:** Create the secrets file:
  ```bash
  echo "your_umami_admin_password" > /Volumes/data/secrets/umami_admin_password
  chmod 600 /Volumes/data/secrets/umami_admin_password
  ```

**2. Umami service must be running at http://localhost:3010**
- If Umami is stopped or on a different port, all tool calls fail immediately.
- **Fix:** Start Umami (Docker, binary, or systemd). Confirm with:
  ```bash
  curl -s http://localhost:3010 | head -20
  ```

**3. Website IDs are numeric; you must know the ID to query stats**
- `website_stats(website_id="1")` retrieves stats for website #1.
- To find IDs, call `websites_list()` first.
- **Workaround:** No way to filter by domain name; must use ID lookup.

**4. Time ranges use Unix milliseconds, not seconds**
- `start_at` and `end_at` are Unix timestamps **in milliseconds**, not seconds.
- Example: `int(time.time() * 1000)` is now in milliseconds.
- **Common error:** Passing seconds (e.g., `int(time.time())`) results in
  dates in 1970 (or way in the future), with no pageviews returned.
- **Fix:** Always multiply by 1000: `start_at = int((time.time() - 7*86400) * 1000)`

**5. Bounce rate is not a percentage; it's a ratio or count**
- The stat returned is labeled "bounce rate" but may be a ratio (0–1) or raw count.
- **Interpretation unclear:** 0.34 could mean 34% bounce rate or 34 bounces. Check Umami dashboard for ground truth.

**6. Per-page breakdown is not available via MCP**
- `website_top_pages()` returns only total pageviews, not per-page data.
- The endpoint exists in Umami (metrics/details API) but is not implemented in this MCP.
- **Workaround:** Use Umami web UI (http://localhost:3010) for top pages report.

**7. Referrer data is not available via MCP**
- `website_referrers()` always returns "not implemented" message.
- **Workaround:** Use Umami web UI for referrer insights.

**8. No custom event tracking via MCP**
- This MCP reads stats only; it doesn't track events, goals, or conversions.
- Custom events must be sent directly to Umami (via JavaScript library in web pages).

**9. Token caching is per-server process**
- The token is stored in a global variable (`_token`) in the MCP process.
- If the process restarts (proxy restart), the token is lost and a new login is needed.
- If the token expires server-side (before refresh), the MCP detects 401 and re-authenticates.

**10. No analytics data export**
- MCP reads stats but doesn't export to CSV, JSON, or other formats.
- **Workaround:** Use Umami web UI export feature or query the raw database.

## Real-world example: Daily analytics check

```
1. websites_list()
   → List all tracked sites, find IDs

2. website_stats(website_id="1", days=7)
   → Get summary (pageviews, visitors, sessions)

3. website_pageviews(website_id="1", days=7, unit="day")
   → Get daily trend (table of dates + pageviews)

4. website_top_pages(website_id="1", days=7)
   → Get total pageviews for the period
   → (Note: per-page breakdown requires web UI)
```

## Quick self-check

**Confirm Umami is running:**
```bash
curl -s http://localhost:3010 | head -20
```

Should return HTML (Umami web UI). If it times out or 404, Umami is down.

**Confirm admin password is readable:**
```bash
cat /Volumes/data/secrets/umami_admin_password
```

Should print non-empty string (your Umami admin password).

**Test login:**
```bash
curl -s -X POST http://localhost:3010/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"$(cat /Volumes/data/secrets/umami_admin_password)\"}" | jq .
```

Should return a JSON object with `token` field (a long Bearer token string).
