# Docker Dependency Cascade — Auto-Restart Dependents

**Category:** infrastructure  
**Priority:** MEDIUM  
**Created:** 2026-08-20  
**Confidence triggers:** Docker dependencies, container restart, cascade, dependent containers

**Source:** [ondrovic/docker-watchdog](https://github.com/ondrovic/docker-watchdog)

## Problem Solved

**docker-autoheal:** Restarts unhealthy containers  
**docker-watchdog:** Restarts **dependent** containers when dependency restarts

**Example:** helmsman-db restarts → auto-restart bridge + stdout + talos-agent

## Setup

```yaml
services:
  watchdog:
    image: ondrovic/docker-watchdog:latest
    environment:
      - DEPENDENCIES=helmsman-db:bridge,stdout,talos-agent|postgres:helmsman-db
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

**Pattern:** `dependency:dependent1,dependent2|dependency2:dependent3`

## Use Case

Services that cache DB connections break when DB restarts. This auto-restarts them.

**Complements:** `docker-health-monitoring.md` (monitors health, this handles cascades)
