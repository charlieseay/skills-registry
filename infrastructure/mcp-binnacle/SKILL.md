---
name: mcp-binnacle
description: Navigation and status surface for the Seaynic fleet — read-only access to Mac system state, calendar, reminders, Shortcuts, clipboard, Spotlight search, files, network, display settings, and Finder metadata. 31 tools spanning system info, macOS integrations, and file/desktop operations.
---

# Binnacle MCP — macOS System & Desktop Surface

Binnacle is a **compiled, read-only MCP server** (Mach-O binary at `/usr/local/bin/binnacle`,
version 0.3.1) that exposes **31 tools** for querying and controlling macOS system state,
calendar, reminders, Shortcuts, notifications, clipboard, file system, network, display,
and battery. It's designed as a "navigation cockpit" for understanding what's happening on
the Mac in real time and performing routine desktop operations.

**Nature of the tool:** Mostly read-only queries (20 tools), with selective write capabilities
(11 tools: calendar create/update/delete, reminders create/complete, clipboard write, app launch,
shortcuts run, notifications, system toggles).

## Tool catalog (31 tools verified via MCP protocol 2026-09-30)

Grouped by domain for easy scanning.

### Health & Status (read-only)

**`ping() -> dict`**
- Health check — returns server version and status.
- Always succeeds if the server is running.
- Response: `{"server": "binnacle", "version": "0.3.1", "status": "ok"}`
- Use this to confirm Binnacle is alive before calling other tools.

### System Information (read-only)

**`system_get_info() -> dict`**
- CPU usage (%), memory usage (%), disk space (%), battery level (%), charging status, uptime.
- Example response:
  ```json
  {
    "cpu_percent": 8.2,
    "memory_percent": 42.1,
    "disk_percent": 61.3,
    "battery_level": 87,
    "is_charging": false,
    "uptime_seconds": 1234567
  }
  ```
- Use this for quick health snapshots of the Mac.

**`system_get_display_info() -> dict`**
- Display resolution, connected displays (count/details).
- Example: `{"displays": [{"resolution": "3456x2304", "is_external": false}]}`

**`get_display_settings() -> dict`**
- Current display configuration: resolution, scaling factor, color profile, arrangement for
  all connected displays.
- Richer than `system_get_display_info`; includes scaling and color profile details.

**`get_wifi_info() -> dict`**
- Current WiFi network name, signal strength (RSSI in dBm), IP address, interface details.
- Example: `{"ssid": "HomeLab", "rssi": -45, "ip_address": "192.168.68.78", "interface": "en0"}`

**`get_battery_status() -> dict`**
- Battery level (%), charging state, power source, cycle count, health estimate.
- Example: `{"percent": 87, "is_charging": false, "power_source": "battery", "cycles": 234, "health": "normal"}`

**`get_storage_summary() -> dict`**
- Disk usage breakdown: total, used, free space, and per-volume details.
- Useful for checking if the Mac is running low on disk before a big operation.

**`system_get_volume() -> dict`**
- Current audio output volume level (0–100) and mute state (true/false).

### Calendar (read-only + write)

**`calendar_list() -> list`** (read-only)
- List all calendars available on this Mac.
- Returns: `[{"calendar_id": "...", "name": "Work"}, {"calendar_id": "...", "name": "Personal"}]`

**`calendar_today() -> list`** (read-only)
- List today's calendar events (date range is implicit: 00:00–23:59 today).
- Returns: `[{"title": "...", "start": "2026-09-30T09:00:00", "end": "2026-09-30T10:00:00", ...}]`

**`calendar_range(start: str, end: str) -> list`** (read-only)
- List calendar events in a date range (ISO8601 format, e.g., "2026-09-30").
- Returns: list of event dicts.

**`calendar_create(title: str, start: str, end: str, calendar_id: str = "", location: str = "", notes: str = "") -> dict`** (write)
- Create a calendar event.
- `start` and `end` must be ISO8601 datetime strings (e.g., "2026-10-01T14:00:00").
- `calendar_id` (optional): specific calendar to add to (defaults to primary calendar).
- `location` and `notes` (optional): additional event metadata.
- Returns: `{"success": true, "event_id": "...", ...}` or error.

**`calendar_update(event_id: str, title: str = "", start: str = "", end: str = "", location: str = "", notes: str = "") -> dict`** (write)
- Update an existing calendar event.
- Pass only the fields you want to change (all parameters except `event_id` are optional).
- Returns: `{"success": true, ...}` or error.

**`calendar_delete(event_id: str) -> dict`** (write)
- Delete a calendar event.
- Returns: `{"success": true, ...}` or error.

### Reminders (read-only + write)

**`reminders_list(list_name: str = "") -> list`** (read-only)
- List reminders, optionally filtered by list name.
- Returns: `[{"reminder_id": "...", "title": "Buy milk", "due_date": "2026-10-01", "is_completed": false}]`
- If `list_name` is empty, returns all reminders from all lists.

**`reminders_create(title: str, list_name: str = "", due_date: str = "") -> dict`** (write)
- Create a new reminder.
- `title` (required): reminder text.
- `list_name` (optional): which list to add to (defaults to "Reminders").
- `due_date` (optional): ISO8601 date (e.g., "2026-10-05").
- Returns: `{"success": true, "reminder_id": "...", ...}` or error.

**`reminders_complete(reminder_id: str) -> dict`** (write)
- Mark a reminder as complete.
- Returns: `{"success": true, ...}` or error.

### Shortcuts (read-only + execute)

**`shortcuts_list() -> list`** (read-only)
- List all Shortcuts available on this Mac.
- Returns: `[{"name": "Send Email", "id": "..."}, ...]`

**`shortcuts_folders() -> list`** (read-only)
- List Shortcut folders/categories.
- Returns: `[{"name": "Productivity", "id": "..."}, ...]`

**`shortcuts_run(name: str, input_text: str = "") -> dict`** (execute)
- Run a Shortcut by name with optional text input.
- `name`: exact name of the Shortcut (case-sensitive).
- `input_text` (optional): text to pass as input to the Shortcut.
- Returns: `{"success": true, "output": "...", ...}` or error with reason.

### Notifications & Alerts (read-only + write)

**`notification_send(title: str, body: str, subtitle: str = "") -> dict`** (write)
- Send a macOS notification (appears in Notification Center).
- `title`: main notification text.
- `body`: longer message body.
- `subtitle` (optional): secondary heading.
- Returns: `{"success": true, ...}` or error.

### Clipboard (read-only + write)

**`clipboard_read() -> str`** (read-only)
- Read the current text content from the macOS clipboard.
- Returns: plain text string (e.g., "hello world").
- Fails if clipboard is empty or contains non-text data (images, files).

**`clipboard_write(text: str) -> dict`** (write)
- Write text to the macOS clipboard.
- Returns: `{"success": true, ...}` or error.

### File System & Finder (read-only + metadata)

**`spotlight_search(name: str = "", content: str = "", kind: str = "", date_modified: str = "") -> list`** (read-only)
- Search files using Spotlight by name, content, kind (file type), or modification date.
- All parameters are optional and combined with AND logic.
- Example: `spotlight_search(name="invoice", kind="pdf")` finds PDFs with "invoice" in the name.
- Returns: `[{"path": "/Users/charlie/...", "modified": "2026-09-30", ...}]`

**`finder_info(path: str) -> dict`** (read-only)
- Get extended file info for a file: size, creation/modification dates, file type, Finder comments, Spotlight metadata.
- Returns: `{"size": 12345, "created": "2026-01-01", "modified": "2026-09-30", "kind": "PDF", "comments": "...", ...}`

**`finder_tags(path: str, action: str, tags: list[str] = []) -> dict`** (read-only + write)
- List, get, or set Finder tags on files.
- `action`: "list" (all tags on a file), "set" (replace tags), or "add" (append tag).
- `tags`: list of tag strings (e.g., ["Project", "Important"]).
- Examples:
  - `finder_tags("/path/to/file", "list")` → returns all tags on the file.
  - `finder_tags("/path/to/file", "set", tags=["Done", "Archive"])` → replaces all tags.
  - `finder_tags("/path/to/file", "add", tags=["Review"])` → adds a tag.
- Returns: `{"success": true, "tags": [...]}` or error.

**`get_downloads() -> list`** (read-only)
- List recent files in ~/Downloads with name, size, and modification date.
- Returns: `[{"name": "invoice-2026-09.pdf", "size": 1234567, "modified": "2026-09-30"}, ...]`

### Applications (read-only + execute)

**`open_app(name: str) -> dict`** (execute)
- Launch or activate a macOS application by name.
- `name`: app name as it appears in Applications folder (e.g., "Safari", "Slack", "Xcode").
- Returns: `{"success": true, ...}` or error (app not found, permission denied).

**`get_running_apps() -> list`** (read-only)
- List currently running applications with process IDs.
- Returns: `[{"name": "Finder", "pid": 123}, {"name": "Slack", "pid": 456}, ...]`

### System Toggles (read-only + write)

**`toggle_dark_mode(mode: str = "") -> dict`** (write)
- Toggle between light and dark appearance, or set a specific mode.
- `mode`: "" (toggle), "light", or "dark".
- Returns: `{"success": true, "new_mode": "dark", ...}` or error.

**`toggle_dnd(state: str = "") -> dict`** (write)
- Toggle Do Not Disturb (Focus) mode on or off.
- `state`: "" (toggle), "on", or "off".
- Returns: `{"success": true, "new_state": "on", ...}` or error.

## Known gotchas (observed from MCP handshake + tool definitions, 2026-09-30)

1. **Spotlight search doesn't support regex.** All search parameters are literal substring/keyword
   matching, not regex. If you need to find "invoice*.pdf", search by name="invoice" and kind="pdf"
   separately; you can't use wildcards.

2. **Finder tags action parameter is critical.** Passing the wrong action string results in an error.
   Valid values are exactly: "list", "get", "set", "add". Anything else will fail.

3. **Shortcuts names are case-sensitive.** `shortcuts_run("Send Email")` will fail if the Shortcut is
   named "send email" or "SEND EMAIL". Use `shortcuts_list()` first to get the exact name.

4. **Calendar event times must be ISO8601 datetime, not just date.** `calendar_create(..., start="2026-10-01")`
   will fail; you must pass `start="2026-10-01T14:00:00"` (or include timezone if needed).

5. **Clipboard reads fail silently on non-text data.** If the clipboard contains an image or file
   reference, `clipboard_read()` returns an empty string or error rather than attempting to serialize
   the data. Always check the return value.

6. **get_downloads returns only recent files.** It doesn't list ALL files in ~/Downloads; it's a
   "recent items" snapshot. If you need to find an older download, use `spotlight_search()` with
   date_modified filters instead.

7. **Reminders list filtering is by exact list name.** `reminders_list("Work")` returns reminders
   only from a list named "Work" (case-sensitive). If the list is named "work" or "Work Items",
   the query fails silently and returns nothing.

8. **open_app requires the app to be installed.** Passing a name that doesn't exist or is misspelled
   returns an error like "App not found: XyzApp". Check app availability (via Spotlight or just
   common sense) before trying to launch it.

9. **System toggles (dark mode, DND) may be overridden by system settings.** If dark mode is scheduled
   (e.g., "automatic: light at 8am, dark at 8pm"), calling `toggle_dark_mode("light")` will work, but
   the system may flip it back at the scheduled time. This is expected macOS behavior, not a tool bug.

10. **Binnacle is read-only from a security perspective.** While tools like `calendar_create` and
    `notification_send` are writes, they don't expose system secrets or authentication. If you need
    to access sensitive system settings (SSH keys, keychain entries, credentials), Binnacle doesn't
    expose them (and shouldn't).

## Environment facts

- Binnacle binary: `/usr/local/bin/binnacle` (compiled Mach-O, not a Python script).
- Version: 0.3.1 (confirmed via MCP handshake).
- Configuration: Binnacle has no config file; behavior is hard-coded in the binary.
- Access: Available via mcp-proxy at the configured Binnacle endpoint, or standalone via stdio.

## Quick self-check: Is this skill stale?

```bash
# 1. Confirm Binnacle is installed
which binnacle
file /usr/local/bin/binnacle  # should be Mach-O 64-bit arm64

# 2. Query the live tool list via MCP (requires MCP handshake)
# This is not a one-liner since binnacle requires MCP protocol negotiation.
# Easier approach: run the tool list query in the Claude Code session with the MCP tool
# and compare against the 31 tools listed above.

# 3. Check version
binnacle --version 2>&1 | head -5
# Note: binnacle doesn't have a --version flag; it starts the server immediately.
# Version is reported only during MCP initialization.
```

If the tool count has changed from 31, this skill is missing or has stale tool definitions — update it.

## When to use Binnacle

- **Real-time system monitoring:** Quick check on CPU/memory/battery without opening System Preferences.
- **Calendar/reminder operations:** Add an event or reminder programmatically without UI automation.
- **Shortcut execution:** Run a Shortcut as part of a larger workflow (e.g., "run my email sender Shortcut").
- **File system operations:** Search Spotlight, read file metadata, add Finder tags, without opening Finder.
- **Desktop automation:** Toggling dark mode, DND, launching apps as side effects of a task.
- **Clipboard manipulation:** Copy/paste data in a workflow.

## When NOT to use Binnacle

- **Tasks that need write access to keychain/credentials.** Binnacle doesn't expose sensitive system APIs.
- **Real-time monitoring loops.** Binnacle is a client tool for individual queries, not a daemon; repeated
  calls in a loop will be slower than using native system monitoring tools.
- **Tasks requiring advanced Finder operations.** Move/copy/delete files via Binnacle works, but if you need
  complex Finder interactions, AppleScript or direct file system APIs may be more efficient.
- **Calendar/reminder sync with external services.** Binnacle only touches local calendars/reminders on this Mac.

## Architecture note

Binnacle is a **compiled binary**, not a Python/Node script. This means:
- Fast startup and execution (no interpreter overhead).
- No source code to inspect directly; the skill documentation is the contract.
- Updates to Binnacle require replacing the binary at `/usr/local/bin/binnacle`.
- If Binnacle crashes, the binary is the failure point (not configuration or Python runtime issues).
