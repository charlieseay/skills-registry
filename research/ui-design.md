# UI Design

Generate high-craft, pixel-perfect frontend interfaces following the Seaynic Labs Design System.

## What it does

Loads design system standards before generating any UI component or page. Prevents generic "AI boilerplate" by enforcing:
- Design token architecture (CSS variables)
- Motion physics (spring animations, not linear)
- Component libraries (Magic UI, Aceternity UI, shadcn/ui)
- Accessibility patterns (WCAG 2.1 AA, keyboard-first)
- Visual polish (layered shadows, fluid typography, 8px rhythm)

## When to use

Invoke this skill before:
- Building React/Next.js components
- Generating Tailwind CSS layouts
- Adding animations with Framer Motion or GSAP
- Creating landing pages, dashboards, or marketing sites

## How it works

1. Loads `Standards/UI Design System.md` into context
2. Queries `tech-kb` for Next.js/Tailwind/Framer Motion documentation
3. References `Research/UI Component Libraries.md` for production patterns
4. Applies design tokens and motion physics
5. Validates output against accessibility checklist

## Usage

```
/ui-design
```

Then describe the component or page you want to build. The skill will:
- Apply design system standards automatically
- Reference component libraries before generating from scratch
- Ensure keyboard navigation and ARIA attributes
- Use spring physics for all animations
- Follow 8px spacing rhythm

## Examples

**Hero section:**
```
/ui-design
Build a hero section for the Hone landing page with:
- Fluid typography scaling from mobile to desktop
- Subtle gradient background (zinc palette)
- CTA button with emerald accent color
- Scroll-triggered fade-in animation
```

**Interactive card:**
```
/ui-design
Create a feature card component with:
- Hover scale effect (spring physics)
- Inner glow on hover
- Sharp borders with layered shadows
- Nested border radius (parent rounded-2xl, child rounded-xl)
```

**Form input:**
```
/ui-design
Build an accessible email input with:
- Focus ring styling
- Inline validation error state
- Helper text below input
- Keyboard navigable
```

## Anti-Patterns (Will be rejected)

- Generic purple-to-indigo gradients
- Solid blue buttons without design tokens
- Flat black backgrounds (`bg-black`)
- `duration-300` for all animations (use spring physics)
- Missing keyboard focus indicators
- Hardcoded colors instead of CSS variables

## Quality Gates

Before marking work complete, verify:
- [ ] Uses design tokens (CSS variables, not hardcoded hex)
- [ ] Typography follows established hierarchy
- [ ] Spacing aligns to 8px grid
- [ ] Interactive elements have hover/active/focus states
- [ ] Keyboard navigable (test with Tab only)
- [ ] ARIA attributes present on custom controls
- [ ] Dark mode styled (not just inverted colors)
- [ ] Motion respects `prefers-reduced-motion`

## Related Skills
- `/frontend-aesthetics` — Visual polish and animation
- `/ui-ux-pro-max` — UX patterns and flows
- `/frontend-design:frontend-design` — Full design workflow

## Files Referenced
- `Standards/UI Design System.md` — Core design principles
- `Research/UI Component Libraries.md` — Component catalog
- `~/Projects/claude-config/bin/load-ui-standards.sh` — Shell loader

---

## Implementation

```typescript
import { motion } from 'framer-motion'

// Load design system
const VAULT_ROOT = process.env.HOME + '/Library/Mobile Documents/iCloud~md~obsidian/Documents/SeaynicNet'
const designSystemPath = `${VAULT_ROOT}/Standards/UI Design System.md`
const componentLibsPath = `${VAULT_ROOT}/Research/UI Component Libraries.md`

// Read standards
const designSystem = fs.readFileSync(designSystemPath, 'utf-8')
const componentLibs = fs.readFileSync(componentLibsPath, 'utf-8')

// Query tech-kb for platform docs (requires NotebookLM auth)
// nlm notebook query tech-kb "Next.js App Router data fetching patterns"

// Generate UI with design system context
console.log('✅ Design system loaded')
console.log('🎨 Applying design tokens, motion physics, and accessibility patterns')
```

## Next Steps

After generating UI:
1. Test keyboard navigation (Tab through all interactive elements)
2. Verify dark mode rendering
3. Check motion respects `prefers-reduced-motion`
4. Run Lighthouse accessibility audit
5. Commit to git with `/checkpoint`
