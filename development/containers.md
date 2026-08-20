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

## Lessons

- **2026-06-15** — `docker_restart_stale_image`: Always rebuild the Docker image before restarting — docker restart re-runs the old image, not the new code _(context: Bridge code changes were committed but not visible because container was restarted without rebuild)_ [src: teachable-moment/bridge-docker-rebuild]
- **2026-06-15** — `gunicorn_worker_cache`: Run pkill -9 -f 'gunicorn.*<port>' before restarting any gunicorn service — workers cache old code and a plain restart re-serves the stale version _(context: helmsman-db server changes not taking effect; pkill forced fresh worker spawn)_ [src: teachable-moment/gunicorn-cache]
- **2026-06-15** — `fly_secrets_env_not_files`: On Fly.io, read secrets via os.environ not file paths — Fly injects secrets as env vars, not /run/secrets files _(context: enchapter TTS uploads silently failed because code tried to read /run/secrets/key which doesn't exist on Fly)_ [src: memory/feedback_fly_secrets_env_not_files]
- **2026-06-15** — `macos_bash32_ifs_strips_x01`: Pin shebang to /opt/homebrew/bin/bash when using IFS=$'\x01' — macOS /bin/bash 3.2 silently strips \x01 in here-string reads _(context: dispatch scripts were dropping fields 2+ silently; fixed by switching shebang)_ [src: memory/feedback_macos_bash_3_2_strips_x01]
- **2026-06-15** — `l_xl_tasks_must_be_decomposed_into_phase`: L/XL tasks MUST be decomposed into phase-linked S/M task chains. Each phase is a separate task with clear success criteria and artifact handoff. Benefits: (1) Real-time progress tracking in Bridge, (2) Know exactly which phase failed, (3) Resume from checkpoint not scratch, (4) Token efficient, (5) Better troubleshooting. Pattern: Phase 1 (S) -> Phase 2 (M) -> Phase 3 (S). Each phase blocked_by previous, chains_to next. Example: Install Hermes becomes: Phase 1 Find URL (S), Phase 2 Download (S), Phase 3 Install (S), Phase 4 Configure (M), Phase 5 Test (S). Applies to ALL tasks: Talos jobs, internal services, workflows, microservices, research, everything. Standard: Standards/Task Decomposition Standard.md [src: task-unknown]
- **2026-06-15** — `home_assistant_restart_takes_15__minutes`: Home Assistant restart takes 15+ minutes (Raspberry Pi with many integrations), not 2-3 minutes. Monitor with 30-second intervals for minimum 20 minutes (40 checks). Pattern: offline → HTTP errors → HTTP 200. _(context: HA restart monitoring timed out because we expected 2-3 minutes. Actual restart was faster but can take up to 15 minutes. Must build longer timeouts.)_ [src: task-unknown]
- **2026-06-15** — `network_ping___ha_integration_health__al`: Network ping ≠ HA integration health. Always check both: (1) ping for physical connectivity, (2) /api/config/config_entries/entry for integration state. Device online + integration setup_retry = will not connect. _(context: Aqara Hub responded to ping but stayed unavailable because Matter integration was stuck in setup_retry. Two failure domains: network layer vs HA integration layer.)_ [src: task-unknown]
- **2026-06-16** — `volumes_data_tcc_blocks_launchd`: Background/launchd jobs cannot read /Volumes/data (external volume, TCC 'Operation not permitted') even as the owning user; mirror needed secrets to ~/.config (0700) and read those in launchd contexts. _(context: 287 secrets unreadable by launchd, all alerting/backup silently failed for days. Home-dir mirror + sync-on-checkpoint fixed it.)_ [src: session/2026-06-15-trust-signal]
- **2026-06-16** — `launchd_no_local_bin_on_path`: launchd/cron jobs do NOT have ~/.local/bin on PATH; call helper tools by absolute path or 'not found' silently kills the job. _(context: slack-post-filtered did exec slack-post, not found in launchd, alerting dead.)_ [src: session/2026-06-15-trust-signal]
- **2026-06-16** — `watchdog_periodic_vs_daemon`: A watchdog must NOT police periodic (StartInterval) launchd jobs as always-on daemons; pid='-' is their NORMAL healthy state between runs. Only restart KeepAlive daemons. _(context: infra-watchdog false-restarted centaur-heartbeat (interval=60) every 5min, 659+ noise lines, looked like a crash loop in the audit. It was never broken.)_ [src: session/2026-06-15-trust]
- **2026-06-16** — `fly_redis_reachable_only_internal`: Fly Redis/apps are NOT reachable via public .fly.dev DNS; from a WireGuard-peered host use .internal/.flycast hostnames. A worker outside Fly needs WireGuard up + the .internal URL. _(context: tts-worker ENOTFOUND on enchapter-redis.fly.dev; MBP worker correctly used .internal over the 'fly' WG interface (+PONG). The stray Mac-Mini copy had the wrong public URL.)_ [src: session/2026-06-15-trust]
- **2026-06-16** — `vault-reading-launchd-jobs-relocate-or-retire`: launchd jobs that read the iCloud vault fail under TCC. Relocate to the checkpoint (FDA) context if needed, OR retire if a working FDA-context job already covers it. Don't leave broken launchd duplicates erroring forever. _(context: project-reconcile-nightly -> moved into checkpoint. infrastructure-sync -> retired (TCC-blocked + UnboundLocalError + duplicates sync-project-headers which checkpoint runs).)_ [src: session/2026-06-15-trust]
- **2026-06-25** — `docker_vm_data_on_volumes`: Put Docker VM data image on /Volumes/data, never the internal drive _(context: OrbStack crashed from ENOSPC on 13GB internal drive during image pulls)_ [src: session/2026-06-24-docker-migration]
- **2026-06-25** — `docker_vm_rightsize_memory`: Right-size Docker Desktop VM memory to actual container use + headroom not max; over-allocation squeezes macOS and causes 137 SIGKILLs; verify with memory_pressure free% not vm_stat _(context: 16GB VM with 5GB containers caused intermittent container SIGKILLs on 24GB Mac; lowered to 12GB)_ [src: session/2026-06-24-memory]
