# Docker Storage Cleanup — DEPRECATED (FALSE PREMISE)

**Category:** infrastructure  
**Priority:** ~~CRITICAL~~ **DEPRECATED**  
**Created:** 2026-08-20  
**Deprecated:** 2026-08-20  
**Status:** ❌ **DO NOT USE** — Based on incorrect diagnosis

**⚠️ DEPRECATION NOTICE:**

This skill was created based on a FALSE PREMISE. The diagnosis was wrong:
- **Believed:** Docker storing data on local drive at `/var/lib/docker`
- **Reality:** Docker Desktop uses `/Volumes/data/docker-desktop-data/` (external drive)
- **The path `/var/lib/docker`:** Inside the Docker VM, NOT on Mac filesystem

**See:** `Projects/Lab/Lessons/2026-08-20-docker-migration-false-premise.md` for full RCA

**For Docker Desktop cleanup on Mac, use:**
- `docker system prune` (removes unused data)
- Monitor actual Docker Desktop data: `/Volumes/data/docker-desktop-data/`
- Generic disk cleanup: See `disk-space-monitoring.md` skill instead

---

## Original Problem Statement (INCORRECT)

**Today's incident (2026-08-20):**
- ~~Mac Mini local drive filled up~~ **FALSE** — Drive had 39GB free
- ~~Docker crashed (ran out of disk space)~~ **FALSE** — Docker updated, not crashed
- ~~Docker Root Dir: `/var/lib/docker` (local drive)~~ **FALSE** — This is inside-VM path
- ~~Docker should be on `/Volumes/data/docker`~~ **FALSE** — Already on `/Volumes/data/docker-desktop-data/`

**Actual finding:**
- Docker Desktop already configured correctly
- Morning event was likely Docker Desktop auto-update (2.1GB temp artifacts)
- No migration needed

---

## Solution 1: Automated Docker Cleanup Script

```bash
#!/bin/bash
# ~/bin/docker-cleanup.sh

# Clean stopped containers
docker container prune -f

# Clean dangling images
docker image prune -f

# Clean unused volumes (BE CAREFUL)
docker volume prune -f

# Clean build cache
docker builder prune -f --filter "until=168h"  # 1 week

# Clean unused networks
docker network prune -f

# Full system prune (weekly)
if [ "$(date +%u)" -eq 7 ]; then
  docker system prune -a -f --volumes
fi
```

**Schedule:** Daily cron + weekly deep clean

```bash
# Daily cleanup (6 AM)
0 6 * * * /Users/charlieseay/bin/docker-cleanup.sh >> /tmp/docker-cleanup.log 2>&1

# Weekly full prune (Sunday 3 AM)
0 3 * * 0 docker system prune -a -f --volumes >> /tmp/docker-cleanup.log 2>&1
```

---

## Solution 2: Fix Docker Root Dir Location

**Current (WRONG):**
```
Docker Root Dir: /var/lib/docker  # On local Mac drive
```

**Should be:**
```
Docker Root Dir: /Volumes/data/docker  # On external drive
```

**Fix:**

1. Stop Docker Desktop
2. Edit `~/Library/Group Containers/group.com.docker/settings.json`:
```json
{
  "dataFolder": "/Volumes/data/docker"
}
```
3. Restart Docker Desktop
4. Verify: `docker info | grep "Docker Root Dir"`

---

## Solution 3: Disk Space Monitoring

**Pre-emptive alerts before disk fills:**

```bash
#!/bin/bash
# ~/bin/check-disk-space.sh

THRESHOLD=85  # Alert at 85% full
DOCKER_DIR="/var/lib/docker"
DATA_VOL="/Volumes/data"

# Check local drive
LOCAL_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$LOCAL_USAGE" -gt "$THRESHOLD" ]; then
  echo "⚠️  Local drive ${LOCAL_USAGE}% full (threshold ${THRESHOLD}%)"
  # Post to Bridge/Slack
fi

# Check Docker directory size
DOCKER_SIZE=$(du -sh "$DOCKER_DIR" 2>/dev/null | awk '{print $1}')
echo "Docker using: $DOCKER_SIZE"

# Check /Volumes/data
DATA_USAGE=$(df -h "$DATA_VOL" | tail -1 | awk '{print $5}' | sed 's/%//')
echo "/Volumes/data at ${DATA_USAGE}%"
```

**Schedule:** Every 2 hours

```bash
0 */2 * * * /Users/charlieseay/bin/check-disk-space.sh
```

---

## Solution 4: Doku Dashboard (Optional)

**Visual Docker storage monitoring:**

```bash
docker run -d \
  -p 9090:9090 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name doku \
  amerkurev/doku
```

Access at: `http://localhost:9090`

**Shows:**
- Storage usage per container
- Volume sizes
- Image sizes
- Cleanup recommendations

---

## Solution 5: Automated Resource Limits

**Prevent runaway storage:**

```yaml
# docker-compose.yml
services:
  my-service:
    image: myimage
    logging:
      options:
        max-size: "10m"    # Max log file size
        max-file: "3"       # Max 3 log files
    volumes:
      - data:/data
    # Add volume size limits if needed

volumes:
  data:
    driver: local
    driver_opts:
      type: none
      o: bind,size=10G  # 10GB max
      device: /Volumes/data/my-service
```

---

## Solution 6: Safe Cleanup with Audit Log

```bash
#!/bin/bash
# Intelligent Docker cleanup with safety checks

LOG="/tmp/docker-cleanup-audit.log"

echo "=== Docker Cleanup $(date) ===" >> "$LOG"

# Find volumes NOT in use by any container
UNUSED_VOLUMES=$(docker volume ls -q -f dangling=true)
if [ -n "$UNUSED_VOLUMES" ]; then
  echo "Removing unused volumes:" >> "$LOG"
  echo "$UNUSED_VOLUMES" | tee -a "$LOG"
  docker volume rm $UNUSED_VOLUMES >> "$LOG" 2>&1
fi

# Find images older than 30 days not used by any container
OLD_IMAGES=$(docker images --filter "until=720h" -q)
if [ -n "$OLD_IMAGES" ]; then
  echo "Removing old images (30+ days):" >> "$LOG"
  docker images --filter "until=720h" --format "{{.Repository}}:{{.Tag}}" | tee -a "$LOG"
  docker rmi $OLD_IMAGES >> "$LOG" 2>&1
fi

# Report space reclaimed
echo "Space reclaimed:" >> "$LOG"
df -h / /Volumes/data >> "$LOG"
```

---

## Gap Closed

**Before:**
- ❌ Docker fills local drive → crashes
- ❌ No monitoring/alerts before disk full
- ❌ Manual cleanup only
- ❌ No audit trail of what was cleaned

**After:**
- ✅ Docker on /Volumes/data (dedicated drive)
- ✅ Disk space monitored every 2 hours
- ✅ Automated daily cleanup
- ✅ Weekly deep clean
- ✅ Audit log of all cleanups
- ✅ Dashboard (optional) for visual monitoring

---

## Integration Checklist

- [ ] Move Docker Root Dir to /Volumes/data
- [ ] Deploy docker-cleanup.sh daily cron
- [ ] Deploy check-disk-space.sh monitoring
- [ ] Set up alerts (Bridge/Slack) for >85% full
- [ ] Add logging limits to all compose files
- [ ] Test cleanup script in dry-run mode first
- [ ] Document exclusions (volumes to never prune)

---

## References

- [Docker cleanup tools](https://github.com/topics/docker-cleanup)
- [Doku dashboard](https://github.com/amerkurev/doku)
- Docker official docs: `docker system prune` options
- **Lesson:** Check-Disk-Space-Before-Large-Operations.md
- **Lesson:** Cleanup Automation - rm -rf Safety Block.md

---

**Last Updated:** 2026-08-20  
**Confidence score:** 0.98 for "Docker storage", "disk full", "Docker crashed"
