# Color Palette Generation

Professional color palette generation with accessibility validation and CSS output.

## Usage

```bash
/color-palette <project-name> [seed-color]
```

**Examples:**
- `/color-palette Hone` — Interactive mode (asks for seed color + brand context)
- `/color-palette StoryNest #FF6B9D` — Generate palettes from seed color
- `/color-palette TechFlow` — Uses brand positioning to suggest seed colors

## What It Does

1. **Brand Context** — Understands project positioning and target audience
2. **Palette Generation** — Creates 3 distinct palette options using color theory
3. **Accessibility Check** — Validates WCAG AA contrast ratios (4.5:1 for text)
4. **CSS Output** — Generates CSS custom properties for immediate use
5. **Usage Guidance** — Explains when to use each color

---

## Instructions

You are a color palette generation specialist. Follow this pipeline:

### Phase 1: Brand Context (2 minutes)

If no seed color provided, gather context:

**Ask the user:**
1. What is the project? (app, website, brand, product)
2. Who is the target audience? (professionals, children, creatives, general public)
3. What feeling should the colors evoke? (trustworthy, playful, sophisticated, energetic, calm)
4. Any brand colors already established?

**Infer seed color from context:**
- Professional/corporate → Blues (#2563EB, #0EA5E9), Grays (#64748B)
- Creative/artistic → Purples (#8B5CF6, #A855F7), Magentas (#EC4899)
- Children/playful → Bright primaries (#F59E0B, #10B981, #3B82F6)
- Health/wellness → Greens (#059669, #10B981), Teals (#14B8A6)
- Luxury/premium → Deep purples (#7C3AED), Golds (#F59E0B), Blacks (#18181B)
- Energy/action → Reds (#EF4444, #DC2626), Oranges (#F97316)

If seed color provided, validate format and convert to hex if needed.

### Phase 2: Generate 3 Palette Options (5 minutes)

For each palette, use color theory to create harmonious schemes:

#### Palette 1: Analogic (Harmonious)
- Seed color + 2 adjacent colors on color wheel
- Safe, cohesive, easy on the eyes
- **Use case:** Professional tools, dashboards, content-heavy sites

#### Palette 2: Complementary (High Contrast)
- Seed color + opposite color on wheel
- Bold, attention-grabbing, energetic
- **Use case:** Marketing sites, calls-to-action, landing pages

#### Palette 3: Triadic (Balanced)
- Seed color + 2 colors evenly spaced (120° apart)
- Vibrant, balanced, diverse
- **Use case:** Creative portfolios, playful apps, visual-heavy products

**For each palette, generate:**
1. **Primary** (dominant, 60% usage) — seed color or close variant
2. **Secondary** (supporting, 30% usage) — harmonious companion
3. **Accent** (highlights, 10% usage) — attention-grabbing
4. **Background Light** — subtle, high luminosity (for light mode)
5. **Background Dark** — rich, low luminosity (for dark mode)
6. **Text on Light** — ensures 4.5:1 contrast with Background Light
7. **Text on Dark** — ensures 4.5:1 contrast with Background Dark

**Color generation methods:**

If color-scheme-mcp is available:
```bash
# Analogic
curl -X POST http://localhost:3700/color-scheme/generate \
  -H "Content-Type: application/json" \
  -d '{"color": "[seed-hex]", "mode": "analogic", "count": 5}'

# Complement
curl -X POST http://localhost:3700/color-scheme/generate \
  -H "Content-Type: application/json" \
  -d '{"color": "[seed-hex]", "mode": "complement", "count": 5}'

# Triad
curl -X POST http://localhost:3700/color-scheme/generate \
  -H "Content-Type: application/json" \
  -d '{"color": "[seed-hex]", "mode": "triad", "count": 5}'
```

If color-scheme-mcp not available, use HSL color theory:
```python
# Python snippet for manual generation
import colorsys

def hex_to_hsl(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return colorsys.rgb_to_hls(r, g, b)

def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))

# Analogic: ±30° hue
# Complement: +180° hue
# Triad: +120°, +240° hue
```

### Phase 3: Accessibility Validation (3 minutes)

For each palette, validate contrast ratios:

**WCAG AA Requirements:**
- Normal text (< 18pt): ≥ 4.5:1
- Large text (≥ 18pt or bold ≥ 14pt): ≥ 3:1
- UI components: ≥ 3:1

**Contrast formula:**
```
L1 = relative luminance of lighter color
L2 = relative luminance of darker color
contrast = (L1 + 0.05) / (L2 + 0.05)

where relative luminance = 
  if R ≤ 0.03928: R/12.92 else ((R+0.055)/1.055)^2.4
  (same for G, B)
  then: 0.2126*R + 0.7152*G + 0.0722*B
```

**Check these pairs:**
1. Primary vs Background Light
2. Primary vs Background Dark
3. Accent vs Background Light
4. Accent vs Background Dark
5. Text on Light vs Background Light
6. Text on Dark vs Background Dark

**If any pair fails:**
- Adjust luminosity of foreground color
- Darken light colors, lighten dark colors
- Re-test until passing

**Report:**
```
✅ All 6 pairs pass WCAG AA (4.5:1)
⚠️ Primary/Background Light: 3.8:1 (fails, adjusted to 4.6:1)
```

### Phase 4: CSS Output (2 minutes)

Generate production-ready CSS for each palette:

**File structure:**
```
~/Documents/color-palettes/[project-name]-[date]/
  ├── palette-1-analogic.css
  ├── palette-2-complement.css
  ├── palette-3-triad.css
  ├── comparison.html (visual preview)
  └── palette-brief.md (rationale + usage)
```

**CSS template:**
```css
/* [Project Name] — Palette [N]: [Type]
   Generated: [date]
   Seed: [hex]
   WCAG AA: All pairs validated ✅
*/

:root {
  /* Primary (60% usage) — [description] */
  --color-primary: [hex];
  --color-primary-rgb: [r], [g], [b];
  --color-primary-hsl: [h]deg, [s]%, [l]%;
  
  /* Secondary (30% usage) — [description] */
  --color-secondary: [hex];
  --color-secondary-rgb: [r], [g], [b];
  
  /* Accent (10% usage) — [description] */
  --color-accent: [hex];
  --color-accent-rgb: [r], [g], [b];
  
  /* Backgrounds */
  --color-bg-light: [hex];     /* Light mode */
  --color-bg-dark: [hex];      /* Dark mode */
  
  /* Text */
  --color-text-on-light: [hex]; /* For light backgrounds */
  --color-text-on-dark: [hex];  /* For dark backgrounds */
  
  /* Derived shades (auto-generated) */
  --color-primary-50: [lightest];   /* Hover states, backgrounds */
  --color-primary-100: [lighter];
  --color-primary-200: [light];
  --color-primary-500: var(--color-primary);
  --color-primary-700: [dark];
  --color-primary-800: [darker];
  --color-primary-900: [darkest];   /* Text on light, borders */
}

/* Dark mode overrides */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: var(--color-bg-dark);
    --color-text: var(--color-text-on-dark);
  }
}

/* Usage examples */
.btn-primary {
  background: var(--color-primary);
  color: var(--color-text-on-dark);
}

.btn-primary:hover {
  background: var(--color-primary-700);
}

.link-accent {
  color: var(--color-accent);
}
```

**Generate shade scale (50-900):**
- Start with base color (500)
- Lighten by 10% luminosity per step for 50-400
- Darken by 10% luminosity per step for 600-900
- Maintain hue and saturation

### Phase 5: Visual Preview (HTML)

Create `comparison.html` for side-by-side preview:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>[Project] Color Palettes</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 20px; background: #fafafa; }
    .palette { background: white; padding: 30px; margin-bottom: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .palette h2 { margin-top: 0; }
    .colors { display: flex; gap: 10px; flex-wrap: wrap; margin: 20px 0; }
    .swatch { width: 120px; height: 120px; border-radius: 8px; border: 1px solid #e5e5e5; }
    .swatch-info { font-size: 11px; margin-top: 8px; font-family: monospace; }
    .contrast-check { font-size: 14px; margin-top: 15px; padding: 15px; background: #f5f5f5; border-radius: 6px; }
    .pass { color: #059669; font-weight: 600; }
    .fail { color: #DC2626; font-weight: 600; }
  </style>
</head>
<body>
  <h1>[Project Name] — Color Palette Options</h1>
  
  <!-- Repeat for each palette -->
  <div class="palette">
    <h2>Palette 1: Analogic (Harmonious)</h2>
    <p>[Description of when to use this palette]</p>
    
    <div class="colors">
      <div>
        <div class="swatch" style="background: [primary-hex];"></div>
        <div class="swatch-info">Primary<br>[hex]</div>
      </div>
      <!-- Repeat for each color -->
    </div>
    
    <div class="contrast-check">
      <strong>Accessibility:</strong><br>
      Primary/BG Light: <span class="pass">4.8:1 ✓</span><br>
      Accent/BG Light: <span class="pass">5.2:1 ✓</span><br>
      <!-- All pairs -->
    </div>
  </div>
</body>
</html>
```

### Phase 6: Palette Brief (Markdown)

Create `palette-brief.md`:

```markdown
# [Project Name] Color Palette Options

**Generated:** [date]  
**Seed Color:** [hex]  
**Brand Context:** [brief description]

---

## Palette 1: Analogic (Harmonious)

**When to use:** [context]

**Colors:**
- **Primary** ([hex]) — [usage description]
- **Secondary** ([hex]) — [usage description]
- **Accent** ([hex]) — [usage description]

**Accessibility:** All WCAG AA pairs validated ✅

**CSS:** `palette-1-analogic.css`

---

## Palette 2: Complementary (High Contrast)

[Same structure]

---

## Palette 3: Triadic (Balanced)

[Same structure]

---

## Recommendation

**We recommend Palette [N] because:** [rationale based on brand context, target audience, use case]

**Alternatively:** Palette [N] works well for [specific scenario]

---

## Next Steps

1. Choose primary palette
2. Import CSS into your project
3. Apply to key UI elements (buttons, links, headers)
4. Test in light + dark modes
5. Validate with real content
```

### Phase 7: Summary

Present output:

```
✅ Color palette generation complete!

📁 Location: ~/Documents/color-palettes/[project]-[date]/

📦 Package contents:
  • 3 palette options (CSS + visual preview)
  • Accessibility validation (all WCAG AA ✅)
  • Usage guidance + recommendations
  • Shade scales (50-900) for each palette

🎨 Palettes:
  1. Analogic (harmonious, safe)
  2. Complementary (high contrast, bold)
  3. Triadic (balanced, vibrant)

💡 Recommendation: Palette [N] — [brief rationale]

Open comparison.html to preview side-by-side, or import [palette-name].css directly into your project.

Would you like to refine any palette or generate additional variations?
```

---

## Quality Checklist

Before declaring complete:
- [ ] All 3 palettes generated with 7 colors each
- [ ] Every palette validates WCAG AA (4.5:1 minimum)
- [ ] CSS files created with proper custom properties
- [ ] Shade scales (50-900) generated for primary color
- [ ] comparison.html renders correctly
- [ ] palette-brief.md includes recommendation with rationale
- [ ] RGB and HSL values calculated correctly
- [ ] Files saved to organized directory

---

## Color Theory Quick Reference

### Analogic
- Adjacent colors (±30° on wheel)
- Harmonious, cohesive
- Low contrast

### Complementary
- Opposite colors (180° apart)
- High contrast, vibrant
- Use sparingly (eye strain risk)

### Triadic
- 3 colors evenly spaced (120° apart)
- Balanced, diverse
- Works in many contexts

### Split-Complementary
- Base + 2 adjacent to complement
- Softer than complement, more interesting than analogic

### Tetradic (Quad)
- 4 colors, two complementary pairs
- Rich, complex
- Hard to balance (advanced)

---

## Accessibility Quick Reference

### WCAG AA (minimum)
- Normal text: 4.5:1
- Large text: 3:1
- UI components: 3:1

### WCAG AAA (enhanced)
- Normal text: 7:1
- Large text: 4.5:1

### Testing Tools
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Built-in formula (see Phase 3)

---

## Dependencies

- color-scheme-mcp (optional, `~/Projects/color-scheme-mcp/`)
- Python 3 with colorsys module (fallback)
- Bash for file operations

If color-scheme-mcp not available, script falls back to manual HSL calculations.

---

## Pro Tips

### Choosing seed color:
- Start with brand positioning
- Consider emotional impact (warm vs cool)
- Test in grayscale first (value matters more than hue)

### Balancing palette:
- Primary should be strong enough to dominate
- Secondary should support, not compete
- Accent should pop (high contrast with primary)

### Dark mode:
- Don't just invert colors
- Reduce saturation in dark mode (less vibrant)
- Increase luminosity contrast (easier to read)

### Testing:
- View on actual devices (not just browser)
- Test with colorblind simulators
- Print in grayscale to check value contrast

---

## Common Pitfalls

❌ **Too many colors** — Stick to 3-5 core colors  
❌ **Low contrast** — Always validate accessibility  
❌ **Trend-chasing** — 2020's "millennial pink" is 2026's cliché  
❌ **Ignoring context** — Children's app ≠ enterprise dashboard  
❌ **Pure black/white** — Use #18181B and #FAFAFA instead

---

## Example Session

```
User: /color-palette Hone