---
name: mcp-grafana
description: Query Grafana dashboards, datasources, Prometheus metrics, and alerts via the custom grafana-mcp Python MCP server. Use when a task needs to fetch dashboard panels, list configured datasources, run PromQL queries, or check active alerts. Requires a Grafana service account token at `/Volumes/data/secrets/grafana_mcp_token` and assumes Grafana runs at `http://localhost:3000`.
---

# Grafana MCP

The `grafana` MCP server is a custom Python MCP implementation at
`~/Projects/grafana-mcp/.venv/bin/grafana-mcp` that queries a local Grafana
instance. Configured in `/Users/charlieseay/.config/mcp-proxy/config.json` with
no arguments (all config is in the Python source).

**Source:** `/Users/charlieseay/Projects/grafana-mcp/src/grafana_mcp/server.py`
(228 lines, uses FastMCP + httpx).

**Auth:** Service account token from
`/Volumes/data/secrets/grafana_mcp_token` (never logged, never printed).

**Grafana instance:** `http://localhost:3000` (hardcoded in server.py line 8).

## Tool catalog (5 tools, confirmed live in source 2026-09-30)

All tools return formatted text strings (not JSON structures) — useful for
reading by humans and agents, less useful for downstream parsing. If you need
machine-readable output, consider calling Grafana's HTTP API directly.

### `dashboards_list()`
**No arguments.**

Lists all dashboards with titles, UIDs, and folder names. Returns formatted
text like:
```
• My Dashboard (uid=abc123, folder=General)
• Alerting Dashboard (uid=xyz789, folder=Monitoring)
```

Use this to find a dashboard UID before calling `dashboard_get()`.

**Known behavior:**
- Empty result returns "No dashboards found."
- Includes folderTitle in output (useful for disambiguation if multiple
  dashboards have the same name in different folders).

### `dashboard_get(uid: str)`
**Arguments:**
- `uid` (string, required) — The dashboard UID (NOT the numeric ID; use the
  value from `dashboards_list()` output).

Fetches a dashboard and returns its metadata and all panels. Output format:
```
Title: My Dashboard
Description: Platform overview
Last Updated: 2026-09-30T14:22:00Z

Panels (3):
  • Request Rate (graph) — rate(http_requests_total[5m])
  • Error Rate (graph) — rate(http_errors_total[5m])
  • Latency P95 (graph) — histogram_quantile(0.95, ...)
```

**Known behavior:**
- Truncates long query expressions (shows first 2 targets per panel).
- Returns "Unknown" for missing metadata.
- Error if the UID doesn't exist ("Error fetching dashboard abc123: ...")

### `datasources_list()`
**No arguments.**

Lists all configured datasources (Prometheus, InfluxDB, Loki, etc.) with type
and URL. Output:
```
• Prometheus (prometheus) — http://prometheus:9090
• InfluxDB (influxdb) — http://influxdb:8086
• Loki (loki) — http://loki:3100
```

Use this to confirm a datasource exists before running `query_prometheus()`.

### `query_prometheus(expr: str, start: str = "now-1h", end: str = "now", step: str = "60s")`
**Arguments:**
- `expr` (string, required) — A PromQL expression (e.g., `up`, `rate(http_requests_total[5m])`)
- `start` (string, optional) — Start time for the range query. Default: `now-1h`
  - Format: Grafana time range strings (`now-1h`, `now-6h`, `2026-09-30T10:00:00Z`)
- `end` (string, optional) — End time. Default: `now`
- `step` (string, optional) — Resolution/step size. Default: `60s`

Returns a time-series table (timestamp | value pairs):
```
Timestamp | Value
2026-09-30T13:00:00+00:00 | 42.5
2026-09-30T13:01:00+00:00 | 43.1
2026-09-30T13:02:00+00:00 | 41.9
```

**Known behavior:**
- Timestamps are formatted as ISO 8601 UTC (milliseconds since epoch in the
  Grafana API, converted to readable format in the MCP output).
- Returns "No data returned for query: ..." if the metric doesn't exist or no
  data is in the range.
- Silently finds the first Prometheus datasource in the instance (doesn't let
  you choose; if multiple Prometheus sources exist, you can't pick which one
  to query).
- Empty frames return "Unexpected response format..."

**PromQL tips:**
- Simple metric: `up` (all "up" metrics across targets)
- Rate: `rate(http_requests_total[5m])` (5-minute rate of HTTP requests)
- Aggregation: `avg(node_cpu_seconds_total)` (average CPU across nodes)
- Filtering: `up{job="prometheus"}` (only Prometheus job's "up" metric)

### `alerts_list()`
**No arguments.**

Lists all active Grafana alerts (from the alerting system, not Prometheus alert
rules) with state and dashboard. Output:
```
• High CPU Alert [firing] — Infrastructure Dashboard
• Disk Low Alert [alerting] — Node Exporter
• Test Alert [paused] — Test Dashboard
```

State values: `firing`, `alerting`, `paused`, `pending`, etc. (depends on
Grafana version and alert rule definition).

## Connection & auth troubleshooting

| Problem | Check |
|---------|-------|
| "Error: No Prometheus datasource found" when calling `query_prometheus()` | Confirm Grafana at `localhost:3000` is running and has a Prometheus datasource configured |
| Authorization error ("Bearer token rejected") | Verify `/Volumes/data/secrets/grafana_mcp_token` exists and is not empty; the token must be a valid service account token in Grafana |
| Connection refused | Confirm Grafana listens on `localhost:3000` (not a different host/port) |
| Dashboard UID not found | Use `dashboards_list()` first to get the actual UID; don't guess or use the numeric ID |

## Known limitations

1. **Text output only.** All tools return formatted strings, not JSON. If you
   need to parse results programmatically or chain queries (e.g., "get the
   first dashboard's UID and fetch it"), you'll need to parse the text output.

2. **No direct Prometheus alert rules.** `alerts_list()` queries Grafana's own
   alert system, not Prometheus alert manager. If you need Prometheus alert
   rules, query Prometheus directly or use the `query_prometheus()` tool to
   check specific metrics.

3. **Single Prometheus datasource only.** `query_prometheus()` doesn't let you
   pick which Prometheus instance to query if multiple exist — it uses the
   first one it finds. If you have multiple Prometheus sources and need to
   query a specific one, you'll need to call Grafana's HTTP API directly or
   query Prometheus directly.

4. **No dashboard create/edit.** This MCP is read-only for dashboards. You
   cannot create, modify, or delete dashboards through these tools.

5. **No user/org management.** No tools to manage users, organizations, or
   permissions.

## Quick verification for this skill

```bash
# Confirm Grafana is running and accessible:
curl -s -H "Authorization: Bearer $(cat /Volumes/data/secrets/grafana_mcp_token)" \
  http://localhost:3000/api/search?type=dash-db | head -20

# Confirm the MCP server starts:
/Users/charlieseay/Projects/grafana-mcp/.venv/bin/grafana-mcp --help
```

If the first command returns a list of dashboards, Grafana is up and the token
is valid. If it fails, check:
1. Is Grafana running? (`ps aux | grep grafana`)
2. Does the token file exist? (`cat /Volumes/data/secrets/grafana_mcp_token`)
3. Is it a valid service account token? (Create one at
   `http://localhost:3000/admin/service-accounts` if unsure)

## Environment

- **MCP server:** `/Users/charlieseay/Projects/grafana-mcp/.venv/bin/grafana-mcp`
- **Source:** `/Users/charlieseay/Projects/grafana-mcp/src/grafana_mcp/server.py`
- **Config:** `/Users/charlieseay/.config/mcp-proxy/config.json`
  - No CLI args (all config hardcoded in Python source)
- **Grafana URL:** `http://localhost:3000` (line 8 in server.py)
- **Auth token location:** `/Volumes/data/secrets/grafana_mcp_token`
- **Language:** Python 3.11+, uses FastMCP + httpx
