---
name: mcp-influxdb
description: Query and write InfluxDB time-series metrics via the `influxdb` MCP server (buckets, Flux queries, recent metrics, measurements, writes). Use when a task needs to check historical/time-series metrics, write a new data point, or debug why a metrics dashboard shows no data. Also use when an influxdb tool call "succeeds" (isError: false) but the text content clearly describes a connection or query error — see the gotcha below before trusting the isError flag.
---

# InfluxDB MCP

The `influxdb` MCP server (proxy name `influxdb`, Python FastMCP server at
`/Users/charlieseay/Projects/influxdb-mcp/src/influxdb_mcp/server.py`,
version string reports "InfluxDB 1.27.0" at the MCP protocol level — that's
the MCP SDK version, not the actual InfluxDB database version) talks to a
real InfluxDB v2-style HTTP API at `http://localhost:8086` (`BASE`,
hardcoded, server.py line 11).

**Auth:** token loaded from `/Volumes/data/secrets/helmsman_influxdb_token`
(server.py line 12, `TOKEN_PATH`), sent as `Authorization: Token <value>`.

## Critical gotcha #1: `isError: false` does not mean the call succeeded

Confirmed live (2026-10-01): calling `buckets_list()` when the InfluxDB
backend isn't reachable from the current network context returns:
```json
{"result": {"content": [{"type": "text", "text": "Error listing buckets: [Errno 61] Connection refused"}], "structuredContent": {"result": "Error listing buckets: [Errno 61] Connection refused"}, "isError": false}}
```
**`isError` is `false` even though the text content is plainly an error
message.** This is a server-side bug (every tool catches its own exceptions
and returns the message as normal text output rather than setting
`isError: true`) — don't trust the flag. **Always check whether the result
text starts with "Error "** before treating a call as successful.

## Critical gotcha #2: org ID is auto-derived from the FIRST bucket, not configured

`_get_org_id()` (server.py lines 32-52) does not read a configured org ID —
it calls `GET /api/v2/buckets`, takes the **first bucket in the response**,
and reads its `orgID` field, caching that for the rest of the process
lifetime. **If InfluxDB has zero buckets, every query/write tool fails** with
"Cannot determine InfluxDB org ID. No buckets found or API error." **If
InfluxDB ever hosts more than one org**, this will silently resolve to
whichever org's bucket happens to sort first in the API response — not
necessarily the org you intended. There is no parameter to override this.

## Tool catalog (5 tools, confirmed live via direct MCP handshake 2026-10-01)

- `buckets_list()` — no args. Lists all buckets with retention periods.
- `query_flux(flux)` — run a raw Flux query, returns CSV-like text. Example
  from the tool's own description: `from(bucket:'governor') |> range(start:
  -1h) |> filter(fn: (r) => r._measurement == 'cpu')`
- `metrics_recent(bucket, measurement="", hours=1, limit=20)` — convenience
  wrapper over a Flux range query; use this instead of hand-writing Flux for
  the common "show me the last N points" case.
- `measurements_list(bucket)` — list measurement names in a bucket (useful
  before `metrics_recent` if you don't know what's actually being recorded).
- `write_point(bucket, measurement, fields, tags="")` — write one line-protocol
  point. `fields` format is `"key=value,key2=value2"`, `tags` same shape.
  Example from source: `measurement='test', fields='value=42.0'`.

## Quick verification pattern

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"buckets_list","arguments":{}}}' \
  | /Users/charlieseay/Projects/influxdb-mcp/.venv/bin/influxdb-mcp
```
If the result text contains "Connection refused", the InfluxDB backend at
`localhost:8086` isn't reachable from wherever this is run — check that
you're running it in a context with access to that port (the MCP server
process itself starts fine even when the backend is down; don't mistake a
clean server startup for a working connection).
