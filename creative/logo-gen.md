# Logo Generation Pipeline

Complete logo generation workflow: brand research → aesthetic direction → concept generation → delivery in multiple formats.

## Usage

```bash
/logo-gen <app-name> [description]
```

**Examples:**
- `/logo-gen Acme` — Interactive mode (asks for description)
- `/logo-gen StoryNest "a children's storybook reading app"`
- `/logo-gen TechFlow "SaaS platform for developers"`

## What It Does

Orchestrates multiple skills to produce production-ready logo concepts:

1. **Brand Research** (`/brand-name`) — Conflict check, positioning, personality
2. **Aesthetic Direction** (`/frontend-aesthetics`) — Visual direction questionnaire
3. **Concept Generation** — Produces 3 logo concepts:
   - **Vector SVG** via `/gemini-svg-creator` (scalable, editable)
   - **Raster hero** via `/banana generate` (photo-realistic, detailed)
   - **Simplified icon** via `/gemini-svg-creator` (app icon, favicon)
4. **Delivery Package** — Organized output with all formats

---

## Instructions

You are a logo generation orchestrator. Follow this pipeline exactly:

### Phase 1: Brand Research (5 minutes)

Run `/brand-name <app-name> [description]` to get:
- Trademark conflicts (severity: 🔴 Blocking / 🟡 Concern / 🟢 Clear)
- Domain availability
- Name variants (if conflicts exist)
- Positioning statement
- Brand personality (3-5 adjectives)
- Recommended color palettes (3 options with rationale)
- Typography direction
- Icon concepts (2-3 descriptions)
- Tagline options

**Decision point:** If name has 🔴 Blocking conflicts, present variants and ask user to choose. Otherwise proceed with original name.

### Phase 2: Aesthetic Direction (3 minutes)

Run `/frontend-aesthetics` with focus on logo design. Get:
- Tone (which extreme aesthetic: minimal, maximalist, retro-futuristic, etc.)
- Typography stack (display + body fonts)
- Color palette (dominant + accent with hex codes)
- Differentiation (the unforgettable element)

**Use the brand research colors as starting point** — refine with user input.

### Phase 3: Concept Generation (10-15 minutes)

Generate 3 distinct logo concepts in parallel:

#### Concept A: Vector Wordmark + Symbol
```bash
/gemini-svg-creator "Professional logo for [app-name]: [positioning]. Style: [tone from aesthetics]. Wordmark in [display font style] with [symbol description]. Colors: [dominant] primary, [accent] accent. Clean, scalable, memorable. Output as single SVG with grouped elements."
```

#### Concept B: Raster Hero Logo
```bash
/banana generate "High-quality logo design for [app-name], [positioning]. Visual style: [tone]. [Detailed description of imagery, metaphors, composition]. Colors: [palette]. Dramatic lighting, professional, award-winning design. Output: square format, 2048x2048px."
```

#### Concept C: Icon/Emblem
```bash
/gemini-svg-creator "App icon / emblem for [app-name]. Simplified symbol only, no text. Style: [tone]. [Icon concept from brand research]. Single strong shape, works at 16x16px, recognizable in monochrome. Colors: [dominant] + [accent]. Output as centered SVG icon."
```

**Prompt construction rules:**
1. Include positioning statement for context
2. Reference aesthetic tone explicitly
3. Specify colors with hex codes when possible
4. For SVG: emphasize "scalable", "clean paths", "grouped elements"
5. For raster: emphasize "high-quality", "professional", "detailed"
6. For icons: emphasize "simplified", "recognizable at small size", "strong silhouette"

### Phase 4: Delivery Package

Create organized output directory:

```bash
mkdir -p ~/Documents/logos/[app-name]-$(date +%Y%m%d)
cd ~/Documents/logos/[app-name]-$(date +%Y%m%d)
```

Copy generated files:
- `concept-a-wordmark.svg` — Vector wordmark from Concept A
- `concept-b-hero.png` — Raster hero from Concept B  
- `concept-c-icon.svg` — Icon/emblem from Concept C
- `brand-brief.md` — Summary of brand research + aesthetic decisions
- `color-palette.css` — CSS custom properties for the chosen colors

**brand-brief.md template:**
```markdown
# [App Name] Brand Brief

## Positioning
[positioning statement from brand research]

## Brand Personality
[3-5 adjectives with explanations]

## Visual Direction
- **Tone:** [aesthetic tone]
- **Typography:** [display font] / [body font]
- **Colors:** [dominant] (primary), [accent] (accent)
- **Differentiation:** [the unforgettable element]

## Logo Concepts

### Concept A: Wordmark + Symbol
[description]
File: concept-a-wordmark.svg

### Concept B: Hero Logo
[description]
File: concept-b-hero.png

### Concept C: Icon/Emblem
[description]
File: concept-c-icon.svg

## Next Steps
- [ ] Choose primary concept
- [ ] Refine selected concept
- [ ] Generate additional sizes/formats
- [ ] Create brand guidelines document
```

**color-palette.css template:**
```css
:root {
  /* [App Name] Brand Colors — Generated [date] */
  
  /* Primary */
  --brand-primary: [dominant-hex];
  --brand-primary-rgb: [r], [g], [b];
  
  /* Accent */
  --brand-accent: [accent-hex];
  --brand-accent-rgb: [r], [g], [b];
  
  /* Derived shades (lighter/darker variants) */
  --brand-primary-light: [calculated];
  --brand-primary-dark: [calculated];
  --brand-accent-light: [calculated];
  --brand-accent-dark: [calculated];
  
  /* Text on brand colors */
  --brand-on-primary: #ffffff;  /* or #000000 based on contrast */
  --brand-on-accent: #ffffff;   /* or #000000 based on contrast */
}
```

### Phase 5: Summary & Next Steps

Present the delivery package location and contents. Show thumbnails if available (use screenshot/preview tools).

**Template:**
```
✅ Logo generation complete!

📁 Location: ~/Documents/logos/[app-name]-[date]/

📦 Package contents:
  • 3 logo concepts (SVG + PNG)
  • Brand brief with positioning & personality
  • Color palette CSS variables
  • Typography recommendations

🎨 Concepts:
  A. Wordmark + Symbol (vector, scalable)
  B. Hero Logo (raster, detailed)
  C. Icon/Emblem (simplified, app icon ready)

💡 Recommended next steps:
  1. Review all three concepts
  2. Choose your favorite (or request refinements)
  3. Generate additional formats: favicon, social media, letterhead
  4. Create full brand guidelines document

Would you like me to refine any concept or generate additional variations?
```

---

## Error Handling

**If banana-claude fails:**
- Fall back to gemini-svg-creator for Concept B (vector instead of raster)
- Note limitation in delivery summary

**If gemini-svg-creator fails:**
- Fall back to banana-claude for SVG concepts (will be raster)
- Suggest manual vectorization or Inkscape trace

**If brand-name finds blocking conflicts:**
- Present variants
- Wait for user decision before proceeding
- Do not auto-proceed with conflicted name

**If frontend-aesthetics questionnaire times out:**
- Use brand-name recommendations as defaults
- Note that aesthetic direction was auto-selected

---

## Quality Checklist

Before declaring complete:
- [ ] All 3 concepts generated successfully
- [ ] Files saved to organized directory
- [ ] brand-brief.md created with all sections
- [ ] color-palette.css created with proper CSS variables
- [ ] Hex-to-RGB conversion correct (use: rgb = (parseInt(hex.slice(1,3), 16), ...))
- [ ] Contrast check: --brand-on-primary/accent passes WCAG AA (4.5:1)
- [ ] Summary presented with clear next steps
- [ ] User knows where files are located

---

## Pro Tips

### For wordmarks (Concept A):
- Specify letter-spacing and kerning preferences
- Request "optically balanced" spacing
- Mention if all-caps, title-case, or lowercase preferred

### For hero logos (Concept B):
- Reference specific art styles: "flat design", "isometric", "hand-drawn"
- Mention composition: "centered", "dynamic diagonal", "negative space"
- Lighting matters: "soft diffused light", "dramatic side lighting", "rim light"

### For icons (Concept C):
- Test description: "recognizable at 16x16px in monochrome"
- Avoid fine details, thin lines, or complex gradients
- Strong silhouette > intricate detail

### Typography:
- Display fonts: distinctive, memorable (NOT Inter/Roboto/system fonts)
- Body fonts: readable, pairs well with display
- Resources: Google Fonts, Adobe Fonts, Font Squirrel

### Colors:
- Primary should dominate (60-70% usage)
- Accent for CTAs and highlights (10-15% usage)
- Ensure 4.5:1 contrast ratio with white/black for accessibility
- Test in grayscale — logo should work without color

---

## Dependencies

- `/brand-name` skill (installed at `~/.claude/commands/brand-name.md`)
- `/frontend-aesthetics` skill (installed at `~/.claude/commands/frontend-aesthetics.md`)
- `/banana` skill (installed at `~/.claude/skills/banana/`)
- `/gemini-svg-creator` skill (installed at `~/.claude/commands/gemini-svg-creator/`)

All should be available. If any are missing, install from:
- brand-name, frontend-aesthetics: already in Charlie's setup
- banana: `~/Projects/banana-claude/`
- gemini-svg-creator: `~/Projects/gemini-svg-creator/`

---

## Example Session

```
User: /logo-gen Hive "a project management tool for remote teams"