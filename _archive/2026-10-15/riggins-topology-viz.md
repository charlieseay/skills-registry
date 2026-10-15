---
name: riggins-topology-viz
version: 1.0.0
description: 'Generate animated infrastructure topology diagrams for StdOut Observatory using DashMotion. Converts discovered infrastructure (hosts, services, integrations) into visual topology maps with animated request flows. Use when Riggins needs to visualize network topology, service dependencies, or infrastructure architecture from discovered_hosts and integration_configs data.'
requires: [dashmotion]
---

# Riggins Topology Visualization

Generate animated infrastructure topology diagrams from StdOut's discovered infrastructure data.

## When to Use

Trigger this skill when:
- User asks for "topology view", "infrastructure map", "network diagram"
- StdOut UI requests topology visualization (Infrastructure → Topology View tab)
- Need to visualize discovered hosts, services, and their relationships
- Export infrastructure documentation with animated diagrams

## Prerequisites

1. **DashMotion skill** must be installed (`/Volumes/data/skills/dashmotion/`)
2. **StdOut database** access to query `discovered_hosts` and `integration_configs`
3. **Python 3** available for DashMotion layout engine

## Data Sources

### Primary Tables

**`discovered_hosts`** — Network-discovered devices
```sql
SELECT 
  host_id, 
  ip_address, 
  hostname, 
  mac_address, 
  device_type,  -- router, server, container, desktop, printer, iot
  last_seen
FROM discovered_hosts 
WHERE last_seen > datetime('now', '-7 days');
```

**`integration_configs`** — Configured service integrations
```sql
SELECT 
  config_id,
  host_id,  -- FK to discovered_hosts
  integration_type,  -- prometheus, grafana, mysql, postgresql, redis, docker, ssh
  connection_status,  -- connected, needs_config, failed, ignored
  service_name,
  port,
  metadata  -- JSON with service-specific details
FROM integration_configs
WHERE connection_status != 'ignored';
```

**`monitors`** — Active monitors (for dependency arrows)
```sql
SELECT 
  monitor_id,
  name,
  monitor_type,  -- http, tcp, docker, json_freshness
  target_url,
  check_interval_seconds
FROM monitors
WHERE is_active = 1;
```

## Diagram Generation Flow

### Step 1: Query Infrastructure Data

```bash
# Run on StdOut ThinkPad (192.168.68.89:8112)
ssh thinkpad "docker exec stdout sqlite3 /data/stdout.db '
  SELECT json_object(
    \"hosts\", (SELECT json_group_array(json_object(
      \"id\", host_id,
      \"ip\", ip_address,
      \"hostname\", hostname,
      \"type\", device_type
    )) FROM discovered_hosts WHERE last_seen > datetime(\"now\", \"-7 days\")),
    \"integrations\", (SELECT json_group_array(json_object(
      \"host_id\", host_id,
      \"type\", integration_type,
      \"status\", connection_status,
      \"name\", service_name,
      \"port\", port
    )) FROM integration_configs WHERE connection_status != \"ignored\")
  );
' | jq ."
```

Save output to `/tmp/stdout-infrastructure.json`

### Step 2: Transform to DashMotion Semantic Graph

Convert StdOut data to DashMotion's Architecture mode format:

```json
{
  "mode": "architecture",
  "title": "StdOut Infrastructure Topology",
  "subtitle": "Live infrastructure as of {timestamp}",
  "summary": [
    {
      "accent": "cyan",
      "title": "Discovered Hosts",
      "items": ["{count} hosts", "{subnets} subnets", "{device_types} types"]
    },
    {
      "accent": "violet",
      "title": "Service Integrations",
      "items": ["{connected} connected", "{needs_config} need config", "{monitoring} types"]
    },
    {
      "accent": "rose",
      "title": "Health Status",
      "items": ["{online}% online", "{degraded} degraded", "{offline} offline"]
    }
  ],
  "nodes": [
    {
      "id": "host-{host_id}",
      "label": "{hostname}\\n{ip_address}",
      "type": "{device_type}",  // maps to DashMotion component types
      "group": "{subnet}"  // 192.168.68.x → "home-network"
    }
  ],
  "edges": [
    {
      "from": "host-client",
      "to": "host-gateway",
      "kind": "http",
      "label": "HTTP"
    }
  ],
  "groups": [
    {
      "id": "{subnet}",
      "label": "{subnet_name}",
      "style": "region"  // DashMotion boundary style
    }
  ],
  "journeys": [
    {
      "name": "monitoring-flow",
      "color": "cyan",
      "path": ["riggins", "prometheus", "targets"]
    }
  ],
  "legendExtra": [
    "✅ Connected (auto-configured)",
    "⚠️ Needs Config (credentials required)",
    "❌ Failed (connection error)"
  ]
}
```

### Step 3: Map StdOut Types to DashMotion Component Types

**Device Type Mapping:**

| StdOut `device_type` | DashMotion `type` | Color | Description |
|---------------------|------------------|-------|-------------|
| `router` | `gateway` | Blue | Network gateway, ingress |
| `server` | `service` | Green | Physical/VM servers |
| `container` | `service` | Green | Docker containers |
| `desktop` | `client` | Cyan | User workstations |
| `printer` | `external` | Gray | Peripherals, IoT |
| `iot` | `external` | Gray | Smart devices |
| `unknown` | `service` | Yellow | Unclassified hosts |

**Integration Type Mapping:**

| StdOut `integration_type` | DashMotion `type` | Icon/Shape |
|--------------------------|------------------|-----------|
| `prometheus` | `monitoring` | 📊 gauge |
| `grafana` | `monitoring` | 📈 chart |
| `mysql` | `database` | 🗄️ cylinder |
| `postgresql` | `database` | 🗄️ cylinder |
| `redis` | `cache` | ⚡ bolt |
| `mongodb` | `database` | 🗄️ cylinder |
| `docker` | `orchestration` | 🐳 whale |
| `ssh` | `admin` | 🔑 key |

### Step 4: Generate Diagram with DashMotion

```bash
# Write semantic graph to temp file
cat > /tmp/dashmotion-graph.json <<'EOF'
{semantic graph JSON from Step 2}
EOF

# Render with DashMotion layout engine
python3 /Volumes/data/skills/dashmotion/scripts/layout.py \
  /tmp/dashmotion-graph.json \
  --render stdout-topology-{timestamp}.html

# Verify structure (mandatory)
python3 /Volumes/data/skills/dashmotion/scripts/check_diagram.py \
  stdout-topology-{timestamp}.html

# Output: Self-contained HTML file with animated topology
```

### Step 5: Deliver to StdOut UI

**Option A: Embed in StdOut page**
```html
<!-- src/routes/app/infrastructure/topology.astro -->
<iframe 
  src="/static/topology/latest.html" 
  width="100%" 
  height="800px" 
  frameborder="0"
  title="Infrastructure Topology">
</iframe>
```

**Option B: Standalone export**
- Save to `public/topology/stdout-topology-{timestamp}.html`
- Provide download link for documentation

## Animation Patterns

### 1. Monitoring Flow Journey
Shows Riggins → Prometheus → discovered targets

```json
{
  "journeys": [
    {
      "name": "monitoring-flow",
      "color": "cyan",
      "path": ["riggins-agent", "prometheus-server", "target-host-1", "target-host-2"],
      "duration": "3s"
    }
  ]
}
```

### 2. User Request Flow Journey
Shows typical HTTP request path

```json
{
  "journeys": [
    {
      "name": "user-request",
      "color": "violet",
      "path": ["client-browser", "nginx-gateway", "stdout-app", "sqlite-db"],
      "duration": "2.5s"
    }
  ]
}
```

### 3. Service Dependency Flow
Shows service-to-service communication

```json
{
  "journeys": [
    {
      "name": "service-deps",
      "color": "rose",
      "path": ["stdout-app", "redis-cache", "docker-api"],
      "duration": "2s"
    }
  ]
}
```

## Grouping Strategies

### Group by Network Segment
```json
{
  "groups": [
    {
      "id": "subnet-68-0",
      "label": "Home Network (192.168.68.x)",
      "style": "region"
    },
    {
      "id": "subnet-192-0",
      "label": "Management Network (192.168.0.x)",
      "style": "region"
    }
  ]
}
```

### Group by Service Type
```json
{
  "groups": [
    {
      "id": "monitoring-stack",
      "label": "Monitoring & Observability",
      "style": "namespace"
    },
    {
      "id": "database-tier",
      "label": "Data Layer",
      "style": "namespace"
    }
  ]
}
```

### Group by Health Status
```json
{
  "groups": [
    {
      "id": "healthy-services",
      "label": "✅ Connected Services",
      "style": "region"
    },
    {
      "id": "degraded-services",
      "label": "⚠️ Needs Configuration",
      "style": "security"
    }
  ]
}
```

## Real-Time Updates

### Auto-Refresh on Discovery Changes

Monitor StdOut database for changes:

```bash
# Watch for new discoveries (simplified)
while true; do
  NEW_COUNT=$(sqlite3 /data/stdout.db "SELECT COUNT(*) FROM discovered_hosts WHERE last_seen > datetime('now', '-5 minutes')")
  if [ "$NEW_COUNT" -gt 0 ]; then
    echo "New hosts discovered, regenerating topology..."
    # Re-run Steps 1-4
  fi
  sleep 300  # Check every 5 minutes
done
```

### StdOut UI Integration

Add "Refresh Topology" button that:
1. Triggers Riggins to re-query infrastructure
2. Regenerates DashMotion diagram
3. Updates iframe src or reloads embedded HTML

## Output Deliverables

### 1. Topology View (embedded in StdOut UI)
- **Location**: `/app/infrastructure/topology`
- **Format**: Embedded iframe of generated HTML
- **Auto-refresh**: Every 15 minutes or on manual trigger

### 2. Standalone Export
- **Location**: `public/topology/stdout-topology-{timestamp}.html`
- **Format**: Self-contained HTML (no external dependencies)
- **Use case**: Documentation, reports, offline reference

### 3. Thumbnail Preview
- **Location**: `public/topology/stdout-topology-{timestamp}.png`
- **Format**: Static screenshot (via headless Chrome)
- **Use case**: Dashboard widget, email reports

## Example Implementation

### Riggins Tool Function

```typescript
// src/lib/observatory/tools/generate-topology.ts
export async function generateTopologyDiagram(): Promise<string> {
  // Step 1: Query infrastructure data
  const infrastructure = await db.query(`
    SELECT json_object(
      'hosts', (SELECT json_group_array(...) FROM discovered_hosts),
      'integrations', (SELECT json_group_array(...) FROM integration_configs)
    )
  `);
  
  // Step 2: Transform to DashMotion format
  const semanticGraph = transformToSemanticGraph(infrastructure);
  
  // Step 3: Write temp file
  await fs.writeFile('/tmp/dashmotion-graph.json', JSON.stringify(semanticGraph));
  
  // Step 4: Generate diagram
  const output = await exec(`
    python3 /Volumes/data/skills/dashmotion/scripts/layout.py 
      /tmp/dashmotion-graph.json 
      --render public/topology/latest.html
  `);
  
  // Step 5: Verify
  await exec(`
    python3 /Volumes/data/skills/dashmotion/scripts/check_diagram.py 
      public/topology/latest.html
  `);
  
  return '/topology/latest.html';
}
```

## Success Criteria

- ✅ Diagram renders all discovered hosts (no omissions)
- ✅ Service integrations show correct status colors
- ✅ Network segments properly grouped
- ✅ Animated journeys follow realistic request paths
- ✅ Passes DashMotion structure check (0 violations)
- ✅ Self-contained HTML (no external dependencies)
- ✅ Renders correctly in StdOut UI iframe
- ✅ Export works offline (filesystem open)

## Troubleshooting

### Diagram shows no hosts
- Verify `discovered_hosts` has data: `SELECT COUNT(*) FROM discovered_hosts;`
- Check `last_seen` filter (default 7 days)
- Confirm DB path is correct (`/data/stdout.db`)

### Python script fails
- Verify Python 3 installed: `python3 --version`
- Check DashMotion skill path: `ls /Volumes/data/skills/dashmotion/scripts/`
- Run check script directly for error details

### Overlapping nodes in diagram
- Re-run with larger `gap` values in semantic graph
- Reduce nodes per tier (split into multiple groups)
- Check DashMotion structure validation output

### Animated journeys don't show
- Verify `journeys` array has valid node IDs
- Check path follows existing edges
- Ensure duration is reasonable (2-3s)

## Related Skills

- `/Volumes/data/skills/dashmotion/` — Core diagram generation
- `/Volumes/data/skills/network-discovery-fast.md` — Fast ARP-based discovery
- `/Volumes/data/skills/architecture-diagram-generator.md` — Alternative static diagrams

## Version History

- **1.0.0** (2026-08-25) — Initial Riggins topology visualization skill
