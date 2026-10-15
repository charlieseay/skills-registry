---
name: mcp-inkscape
description: AI-powered vector graphics creation and editing via Inkscape CLI. Create/edit/layer/animate SVG files (shapes, text, paths, booleans, SMIL animations, Live Path Effects). Export to PNG/PDF/EPS/DXF. Fleet pipelines hand off to GIMP, Blender, Unity. Requires Inkscape.app installed; runs headless by default via `inkscape --actions`.
---

# Inkscape MCP Server

The `inkscape` MCP server (proxy name `inkscape`, Python FastMCP launcher at
`/Users/charlieseay/Projects/inkscape-mcp/run_server.py`) provides MCP tools
for creating, editing, and exporting SVG files using the **Inkscape CLI**. It
shells out to `inkscape --actions` for all operations, runs **headless by
default** (no GUI), and supports advanced vector workflows like SMIL animation,
Live Path Effects, and fleet hand-offs to Blender/GIMP/Unity.

**Installation dependency:** Inkscape.app must be installed at
`/Applications/Inkscape.app/Contents/MacOS/inkscape`. The server auto-detects
it during `initialize()` (confirmed live 2026-09-30); if not found, tool calls
will fail with "Inkscape CLI not found" errors.

**How it runs:**
- **Default (headless):** Agent→FastMCP→`inkscape --actions` CLI batch processing
- **Optional (live GUI):** Open Inkscape.app manually, then use `--active-window`
  flag in tool calls to co-edit with the agent

## Quick start: what agents typically do

> "Create an SVG file at /tmp/circle.svg with a centered pink circle, 200px diameter."
> → Creates the file via CLI; returns success + file size.

> "List all layers in /tmp/design.svg, then hide the background layer."
> → Reads layer tree, executes hide action via CLI.

> "Convert the text element 'Heading' to paths in /tmp/poster.svg, then apply
> a roughen LPE."
> → Text→paths transformation, then LPE effect injection.

> "Export /tmp/animated.svg to PNG at /tmp/out.png with 2x scale."
> → PNG export via CLI; honors scale parameter.

## Tool catalog (9 tool groups, tested live 2026-09-30)

**File & Export Operations:**
- `inkscape_create_svg()` — create a new SVG file with optional dimensions/background color
- `inkscape_export_png()` — export SVG to PNG with scale/DPI control
- `inkscape_export_pdf()` — export SVG to PDF
- `inkscape_export_eps()` — export SVG to PostScript (EPS)
- `inkscape_export_dxf()` — export SVG to DXF (laser cutter, CNC, AutoCAD)

**Vector Drawing (shapes, paths, text):**
- `inkscape_create_shape()` — create rect/circle/polygon/path primitives
- `inkscape_create_text()` — add text element with font/size/color
- `inkscape_create_path()` — create a path from SVG path string (e.g., "M 10 10 L 100 100")
- `inkscape_create_line()` — draw a line with stroke/width control

**Boolean Operations:**
- `inkscape_boolean_union()` — union two or more objects
- `inkscape_boolean_difference()` — subtract objects
- `inkscape_boolean_intersect()` — keep only overlapping areas
- `inkscape_boolean_exclusion()` — keep non-overlapping areas

**Layer Management:**
- `inkscape_list_layers()` — read all layers (tree structure, visibility, locking)
- `inkscape_create_layer()` — add a new layer
- `inkscape_rename_layer()` — rename an existing layer
- `inkscape_set_layer_visibility()` — show/hide layer
- `inkscape_set_layer_lock()` — lock/unlock layer for editing
- `inkscape_move_layer_to_position()` — reorder layers

**SMIL Animation (preset keyframe animations):**
- `inkscape_animate_bounce()` — bouncing motion (configurable duration/height)
- `inkscape_animate_fade()` — opacity fade in/out
- `inkscape_animate_slide()` — slide from one position to another
- `inkscape_animate_rotate()` — spin/rotation animation
- `inkscape_animate_pulse()` — scale pulse (grow/shrink repeating)
- `inkscape_animate_shake()` — jitter/shake effect

**Live Path Effects (LPEs):**
- `inkscape_apply_lpe_roughen()` — roughen/scribble effect (configurable intensity)
- `inkscape_apply_lpe_bend()` — bend path along a guide curve
- `inkscape_apply_lpe_envelope()` — envelope distortion (4-point warp)
- `inkscape_apply_lpe_power_stroke()` — variable-width strokes (Illustrator-style)
- `inkscape_apply_lpe_spiro()` — smooth spline interpolation

**Text Operations:**
- `inkscape_text_to_path()` — convert text elements to outlines (for export reliability)
- `inkscape_set_text_properties()` — modify font/size/color/alignment on existing text

**Object Inspection & Manipulation:**
- `inkscape_get_object_by_id()` — fetch object properties by XML ID
- `inkscape_list_objects()` — enumerate all objects in an SVG
- `inkscape_set_object_fill()` — change fill color/pattern
- `inkscape_set_object_stroke()` — change stroke color/width/caps

**Validation & Analysis:**
- `inkscape_validate_svg()` — check SVG well-formedness and Inkscape compatibility
- `inkscape_get_bounding_box()` — measure object extents

**Agentic Sampling (AI-powered generation & iteration):**
- `inkscape_sampling_generate_icon()` — generate an icon from text description (uses LLM sampling)
- `inkscape_sampling_iterate_design()` — take user feedback and iterate a design
- `inkscape_sampling_analyze_composition()` — analyze a design's balance/alignment/color theory

**Fleet Pipelines (hand-off to other tools):**
- `inkscape_fleet_to_blender()` — export SVG in a format Blender can import (DXF or exported path JSON)
- `inkscape_fleet_to_gimp()` — rasterize and pass to GIMP for pixel-level editing
- `inkscape_fleet_to_unity()` — export for game engine integration (PDF or sprite sheet)

## Critical gotchas & real-world findings (tested 2026-09-30)

**1. Inkscape.app must be installed**
- The server probes for `/Applications/Inkscape.app/Contents/MacOS/inkscape` on startup.
- If not found, the initialize log prints `WARNING: Inkscape not found`, and **all CLI-based tools will fail silently or error**.
- **Fix:** `brew install inkscape` or download from inkscape.org. Then restart the MCP proxy.

**2. Headless mode (default) cannot interact with live GUI**
- If you manually open Inkscape and want the agent to edit the same document, **you must use `--active-window` flag explicitly in tool calls**.
- Without it, the CLI operates on files on disk, not the GUI instance.
- **Mixing modes:** CLI writes to file → GUI reloads = potential data loss if GUI has unsaved edits.

**3. Export DPI/scale is PNG-specific**
- `inkscape_export_png()` accepts `dpi` and `scale` parameters.
- `inkscape_export_pdf()`, `inkscape_export_eps()`, `inkscape_export_dxf()` do **not** scale; they export 1:1.
- **Workaround:** Scale the SVG objects themselves before exporting non-PNG formats.

**4. SMIL animations are Inkscape-native, not browser-standard**
- Preset animations like `bounce`, `fade`, `rotate` are injected as Inkscape-compatible SMIL.
- **Browser compatibility:** Some browsers (Firefox, Chrome) support SMIL; others (Safari) do not.
- **Safer approach:** Export animated SVG to MP4/WebM via an external tool, or use CSS/JavaScript animation as fallback.

**5. Live Path Effects (LPEs) are Inkscape-specific**
- An SVG with LPEs applied in Inkscape will **lose the LPE** when exported to PNG/PDF.
- Exported files only contain the **flattened result** (the visual output, not the parametric effect).
- **Consequence:** If you export then re-import, the LPE is gone. Store the `.svg` source separately.

**6. Text-to-path is lossy**
- `inkscape_text_to_path()` converts text elements to outlines (path objects).
- **Not reversible:** Once converted, you cannot edit the text content anymore.
- **Why:** Ensures font compatibility across systems (no font substitution on import).
- **Use case:** Before exporting to PDF/EPS for printing, to ensure font embedding.

**7. Animated SVG export doesn't preserve interactivity**
- Exporting an animated SVG to PNG = PNG is a static frame, no animation.
- **Workaround:** Keep the `.svg` source for animation; export to PNG only for static preview.

**8. Fleet hand-offs (Blender/GIMP/Unity) may require format conversion**
- `inkscape_fleet_to_blender()` exports DXF or embeds curve data JSON.
- Blender's SVG/DXF import is partial (some paths/effects may not round-trip perfectly).
- **Best practice:** Test the hand-off on a simple shape first; don't assume complex designs will transfer 1:1.

## Quick self-check

**Confirm Inkscape is installed:**
```bash
/Applications/Inkscape.app/Contents/MacOS/inkscape --version
```

If this returns a version string, the dependency is satisfied. If it errors
("no such file"), install Inkscape first.

**Test the MCP server initialization:**

The server performs Inkscape detection at startup (confirmed in live 2026-09-30 logs):
```
Found Inkscape at: /Applications/Inkscape.app/Contents/MacOS/inkscape
Initialized Inkscape CLI wrapper
```

If you see `WARNING: Inkscape not found` instead, Inkscape is not installed or in an unexpected location.
