Create a draw.io (.drawio) diagram file based on the user's description.

## Usage

- `/diagram network topology` — creates a diagram from a description passed as an argument
- `/diagram` — prompts interactively for diagram details

If an argument is provided, use it as the diagram description. If not, use AskUserQuestion to ask:
- What should the diagram show?
- What type? (flowchart, network, architecture, swimlane, sequence, ERD, org chart, free-form)

## Procedure

1. **Gather inputs** — get the diagram description from the argument or by asking
2. **Determine diagram type** — infer from the description or ask
3. **Plan the layout** — identify all shapes, connections, labels, and groupings
4. **Generate the .drawio XML** — follow the XML reference below exactly
5. **Write the file** — save as `<slugified-name>.drawio` in the current working directory
6. **Report** — show the file path as a clickable markdown link. Do NOT auto-open.

## Naming

Slugify the diagram title: lowercase, hyphens for spaces, strip special characters. Example: "Network Topology" → `network-topology.drawio`

## XML Structure Reference

Every .drawio file follows this structure:

```xml
<mxfile host="Claude Code" modified="{{ISO_DATE}}" agent="Claude Code" version="1.0" type="device">
  <diagram id="{{DIAGRAM_ID}}" name="{{PAGE_NAME}}">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- All shapes and edges go here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### Mandatory cells

Every diagram MUST include these two cells first:
```xml
<mxCell id="0"/>
<mxCell id="1" parent="0"/>
```

Cell `0` is the invisible root. Cell `1` is the default layer. All top-level shapes use `parent="1"`.

### Vertices (Shapes)

```xml
<mxCell id="{{UNIQUE_ID}}" value="{{LABEL}}" style="{{STYLE_STRING}}" vertex="1" parent="1">
  <mxGeometry x="{{X}}" y="{{Y}}" width="{{W}}" height="{{H}}" as="geometry"/>
</mxCell>
```

### Edges (Connections)

```xml
<mxCell id="{{UNIQUE_ID}}" value="{{LABEL}}" style="{{STYLE_STRING}}" edge="1" parent="1" source="{{SOURCE_ID}}" target="{{TARGET_ID}}">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

Edge labels in style: add `labelBackgroundColor=#ffffff;` for readability.

### Edge with waypoints

```xml
<mxCell id="{{ID}}" value="" style="endArrow=classic;html=1;" edge="1" parent="1" source="{{SRC}}" target="{{TGT}}">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="{{X1}}" y="{{Y1}}"/>
      <mxPoint x="{{X2}}" y="{{Y2}}"/>
    </Array>
  </mxGeometry>
</mxCell>
```

## Shape Style Reference

Use these style strings as the base. Add color and text properties as needed.

### Basic Shapes

| Shape | Style |
|-------|-------|
| Rectangle | `whiteSpace=wrap;html=1;` |
| Rounded Rectangle | `rounded=1;whiteSpace=wrap;html=1;arcSize=10;` |
| Ellipse | `shape=ellipse;whiteSpace=wrap;html=1;` |
| Diamond / Decision | `shape=rhombus;whiteSpace=wrap;html=1;` |
| Cylinder / Database | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;stencilColors=1;size=15;` |
| Cloud | `shape=cloud;whiteSpace=wrap;html=1;` |
| Document | `shape=document;whiteSpace=wrap;html=1;` |
| Hexagon | `shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;` |
| Parallelogram | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;` |
| Triangle | `shape=triangle;whiteSpace=wrap;html=1;` |
| Callout | `shape=callout;whiteSpace=wrap;html=1;` |
| Note | `shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;` |
| Actor (stick figure) | `shape=mxgraph.basic.person;whiteSpace=wrap;html=1;` |

### Flowchart Shapes

| Shape | Style |
|-------|-------|
| Start/End (terminator) | `rounded=1;whiteSpace=wrap;html=1;arcSize=50;` |
| Process | `whiteSpace=wrap;html=1;` |
| Decision | `shape=rhombus;whiteSpace=wrap;html=1;` |
| Data (I/O) | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;` |
| Predefined Process | `shape=process;whiteSpace=wrap;html=1;` |
| Manual Operation | `shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;html=1;` |
| Delay | `shape=delay;whiteSpace=wrap;html=1;` |
| Stored Data | `shape=dataStorage;whiteSpace=wrap;html=1;` |

### Containers

| Shape | Style |
|-------|-------|
| Swimlane (horizontal) | `swimlane;whiteSpace=wrap;html=1;startSize=30;` |
| Swimlane (vertical) | `swimlane;horizontal=0;whiteSpace=wrap;html=1;startSize=30;` |
| Group | `group;` |
| Frame | `shape=mxgraph.basic.rect;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#666666;dashed=1;` |

### Network / Infrastructure

| Shape | Style |
|-------|-------|
| Server | `shape=mxgraph.cisco.servers.standard_server;whiteSpace=wrap;html=1;` |
| Database | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;stencilColors=1;size=15;` |
| Cloud | `shape=cloud;whiteSpace=wrap;html=1;` |
| Firewall | `shape=mxgraph.cisco.firewalls.firewall;whiteSpace=wrap;html=1;` |
| Router | `shape=mxgraph.cisco.routers.router;whiteSpace=wrap;html=1;` |
| Desktop | `shape=mxgraph.cisco.computers_and_peripherals.pc;whiteSpace=wrap;html=1;` |
| Laptop | `shape=mxgraph.cisco.computers_and_peripherals.laptop;whiteSpace=wrap;html=1;` |

### Edge Styles

| Type | Style |
|------|-------|
| Straight arrow | `endArrow=classic;html=1;` |
| Orthogonal | `edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;` |
| Curved | `curved=1;html=1;endArrow=classic;` |
| Entity Relation | `edgeStyle=entityRelationEdgeStyle;html=1;endArrow=ERone;startArrow=ERmandOne;` |
| Dashed | `dashed=1;html=1;endArrow=classic;` |
| No arrow | `endArrow=none;html=1;` |
| Two-way arrow | `endArrow=classic;startArrow=classic;html=1;` |

### Arrow Types

`classic`, `block`, `open`, `oval`, `diamond`, `diamondThin`, `dash`, `cross`, `none`, `ERone`, `ERmandOne`, `ERmany`, `ERoneToMany`, `ERzeroToMany`, `ERzeroToOne`

## Color Palettes

Use these coordinated palettes for professional diagrams:

### Default (Blue theme)
| Role | Fill | Stroke |
|------|------|--------|
| Primary | `#dae8fc` | `#6c8ebf` |
| Success | `#d5e8d4` | `#82b366` |
| Warning | `#fff2cc` | `#d6b656` |
| Danger | `#f8cecc` | `#b85450` |
| Purple | `#e1d5e7` | `#9673a6` |
| Orange | `#ffe6cc` | `#d79b00` |
| Gray | `#f5f5f5` | `#666666` |
| Dark | `#333333` | `#000000` |

### Dark theme
| Role | Fill | Stroke | Font |
|------|------|--------|------|
| Background | `#1a1a2e` | `#16213e` | `#e0e0e0` |
| Primary | `#0f3460` | `#1a73e8` | `#e0e0e0` |
| Accent | `#533483` | `#7b68ee` | `#e0e0e0` |
| Success | `#1b4332` | `#52b788` | `#e0e0e0` |
| Danger | `#6a040f` | `#e63946` | `#e0e0e0` |

## Common Style Properties

| Property | Values | Purpose |
|----------|--------|---------|
| `fillColor` | `#hex` or `none` | Background color |
| `strokeColor` | `#hex` | Border color |
| `fontColor` | `#hex` | Text color |
| `fontSize` | number | Font size in pt |
| `fontStyle` | `0`=normal, `1`=bold, `2`=italic, `3`=bold+italic | Font weight/style |
| `strokeWidth` | number | Border width in px |
| `dashed` | `0` or `1` | Dashed border |
| `dashPattern` | e.g. `3 3` | Custom dash pattern |
| `rounded` | `0` or `1` | Rounded corners |
| `arcSize` | number | Corner radius |
| `shadow` | `0` or `1` | Drop shadow |
| `opacity` | `0`-`100` | Fill opacity |
| `align` | `left`, `center`, `right` | Horizontal text align |
| `verticalAlign` | `top`, `middle`, `bottom` | Vertical text align |
| `whiteSpace` | `wrap` or `nowrap` | Text wrapping |
| `html` | `0` or `1` | Enable HTML in labels |
| `container` | `0` or `1` | Marks cell as container |
| `collapsible` | `0` or `1` | Container can collapse |

## Layout Guidelines

- **Grid**: Use 10px grid. Snap coordinates to multiples of 10 or 20.
- **Spacing**: Keep at least 40px between shapes. 80-120px between columns/rows.
- **Shape sizes**: Typical rectangle 120x60. Decision diamond 80x80. Database cylinder 60x80. Cloud 120x80.
- **Flow direction**: Default top-to-bottom or left-to-right. Be consistent within a diagram.
- **Alignment**: Align shapes on their centers for clean layouts.
- **Labels**: Keep labels short. Use HTML (`html=1`) only when multi-line or formatted text is needed.
- **IDs**: Use descriptive IDs (e.g., `server_web1`, `edge_web_to_db`) — never just numbers.
- **Colors**: Use a consistent palette. Don't mix more than 4-5 colors per diagram.

## Multi-page Diagrams

For complex diagrams, split into multiple pages:

```xml
<mxfile host="Claude Code" ...>
  <diagram id="page1" name="Overview">
    <mxGraphModel ...>
      <root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <!-- Page 1 content -->
      </root>
    </mxGraphModel>
  </diagram>
  <diagram id="page2" name="Detail View">
    <mxGraphModel ...>
      <root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <!-- Page 2 content -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Each page has its own independent set of cell IDs.

## Groups and Containers

Children of a group use the group's ID as their `parent`:

```xml
<mxCell id="group1" value="Server Cluster" style="swimlane;whiteSpace=wrap;html=1;startSize=30;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="300" height="200" as="geometry"/>
</mxCell>
<mxCell id="child1" value="Node 1" style="whiteSpace=wrap;html=1;" vertex="1" parent="group1">
  <mxGeometry x="20" y="40" width="100" height="40" as="geometry"/>
</mxCell>
```

Child coordinates are relative to the group's top-left corner.

## Swimlane Diagrams

```xml
<!-- Swimlane container -->
<mxCell id="lane1" value="Department A" style="swimlane;whiteSpace=wrap;html=1;startSize=30;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
  <mxGeometry x="50" y="50" width="400" height="200" as="geometry"/>
</mxCell>
<!-- Shapes inside the lane use parent="lane1" -->
<mxCell id="task1" value="Review" style="whiteSpace=wrap;html=1;" vertex="1" parent="lane1">
  <mxGeometry x="30" y="50" width="100" height="40" as="geometry"/>
</mxCell>
```

## Entry/Exit Points

Control exactly where edges connect to shapes:

| Point | exitX/entryX | exitY/entryY |
|-------|-------------|-------------|
| Top center | `0.5` | `0` |
| Bottom center | `0.5` | `1` |
| Left center | `0` | `0.5` |
| Right center | `1` | `0.5` |
| Top-left | `0` | `0` |
| Top-right | `1` | `0` |
| Bottom-left | `0` | `1` |
| Bottom-right | `1` | `1` |

Example: `exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;`

## HTML Labels

When `html=1` is in the style, escape HTML in the `value` attribute:

```xml
value="&lt;b&gt;Title&lt;/b&gt;&lt;br&gt;Description"
```

## Quality Checklist

Before writing the file, verify:
- [ ] Every `mxCell` has a unique `id`
- [ ] Cells `0` and `1` are present
- [ ] Every vertex has `vertex="1"` and an `mxGeometry`
- [ ] Every edge has `edge="1"`, `source`, and `target` matching valid vertex IDs
- [ ] Coordinates are snapped to grid (multiples of 10)
- [ ] Colors are consistent and from a single palette
- [ ] Labels are concise and readable
- [ ] Layout flows in a consistent direction
- [ ] No overlapping shapes
- [ ] XML is well-formed (all tags closed, attributes quoted, special chars escaped)

## Notes

- If the file already exists at the target path, warn the user before overwriting
- For complex diagrams (>15 shapes), consider splitting into multiple pages
- draw.io files can be opened in: draw.io desktop, VS Code (with draw.io extension), diagrams.net in browser
- The file is plain XML — it can be version-controlled in git
- Prefer swimlanes over groups when showing process ownership or responsibility
- Use orthogonal edges for architecture/network diagrams, straight for simple flowcharts
