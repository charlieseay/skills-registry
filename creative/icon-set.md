# Icon Set Generation

Generate cohesive SVG icon libraries with consistent style, optimized for web/mobile use.

## Usage

```bash
/icon-set <project-name> [icon-list]
```

**Examples:**
- `/icon-set Hone` — Interactive (asks for icon list + style)
- `/icon-set StoryNest "home, book, star, heart, settings, profile, search, bookmark"`
- `/icon-set TechFlow --style=outline --count=12`

## What It Does

1. **Style Selection** — Choose icon style (outline, filled, duotone, hand-drawn)
2. **Icon Generation** — Generate 8-16 icons via gemini-svg-creator
3. **Consistency Check** — Validate visual coherence (stroke width, sizing, style)
4. **Optimization** — Clean SVG code (SVGO), remove unnecessary attributes
5. **Component Export** — Optional React/Vue components
6. **Sprite Sheet** — Generate SVG sprite for efficient loading

---

## Instructions

### Phase 1: Gather Requirements

**If icon list not provided, ask:**
1. What actions/objects need icons? (List 8-16 common UI needs)
2. Icon style preference? (outline, filled, duotone, hand-drawn, flat, 3D)
3. Size target? (16px, 24px, 32px — affects detail level)
4. Export format? (SVG only, or + React components)

**Common icon sets:**
- **Navigation:** home, search, settings, profile, menu, close, back, forward
- **Actions:** add, edit, delete, save, share, download, upload, refresh
- **Communication:** mail, message, notification, phone, video, chat
- **Media:** play, pause, stop, volume, image, camera, mic
- **E-commerce:** cart, wishlist, payment, shipping, receipt
- **Status:** check, error, warning, info, loading, success, pending

### Phase 2: Generate Icons (15-20 minutes)

For each icon, call gemini-svg-creator with consistent parameters:

```bash
/gemini-svg-creator "[icon-name] icon, [style] style, [detail-level], monochrome, 24x24px viewBox, centered, clean paths, optimized for web. Stroke width: 2px (if outline), no gradients (unless duotone)."
```

**Style-specific prompts:**

**Outline:**
```
"[Icon] icon, outline style, 2px stroke, rounded line caps, no fill, 24x24px viewBox, minimalist"
```

**Filled:**
```
"[Icon] icon, filled solid style, single color, no stroke, 24x24px viewBox, simple shapes"
```

**Duotone:**
```
"[Icon] icon, duotone style, two-tone fill (primary + 40% opacity secondary), 24x24px viewBox"
```

**Hand-drawn:**
```
"[Icon] icon, hand-drawn sketch style, organic lines, slight imperfections, 24x24px viewBox"
```

**Batch generation:** Use `/banana batch` if generating >8 icons, or loop gemini-svg-creator.

### Phase 3: Consistency Validation

Check generated icons for coherence:

- [ ] **Stroke width:** All outline icons use same stroke (2px typical)
- [ ] **ViewBox:** All icons use 24x24 (or chosen size)
- [ ] **Alignment:** Icons centered in viewBox
- [ ] **Detail level:** Similar complexity across set
- [ ] **Style:** Visual language consistent (all sharp corners OR all rounded)

**If inconsistent:** Regenerate outliers with refined prompts matching majority style.

### Phase 4: SVG Optimization

Use SVGO to clean generated SVGs:

```bash
cd ~/Documents/icon-sets/[project]/raw/
for file in *.svg; do
  npx svgo "$file" -o "../optimized/${file}" \
    --multipass \
    --precision=2 \
    --disable=removeViewBox \
    --enable=removeDimensions
done
```

**Manual fallback (if SVGO unavailable):**
- Remove `width` and `height` attributes (keep only `viewBox`)
- Remove unnecessary `id` attributes
- Simplify paths (combine when possible)
- Remove comments and metadata

### Phase 5: Component Export (Optional)

If React components requested:

```tsx
// ~/Documents/icon-sets/[project]/components/Icon[Name].tsx
import React from 'react';

interface IconProps {
  size?: number;
  color?: string;
  className?: string;
}

export const IconHome: React.FC<IconProps> = ({ 
  size = 24, 
  color = 'currentColor',
  className = ''
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke={color}
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    {/* SVG path here */}
  </svg>
);
```

**Index file:**
```tsx
// ~/Documents/icon-sets/[project]/components/index.ts
export { IconHome } from './IconHome';
export { IconSearch } from './IconSearch';
// ... all icons
```

### Phase 6: SVG Sprite Sheet

Create single sprite file for efficient loading:

```svg
<!-- ~/Documents/icon-sets/[project]/sprite.svg -->
<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
  <symbol id="icon-home" viewBox="0 0 24 24">
    <!-- home icon paths -->
  </symbol>
  <symbol id="icon-search" viewBox="0 0 24 24">
    <!-- search icon paths -->
  </symbol>
  <!-- ... all icons -->
</svg>
```

**Usage in HTML:**
```html
<svg class="icon"><use href="/sprite.svg#icon-home"></use></svg>
```

### Phase 7: Delivery Package

```
~/Documents/icon-sets/[project]-[date]/
  ├── raw/               # Original generated SVGs
  ├── optimized/         # SVGO processed
  ├── components/        # React/Vue components (if requested)
  ├── sprite.svg         # Combined sprite sheet
  ├── icon-manifest.json # Metadata (names, sizes, tags)
  └── README.md          # Usage instructions
```

**icon-manifest.json:**
```json
{
  "project": "[name]",
  "style": "[outline|filled|duotone]",
  "count": 12,
  "size": "24x24",
  "icons": [
    {
      "id": "home",
      "name": "Home",
      "tags": ["navigation", "house", "start"],
      "file": "optimized/home.svg"
    }
  ]
}
```

### Phase 8: Summary

```
✅ Icon set generation complete!

📁 Location: ~/Documents/icon-sets/[project]-[date]/

📦 Package contents:
  • [N] icons in [style] style
  • Optimized SVGs (SVGO processed)
  • SVG sprite sheet (single file loading)
  • React components (optional)
  • Icon manifest with metadata

🎨 Icons:
  [list icon names]

💡 Usage:
  - Import individual SVGs: /optimized/[icon].svg
  - Use sprite: <use href="/sprite.svg#icon-[name]"></use>
  - React: import { Icon[Name] } from './components'

All icons validated for consistency (stroke width, viewBox, alignment).

Need additional icons or want to adjust the style?
```

---

## Dependencies

- `/gemini-svg-creator` (primary generator)
- `npx svgo` (optimization, optional)
- Node.js (for React component generation)

---

## Pro Tips

- **Stroke width matters:** 1px = delicate, 2px = standard, 3px = bold
- **Rounded caps:** More friendly than sharp (strokeLinecap="round")
- **Test at target size:** 16px icons need less detail than 32px
- **Color:** Use `currentColor` for inherit from text color
- **Accessibility:** Add `aria-label` or `<title>` for screen readers

---

## Example

```
User: /icon-set Hone
Assistant: Generates 12 cohesive outline icons for Hone platform
```
