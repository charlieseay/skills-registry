---
name: diagram
description: Generate static architecture, network topology, or infrastructure diagrams using HTML/SVG, draw.io, or Cisco Network Sketcher. Use when drawing system architecture, network topologies, infrastructure maps, or engineering diagrams that don't need animation.
---

# Diagram: Static Architecture, Network, and Topology Visualizations

Create professional architecture and network diagrams using multiple backends: HTML/SVG (browser-rendered), draw.io-compatible (editable), or Cisco Network Sketcher (engineering-grade L1/L2/L3).

## When to Use

- **Architecture diagrams:** System components, data flows, cloud infrastructure
- **Network topologies:** Physical/logical network layouts, IP addressing, segments
- **Infrastructure maps:** Host interconnections, service discovery results, container relationships
- **Engineering diagrams:** Cisco-style professional network documentation
- **Technical documentation:** Standalone diagrams for specs, runbooks, proposals

**NOT for animated/interactive flows:** Use `dashmotion` for animated architecture diagrams, flowcharts, or motion graphics.

## Three Backends Available

### 1. HTML/SVG Generator (Fast, Embedded)

**Use when:** You need a self-contained HTML file that works in any browser without dependencies.

**Strengths:**
- Instant rendering (no external tools needed)
- Professional dark theme styling
- Single file (embed anywhere, share easily)
- Export buttons built-in (PNG, PDF, Copy)
- Iterative refinement via chat

**Example:**
```
Generate an architecture diagram showing:
- Frontend: React app
- Backend: Node.js API
- Database: PostgreSQL  
- Cache: Redis
- Message queue: RabbitMQ

Color code by tier: blue=frontend, green=backend, purple=database, yellow=queue
```

**Output:** Single `.html` file with embedded SVG and CSS

### 2. Draw.io-Compatible (Editable in Lucidchart/draw.io)

**Use when:** You want a diagram others can edit in their preferred diagramming tool.

**Strengths:**
- Open in draw.io, Lucidchart, or similar tools
- Fully editable (shapes, colors, connections)
- Standard format `.xml` or `.drawio`
- Revision-friendly (version control friendly)
- Team collaboration

**Example:**
```
Create a draw.io diagram of our StdOut infrastructure:
- Gateway router (192.168.68.1) at top
- Mac Mini M4 Pro (192.168.68.78) 
- ThinkPad P1 (192.168.68.89)
- Containers: Bridge, Helmsman, nvidia-agent
Show network connections with IP addresses labeled
```

**Output:** `.drawio` or `.xml` file, editable in draw.io/Lucidchart

### 3. Cisco Network Sketcher (Engineering Grade)

**Use when:** You need professional L1/L2/L3 network documentation with Cisco-style rendering.

**Strengths:**
- Engineering-grade visual quality (Cisco standard)
- Three-layer visualization (physical, VLAN, IP)
- Device tables with inventory metadata
- PowerPoint export (`.pptx`)
- Runs locally (data stays on your machine)
- Supports import from live network inventory (Cisco ACI, Meraki, NetBox, etc.)

**Example:**
```
Using Network Sketcher, create an L1/L2/L3 diagram:
- Edge: Gateway router (192.168.68.1)
- Infrastructure: Core switch, NAS (192.168.68.68)
- Servers: M4 Pro, ThinkPad (192.168.68.78, .89)
- Containers: Docker services
Group by network segment, color by device type, show all VLANs
Export as SVG and device table
```

**Output:** SVG diagrams (L1/L2/L3), HTML device table, PowerPoint (`.pptx`)

**Prerequisites:** Python 3.10+, Network Sketcher MCP installed

## Recommended: HTML/SVG for Most Cases

**HTML/SVG is the default** because it's:
- ✅ Instant (no setup)
- ✅ Self-contained (one file)
- ✅ Shareable (paste in Slack/email/docs)
- ✅ Iterative (refine via chat)
- ✅ Export-ready (PNG/PDF buttons built-in)

Use draw.io only if someone else needs to edit it. Use Network Sketcher only for Cisco-style engineering diagrams.

## Quick Start

### HTML/SVG Workflow

1. **Describe** your architecture in text
2. Ask Claude to generate a diagram using this skill
3. Get a standalone `.html` file
4. Iterate: "Add Redis here", "Change colors to brand palette", "Add monitoring stack"
5. Export: Use toolbar buttons for PNG/PDF

### Draw.io Workflow

1. Ask: "Create a draw.io diagram of [your system]"
2. Receive `.drawio` file
3. Open in draw.io.com or Lucidchart
4. Edit, share, version control with your team

### Network Sketcher Workflow

1. Ensure prerequisites are met (Python 3.10+, MCP installed)
2. Provide network inventory (IP, device type, location)
3. Claude generates L1/L2/L3 diagrams via Cisco Network Sketcher
4. Export PowerPoint slides or review device table

## Example Prompts

**Quick Architecture:**
> "Create an architecture diagram for a SaaS app: React frontend (AWS CloudFront), Node.js backend (ECS), PostgreSQL (RDS), Redis cache, and SQS queue. Blue for frontend, green for compute, purple for data, yellow for messaging."

**Infrastructure Inventory:**
> "Draw the StdOut infrastructure topology showing Mac Mini at 192.168.68.78, ThinkPad at .89, containers on each host, and network connections. Color code by host."

**Editable Version:**
> "Create a draw.io diagram I can share with my team showing our microservices architecture. Include: API gateway, 3 services (Users, Orders, Products), 2 databases, Kafka, and monitoring."

**Cisco-Grade Network Documentation:**
> "Using Network Sketcher, document our office network: 50 total devices across 3 subnets, including servers, workstations, IoT devices, switches, firewall. Generate L1/L2/L3 diagrams and a device table."

## Color Conventions (HTML/SVG)

- **Blue** (`#3b82f6`): Frontend, user-facing
- **Green** (`#10b981`): Backend, compute, processing
- **Purple** (`#8b5cf6`): Database, storage, persistence
- **Orange** (`#f97316`): Cloud, infrastructure, platform
- **Red** (`#ef4444`): Security, auth, critical
- **Yellow** (`#f59e0b`): Cache, queue, messaging, transient

## Advanced: Draw.io Shapes Reference

When requesting a draw.io diagram, you can ask for specific shapes:

- **Boxes:** `box`, `rectangle`, `rounded box`
- **Cylinders:** `database`, `storage`
- **Circles:** `service`, `actor`
- **Connectors:** `arrow`, `dashed`, `bidirectional`
- **Grouping:** `swimlane`, `container`, `zone`

Example: "Group all AWS services in a blue container, label it 'AWS Account'. Use cylinders for databases."

## Integration Points

### StdOut Topology View
Query `discovered_hosts` table → describe as text → generate HTML diagram → embed in `/app/infrastructure/topology`

### Bridge Infrastructure Dashboard
Auto-generate architecture diagrams for all microservices, grouped by host and colored by type

### Technical Documentation
Auto-generate system diagrams for onboarding docs, RFPs, security audits

### Team Presentations
Quick diagram generation for slides (copy PNG to clipboard, paste into Keynote/PowerPoint)

## Iteration Examples

After generating, ask Claude:

- "Add monitoring (Prometheus, Grafana) to the diagram"
- "Change the theme to use my brand colors"
- "Make the database icons bigger"
- "Add labels showing latency between services"
- "Group all the containers into a Docker Host box"
- "Show active vs. standby components in different colors"

## Notes on Tool Selection

| Need | Backend | Why |
|------|---------|-----|
| Quick visual | **HTML/SVG** | Instant, shareable, self-contained |
| Team editing | **draw.io** | Editable, standard format, version control |
| Cisco-style docs | **Network Sketcher** | L1/L2/L3, engineering grade, professional |

## See Also

- **dashmotion** — For animated flows, architecture visualizations with motion, or interactive diagrams
- **gemini-svg-creator** — For custom SVG generation (defer diagram requests to this skill instead)
