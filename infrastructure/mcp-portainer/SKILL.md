---
name: mcp-portainer
description: Docker container management via Portainer API through the `portainer` MCP server (5 tools). List containers, view logs, start/stop/restart containers, check resource usage (CPU/memory), and list Docker images. Use when you need to manage containers running in the local Docker environment without SSH or CLI access.
---

# Portainer MCP

The `portainer` MCP server (proxy name `portainer`, Python bridge at `/Users/charlieseay/Projects/portainer-mcp/.venv/bin/portainer-mcp`) is a wrapper around the Portainer API. It connects to a **local Portainer instance at `https://localhost:9443/api`** and proxies container/image management calls. All 5 tools confirmed live against source at `/Users/charlieseay/Projects/portainer-mcp/src/portainer_mcp/server.py:78-244`.

**Auth requirement**: Portainer API token at `/Volumes/data/secrets/code_server_portainer_token` (48 bytes, loaded automatically by the bridge). The bridge reads this file; agents never need to see the token.

**Certificate note**: The bridge connects to `https://localhost:9443` (Portainer's default secure port) with `verify=False` (self-signed cert bypassed). This is intentional for local-only access.

## Quick patterns before calling any tool

**Container identification**: Use container **name** (without leading `/`) to reference a container, e.g., `nginx`, `postgres_prod`. The tool also accepts **partial container ID match** if you use the first 12+ hex characters.

**Container state**: Tools use Portainer's state values:
- `running` — container is up
- `created`, `exited`, `paused` — container exists but is not running
- Use `all_containers=true` in `containers_list` to include stopped containers

**Endpoint discovery**: The server auto-discovers the local Docker endpoint (Type=1 in Portainer's endpoint list). If multiple endpoints exist, it picks the first local Docker endpoint. Fallback is endpoint ID 1.

**Error handling**: Network errors (e.g., Portainer down) return "Error: Could not connect..." messages. API auth errors return "Error: Portainer API returned 401" or similar with the status code.

## Tool catalog (5 tools, verified live 2026-10-01 against source)

**`containers_list`** — List Docker containers.
- `all_containers` (boolean, optional): If true, include stopped containers. Default: false (running only)
- Returns: Formatted table with columns: name | state | image | container_id (12-char prefix)
- Example output:
  ```
  nginx | running | nginx:latest | a1b2c3d4e5f6
  postgres | exited | postgres:15 | b2c3d4e5f6a1
  ```
- Returns "No containers found." if empty
- **State values** include: running, exited, created, paused, restarting, removing, dead

**`container_logs`** — Get recent logs from a container by name or ID.
- `name` (string, required): Container name (without `/`) or partial/full container ID
- `tail` (integer, optional): Number of lines to return (default: 50, no enforced max but very large values may timeout)
- Returns: Formatted log lines (last `tail` lines only)
- Returns error "Container 'X' not found." if container doesn't exist
- Captures both stdout and stderr

**`container_action`** — Start, stop, or restart a container by name.
- `name` (string, required): Container name or partial container ID
- `action` (string, required): Must be exactly `start`, `stop`, or `restart`
- Returns: Confirmation message "Container 'X' started successfully." or error with status code
- Returns error if action is not one of the three valid values
- Returns error "Container 'X' not found." if container doesn't exist
- **Stopping a container** is graceful (SIGTERM) by default; Portainer waits for graceful shutdown before force-killing
- **Restarting** is equivalent to stop then start

**`containers_stats`** — Get CPU and memory usage for all running containers.
- No parameters
- Returns: Formatted table with columns: name | CPU: X.X% | Mem: YMB/ZMB
- Limits to top 10 running containers (API performance optimization)
- CPU percentage is calculated from delta since last stats snapshot
- Memory is in MB (usage/limit); limit is the container's memory cap (or host total if no cap)
- Returns "No running containers found." if no containers are running
- Skips containers if stats fetch fails (e.g., paused containers)
- Sorted by memory usage (descending)
- Example output:
  ```
  postgres | CPU: 2.3% | Mem: 256MB/2048MB
  nginx | CPU: 0.1% | Mem: 12MB/512MB
  ```

**`images_list`** — List Docker images with size and tags.
- No parameters
- Returns: Formatted table with columns: tags (comma-separated) | size in MB
- Lists all images; filter for specific tags manually
- Tag format includes registry prefix if present (e.g., `ghcr.io/owner/image:latest`)
- Untagged images show as `<none>`
- Returns "No images found." if no images exist
- Example output:
  ```
  nginx:latest, nginx:1.25 | 187 MB
  postgres:15, postgres:latest | 423 MB
  <none> | 512 MB
  ```

## Known environment facts

- **Portainer instance**: Runs at `https://localhost:9443` (hardcoded in server.py:10)
- **API base URL**: `https://localhost:9443/api` (server.py:10)
- **Token location**: `/Volumes/data/secrets/code_server_portainer_token` (server.py:19)
- **Local Docker endpoint**: Auto-discovered; assumes "Type=1" (Docker) endpoint exists
- **SSL verification**: Disabled (`verify=False` in server.py:29) — self-signed certs accepted for local access

If Portainer is not running at `https://localhost:9443`, the tools will fail with "Error: Could not connect to Portainer API..." — this indicates Portainer is down or listening on a different port.

## Gotchas and limitations

**Portainer down**: If the Portainer instance is not running or unreachable at `https://localhost:9443`, all tools return connection errors. Restart Portainer to fix.

**Container name resolution**: Tools search for containers by exact name (with leading `/` stripped) or partial ID match. If two containers have similar names, use more specific matching or the full ID.

**Stats limited to 10 containers**: `containers_stats` only fetches stats for the top 10 running containers to avoid slow API calls. If you need stats for a specific container not in the top 10, use individual container API calls (not exposed in this skill).

**No container creation/deletion in this skill**: These 5 tools are view/control only. Creating or deleting containers requires direct Portainer/Docker CLI access. Modifying the portainer-mcp source would be needed to expose those operations.

**Image list shows all images**: There's no filter parameter; you must filter by tag or name manually from the output.

**Logs may be truncated**: Very large log buffers may timeout or be truncated by the API. For long-running containers, consider piping logs to a file or using the Docker CLI directly.

**No live log streaming**: `container_logs` returns a snapshot of recent logs, not a live stream. Call repeatedly to poll for new logs.

## Quick verification pattern for this skill

```bash
# Test that Portainer is reachable and the token is valid
TOKEN=$(cat /Volumes/data/secrets/code_server_portainer_token)
curl -s -k -H "X-API-Key: $TOKEN" \
  https://localhost:9443/api/endpoints | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print('PASS: Portainer reachable' if d else 'FAIL')"
```

If this fails:
- Check that Portainer is running: `docker ps | grep portainer`
- Verify the token file exists: `ls -la /Volumes/data/secrets/code_server_portainer_token`
- Verify the token is readable: `cat /Volumes/data/secrets/code_server_portainer_token` (should output ~48 chars)
- Check that Portainer is listening on port 9443: `lsof -i :9443` or `netstat -tulpn | grep 9443`
