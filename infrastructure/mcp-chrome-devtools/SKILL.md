---
name: mcp-chrome-devtools
description: Full browser debugging and advanced automation via Chrome DevTools Protocol (CDP). Use for inspecting console messages, monitoring network traffic, analyzing performance/Core Web Vitals, inspecting CSS, debugging accessibility trees, taking heap snapshots, running Lighthouse audits. Use playwright for simple bot-like automation (navigation, clicking, filling forms) instead.
---

# Chrome DevTools MCP

Chrome DevTools Protocol (CDP) access via a remote MCP connector. This provides
full browser debugging capabilities — network inspection, console messages,
performance tracing, memory profiling, CSS debugging, accessibility tree
snapshots, and Lighthouse audits — plus advanced automation features you won't
find in playwright (like drag/drop, event emulation, keyboard shortcuts).

**Key distinction from playwright:** DevTools is for inspecting and debugging
what's happening inside a page (console output, network requests, CSS rules,
memory use). Playwright is for automating user interactions (clicking, filling
forms, navigating). Many tasks need both: use playwright to automate, then
chrome-devtools to inspect the results.

## How pages and page IDs work

Every action targets a specific browser tab/page via a `pageId` integer:
- `new_page(url)` — create a tab, returns its ID
- `select_page(pageId)` — make a tab the context for future calls (some tools
  auto-select, others need explicit selection)
- `list_pages()` — list all open tabs and their current URLs
- `close_page(pageId)` — close a tab

Multiple pages can be open simultaneously. Each is independent (different URL,
different console, different cookies if not in the same isolated context).

## Tool catalog (25+ tools, confirmed live in this session)

### Navigation & page control
- `new_page(url, background=false, isolatedContext=None)` — open a new tab,
  optionally in the background, optionally in an isolated browser context (same
  context = shared cookies/storage, different contexts = fully isolated for
  testing auth/cookies in parallel)
- `navigate_page(pageId, type, url=None, handleBeforeUnload, ignoreCache, initScript, timeout)`
  - `type`: "url" (navigate to URL), "back" (history back), "forward" (history
    forward), "reload" (refresh)
  - Always uses the specified pageId; some other tools auto-navigate based on
    the currently selected page
- `close_page(pageId)` — close a tab (cannot close the last open tab)
- `select_page(pageId, bringToFront=false)` — make a tab the current context
  for future tool calls; optionally bring it to front (gives it focus)

### Interaction & automation
- `take_snapshot(pageId, filePath=None, verbose=false)` — get the **accessibility
  tree** (a11y tree) of the current page as structured text with unique element
  identifiers (uids). Each element has a type (button, link, textbox, etc.), its
  text content, and a uid. Use uids to target elements for clicks/fills.
  - `verbose=true` includes all possible a11y info (useful for detailed
    inspection but verbose)
  - This is different from a screenshot — it's a machine-readable tree, not an
    image
  - Always call this first if you need to click/fill elements; it gives you the
    uids to target
- `click(pageId, uid, dblClick=false, includeSnapshot=false)` — click an
  element identified by its uid from a snapshot
- `fill(pageId, uid, value, includeSnapshot=false)` — fill a text input, textarea,
  or select an option in a `<select>` element
- `type_text(pageId, text, submitKey=None)` — type text into a previously
  focused input (no uid needed; types into whatever has focus)
  - `submitKey` — press a key after typing (e.g., "Enter", "Tab", "Escape")
- `press_key(pageId, key, includeSnapshot=false)` — press a key or key combo
  (e.g., "Enter", "Control+A", "Control+Shift+R")
  - Modifiers: Control, Shift, Alt, Meta (e.g., "Meta+L" for Windows key + L)
- `hover(pageId, uid, includeSnapshot=false)` — mouse over an element
- `drag(pageId, from_uid, to_uid, includeSnapshot=false)` — drag one element
  onto another
- `wait_for(pageId, text[], timeout=None)` — block until specified text appears
  on the page (useful for waiting for async content to load)
- `resize_page(pageId, width, height)` — resize the viewport (useful for
  testing responsive design at 375px, 768px, etc.)

### Screenshot & visual inspection
- `take_screenshot(pageId, format="png", quality=None, fullPage=false, uid=None, filePath=None)`
  - Returns PNG/JPEG/WebP screenshot
  - `fullPage=true` — capture entire scrolled page (expensive, can be large)
  - `uid` — screenshot a single element instead of the whole page
  - `filePath` — save to disk instead of attaching to response
  - Default is viewport-only (what you see, not scrolled content)

### Console inspection
- `list_console_messages(pageId, types=[], includeStackTraces=false, includePreservedMessages=false, pageIdx=0, pageSize=None)`
  - Returns all console messages (log, error, warn, debug, info, etc.) since
    last navigation
  - `types` — filter by message type (e.g., `["error", "warn"]`)
  - `includeStackTraces=true` — include stack traces (makes response larger)
  - `includePreservedMessages=true` — include messages from the last 3
    navigations (useful if you navigated away and want to see old logs)
  - **Results are paginated** — use `pageIdx` and `pageSize` to page through
- `get_console_message(pageId, msgid)` — get full details of a specific console
  message by its msgid (from list_console_messages results)

### Network inspection
- `list_network_requests(pageId, resourceTypes=[], includePreservedRequests=false, pageIdx=0, pageSize=None)`
  - Lists all network requests (XHR, fetch, images, scripts, etc.) since last
    navigation
  - `resourceTypes` — filter by type (e.g., `["xhr", "fetch", "script"]`).
    Available types: document, stylesheet, image, media, font, script,
    texttrack, xhr, fetch, prefetch, eventsource, websocket, manifest,
    signedexchange, ping, cspviolationreport, preflight, fedcm, other
  - Paginated like console messages; use `pageIdx` and `pageSize`
- `get_network_request(pageId, reqid=None, requestFilePath=None, responseFilePath=None)`
  - Get full details of a network request (headers, response body, cookies, etc.)
  - If `reqid` is omitted, returns the currently selected request in DevTools
    Network panel
  - `requestFilePath` / `responseFilePath` — save bodies to files instead of
    returning inline

### CSS & styling inspection
- `get_css_styles(pageId, uid, pageIdx=0, pageSize=10)`
  - Get matched CSS rules, inline styles, inherited styles, and cascade info
    for an element
  - Returns paginated CSS rules (10 per page by default)
  - Useful for debugging why a style is applied/overridden
  - Requires a uid from `take_snapshot()`

### Performance & profiling
- `performance_start_trace(pageId, autoStop=true, reload=true, filePath=None)`
  - Start recording a performance trace (CPU, rendering, layout, etc.)
  - `reload=true` — automatically reload the page after starting trace
    (recommended; navigate to the URL first with `navigate_page()` if you want
    to trace a specific URL)
  - `autoStop=true` — automatically stop after page load completes
  - `filePath` — save raw trace data to a .json or .json.gz file
  - Traces capture Core Web Vitals (LCP, INP, CLS) and detailed performance info
- `performance_stop_trace(pageId, filePath=None)` — manually stop an active
  trace recording
  - Only needed if `autoStop=false`
- `performance_analyze_insight(pageId, insightSetId, insightName)`
  - Get detailed analysis of a specific performance insight from a trace
  - `insightSetId` and `insightName` come from the results of a trace

### Lighthouse audits
- `lighthouse_audit(pageId, device="desktop", mode="navigation", outputDirPath=None)`
  - Run a Lighthouse audit (accessibility, SEO, best practices, agentic browsing)
  - `device` — "desktop" or "mobile"
  - `mode` — "navigation" (reloads and audits), "snapshot" (analyzes current state)
  - `outputDirPath` — save reports to this directory (HTML, JSON); if omitted,
    uses temp files
  - **Performance is separate** — use `performance_start_trace` for Core Web
    Vitals; Lighthouse audit covers accessibility, SEO, best practices

### Emulation
- `emulate(pageId, colorScheme=None, cpuThrottlingRate=None, extraHttpHeaders=None, geolocation=None, networkConditions=None, userAgent=None, viewport=None)`
  - Emulate device features
  - `colorScheme` — "light", "dark", or "auto" (reset)
  - `cpuThrottlingRate` — slow down CPU (1=normal, 2=2x slower, etc.; max 20)
  - `networkConditions` — throttle network ("Offline", "Slow 3G", "Fast 3G",
    "Slow 4G", "Fast 4G")
  - `geolocation` — set GPS coordinates (e.g., "37.7749,-122.4194" for SF)
  - `userAgent` — spoof user agent string
  - `viewport` — emulate screen size (e.g., "375x667x2,mobile,touch,landscape")
    - Format: `<width>x<height>x<devicePixelRatio>[,mobile][,touch][,landscape]`
- `handle_dialog(pageId, action, promptText=None)` — handle alert/confirm/prompt
  dialogs
  - `action` — "accept" or "dismiss"
  - `promptText` — text to enter in a prompt() dialog

### File upload
- `upload_file(pageId, uid, filePaths[])`
  - Upload files through a file input element
  - `filePaths` — local file paths to upload
  - `uid` — the uid of the file input element (from snapshot)

### Page info
- `list_pages()` — list all open tabs, their URLs, and current selection status
- `get_console_message(pageId, msgid)` — get details of a specific console message
- `get_network_request(pageId, reqid)` — get details of a specific network request

### Debugging memory & performance
- `take_heapsnapshot(pageId, filePath)` — capture a heap snapshot (.heapsnapshot file)
  - Analyzes JavaScript object distribution and memory use
  - Useful for debugging memory leaks
  - `filePath` is required and must end in `.heapsnapshot`

## Real test results from this session (2026-09-30)

1. **Snapshot structure:** When calling `take_snapshot(pageId=2)` on example.com,
   the response is an a11y tree with each element getting a unique uid (e.g.,
   `2_0` for the root, `2_1`, `2_2`, etc. for children). Elements include type,
   text content, and attributes. Text is split character-by-character into
   StaticText nodes in the tree (not merged into single text nodes) — this is
   verbose but predictable.

2. **Navigate blocks until load:** `navigate_page()` blocks until the page
   loads; the call returns successfully only after the page is navigable.

3. **Snapshot is always needed before click/fill:** You cannot click or fill an
   element without first taking a snapshot and using its uid. No CSS selectors
   or text-based targeting.

## Known gotchas & patterns

1. **Always snapshot before clicking.** Call `take_snapshot()` first to get the
   a11y tree and element uids, then use those uids in `click()`, `fill()`,
   `hover()`, etc.

2. **Text-based waiting.** `wait_for(pageId, ["Welcome", "Error"])` waits for
   any of the listed strings to appear on the page. Useful for waiting for
   async content, alerts, or error messages without needing exact selectors.

3. **Lighthouse is not performance.** The `lighthouse_audit()` tool covers
   accessibility, SEO, best practices, and agentic browsing — NOT performance.
   Use `performance_start_trace()` for Core Web Vitals (LCP, INP, CLS).

4. **Network inspection is request-level, not application-level.** You can see
   every XHR/fetch call, but you won't see application-level events (e.g.,
   "user clicked submit") — only network boundaries.

5. **Console & network are cleared on navigation.** When a page navigates,
   console messages and network requests from the old page are discarded (unless
   you pass `includePreservedMessages=true` / `includePreservedRequests=true`,
   which keeps up to 3 previous navigations worth of data).

6. **Isolated contexts are truly isolated.** Pages in different isolated contexts
   share nothing — not cookies, localStorage, or even Service Worker registrations.
   Useful for testing clean auth flows in parallel.

## Playwright vs. chrome-devtools reference

| Task | Tool | Why |
|------|------|-----|
| Navigate to URL, wait for page | Either | Both work fine; playwright is simpler |
| Fill a form, submit | playwright | Simpler API |
| Automate a multi-step workflow | playwright | Made for this; cleaner API |
| Check for console errors | chrome-devtools | Has `list_console_messages()` |
| Inspect what XHRs a page fired | chrome-devtools | Has `list_network_requests()` |
| Debug why CSS isn't applying | chrome-devtools | Has `get_css_styles()` |
| Find accessibility issues | chrome-devtools | Has `lighthouse_audit()` and `take_snapshot()` |
| Measure Core Web Vitals (LCP, INP, CLS) | chrome-devtools | Has `performance_start_trace()` |
| Take a screenshot | Either | Both work; chrome-devtools has more options |
| Drag and drop | chrome-devtools | Has `drag()`; playwright may not have this |
| Test the page with slow network | chrome-devtools | Has `emulate(networkConditions=...)` |

## Quick self-check

```bash
# Confirm chrome-devtools is available:
# (These tools are session-based and come from a remote MCP connector;
#  if you can call mcp__chrome-devtools__new_page, you're good.)

# Example test: Open a page and take a snapshot
# 1. mcp__chrome-devtools__new_page url=https://example.com
# 2. mcp__chrome-devtools__take_snapshot pageId=<returned id>
# Should return an a11y tree with multiple uid nodes. If it does, the tool works.
```

## Environment

- **Type:** Remote MCP connector (DIRECT tool access in Claude Code sessions)
- **Tools available:** `mcp__chrome-devtools__*` (25+ tools listed above)
- **No local config needed** — the connector is already set up
- **Browser instance:** Runs inside the MCP connector (may be shared across
  sessions; multiple pages are isolated from each other)
