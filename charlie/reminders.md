---
name: charlie-reminders
description: Query Charlie's iCloud Reminders via CalDAV
trigger_patterns: reminder|reminders|to-do|todo|task list
contexts: reminders, tasks, icloud
access: [charlie]
success_indicators: reminders retrieved from iCloud
---

# charlie-reminders

**iCloud Reminders Access for Charlie**

**Access:** Charlie only  
**Data Sources:** iCloud CalDAV (app-specific password, read-only)

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user != "charlie":
    print(f"ERROR: Access denied. iCloud Reminders access is limited to Charlie.")
    print(f"User '{user}' does not have reminders access.")
    exit(1)
```

---

## Commands

### list

List all reminder lists (equivalent to iCloud Reminders categories).

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import sys
import asyncio
sys.path.insert(0, 'lib')
from icloud_calendar import list_calendars

async def main():
    lists = await list_calendars()

    # Filter to just reminder lists (iCloud stores calendars and reminders together)
    reminder_lists = [l for l in lists if 'reminder' in l['name'].lower() or 'tasks' in l['name'].lower()]

    if not reminder_lists:
        print("No reminder lists found. Showing all available lists:")
        for lst in lists:
            print(f"- {lst['name']} ({lst['href']})")
    else:
        print("**iCloud Reminder Lists:**\n")
        for lst in reminder_lists:
            print(f"- **{lst['name']}**")
            print(f"  href: {lst['href']}")

asyncio.run(main())
EOF
```

### show

Show reminders from a specific list.

**Arguments:** `<list_name>` (name of reminder list), `[include_completed=false]`

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import sys
import asyncio
sys.path.insert(0, 'lib')
from icloud_calendar import list_calendars, get_reminders

list_name = """<LIST_NAME>"""
include_completed = <INCLUDE_COMPLETED:false>

async def main():
    # Find the list href
    lists = await list_calendars()
    target_list = None

    for lst in lists:
        if list_name.lower() in lst['name'].lower():
            target_list = lst
            break

    if not target_list:
        print(f"List '{list_name}' not found. Available lists:")
        for lst in lists:
            print(f"- {lst['name']}")
        return

    # Get reminders
    reminders = await get_reminders(target_list['href'], include_completed=include_completed)

    if not reminders:
        status = "all tasks" if include_completed else "incomplete tasks"
        print(f"No {status} found in '{target_list['name']}'")
        return

    print(f"**Reminders in '{target_list['name']}':**\n")

    # Group by status
    incomplete = [r for r in reminders if r.get('status') != 'COMPLETED']
    completed = [r for r in reminders if r.get('status') == 'COMPLETED']

    if incomplete:
        print("**Incomplete:**")
        for reminder in incomplete:
            title = reminder.get('title', 'Untitled')
            due = reminder.get('due_date', '')
            priority = reminder.get('priority', 0)
            notes = reminder.get('notes', '')

            print(f"- [ ] {title}")
            if due:
                print(f"      Due: {due}")
            if priority and priority < 5:
                print(f"      Priority: {priority} (high)")
            if notes:
                print(f"      Notes: {notes[:100]}")
        print()

    if completed and include_completed:
        print(f"**Completed ({len(completed)}):**")
        for reminder in completed[:5]:  # Show first 5 completed
            print(f"- [x] {reminder.get('title', 'Untitled')}")
        print()

    print(f"**Total:** {len(incomplete)} incomplete, {len(completed)} completed")

asyncio.run(main())
EOF
```

### all

Show all reminders across all lists.

**Arguments:** `[include_completed=false]`

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import sys
import asyncio
sys.path.insert(0, 'lib')
from icloud_calendar import list_calendars, get_reminders

include_completed = <INCLUDE_COMPLETED:false>

async def main():
    lists = await list_calendars()

    all_reminders = []
    for lst in lists:
        try:
            reminders = await get_reminders(lst['href'], include_completed=include_completed)
            for reminder in reminders:
                reminder['list'] = lst['name']
            all_reminders.extend(reminders)
        except Exception as e:
            # Skip lists that aren't reminder lists (calendars)
            continue

    if not all_reminders:
        print("No reminders found across all lists")
        return

    # Group by list
    by_list = {}
    for reminder in all_reminders:
        list_name = reminder.get('list', 'Unknown')
        if list_name not in by_list:
            by_list[list_name] = []
        by_list[list_name].append(reminder)

    print("**All iCloud Reminders:**\n")

    for list_name, reminders in by_list.items():
        incomplete = [r for r in reminders if r.get('status') != 'COMPLETED']
        if not incomplete and not include_completed:
            continue

        print(f"**{list_name}** ({len(incomplete)} incomplete)")
        for reminder in incomplete[:5]:  # Show first 5 per list
            title = reminder.get('title', 'Untitled')
            due = reminder.get('due_date', '')
            print(f"- [ ] {title}")
            if due:
                print(f"      Due: {due}")
        if len(incomplete) > 5:
            print(f"      ... and {len(incomplete) - 5} more")
        print()

    total_incomplete = sum(1 for r in all_reminders if r.get('status') != 'COMPLETED')
    total_completed = sum(1 for r in all_reminders if r.get('status') == 'COMPLETED')
    print(f"**Grand Total:** {total_incomplete} incomplete, {total_completed} completed")

asyncio.run(main())
EOF
```

---

## Setup

**One-time credential setup:**

1. Generate Apple app-specific password at appleid.apple.com
2. Save credentials to M5:
   ```bash
   echo "cseay@live.com" > /Volumes/data/secrets/icloud_caldav_username
   echo "<app-specific-password>" > /Volumes/data/secrets/icloud_caldav_password
   chmod 600 /Volumes/data/secrets/icloud_caldav_*
   ```

**Subsequent uses:** Automatic (credentials read from secrets)

---

## Usage Examples

```bash
# List all reminder lists
/charlie-reminders list

# Show reminders from "Work" list
/charlie-reminders show "Work"

# Show ALL reminders including completed
/charlie-reminders all true

# Show specific list with completed tasks
/charlie-reminders show "Personal" true
```

---

## Notes

- **Read-only:** Can read reminders, cannot create/modify/delete
- **App-specific password:** Scoped, revocable from appleid.apple.com
- **CalDAV:** Uses Apple's CalDAV API (standard protocol)
- **Lists vs Calendars:** iCloud stores both in same namespace, skill filters automatically

---

## Error Handling

- **Missing credentials:** Check `/Volumes/data/secrets/icloud_caldav_*`
- **401 Unauthorized:** App-specific password revoked (regenerate at appleid.apple.com)
- **Network error:** iCloud CalDAV API unavailable (retry later)

All errors logged with clear messages.
