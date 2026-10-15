---
name: containers
category: development
description: Work with Docker containers and compose files
triggers:
  patterns:
  - docker
  - container
  - compose
  - docker-compose
  contexts:
  - deployment
  - infrastructure
  - development
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when work with docker containers and compose files
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 15
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Manage Docker containers on your home lab via MCP tools.

## Usage
- `/containers health` — run health check on all services, interpret results, flag issues
- `/containers logs [service] [lines]` — tail container logs (default 50 lines)
- `/containers restart [service]` — restart a container and verify it came back up
- `/containers shell [service] [cmd]` — execute a read-only command inside a container
- `/containers status` — show all container statuses (running, stopped, health)

If no action is provided, show the usage list above and ask what the user needs.

---

## Actions

### status

Show all container statuses in a clean table format.

1. Call `mcp__claude_ai_claudecp__docker_status` to get container states
2. Present results as a table: **Container | Status | Health | Uptime**
3. Flag any containers that are stopped, unhealthy, or restarting
4. If any containers are down, suggest next steps (check logs, restart)

### health

Run a full health check across all monitored services.

1. Call `mcp__claude_ai_claudecp__service_health_check` to check all 21 services (internal + external)
2. Call `mcp__claude_ai_claudecp__system_info` for disk usage, CPU, memory, Docker stats
3. Present results in two sections:
   - **Service Health** — table of all services with pass/fail status. Group failures at the top.
   - **System Resources** — disk usage, CPU load, memory pressure. Flag anything above 85% utilization.
4. If issues are found:
   - Check if the issue is auto-resolvable (e.g., a container just needs a restart)
   - If resolvable: fix it silently, verify the fix, and report what was done
   - If NOT resolvable: flag it clearly and recommend next steps
   - Only send a Telegram alert (`mcp__claude_ai_claudecp__send_telegram`) if auto-fix fails — never alert for issues that were resolved automatically

### logs

Tail container logs for a specific service.

1. Parse the service name and optional line count from the arguments (default: 50 lines)
2. Call `mcp__claude_ai_claudecp__docker_logs` with the service name and line count
3. Present the logs with:
   - Errors and warnings highlighted (call them out explicitly)
   - A brief summary of what the logs show (healthy operation, errors, startup issues, etc.)
4. If errors are present, suggest potential causes and next steps

### restart

Restart a container and verify it recovered.

1. Parse the service name from the arguments
2. Determine if this is a single container or a compose stack:
   - **Compose stacks** (n8n, arr, authentik) — use `mcp__claude_ai_claudecp__docker_compose_restart`
   - **Individual containers** — use `mcp__claude_ai_claudecp__docker_restart`
3. Only allowlisted containers can be restarted — if the MCP tool rejects the request, report the error and do not retry
4. After restart, verify recovery:
   - Call `mcp__claude_ai_claudecp__docker_status` to confirm the container is running
   - Wait a few seconds, then check logs for startup errors
5. **n8n special case:** After restarting n8n, cron triggers re-register automatically. Mention this in the report so the user knows scheduled workflows will resume.
6. Report: container name, previous state, current state, any startup warnings

### shell

Execute a read-only command inside a container.

1. Parse the service name and command from the arguments
2. Call `mcp__claude_ai_claudecp__docker_exec` with the service and command
3. The MCP tool only allows safe read-only commands: `cat`, `ls`, `df`, `ps`, `env`, `whoami`, `hostname`, `id`, `uname`, `uptime`, `free`, `top -bn1`, `netstat`, `ss`, `ip`, `ifconfig`, `ping`, `nslookup`, `dig`, `curl`, `wget`, `head`, `tail`, `wc`, `du`, `find`, `grep`, `awk`, `sed` (read-only), `printenv`, `date`, `stat`
4. If the command is rejected (not in the allowlist), explain the security boundary and suggest an allowed alternative
5. Present the output cleanly — format as a code block if it's structured data

---

## Key Rules

- **TZ=America/Chicago** — all containers run in Central time. Timestamps in logs reflect this.
- **NPM forward hostname:** `host.docker.internal:<port>` — not `localhost` or the LAN IP from inside Docker.
- **Security boundary:** `docker_exec` is read-only. `docker_restart` is allowlisted. Do not attempt to work around these limits.
- **Alert policy:** Only send Telegram alerts when auto-fix fails. If an issue is resolvable, fix it silently and log the action. Do not spam notifications for transient issues.
- **n8n cron triggers:** After any n8n restart, cron triggers re-register automatically. No manual intervention needed.
- **Compose stacks vs individual containers:** n8n, arr, and authentik are multi-container stacks managed by `docker_compose_restart`. Everything else uses `docker_restart`.

## Notes
- MCP tools are provided by the Vault MCP server (`claude.ai/claudecp`)
- The server runs all containers at `[your-server-ip]`, but Docker containers use `host.docker.internal` for host access
- Service health checks cover 21 services (internal and external endpoints)
- System info includes disk, CPU, memory, and Docker-level stats
