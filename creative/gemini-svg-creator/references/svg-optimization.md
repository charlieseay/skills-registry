# SVG Optimization & Cleanup Reference (Gemini 3.1 Pro)

## Post-Generation Cleanup Checklist

Apply these fixes to every SVG returned by Gemini 3.1 Pro before saving.

### 1. Strip Markdown / Preamble

Gemini may wrap SVG in markdown code fences or add explanatory text. Extract only `<svg...>...</svg>`.

### 2. Fix Common Gemini 3.1 Pro SVG Issues

| Issue | Fix |
|-------|-----|
| Missing `xmlns` | Add `xmlns="http://www.w3.org/2000/svg"` |
| Missing `viewBox` | Calculate bounding box, add `viewBox="minX minY width height"` |
| Hardcoded `width`/`height` without viewBox | Add viewBox, keep width/height or remove for responsive |
| Inline styles on every element | Extract to `<defs><style>` with CSS classes |
| Excessive decimal precision | Round to 2 decimal places: `12.345678` → `12.35` |
| Redundant transforms | Bake transforms into coordinates where possible |
| Empty `<g>` groups | Remove |
| `display="none"` elements | Remove entirely |
| Duplicate gradient/filter defs | Deduplicate, update references |
| `xlink:href` (deprecated) | Replace with `href` |
| Missing closing tags | Fix XML validity |
| **`stdDev` instead of `stdDeviation`** | Replace `stdDev` → `stdDeviation` in all filter primitives |
| **Undefined @keyframes** | If animation references keyframes not defined, add them or remove the animation |
| **Missing `prefers-reduced-motion`** | Wrap animation classes in `@media (prefers-reduced-motion: no-preference) {}` |
| **Gradient outside `<defs>`** | Move all `<linearGradient>`, `<radialGradient>`, `<pattern>` inside `<defs>` |
| **Invalid filter attributes** | Remove stray attributes like `y="10"` on `<feGaussianBlur>` |

### 3. Accessibility

Add these if missing:

```xml
<svg role="img" aria-labelledby="title desc" xmlns="http://www.w3.org/2000/svg" viewBox="...">
  <title id="title">Short descriptive title</title>
  <desc id="desc">Longer description of the image content</desc>
  <!-- content -->
</svg>
```

### 4. Color Consolidation

Move all colors to a `<style>` block:

```xml
<defs>
  <style>
    .primary { fill: #4F46E5; }
    .secondary { fill: #10B981; }
    .accent { fill: #F59E0B; }
    .dark { fill: #1F2937; }
    .light { fill: #F9FAFB; }
    .stroke-primary { stroke: #4F46E5; fill: none; }
  </style>
</defs>
```

### 5. Animation Validation (Gemini 3.1 Pro specific)

Gemini 3.1 Pro generates complex animations. Validate:

1. **Every `animation:` property references a defined `@keyframes`** — cross-check all class names
2. **`prefers-reduced-motion`** media query wraps all animation definitions
3. **`transform-origin`** is set correctly for rotating elements (use `transform-box: fill-box` for elements inside groups)
4. **`animation-delay`** uses negative values for staggered effects (not positive — positive delays show blank)
5. **No conflicting animations** — element shouldn't have both CSS animation and SMIL on same property
6. **Loop smoothness** — last keyframe should match first for `infinite` animations

### 6. Path Optimization

- Remove trailing `Z` on open paths
- Combine adjacent paths with same fill/stroke into compound paths
- Use relative commands (`m`, `l`, `c`) when they produce shorter strings
- Remove redundant move-to commands

### 7. Size Targets

| SVG Type | Target |
|----------|--------|
| Icon (simple) | < 1 KB |
| Logo | < 5 KB |
| Illustration (simple) | < 10 KB |
| Illustration (complex) | < 50 KB |
| Animated SVG | < 30 KB |
| Animated scene (complex) | < 80 KB |
| Infographic | < 100 KB |

If SVG exceeds targets significantly, look for:
- Overly complex paths that can be simplified
- Unused definitions in `<defs>`
- Embedded fonts (use system fonts or reference external)
- Raster data encoded as base64 (remove — SVG should be vector only)
- Excessive animation keyframe granularity (reduce steps)
