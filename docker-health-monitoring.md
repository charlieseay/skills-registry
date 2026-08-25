# Docker Health Monitoring & Auto-Restart — Production Patterns

**Category:** infrastructure  
**Priority:** HIGH  
**Created:** 2026-08-20  
**Status:** active  
**Confidence triggers:** Docker health, container restart, OOM, stale containers, docker monitor, container health checks

---

## When to Use This Skill

Use this skill when:
- Setting up Docker health monitoring
- Debugging OOM kills or container crashes
- Fixing stale container detection issues
- Implementing auto-restart for unhealthy containers
- Working on production Docker infrastructure

**Anti-patterns this skill prevents:**
- Bridge OOM kill at 07:00 CT with no auto-restart (lesson)
- Stale containers showing "Up 3 days" after rebuild (deployment gap)
- Docker monitor crashes on deleted infrastructure references (Postiz lesson)

---

## The Solutions

### 1. docker-autoheal (Primary Recommendation)

**Source:** [willfarrell/docker-autoheal](https://github.com/willfarrell/docker-autoheal) — 3.9K stars

**What it does:** Monitors Docker health checks and auto-restarts unhealthy containers.

#### Setup

```yaml
# docker-compose.yml
services:
  autoheal:
    image: willfarrell/autoheal:latest
    container_name: autoheal
    restart: always
    environment:
      - AUTOHEAL_CONTAINER_LABEL=all  # Monitor all containers
      - AUTOHEAL_INTERVAL=5           # Check every 5 seconds
      - AUTOHEAL_START_PERIOD=30      # Grace period on startup
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

#### Add Health Checks to Your Services

```yaml
services:
  bridge:
    image: bridge:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8117/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    # autoheal will restart this if health check fails
```

**Result:** Any service with a health check that fails 3 times in a row gets auto-restarted by autoheal.

---

### 2. DockMon (Modern Alternative)

**Source:** [darthnorse/dockmon](https://github.com/darthnorse/dockmon) — Modern, 2026

**Key features:**
- External health checks (more reliable than Docker built-in)
- Slack/email alerts
- Web dashboard
- Dependency-aware restarts

#### Setup

```yaml
services:
  dockmon:
    image: darthnorse/dockmon:latest
    container_name: dockmon
    restart: always
    ports:
      - "3030:3030"  # Web dashboard
    environment:
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK}
      - CHECK_INTERVAL=30
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./dockmon.yml:/config/dockmon.yml
```

```yaml
# dockmon.yml
monitors:
  - name: bridge
    container: bridge
    check:
      type: http
      url: http://localhost:8117/api/health
      expected_status: 200
    restart_on_failure: true
    alert_channels: [slack, email]
```

---

### 3. Dependency-Aware Monitoring

**Source:** [ondrovic/docker-watchdog](https://github.com/ondrovic/docker-watchdog)

**Use case:** Automatically restart dependent containers when dependencies fail.

```yaml
# Example: If helmsman-db restarts, also restart bridge + stdout
services:
  watchdog:
    image: ondrovic/docker-watchdog:latest
    environment:
      - DEPENDENCIES=helmsman-db:bridge,stdout|postgres:helmsman-db
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

**Pattern:** `dependency:dependent1,dependent2|dependency2:dependent3`

---

## OOM Prevention Patterns

### 1. Memory Limits + Restart Policy

```yaml
services:
  bridge:
    image: bridge:latest
    mem_limit: 2g
    mem_reservation: 1g
    restart: unless-stopped  # Restart on OOM, but respect manual stops
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8117/api/health"]
      interval: 30s
```

**Why `unless-stopped` over `always`:**
- Respects manual `docker stop` commands
- Restarts on daemon restart
- Restarts on OOM kill
- Best for production services

### 2. OOM Kill Detection

```bash
# Check for OOM kills in logs
docker inspect bridge | jq '.[0].State.OOMKilled'

# Monitor memory usage
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

### 3. Healthcheck for Memory Usage

```yaml
services:
  bridge:
    healthcheck:
      test: |
        sh -c 'memory=$(free | awk "/Mem:/ {printf \"%.0f\", \$3/\$2 * 100}");
        [ $memory -lt 90 ] || exit 1'
```

---

## Stale Container Detection

### Problem: "Up 3 days" After Rebuild

**Root cause:** `docker compose up -d` reuses existing containers if nothing changed.

**Fix:** Force recreate

```bash
# Option 1: Force recreate specific service
docker compose up -d --force-recreate bridge

# Option 2: No-cache rebuild + recreate
docker compose build --no-cache bridge
docker compose up -d --force-recreate bridge

# Option 3: Remove old container first
docker compose down bridge
docker compose up -d bridge
```

### Automated Detection Script

```bash
#!/bin/bash
# check-stale-containers.sh

IMAGE_BUILT=$(docker inspect bridge --format='{{.Created}}')
CONTAINER_STARTED=$(docker inspect bridge --format='{{.State.StartedAt}}')

if [[ "$IMAGE_BUILT" > "$CONTAINER_STARTED" ]]; then
  echo "⚠️  Container is stale! Image built after container started."
  echo "Image:     $IMAGE_BUILT"
  echo "Container: $CONTAINER_STARTED"
  echo "Running: docker compose up -d --force-recreate bridge"
  docker compose up -d --force-recreate bridge
fi
```

---

## Integration with Existing Systems

### For Bridge

```yaml
# /Volumes/data/containers/bridge/docker-compose.yml
services:
  bridge:
    image: bridge:latest
    mem_limit: 2g
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8117/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      - "autoheal=true"  # Monitor with docker-autoheal

  autoheal:
    image: willfarrell/autoheal:latest
    restart: always
    environment:
      - AUTOHEAL_CONTAINER_LABEL=autoheal
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

### For StdOut (ThinkPad)

```yaml
# ThinkPad 192.168.68.89
services:
  stdout:
    image: stdout:latest
    mem_limit: 1g
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8112/health"]
      interval: 30s
    labels:
      - "autoheal=true"
```

---

## Monitoring & Alerts

### Health Check Metrics

```bash
# Check health status of all containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"

# Only show unhealthy containers
docker ps --filter "health=unhealthy" --format "{{.Names}}"
```

### Slack Alerts (via DockMon)

```yaml
# dockmon.yml
alerts:
  slack:
    webhook_url: "${SLACK_WEBHOOK}"
    template: |
      🚨 Container ${container} is ${status}
      Health check: ${health_check}
      Logs: ${logs_tail}
```

---

## References

- [willfarrell/docker-autoheal](https://github.com/willfarrell/docker-autoheal)
- [darthnorse/dockmon](https://github.com/darthnorse/dockmon)
- [hkotka/docker-container-watchdog](https://github.com/hkotka/docker-container-watchdog)
- [ondrovic/docker-watchdog](https://github.com/ondrovic/docker-watchdog)

---

## Quick Start Checklist

- [ ] Add health checks to all production services
- [ ] Deploy docker-autoheal sidecar
- [ ] Set memory limits + `unless-stopped` restart policy
- [ ] Test: Kill a container, verify auto-restart
- [ ] Add OOM detection to monitoring
- [ ] Document health check endpoints for each service

---

**Last Updated:** 2026-08-20  
**Confidence score:** 0.90 for "Docker health", "OOM", "container monitoring"
