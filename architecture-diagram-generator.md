---
name: architecture-diagram-generator
description: Generate beautiful dark-themed architecture diagrams as standalone HTML/SVG files using Claude AI skill
tags: [diagram, architecture, visualization, network, topology, claude-skill]
created: 2026-08-20
author: claude-code
version: 1.1.0
source: https://github.com/Cocoon-AI/architecture-diagram-generator
---

# Architecture Diagram Generator (Claude AI Skill)

Generate professional architecture diagrams in seconds using natural language. Perfect for network topologies, system architecture, and infrastructure maps.

## When to Use

- Building network topology visualizations
- Creating infrastructure architecture diagrams  
- Generating AWS-style architecture diagrams
- Visualizing discovered network infrastructure
- Drawing system component relationships
- Creating technical documentation diagrams

## Why This Skill

- ⭐ **7K+ stars** on GitHub (very popular)
- ✅ **Works as Claude AI skill** (designed for this!)
- ✅ **Dark-themed** (matches StdOut aesthetic)
- ✅ **Single HTML file** (self-contained, easy to embed)
- ✅ **Natural language** → instant diagram
- ✅ **Iterative** (ask to change and it updates)
- ✅ **Export built-in** (Copy/PNG/PDF buttons)
- ✅ **MIT License** (permissive)

## Installation

### Step 1: Download the Skill

```bash
cd ~/Downloads
curl -LO https://github.com/Cocoon-AI/architecture-diagram-generator/raw/main/architecture-diagram.zip
```

### Step 2: Upload to Claude.ai

1. Go to [claude.ai](https://claude.ai)
2. Click **Customize** → **Skills**
3. Click **+** → **+ Create skill** → **Upload a skill**
4. Upload `architecture-diagram.zip`
5. Toggle the skill **ON**

**Prerequisites:** Code Execution must be enabled in **Settings → Capabilities**

## How to Use

### Basic Pattern

1. Describe your architecture in text
2. Ask Claude to use the skill
3. Get a standalone HTML file
4. Iterate via chat to refine

### Example for StdOut Network Topology

```
Use your architecture diagram skill to create a network topology showing:

EDGE LAYER:
- Gateway Router (192.168.68.1)

INFRASTRUCTURE LAYER:
- Core Switch (192.168.68.10)
- NAS Storage (192.168.68.68)

SERVER LAYER:
- Mac Mini M4 Pro (192.168.68.78) - Core Infrastructure
- ThinkPad P1 (192.168.68.89) - StdOut Production

CONTAINER LAYER:
- Bridge Dashboard (localhost:8117)
- Helmsman DB (localhost:5682)
- nvidia-agent (localhost:5901)
- StdOut App (192.168.68.89:8112)

Show connections from gateway fanning out to each layer.
Color code by type (infrastructure=purple, servers=blue, containers=green).
Group devices by network segment.
```

### Example for AWS Serverless

```
Create an architecture diagram showing:
- CloudFront CDN
- API Gateway
- Lambda functions (Node.js)
- DynamoDB
- S3 for static assets
- Cognito for auth
```

### Example for Microservices

```
Create a microservices architecture diagram with:
- React web app and mobile clients
- Kong API Gateway
- User Service (Go), Order Service (Java), Product Service (Python)
- PostgreSQL, MongoDB, and Elasticsearch databases
- Kafka for event streaming
- Kubernetes orchestration
```

## Output Format

**Single HTML file** containing:
- Embedded CSS (no external dependencies)
- Inline SVG diagram
- Dark theme (slate-950 background)
- Export toolbar (Copy/PNG/PDF)
- Professional typography (JetBrains Mono)

## Color Palette (Semantic)

- **Frontend**: Blue (`#3b82f6`)
- **Backend**: Green (`#10b981`)
- **Database**: Purple (`#8b5cf6`)
- **Cloud/Infrastructure**: Orange (`#f97316`)
- **Security/Auth**: Red (`#ef4444`)
- **Cache/Queue**: Yellow (`#f59e0b`)

## Iteration Examples

After generating initial diagram, ask:

- "Add a Redis cache between the API and database"
- "Change the gateway to orange color"
- "Group the containers into a Docker Host box"
- "Add health status indicators (green dots) to servers"
- "Show HTTPS protocol labels on connections"

## Integration Points

### StdOut Topology View

1. Query `discovered_hosts` table
2. Generate text description of network layers
3. Ask Claude (with skill) to generate diagram
4. Embed resulting HTML in `/app/infrastructure/topology`

### Bridge Infrastructure Page

Generate visual map of all services, grouped by host and colored by type.

### Documentation

Auto-generate architecture diagrams for tech specs and runbooks.

## Examples (Included in Repo)

```bash
# View example diagrams
open /tmp/architecture-diagram-generator/examples/web-app.html
open /tmp/architecture-diagram-generator/examples/aws-serverless.html
open /tmp/architecture-diagram-generator/examples/microservices.html
```

## Export Options

Every generated HTML file includes toolbar buttons:

- **📋 Copy** - High-res PNG to clipboard (paste into Slides/Docs/Slack)
- **🖼️ PNG** - Download high-resolution PNG
- **📄 PDF** - Download PDF (preserves dark theme)

## Advanced Usage

### Extract SVG for Embedding

The HTML file contains an inline SVG. To extract:

```bash
grep -oP '<svg[^>]*>.*?</svg>' diagram.html > diagram.svg
```

### Customize Colors

After generation, ask Claude:
```
Change the color scheme to use my brand colors:
- Primary: #F97316
- Secondary: #10B981
- Accent: #3B82F6
```

### Add Custom Components

```
Add these components:
- Monitoring: Uptime Kuma (localhost:3001)
- Observability: Grafana (localhost:3000)
- Logs: Netdata (localhost:19999)

Connect them to the monitoring layer.
```

## Links

- **GitHub**: https://github.com/Cocoon-AI/architecture-diagram-generator
- **Download**: https://github.com/Cocoon-AI/architecture-diagram-generator/raw/main/architecture-diagram.zip
- **License**: MIT

## Installation Status

**Ready to install** - Download zip and upload to Claude.ai Skills

## Next Steps

1. Download `architecture-diagram.zip`
2. Upload to Claude.ai → Skills
3. Enable the skill
4. Try generating a diagram for StdOut's network topology
