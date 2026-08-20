---
description: Production-grade UI design with distinctive aesthetics
---

# Frontend Aesthetics

Guide frontend implementation with bold aesthetic commitment to avoid generic "AI slop" interfaces. Forces clear design direction BEFORE writing code.

## When to Use

- Building new web components
- Creating product pages
- Designing dashboards or admin panels
- Any user-facing UI work
- Redesigning existing interfaces

## Core Principle

**Choose a bold aesthetic direction upfront.** Generic AI interfaces converge on safe choices (Inter font, purple gradients, predictable layouts). Distinctive interfaces commit to an extreme and execute with precision.

## Aesthetic Questionnaire

Before writing ANY UI code, answer these:

### 1. Tone (pick ONE extreme)

Which aesthetic direction?

- **Brutally minimal** — White space dominates, single accent color, restrained typography
- **Maximalist chaos** — Layered elements, rich textures, abundant detail
- **Retro-futuristic** — 80s sci-fi, neon, geometric grids, CRT effects
- **Organic/natural** — Soft curves, earth tones, flowing layouts, natural textures
- **Luxury/refined** — Serif typography, gold accents, elegant spacing, subtle animations
- **Playful/toy-like** — Bright colors, rounded corners, bouncy animations, illustrations
- **Editorial/magazine** — Bold typography hierarchy, asymmetric layouts, high contrast
- **Brutalist/raw** — Exposed structure, monospace fonts, stark contrast, no decoration
- **Art deco/geometric** — Sharp angles, symmetry, metallic accents, bold patterns
- **Soft/pastel** — Muted colors, gentle gradients, rounded shapes, calm aesthetic
- **Industrial/utilitarian** — Function-first, monochrome, grid-based, technical feel

### 2. Typography Stack

**Display font:** [Choose distinctive font — NEVER Inter/Roboto/Arial/system fonts]

**Body font:** [Pair with refined readable font]

**Examples of good pairings:**
- Playfair Display + Source Sans Pro
- Space Grotesk + Inter (only if display is distinctive)
- Bebas Neue + Open Sans
- Raleway + Lora
- Montserrat + Merriweather

### 3. Color Palette

**Dominant color:** [hex] — The color that defines the interface

**Accent color:** [hex] — Sharp contrast for CTAs and highlights

**Background treatment:** Choose one:
- Gradient mesh (complex multi-color gradients)
- Noise texture (grain overlay for depth)
- Geometric pattern (repeating shapes)
- Dramatic shadows (layered depth)
- Layered transparency (glass morphism)

### 4. Differentiation

**What makes this UNFORGETTABLE?**

The one thing someone will remember after using this interface:

[Answer must be specific and visual]

### 5. Complexity Match

- [ ] **Maximalist vision** → Elaborate code required (extensive animations, decorative elements, rich textures, complex effects)
- [ ] **Minimalist vision** → Precision required (careful spacing, subtle details, typography focus, restraint)

Elegance comes from executing the vision well, not from choosing minimalism over maximalism.

## Anti-Patterns (Auto-Reject)

If ANY of these appear in the implementation, reject immediately:

- ❌ Inter, Roboto, Arial, or system fonts as primary typeface
- ❌ Purple gradients on white backgrounds
- ❌ Predictable card-based layouts without variation
- ❌ Cookie-cutter components (generic buttons, standard modals)
- ❌ Evenly distributed color palettes (all colors equal weight)
- ❌ Solid color backgrounds with no texture or depth
- ❌ Generic spacing (always 16px padding, always 24px gaps)
- ❌ No animations or only fade-in effects
- ❌ Default component styling without customization

## Focus Areas

### Typography
- Choose fonts that are beautiful, unique, and interesting
- Pair distinctive display font with refined body font
- Use font weight and size to create hierarchy
- Don't default to system fonts

### Color & Theme
- Commit to cohesive aesthetic
- Use CSS variables for consistency
- Dominant colors with sharp accents > timid palettes
- Dark mode should be equally distinctive

### Motion
- Prioritize CSS-only animations for HTML
- Use Motion library for React
- One well-orchestrated page load > scattered micro-interactions
- Stagger reveals with animation-delay
- Scroll-triggered effects
- Hover states that surprise

### Spatial Composition
- Break the grid intentionally
- Asymmetry for interest
- Overlap elements
- Diagonal flow
- Generous negative space OR controlled density (pick one)

### Backgrounds & Visual Details
- Create atmosphere and depth
- Gradient meshes
- Noise textures
- Geometric patterns
- Layered transparencies
- Dramatic shadows
- Decorative borders
- Custom cursors
- Grain overlays

## Implementation Checklist

Before declaring UI work complete:

- [ ] Aesthetic direction chosen and documented
- [ ] Typography: custom fonts loaded and applied
- [ ] Color: CSS variables defined and used consistently
- [ ] Motion: key interactions have smooth animations
- [ ] Backgrounds: depth created (not solid colors)
- [ ] Anti-patterns: none present
- [ ] Responsive: works on mobile/tablet/desktop
- [ ] Accessibility: color contrast ≥ 4.5:1, focus states visible
- [ ] Distinctive: passes "would I recognize this if I saw it again?" test

## Usage

```bash
# Start new UI component with aesthetic brief
/frontend-aesthetics

# Review existing UI for AI slop
/frontend-aesthetics review <path>
```

## Output

**Aesthetic Brief Document** including:
1. Chosen tone with rationale
2. Typography stack with font CDN links
3. Color palette with hex codes
4. Background treatment with CSS examples
5. Key differentiator
6. Implementation complexity match
7. Anti-pattern checklist

Then proceed with implementation following the brief.

## Example Brief

```markdown
## Aesthetic Brief: Hone Admin Dashboard

**Tone:** Editorial/magazine (bold typography hierarchy, asymmetric layouts, high contrast)

**Typography:**
- Display: Playfair Display (serif, elegant, magazine-style)
- Body: Inter (refined, readable, pairs well)

**Color Palette:**
- Dominant: #1a1a2e (deep navy)
- Accent: #f39c12 (warm gold)
- Background: Noise texture (subtle grain on dark base)

**Differentiation:**
Large, bold section headers that overlap content areas. Numbers and stats displayed in oversized Playfair Display. Asymmetric card layouts that break the grid.

**Complexity:** Maximalist → Needs elaborate code (layered elements, scroll-triggered reveals, hover effects on stat cards)

**Anti-patterns check:** ✓ No Inter as display, ✓ No purple gradients, ✓ Asymmetric layout, ✓ Custom styling
```

## Lessons

- **2026-06-15** — `research_the_actual_ui_pattern_before_co`: Research the actual UI pattern before coding automation - dont assume based on mobile screenshots _(context: Mobile screenshots showed skill input that looked like autocomplete. Coded entire autocomplete interaction pattern. Web search of Freelancer support docs revealed it's actually category-based checkboxes, not free-text input. All the autocomplete code was wrong. Lesson: Use WebSearch to find official docs/support pages that explain the actual UI pattern before writing any code.)_ [src: task-unknown]
- **2026-06-16** — `ui-button-label-vs-action-mismatch`: Verify a UI action button calls the action its LABEL implies. A 'SUBMIT BID' button calling queue_bid (loop-back to Bid Pending) silently never advanced drafts. Check onclick action == label intent. _(context: Bridge bid-review 'SUBMIT BID' called queue_bid not submit_bid -> approving a draft looped it back instead of submitting. Feature existed; was just mis-wired + starved by the broken board.)_ [src: session/2026-06-16-bridge]
- **2026-06-22** — `domain_aware_lesson_filtering`: Lesson routing now validates domain relevance before appending to skill files. Prevents cross-contamination where infrastructure/security lessons land in frontend skills just because they touched a React codebase. _(context: frontend-aesthetics had 11 lessons, only 2 were about frontend design. Rest were CVE fixes, security headers, iOS builds. Added SKILL_DOMAINS map + _is_lesson_relevant() check using NVIDIA fast tier.)_ [src: session/2026-06-22-skill-improvement]
