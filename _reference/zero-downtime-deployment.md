# Zero-Downtime Deployment — Blue-Green with Health Gates

**Category:** deployment  
**Priority:** MEDIUM  
**Created:** 2026-08-20  
**Confidence triggers:** zero downtime, deployment, health check, rollback, docker compose, blue-green

**Source:** [wowu/docker-rollout](https://github.com/wowu/docker-rollout)

## Quick Start

```bash
# Install
npm install -g docker-rollout

# Deploy with health-gated swap
docker-rollout my-service

# What it does:
# 1. Builds new version
# 2. Starts alongside old version
# 3. Waits for health check to pass
# 4. Swaps traffic to new version
# 5. Removes old version
# 6. If health fails → discards new, keeps old
```

## Integration

```yaml
# docker-compose.yml
services:
  my-service:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 10s
      retries: 5
```

```bash
# Deploy script
docker-rollout my-service  # Automatic health-gated swap
```

## Rollback

```bash
# Keeps last 10 deployments
docker-rollout rollback my-service
```

**Fixes:** Stale container detection, manual deployment verification gaps

**References:** [wowu/docker-rollout](https://github.com/wowu/docker-rollout), [shipzero/zero](https://github.com/shipzero/zero)
