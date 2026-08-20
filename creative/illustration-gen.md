---
name: illustration-gen
category: creative
description: Generate custom illustrations for products and marketing
triggers:
  patterns:
  - illustration
  - custom artwork
  - visual asset
  contexts:
  - marketing
  - product design
  - content creation
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when generate custom illustrations for products and marketing
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 25
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

# Illustration Generation

Generate high-quality illustrations with optional vector conversion for editorial use, hero images, and visual storytelling.

## Usage

```bash
/illustration-gen <description> [--style=<style>] [--format=<raster|vector|both>]
```

**Examples:**
- `/illustration-gen "a developer working late at night, warm desk lamp, coffee, code on screen"`
- `/illustration-gen "children reading books in a cozy library" --style=watercolor`
- `/illustration-gen "abstract data visualization, flowing connections" --format=vector`

## What It Does

1. **Creative Direction** — Refine description with style, mood, composition
2. **Raster Generation** — High-quality image via `/banana generate`
3. **Vector Conversion** (optional) — Trace to SVG via inkscape-mcp
4. **Cleanup & Export** — Optimize for web, provide multiple formats

---

## Instructions

### Phase 1: Creative Direction (2 minutes)

Parse user description and enhance with creative direction parameters:

**Ask if not specified:**
1. **Style:** (photorealistic, flat design, watercolor, line art, isometric, hand-drawn, 3D render)
2. **Mood:** (warm, cool, energetic, calm, dramatic, playful)
3. **Composition:** (centered, rule-of-thirds, diagonal, symmetrical, negative space)
4. **Color palette:** (vibrant, muted, monochrome, pastel, high-contrast)
5. **Format:** (raster only, vector only, both)

**Default to:**
- Style: flat design (web-friendly, clean)
- Mood: balanced (not extreme)
- Composition: centered (safe)
- Colors: brand colors if available, otherwise vibrant
- Format: raster (faster, higher quality for complex scenes)

### Phase 2: Raster Generation (3-5 minutes)

Call banana-claude with enhanced prompt:

```bash
/banana generate "[original description], [style] illustration style, [mood] lighting, [composition] composition, [color-palette] colors. Professional, editorial quality, high detail, clean composition, vector-friendly shapes (if vector conversion planned). Output: 2048x2048px, PNG."
```

**Style-specific enhancements:**

**Flat design:**
```
"flat design illustration, simple shapes, bold colors, minimal shadows, clean lines, geometric, modern"
```

**Watercolor:**
```
"watercolor illustration, soft edges, flowing colors, organic textures, hand-painted feel, artistic"
```

**Line art:**
```
"line art illustration, black ink lines, white background, detailed linework, no color fill, sketch style"
```

**Isometric:**
```
"isometric illustration, 3D perspective, precise angles, technical, geometric, clean shadows"
```

**Hand-drawn:**
```
"hand-drawn illustration, organic lines, slight imperfections, sketch marks, authentic, warm"
```

**3D render:**
```
"3D rendered illustration, smooth surfaces, realistic lighting, depth, volumetric, Blender/C4D style"
```

### Phase 3: Vector Conversion (Optional, 10-15 minutes)

If `--format=vector` or `--format=both`:

**Method A: Inkscape Auto-Trace (faster)**
```bash
# Assuming inkscape-mcp is running
# Use inkscape CLI for trace

cd ~/Documents/illustrations/[project]/
inkscape [raster-file].png \
  --actions="select-all;trace-bitmap:autotrace;export-filename:[output].svg;export-do" \
  --batch-process
```

**Method B: Manual Trace (higher quality)**
1. Import raster into Inkscape
2. Use Path > Trace Bitmap
3. Adjust settings:
   - **Flat design:** Brightness cutoff, 8-12 scans
   - **Detailed:** Edge detection, smoothing: 1.5
4. Clean up paths (simplify, remove artifacts)
5. Export as optimized SVG

**Post-trace cleanup:**
```bash
# Simplify paths
npx svgo [output].svg -o [output]-clean.svg \
  --multipass \
  --precision=1 \
  --enable=removeUselessStrokeAndFill \
  --enable=convertPathData

# Further manual cleanup in Inkscape if needed
```

### Phase 4: Formats & Optimization

**Raster exports:**
- **Web hero (1920x1080):** For landing pages, headers
- **Social media (1200x630):** Open Graph, Twitter Card
- **Thumbnail (400x400):** Preview, grid displays
- **Retina (2x):** High-DPI displays

```bash
# Using ImageMagick or sips (macOS)
sips -Z 1920 [source].png --out [output]-hero.png
sips -s format jpeg [source].png --out [output]-og.jpg --setProperty formatOptions 85
sips -Z 400 [source].png --out [output]-thumb.png
```

**Vector exports (if converted):**
- **Optimized SVG:** Web use
- **PDF:** Print-ready
- **EPS:** Legacy software compatibility

### Phase 5: Delivery Package

```
~/Documents/illustrations/[project]-[date]/
  ├── source/
  │   └── [name]-source.png         # Original 2048x2048 from banana
  ├── raster/
  │   ├── [name]-hero-1920.png      # Web hero
  │   ├── [name]-og-1200x630.jpg    # Social media
  │   ├── [name]-thumb-400.png      # Thumbnail
  │   └── [name]-retina-2x.png      # High-DPI
  ├── vector/ (if converted)
  │   ├── [name].svg                # Optimized SVG
  │   ├── [name].pdf                # Print-ready
  │   └── [name].eps                # Legacy format
  ├── illustration-brief.md
  └── usage-guide.md
```

**illustration-brief.md:**
```markdown
# [Project] Illustration

**Description:** [original description]  
**Style:** [style]  
**Mood:** [mood]  
**Generated:** [date]

## Creative Direction

- **Composition:** [composition choice + rationale]
- **Color Palette:** [colors used]
- **Lighting:** [mood lighting description]
- **Key Elements:** [list main visual elements]

## Files

- Source: `source/[name]-source.png` (2048x2048, original quality)
- Hero: `raster/[name]-hero-1920.png` (web header, landing page)
- Social: `raster/[name]-og-1200x630.jpg` (OG image, Twitter Card)
- Thumbnail: `raster/[name]-thumb-400.png` (preview, grid)
- Vector: `vector/[name].svg` (scalable, editable)

## Usage

- **Web:** Use hero (1920px) for headers, og image for social sharing
- **Print:** Use vector PDF for high-quality printing
- **Editing:** Open source PNG in design tool, or SVG in Inkscape/Illustrator

## License

[Specify usage rights — typically all rights for client work]
```

### Phase 6: Summary

```
✅ Illustration generation complete!

📁 Location: ~/Documents/illustrations/[project]-[date]/

📦 Package contents:
  • Source illustration (2048x2048 PNG)
  • 4 raster formats (hero, social, thumbnail, retina)
  • Vector SVG (if converted) + PDF/EPS
  • Creative brief + usage guide

🎨 Style: [style]
💡 Best for: [use case based on style]

Files ready for web, social media, and print.

Need variations or different formats?
```

---

## Quality Checklist

- [ ] Source illustration high-quality (2048x2048 minimum)
- [ ] Style matches requested aesthetic
- [ ] Composition balanced and intentional
- [ ] Color palette cohesive
- [ ] All requested formats exported
- [ ] Vector trace clean (if converted) — no artifacts
- [ ] Files properly named and organized
- [ ] Usage guide complete

---

## Dependencies

- `/banana` (raster generation)
- `inkscape` (vector conversion, optional)
- `sips` or `ImageMagick` (format conversion)
- `npx svgo` (SVG optimization, optional)

---

## Pro Tips

### For vector conversion:
- **Flat designs trace best** — simple shapes, solid colors
- **Avoid complex gradients** — they bloat SVG file size
- **High contrast helps** — clear edges = cleaner traces
- **Simplify first** — fewer colors = smaller vector file

### Composition:
- **Rule of thirds** — place focal point at intersection
- **Leading lines** — guide eye through the scene
- **Negative space** — don't fill every pixel
- **Depth layers** — foreground, midground, background

### Mood through lighting:
- **Warm (yellow/orange):** cozy, friendly, energetic
- **Cool (blue/purple):** calm, professional, tech
- **Dramatic (high contrast):** bold, cinematic, intense
- **Soft (diffused):** gentle, approachable, welcoming

---

## Example

```
User: /illustration-gen "a developer working late at night" --style=flat
Assistant: Generates flat design illustration with warm desk lamp lighting, centered composition, muted colors
```
