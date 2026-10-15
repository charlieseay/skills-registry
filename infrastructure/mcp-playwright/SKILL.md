---
name: mcp-playwright
description: Lightweight browser automation via the `@playwright/mcp@latest` npm package. Use when you need to automate user interactions on a web page (click, fill forms, navigate) in a headless context. Simpler and more reliable than chrome-devtools for automation tasks; use chrome-devtools if you need debugging tools (console inspection, network monitoring, performance tracing, heap snapshots).
---

# Playwright MCP

The `playwright` MCP server runs `@playwright/mcp@latest` from npm, configured
in `/Users/charlieseay/.config/mcp-proxy/config.json` with `--isolated` flag.
It provides lightweight, headless browser automation focused on user interactions
— a different surface than chrome-devtools (see comparison below).

**Important distinction:** Playwright automates user actions (navigation, clicking,
filling forms, waiting for content). Chrome-devtools provides browser debugging
(console messages, network requests, performance traces, heap snapshots, CSS
inspection). Use playwright for bot-like workflows; use chrome-devtools when
you need to inspect what's happening inside the page.

## How it works

Playwright spawns a headless Chromium/Firefox/WebKit browser instance and
sends commands via stdio (MCP stdio transport). The `--isolated` flag means
each page is in its own process/context — no shared cookies or storage between
invocations. Each invocation starts fresh.

## Tool catalog (from playwright-mcp GitHub, confirmed live in source)

The published npm package exposes approximately **18–20 tools**. Full list
depends on package version; check the live source at
https://github.com/microsoft/playwright-mcp for the authoritative catalog.

**Navigation & page control:**
- `createPage` — spawn a new browser tab
- `goto` — navigate to a URL
- `goBack` / `goForward` / `reload` — navigation history
- `close_page` — close a tab
- `getCurrentUrl` — read the current URL

**Interaction:**
- `click` — click an element by CSS selector or text
- `fill` — type text into an input or textarea
- `press` — press keyboard keys (e.g., "Enter", "Escape")
- `hover` — mouse over an element
- `drag_and_drop` — drag one element onto another
- `focus` — focus an input without filling it

**Wait & conditions:**
- `waitForNavigation` — block until page navigation completes
- `waitForSelector` — block until an element appears
- `waitForTimeout` — sleep for N milliseconds

**Inspection (read-only, returns strings/HTML):**
- `getAttribute` — read an attribute from an element
- `getTextContent` — read visible text from an element
- `getInnerHTML` / `getOuterHTML` — read raw HTML
- `screenshot` — take a PNG of the current viewport
- `pdf` — export current page as PDF

**Cookies & storage:**
- `getCookies` — read all cookies
- `setCookies` — set cookies for the next page load
- `clearCookies` — wipe all cookies

**Session:**
- `setViewportSize` — resize the viewport (useful for testing responsive design)

## Known behavior & gotchas

1. **Headless, no UI.** Playwright runs headless by default — no visual
   browser window. If you need to watch automation happen, you'll need
   screenshot output at key steps.

2. **`--isolated` means fresh state every time.** No persistent cookies or
   localStorage between calls. If a workflow needs authentication state to
   persist across multiple steps, you must either:
   - Capture cookies after login and pass them as arguments to later calls, or
   - Do the full login flow again in the same task

3. **Selectors are CSS by default.** Most Playwright tools use CSS selectors
   (e.g., `#submit`, `.button`, `[data-test="foo"]`). Text-based selectors
   (e.g., `text=Click Me`) are often supported but not guaranteed across all
   tools — check the specific tool's docs if you're not sure.

4. **`waitForNavigation` can timeout.** If a page doesn't navigate (e.g., a
   form submit is blocked by validation), the wait will hang until timeout
   (default often 30 seconds). Always pair with a realistic timeout if you're
   not 100% sure navigation will happen.

5. **Screenshot is viewport-only by default.** `screenshot()` captures only
   the currently visible part of the page, not the full scrolled content. If
   you need the whole page, check whether the tool supports a "full page"
   option.

6. **Timing is hard; add explicit waits.** Automation often needs delays for
   JavaScript to run or async content to load. Playwright has built-in wait
   strategies (`waitForNavigation`, `waitForSelector`), but if you're filling
   a form and the submit button is hidden until you fill a particular field,
   you'll need to add an explicit `waitForSelector` after filling that field
   and before clicking submit.

## When to use playwright vs. chrome-devtools

| Task | Use | Reason |
|------|-----|--------|
| Log into a site, fill a form, submit it | playwright | Simpler API, headless, made for automation |
| Scrape dynamic content (load page, wait for JS, read text) | playwright | Designed for this workflow |
| Check console errors after page load | chrome-devtools | Has `list_console_messages` tool |
| Inspect network requests (see what XHRs fired) | chrome-devtools | Has `list_network_requests` and `get_network_request` |
| Profile performance / Core Web Vitals | chrome-devtools | Has `performance_start_trace` and `lighthouse_audit` |
| Debug CSS for an element | chrome-devtools | Has `get_css_styles` |
| Get page accessibility tree (for AI reading) | chrome-devtools | Has `take_snapshot` (a11y tree) |
| Take a screenshot and inspect visuals | Either | Playwright faster, chrome-devtools richer context |

## Quick verification for this skill

To check the current tool list (in case the npm package has been updated),
inspect the playwright-mcp source directly:

```bash
npm view @playwright/mcp@latest repository.url
# Returns: git+https://github.com/microsoft/playwright-mcp.git
# Then check README.md or src/ for the real tool list.
```

Alternatively, the MCP server publishes its tools via the `tools/list` RPC
when running (use the MCP proxy to invoke it if you need the live list).

## Environment

- **Config file:** `/Users/charlieseay/.config/mcp-proxy/config.json`
  - Command: `npx -y @playwright/mcp@latest --isolated`
  - No auth required (runs locally, no external API)
- **Browser engine:** Chromium by default (Firefox/WebKit available as options
  depending on playwright-mcp version)
- **State:** headless, `--isolated` flag ensures no persistent cookies/storage
