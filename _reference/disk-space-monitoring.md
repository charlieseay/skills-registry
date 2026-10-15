# Disk Space Monitoring — Proactive Alerts & Cleanup

**Category:** infrastructure  
**Priority:** CRITICAL  
**Created:** 2026-08-20  
**Triggered by:** Mac Mini disk full incident (crashed Docker)  
**Confidence triggers:** disk full, storage monitoring, disk space alerts, cleanup automation, disk usage

**Source:** [caco3/storage-analyzer](https://github.com/caco3/storage-analyzer) — Automated scanning with cron

---

## Problem

**Today's incident:**
- Mac drive filled to 100%
- Docker crashed
- No warning before failure
- Manual recovery required

**Pattern:** Disk fills gradually, then crashes suddenly.

**Need:** Continuous monitoring + proactive alerts.

---

## Solution: Multi-Tier Monitoring

### Tier 1: Simple Threshold Alerts

```bash
#!/bin/bash
# ~/bin/disk-alert.sh

THRESHOLD=85
CRITICAL=95

check_mount() {
  local mount=$1
  local usage=$(df -h "$mount" | tail -1 | awk '{print $5}' | sed 's/%//')
  
  if [ "$usage" -gt "$CRITICAL" ]; then
    echo "🚨 CRITICAL: $mount at ${usage}% (threshold ${CRITICAL}%)"
    # Emergency cleanup trigger
    /Users/charlieseay/bin/emergency-cleanup.sh "$mount"
  elif [ "$usage" -gt "$THRESHOLD" ]; then
    echo "⚠️  WARNING: $mount at ${usage}% (threshold ${THRESHOLD}%)"
    # Post to Bridge/Slack
  fi
}

check_mount "/"
check_mount "/Volumes/data"
```

**Schedule:** Every 2 hours + before large operations

---

### Tier 2: Storage Analyzer (Automated Scanning)

```bash
# Install storage-analyzer
git clone https://github.com/caco3/storage-analyzer
cd storage-analyzer && make install

# Configure cron scanning
storage-analyzer --scan / --output /tmp/storage-report.json

# Schedule (daily at 2 AM)
0 2 * * * storage-analyzer --scan /Volumes/data --output /tmp/storage-report.json
```

**Features:**
- Automated scanning (hourly/daily/weekly/monthly)
- Trend analysis (growing directories)
- Docker integration
- Single-command deployment

---

### Tier 3: Pre-Operation Disk Checks

**Before large operations (rsync, backups, builds):**

```bash
#!/bin/bash
# check-space-before-operation.sh

REQUIRED_GB=$1
MOUNT=${2:-"/"}

AVAILABLE_GB=$(df -g "$MOUNT" | tail -1 | awk '{print $4}')

if [ "$AVAILABLE_GB" -lt "$REQUIRED_GB" ]; then
  echo "❌ Insufficient space: need ${REQUIRED_GB}GB, have ${AVAILABLE_GB}GB"
  exit 1
fi

echo "✅ Sufficient space: ${AVAILABLE_GB}GB available"
```

**Usage:**
```bash
# Before 286GB rsync
check-space-before-operation 300 /Volumes/data || exit 1
rsync -avP source/ dest/
```

**Lesson reference:** Check-Disk-Space-Before-Large-Operations.md

---

### Tier 4: Automatic Cleanup Triggers

```bash
#!/bin/bash
# emergency-cleanup.sh

MOUNT=$1

echo "Emergency cleanup triggered for $MOUNT"

# 1. Clean Docker (if applicable)
if [ "$MOUNT" = "/" ]; then
  docker system prune -a -f --volumes
fi

# 2. Clean caches
rm -rf ~/.cache/npm
rm -rf ~/Library/Caches/Homebrew
rm -rf ~/Library/Developer/Xcode/DerivedData

# 3. Clean logs older than 7 days
find /tmp -name "*.log" -mtime +7 -delete
find ~/.local/var/log -name "*.log" -mtime +7 -delete

# 4. Report what was freed
df -h "$MOUNT"
```

---

## Integration: Unified Monitor

```bash
#!/bin/bash
# unified-disk-monitor.sh

# Check thresholds
/Users/charlieseay/bin/disk-alert.sh

# Run storage analyzer (daily)
if [ "$(date +%H)" -eq 2 ]; then
  storage-analyzer --scan /Volumes/data --output /tmp/storage-report.json
fi

# Check Docker size
DOCKER_SIZE=$(du -sh /var/lib/docker 2>/dev/null | awk '{print $1}')
echo "Docker using: $DOCKER_SIZE"

# Alert if Docker > 50GB
DOCKER_GB=$(du -sg /var/lib/docker 2>/dev/null | awk '{print $1}')
if [ "$DOCKER_GB" -gt 50 ]; then
  echo "⚠️  Docker using ${DOCKER_GB}GB (trigger cleanup?)"
fi
```

**Launchd schedule:**
```xml
<!-- ~/Library/LaunchAgents/com.seaynic.disk-monitor.plist -->
<key>StartInterval</key>
<integer>7200</integer>  <!-- Every 2 hours -->
```

---

## Monitoring Dashboard (Optional)

**Web UI for storage trends:**

```bash
# Using Doku (Docker-specific)
docker run -d -p 9090:9090 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  amerkurev/doku

# Or use storage-analyzer web interface
storage-analyzer --serve --port 8080
```

---

## Alert Channels

**1. Bridge Dashboard**
```bash
curl -X POST http://localhost:8117/api/alerts \
  -d '{"type":"disk_space","level":"warning","message":"/ at 87%"}'
```

**2. Slack Webhook**
```bash
curl -X POST $SLACK_WEBHOOK \
  -d '{"text":"🚨 Mac Mini disk at 95%"}'
```

**3. Email (Critical Only)**
```bash
if [ "$usage" -gt 95 ]; then
  echo "Disk critically full: ${usage}%" | mail -s "URGENT: Disk Full" charlie@seayniclabs.com
fi
```

---

## Gap Closed

**Before:**
- ❌ Disk filled to 100% with no warning
- ❌ Docker crashed (no graceful degradation)
- ❌ Manual checks only
- ❌ No automated cleanup

**After:**
- ✅ Alerts at 85% (warning) and 95% (critical)
- ✅ Monitoring every 2 hours
- ✅ Automated emergency cleanup at 95%
- ✅ Pre-operation space checks
- ✅ Trend analysis (storage-analyzer)
- ✅ Multi-channel alerts

---

## References

- [caco3/storage-analyzer](https://github.com/caco3/storage-analyzer)
- [Disk cleanup tools](https://github.com/topics/disk-cleanup)
- **Lesson:** Check-Disk-Space-Before-Large-Operations.md
- **Complements:** docker-storage-cleanup.md

---

**Last Updated:** 2026-08-20  
**Confidence score:** 0.95 for "disk full", "storage monitoring", "disk space"
