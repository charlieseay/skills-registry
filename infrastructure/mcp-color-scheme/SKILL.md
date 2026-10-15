---
name: mcp-color-scheme
description: Generate harmonious color palettes via The Color API. 8 color scheme tools (monochrome, analogic, complement, triad, quad, analogic-complement). Input seed color (hex/RGB/HSL), get palette with names/hex/RGB/HSL output. No external API key required — queries https://www.thecolorapi.com/scheme (public endpoint).
---

# Color Scheme Generator MCP

The `color-scheme` MCP server (proxy name `color-scheme`, Node.js launcher at
`/Users/charlieseay/Projects/color-scheme-mcp/build/index.js`) generates
harmonious color palettes using **The Color API** (thecolorapi.com). It
provides 8 scheme generation tools based on color theory (monochrome, analogic,
complement, triad, quad, and their variants). All queries hit the **free public
API** — no API key required.

**Architecture:** TypeScript + MCP SDK, compiled to JavaScript. Uses node-fetch
to query thecolorapi.com endpoints. Accepts seed colors in hex, RGB, or HSL
format; normalizes all inputs and returns results with hex, RGB, HSL, and
color name fields.

## Input format flexibility

The server accepts seed colors in **three formats**, automatically detected:

- **Hex:** `#FF5733`, `FF5733` (with or without `#`)
- **RGB:** `255,87,51` or `rgb(255, 87, 51)` (the tool strips `rgb(...)` wrapper)
- **HSL:** `10,100%,60%` or `hsl(10, 100%, 60%)` (the tool strips `hsl(...)` wrapper)

**Unknown format → defaults to hex.** If the input doesn't match any pattern,
the tool assumes it's a hex string and passes it to the API. The API will reject
invalid hex; the tool returns an HTTP error message.

## Tool catalog (8 tools, tested live 2026-09-30 against /Users/charlieseay/Projects/color-scheme-mcp/src/tools/index.ts:111-296)

**Monochromatic (single hue, varying lightness):**
- `generate_monochrome_scheme(color, count=5)` — variations of a single hue
  (from light to dark). Useful for subtle, cohesive designs.
- `generate_monochrome_dark_scheme(color, count=5)` — dark variants of a hue
  (high saturation, low lightness). For dramatic/moody palettes.
- `generate_monochrome_light_scheme(color, count=5)` — light variants of a hue
  (high lightness, low saturation). For soft, airy palettes.

**Color Wheel (harmonic relationships):**
- `generate_analogic_scheme(color, count=5)` — colors adjacent on the color
  wheel. Creates harmony (e.g., blue + blue-green + green). Safe for complex
  designs.
- `generate_complement_scheme(color, count=5)` — opposite colors on the wheel.
  High contrast (e.g., blue + orange). Use sparingly for accent emphasis.
- `generate_analogic_complement_scheme(color, count=5)` — mix analogic
  (adjacent) + one complement opposite. Balanced contrast without harsh clash.
- `generate_triad_scheme(color, count=5)` — three evenly spaced colors on the
  wheel. Balanced, playful, works well for multi-section layouts.
- `generate_quad_scheme(color, count=5)` — four evenly spaced colors (180°
  apart). Maximum diversity; requires careful balance to avoid visual chaos.

**All tools accept:**
- `color` (string, required) — seed color (hex/RGB/HSL)
- `count` (integer, optional, default 5) — palette size (3–10 colors). Larger
  counts may include repeats or gradations.

**All tools return:**
```json
{
  "scheme_mode": "triad",
  "seed_color": "#FF5733",
  "color_count": 5,
  "colors": [
    {
      "position": 1,
      "hex": "#FF5733",
      "rgb": "rgb(255, 87, 51)",
      "hsl": "hsl(10, 100%, 60%)",
      "name": "Red-Orange"
    },
    ...
  ]
}
```

Each color object includes exact hex/RGB/HSL values **plus a named color** (e.g.,
"Coral Red", "Sky Blue") from The Color API's name database. Useful for
accessibility (screen readers) and designer communication.

## The Color API (thecolorapi.com): behavior & limits

**Query format:**
```
https://www.thecolorapi.com/scheme?hex=FF5733&mode=triad&count=5&format=json
```

**Supported `mode` values:**
- `monochrome`, `monochrome-dark`, `monochrome-light`
- `analogic`, `complement`, `analogic-complement`
- `triad`, `quad`

**Response format:**
Always JSON. API returns an object with:
- `seed` — the input color (in all three formats)
- `colors` — array of color objects (each with hex, rgb, hsl, name)

**Error handling:**
If the API rejects the seed color (e.g., invalid hex `ZZZ000`), the tool
catches the error and returns: `"Error generating <mode> color scheme: <error details>"`.

## Known issues & limitations (tested 2026-09-30)

**1. The Color API may be slow or rate-limited during high demand**
- Each tool call makes a **synchronous HTTP request** to thecolorapi.com.
- If the API is down or slow (>10s timeout), the tool returns an error.
- **No retry logic:** If a call times out, it fails immediately; no backoff.
- **Typical latency:** 200–500 ms per call.

**2. Color names are descriptive, not standardized**
- The API's `name.value` is a human-friendly label, not a CSS/X11 color name.
- Examples: "Vivid Orange Red" (not "OrangeRed"), "Pale Peach" (not a CSS name).
- **Use for:** communication with designers, accessibility labels. **Don't rely on:**
  parsing names to recover hex values (use hex directly).

**3. `count` parameter doesn't guarantee unique colors**
- Requesting `count=10` from a monochrome scheme may return some repeated
  shades (especially at count boundaries).
- **Workaround:** Request `count=5` for consistent, evenly spaced results.
  Request higher counts only if you explicitly want gradations.

**4. No custom color mixing or theory validation**
- The tool applies The Color API's built-in algorithms (color wheel geometry).
- It does **not** implement WCAG contrast checking, color blindness simulation,
  or perceptual uniformity (Oklab/LCH).
- **For accessibility:** You must separately validate contrast ratios of chosen
  colors (use WCAG tools).

**5. API returns RGB values as integers (0–255)**
- The tool formats them as `rgb(R, G, B)` strings.
- If you need CSS rgb() with alpha, append `/ 1.0` yourself (e.g., `rgb(255 87 51 / 0.8)`).

## Quick self-check

**Test a simple color scheme generation:**

Call `generate_triad_scheme(color="#FF5733", count=5)`. Expected response
(format shown above): scheme_mode="triad", 5 colors with hex/rgb/hsl/name.

**Test format detection:**

Seed colors:
- Hex: `#FF5733` → parsed as hex ✓
- RGB: `255,87,51` → parsed as RGB ✓
- HSL: `10,100%,60%` → parsed as HSL ✓
- Unknown: `MyFavoriteRed` → defaults to hex, API rejects, tool returns error

**Verify API connectivity:**

```bash
curl -s "https://www.thecolorapi.com/scheme?hex=FF5733&mode=triad&count=5&format=json" | jq .
```

If this returns a JSON object with `seed` and `colors` fields, the API is reachable.
