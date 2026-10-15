---
name: network-diagram-generator
description: Generate network topology diagrams using Cisco Network Sketcher MCP
tags: [diagram, network, topology, visualization, mcp]
created: 2026-08-20
author: claude-code
version: 1.0.0
---

# Network Diagram Generator

Generate professional network topology diagrams (L1/L2/L3) using Cisco's Network Sketcher MCP server.

## When to Use

- Building network topology visualizations
- Creating infrastructure architecture diagrams
- Generating AWS-style grouped zone diagrams
- Visualizing discovered network infrastructure
- Drawing engineering-grade network diagrams (draw.io style)

## Prerequisites

**Python 3.10+ required**

1. Install dependencies:
```bash
cd /tmp
git clone https://github.com/cisco-open/network-sketcher.git
cd network-sketcher/network-sketcher_local_mcp
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements_mcp.txt
```

2. Add MCP server to Claude Code:
```bash
claude mcp add network-sketcher -- /tmp/network-sketcher/network-sketcher_local_mcp/.venv/bin/python /tmp/network-sketcher/network-sketcher_local_mcp/ns_mcp_server.py
```

## How to Use

Once the MCP server is added, ask Claude Code to generate network diagrams using natural language:

```
Using Network Sketcher, create a network topology diagram showing:
- Edge layer: Gateway router (192.168.68.1)
- Infrastructure layer: Switches and NAS
- Server layer: Docker hosts
- Device layer: Workstations and IoT devices

Group devices by subnet and show connections between layers.
Export as SVG and HTML device table.
```

## Output Formats

- **SVG diagrams**: L1 (physical), L2 (VLAN/broadcast), L3 (IP topology)
- **HTML device table**: Interactive table with device details
- **PowerPoint**: Editable .pptx diagrams
- **AI Context file**: For LLM review/extension

## Example Use Cases

### StdOut Infrastructure Topology
```
Create a network diagram from discovered_hosts table showing:
- Network segments grouped by subnet
- Device types (router, server, nas, workstation)
- Health status (color-coded: green=healthy, yellow=warning, red=offline)
- Connection hierarchy from gateway down to devices
```

### Multi-Site WAN Design
```
Design a 5-site WAN with HQ, two data centers, two branches,
Internet and WAN waypoints, edge routers, L2 segments, and IP addressing.
Generate L1/L2/L3 diagrams and device table.
```

### Docker Infrastructure Map
```
Show Docker host hierarchy:
- Physical hosts at top
- Docker networks as L2 segments
- Containers grouped by stack
- Port mappings and service connections
```

## MCP Tools Available

When MCP server is installed, these tools become available:

- `create_node` - Add devices to the topology
- `create_link` - Define connections between nodes
- `create_site` - Group nodes into sites/zones
- `generate_diagram` - Render SVG/HTML output
- `export_pptx` - Export PowerPoint diagram
- `save_context` - Save AI-readable context file

## Integration Points

### StdOut
Replace D3 force-directed graph or basic card layout with Network Sketcher diagrams:
1. Query `discovered_hosts` table
2. Convert to Network Sketcher format
3. Generate professional topology diagram
4. Display SVG in `/app/infrastructure/topology`

### Bridge
Enhance `/infra` page with visual network maps showing service interconnections.

### General Use
Any project needing network/infrastructure visualization.

## Links

- **GitHub**: https://github.com/cisco-open/network-sketcher
- **MCP Registry**: https://registry.modelcontextprotocol.io/?q=network-sketcher
- **Documentation**: See README.md in repo
- **License**: Apache 2.0

## Notes

- Diagrams are Cisco-style (professional engineering aesthetic)
- AI-native: works via natural language prompts
- Runs locally, data stays on your machine
- Generates draw.io-compatible output
- Supports import from live network inventory (Cisco ACI, Catalyst, Meraki, NetBox, etc.)

## Installation Status

**Not installed** - Run prerequisites above to enable.

Once installed, this skill auto-activates when Claude Code detects diagram/topology/network visualization keywords.
