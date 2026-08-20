---
name: visualize
category: development
description: Visualize codebase architecture and dependencies
triggers:
  patterns:
  - visualize
  - codebase map
  - dependency graph
  contexts:
  - documentation
  - architecture
  - onboarding
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when visualize codebase architecture and dependencies
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 25
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Analyze a project's codebase and generate an interactive component map showing how pieces connect, where data flows, and where gaps exist.

## Usage

- `/visualize ~/Projects/my-app` — analyze a specific project
- `/visualize` — prompts for a project path

If an argument is provided, use it as the project path. If not, use AskUserQuestion to ask which project to visualize. Accept short names (e.g., "hone" → `~/Projects/hone`).

## Procedure

### 1. Identify the Project

Resolve the path. Confirm the project exists. Detect the framework:

| Signal | Framework |
|--------|-----------|
| `astro.config.*` | Astro |
| `Package.swift`, `*.xcodeproj` | Swift/SwiftUI |
| `express` in package.json deps | Express/Node |
| `fastify` in package.json deps | Fastify |
| `next.config.*` | Next.js |
| `src/index.ts` + MCP tool patterns | MCP Server |
| `docker-compose.yml` only | Docker/Infrastructure |

### 2. Find the Vault Project Folder

The visualization saves to the vault, near the tech spec. Map the code project to its vault folder:

- Code at `~/Projects/my-app` → Vault at `Projects/My App/`
- Code at `~/Projects/my-tool` → Vault at `Projects/My Tool/`
- Code at `~/Projects/my-site` → Vault at `Projects/my-site/`

Check for an existing `Tech Spec.md` or similar file in that vault folder. The visualization goes in the same directory.

### 3. Analyze the Codebase

Use Glob and Grep extensively. Build a mental model of:

**Components** — every discrete unit in the codebase:
| Type | What to look for |
|------|-----------------|
| Pages/Routes | `src/pages/`, route definitions, `@Get/@Post` decorators |
| API Endpoints | `src/pages/api/`, route handlers, controller methods |
| UI Components | `src/components/`, `.vue`, `.svelte`, React components |
| Layouts | `src/layouts/`, wrapper components |
| Middleware | `middleware.ts`, auth guards, request interceptors |
| Services | Service classes, API clients, external integrations |
| Models/Types | Data models, TypeScript interfaces, database schemas |
| Config | Environment loading, feature flags, constants |
| Database | Schema files, migrations, ORM models, queries |
| Workers/Jobs | Background tasks, cron jobs, queue consumers |
| External APIs | Third-party API calls (Stripe, Auth providers, etc.) |

**For MCP Servers specifically:**
| Type | What to look for |
|------|-----------------|
| Tools | `server.tool()` or tool handler registrations |
| Resources | `server.resource()` registrations |
| Prompts | `server.prompt()` registrations |
| Transport | stdio, SSE, HTTP transport setup |
| Validation | Zod schemas, input validation |
| External deps | System calls, hardware access, network calls |

**For Swift/SwiftUI:**
| Type | What to look for |
|------|-----------------|
| Views | `struct X: View` |
| ViewModels | `@Observable class`, `ObservableObject` |
| Models | Data structs, Core Data entities |
| Services | Network managers, API clients |
| Navigation | `NavigationStack`, router patterns |

**Relationships** — how components connect:
- Import statements (`import`, `require`, `from`)
- Function calls across modules
- API fetch/axios calls to internal endpoints
- Middleware chains (what runs before what)
- Database access patterns (which services touch which models)
- Event emitters/listeners
- Props/data passed between UI components

**Cross-app dependencies** — when the app reaches outside itself:
- External API calls (Stripe, Authentik, GitHub, etc.)
- Shared auth (OAuth flows, SSO)
- Shared databases
- Inter-service HTTP calls
- Shared environment variables pointing to other services

### 4. Gap Analysis

After mapping components and relationships, identify:

| Gap Type | Detection |
|----------|-----------|
| **Orphaned components** | Files that nothing imports or references |
| **Dead endpoints** | API routes with no client-side callers |
| **Missing error boundaries** | Try/catch gaps in async chains, unhandled promise patterns |
| **One-way data flow breaks** | A component sends data but never receives a response/confirmation |
| **Unprotected routes** | Pages/API endpoints that bypass middleware/auth |
| **Missing validation** | Endpoints that accept input without schema validation |
| **Circular dependencies** | A imports B imports A |
| **Single points of failure** | A critical service with no fallback or error handling |
| **Undocumented externals** | API calls to services not mentioned in env/config |

Not every project will have every gap type. Only report gaps that actually exist. False positives are worse than missing a minor gap.

### 5. Generate the Visualization

Create a **self-contained interactive HTML file** with an embedded D3.js force-directed graph.

**File name:** `component-map.html`
**Location:** Same vault folder as the tech spec (e.g., `[project]/component-map.html`)

The HTML must be completely self-contained — D3.js loaded from CDN, all CSS inline, all data embedded as JSON.

#### Visual Design

**Theme:** Dark background, high-contrast nodes. Professional, not flashy.

**Node types and colors:**

| Type | Color | Shape |
|------|-------|-------|
| Page/Route | `#60a5fa` (blue) | Rectangle |
| API Endpoint | `#34d399` (green) | Rectangle |
| UI Component | `#a78bfa` (purple) | Rectangle |
| Layout | `#818cf8` (indigo) | Rectangle |
| Middleware | `#fbbf24` (amber) | Diamond |
| Service | `#f472b6` (pink) | Rectangle |
| Model/Type | `#94a3b8` (gray) | Rounded rect |
| Database | `#38bdf8` (cyan) | Cylinder (rect with label) |
| External Service | `#fb923c` (orange) | Cloud-shaped or dashed border |
| Config | `#d4d4d8` (light gray) | Small rect |
| Worker/Job | `#c084fc` (light purple) | Hexagon-ish |
| MCP Tool | `#34d399` (green) | Rectangle |
| MCP Resource | `#60a5fa` (blue) | Rectangle |
| View (Swift) | `#a78bfa` (purple) | Rectangle |
| ViewModel | `#f472b6` (pink) | Rectangle |

**Edge types:**
| Relationship | Style |
|-------------|-------|
| Import/dependency | Solid arrow |
| API call | Dashed arrow |
| Data flow | Thick arrow |
| Middleware chain | Dotted line |
| External call | Orange dashed arrow |

**Interaction:**
- Hover a node: highlight it and all connected edges, dim everything else
- Click a node: show detail panel (file path, type, connections in/out, gap warnings)
- Drag nodes to rearrange
- Zoom and pan
- Search/filter by node type (toggle buttons in header)
- Gap indicators: nodes with gaps get a red ring or warning icon

**Layout sections:**
- **Header**: Project name, framework, timestamp, component/connection/gap counts
- **Main area**: Force-directed graph
- **Sidebar** (collapsible): Gap analysis findings, grouped by severity
- **Legend**: Node types and edge types
- **Footer**: "Generated by /visualize — Claude Code"

#### D3.js Force Graph Implementation Notes

Use D3 v7 from CDN: `https://d3js.org/d3.v7.min.js`

Force simulation settings:
- `forceLink` with distance based on relationship type
- `forceManyBody` with negative charge to spread nodes
- `forceCenter` to center the graph
- `forceCollide` to prevent overlap

Group related nodes using `forceX`/`forceY` clusters (e.g., all API endpoints drift toward the right, all UI components toward the left).

### 6. Write the Output

1. **Write the HTML file** to the vault project folder
2. **Update the project note** — add a "Component Map" section with a relative link to the HTML file and a summary of findings (component count, connection count, gaps found)
3. **Report to the user** — show:
   - File path as a clickable link
   - Summary: X components, Y connections, Z gaps found
   - Top 3 most critical gaps (if any)
   - How to open it (browser, VS Code Live Server, etc.)

### 7. Cross-App Detection

If during analysis you find the app depends on other services (shared auth, API calls to sibling apps, shared database), note these as "External Dependencies" in the visualization with dashed-border nodes. Include what the dependency is and which component initiates it.

If the cross-app coupling is significant (>3 touchpoints), suggest running `/visualize` on the connected app too and mention it in the output.

## Quality Checklist

Before writing the file:
- [ ] Every component found has a type, label, and file path
- [ ] Relationships are directional (A depends on B, not just "A and B are related")
- [ ] Gap analysis only flags real issues, not false positives
- [ ] HTML loads and renders without errors (valid JSON data, valid D3 code)
- [ ] Node labels are short enough to read (filename, not full path)
- [ ] External services are clearly distinguished from internal components
- [ ] The sidebar gap list matches the visual gap indicators on nodes
- [ ] Dark theme has sufficient contrast for all text and elements

## Notes

- If the project has no source code (e.g., a vault-only project), say so and suggest `/diagram` instead
- For very large projects (>100 components), group by directory/module to keep the graph readable
- The HTML file is portable — it can be opened from the vault, shared via FileBrowser, or committed to git
- Re-running `/visualize` on the same project overwrites the previous `component-map.html`
- The visualization is a snapshot — it reflects the codebase at generation time, not live state

## Lessons

- **2026-06-15** — `task_completed__w6_dependency_cve_sweep`: Task completed: W6 Dependency CVE Sweep — Phase 1 Research & Design [src: task-1000440]
- **2026-06-15** — `task_completed__w6_dependency_cve_sweep`: Task completed: W6 Dependency CVE Sweep — Phase 1 Research & Design [src: task-1000440]
