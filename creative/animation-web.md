# Web Animation Code Generation

Generate production-ready CSS and JavaScript animation code following motion design principles.

## Usage

```bash
/animation-web <description> [--library=<css|gsap|framer-motion>] [--duration=<ms>]
```

**Examples:**
- `/animation-web "smooth fade-in on page load"`
- `/animation-web "staggered card grid reveal" --library=gsap`
- `/animation-web "button hover with elastic bounce" --library=framer-motion`

## What It Does

1. **Animation Analysis** — Break down the desired animation into steps
2. **Motion Principles** — Apply easing, timing, and orchestration rules
3. **Code Generation** — Output production-ready code for chosen library
4. **Accessibility** — Include `prefers-reduced-motion` support
5. **Usage Example** — Provide HTML/JSX integration example

---

## Instructions

### Phase 1: Animation Specification (2 minutes)

Parse user description and determine:

**Animation type:**
- **Entrance:** fade-in, slide-in, scale-up, bounce-in
- **Exit:** fade-out, slide-out, scale-down, collapse
- **Attention:** pulse, shake, wiggle, glow
- **Transition:** morph, flip, rotate, swap
- **Scroll-driven:** parallax, reveal-on-scroll, sticky-header
- **Hover/interaction:** scale, lift, ripple, color-shift

**Parameters:**
- Duration (default: 300ms for micro-interactions, 600ms for entrances, 1200ms for scroll)
- Easing (default: `cubic-bezier(0.4, 0.0, 0.2, 1)` — ease-out)
- Delay (default: 0ms, or staggered for groups)
- Library preference (default: CSS if simple, GSAP if complex, Framer Motion if React)

**Ask if unclear:**
1. When does animation trigger? (page load, scroll, hover, click)
2. Single element or group? (affects stagger logic)
3. One-time or repeating?
4. Library/framework constraints?

### Phase 2: Motion Principles Application (genjutsu reference)

Apply motion design rules:

**Timing:**
- **Micro-interactions (buttons, toggles):** 200-300ms
- **Element entrances:** 400-600ms
- **Page transitions:** 800-1200ms
- **Complex sequences:** 1500-2500ms

**Easing:**
- **Ease-out (default):** Starts fast, ends slow — natural, most common
- **Ease-in:** Starts slow, ends fast — exits, disappearing elements
- **Ease-in-out:** Symmetrical — smooth, elegant, but can feel slow
- **Spring/elastic:** Overshoots then settles — playful, attention-grabbing
- **Linear:** Constant speed — use sparingly (progress bars, rotations)

**Best easing curves:**
```
ease-out: cubic-bezier(0.4, 0.0, 0.2, 1)  /* Material Design */
ease-in:  cubic-bezier(0.4, 0.0, 1, 1)
ease-in-out: cubic-bezier(0.4, 0.0, 0.6, 1)
spring: cubic-bezier(0.34, 1.56, 0.64, 1) /* Slight overshoot */
```

**Orchestration:**
- **Stagger:** Delay each item by 50-100ms for cascading effect
- **Sequence:** Chain animations (A finishes → B starts)
- **Parallel:** Multiple animations simultaneously

### Phase 3: Code Generation

#### CSS-only (simple animations)

```css
/* [Animation Name] */
@keyframes [name] {
  0% {
    [initial-properties]
  }
  100% {
    [final-properties]
  }
}

.[target-class] {
  animation: [name] [duration]ms [easing] [delay]ms [iteration];
}

/* Accessibility: Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  .[target-class] {
    animation: none;
    /* Instant final state */
    [final-properties]
  }
}
```

**Example (fade-in):**
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 600ms cubic-bezier(0.4, 0.0, 0.2, 1) forwards;
}

@media (prefers-reduced-motion: reduce) {
  .animate-fade-in {
    animation: none;
    opacity: 1;
    transform: translateY(0);
  }
}
```

#### GSAP (complex, timeline-based)

```javascript
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// [Animation Description]
function [functionName]() {
  const timeline = gsap.timeline({
    defaults: {
      duration: [duration / 1000],
      ease: '[ease-name]'
    }
  });
  
  timeline
    .[method]('[selector]', {
      [properties]
    })
    .[method]('[selector]', {
      [properties]
    }, '[position]'); // e.g., "<", "+=0.5"
  
  return timeline;
}

// Accessibility
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!prefersReducedMotion) {
  [functionName]();
}
```

**Example (staggered cards):**
```javascript
import { gsap } from 'gsap';

function animateCards() {
  const tl = gsap.timeline({
    defaults: {
      duration: 0.6,
      ease: 'power2.out'
    }
  });
  
  tl.from('.card', {
    opacity: 0,
    y: 50,
    stagger: 0.1, // 100ms between each card
    clearProps: 'all' // Remove inline styles after animation
  });
  
  return tl;
}

// Respect reduced motion
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  animateCards();
}
```

#### Framer Motion (React)

```tsx
import { motion } from 'framer-motion';

// [Animation Description]
const [variants-name]Variants = {
  hidden: {
    [initial-properties]
  },
  visible: {
    [final-properties],
    transition: {
      duration: [duration / 1000],
      ease: [[ease-array]],
      staggerChildren: [stagger / 1000], // if group
      delayChildren: [delay / 1000]
    }
  }
};

export const [ComponentName] = () => (
  <motion.div
    variants={[variants-name]Variants}
    initial="hidden"
    animate="visible"
    whileHover="hover" // optional
  >
    {/* Content */}
  </motion.div>
);
```

**Example (button hover):**
```tsx
import { motion } from 'framer-motion';

const buttonVariants = {
  rest: {
    scale: 1
  },
  hover: {
    scale: 1.05,
    transition: {
      duration: 0.2,
      ease: [0.34, 1.56, 0.64, 1] // Spring easing
    }
  },
  tap: {
    scale: 0.95
  }
};

export const AnimatedButton = ({ children, ...props }) => (
  <motion.button
    variants={buttonVariants}
    initial="rest"
    whileHover="hover"
    whileTap="tap"
    {...props}
  >
    {children}
  </motion.button>
);
```

### Phase 4: Usage Example

Provide integration code:

**CSS:**
```html
<!-- Add class to target element -->
<div class="animate-fade-in">
  <h1>Hello World</h1>
</div>

<!-- Include CSS file -->
<link rel="stylesheet" href="animations.css">
```

**GSAP:**
```html
<!-- Include GSAP -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script src="your-animation.js"></script>

<!-- Call on DOM ready -->
<script>
  document.addEventListener('DOMContentLoaded', () => {
    animateCards();
  });
</script>
```

**Framer Motion:**
```tsx
// Import component
import { AnimatedButton } from './components/AnimatedButton';

// Use in JSX
<AnimatedButton onClick={() => console.log('Clicked!')}>
  Click Me
</AnimatedButton>
```

### Phase 5: Delivery Package

```
~/Documents/animations/[animation-name]-[date]/
  ├── [library]-animation.{css|js|tsx}
  ├── usage-example.html
  ├── animation-spec.md
  └── preview.html (interactive preview)
```

**animation-spec.md:**
```markdown
# [Animation Name]

**Library:** [CSS | GSAP | Framer Motion]  
**Duration:** [duration]ms  
**Easing:** [easing description]  
**Trigger:** [page load | scroll | hover | click]

## Motion Principles Applied

- **Timing:** [rationale for duration]
- **Easing:** [why this curve]
- **Orchestration:** [stagger/sequence/parallel]

## Accessibility

✅ `prefers-reduced-motion` support included  
✅ Final state rendered instantly when motion disabled

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Fallback: instant final state (no animation)

## Usage

[Step-by-step integration instructions]

## Customization

- **Duration:** Change `[duration]ms` to adjust speed
- **Easing:** Replace `[easing]` with custom curve
- **Delay:** Add `animation-delay` or `delay` property
```

### Phase 6: Summary

```
✅ Animation code generated!

📁 Location: ~/Documents/animations/[name]-[date]/

📦 Package contents:
  • Production-ready [library] code
  • Usage example with HTML/JSX
  • Animation specification with motion principles
  • Interactive preview (open in browser)

⚡ Animation: [description]
⏱️ Duration: [duration]ms
🎭 Easing: [easing-name]
♿ Accessibility: prefers-reduced-motion supported

Copy code to your project and adjust as needed.

Want variations or different library?
```

---

## Motion Principles Quick Reference

### Do:
✅ Use ease-out for entrances (starts fast, feels responsive)  
✅ Keep micro-interactions under 300ms  
✅ Stagger grouped animations (50-100ms per item)  
✅ Support `prefers-reduced-motion`  
✅ Clear inline styles after animation (`clearProps` in GSAP)

### Don't:
❌ Use ease-in-out for everything (feels sluggish)  
❌ Animate width/height (use scale instead — GPU accelerated)  
❌ Make page-load animations >1s (impatient users)  
❌ Forget to test on mobile (60fps only on powerful devices)  
❌ Animate without purpose (motion should communicate)

---

## Performance Tips

**GPU-accelerated properties (fast):**
- `transform` (translate, scale, rotate)
- `opacity`
- `filter`

**CPU-bound properties (slow):**
- `width`, `height`
- `top`, `left`, `margin`, `padding`
- `color`, `background-color` (unless using `will-change`)

**Optimization:**
```css
/* Force GPU layer */
.animated-element {
  will-change: transform, opacity;
  transform: translateZ(0); /* Hardware acceleration hack */
}

/* Remove after animation */
.animated-element.animation-done {
  will-change: auto;
}
```

---

## Dependencies

- genjutsu motion principles (reference)
- CSS (built-in)
- GSAP (CDN or npm: `gsap`)
- Framer Motion (npm: `framer-motion`)

---

## Example

```
User: /animation-web "smooth fade-in on page load"
Assistant: Generates CSS keyframes with ease-out, 600ms duration, includes reduced-motion fallback
```
