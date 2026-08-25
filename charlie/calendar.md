---
name: charlie-calendar
description: Complete calendar overview for Charlie (personal, work, AND family calendars)
trigger_patterns: calendar|schedule|meetings|what's on my calendar|my day|my week
contexts: calendar, charlie-only, scheduling
access: [charlie]
success_indicators: all calendars shown, events listed
---

# charlie-calendar

**Complete Calendar for Charlie**

**Access:** Charlie only  
**Data Source:** iCloud CalDAV (cseay@live.com)  
**Calendars:** Personal + Work + Family (ALL calendars)

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user != "charlie":
    print(f"ERROR: Access denied. This is Charlie's calendar.")
    print(f"User '{user}' cannot access Charlie's calendar.")
    exit(1)
```

---

## Commands

### today

Show today's events from ALL of Charlie's calendars.

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import asyncio
import sys
from datetime import datetime, timedelta
sys.path.insert(0, 'lib')
from icloud_calendar import list_calendars, get_events_range

async def main():
    try:
        cals = await list_calendars()
        
        # Get ALL calendars (personal, work, AND family)
        all_cals = [c for c in cals]
        
        if not all_cals:
            print("No calendars found.")
            sys.exit(1)
        
        today = datetime.now()
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today_start + timedelta(days=1)
        
        # Collect all events with calendar context
        all_events = []
        for cal in all_cals:
            try:
                events = await get_events_range(cal["href"], today_start, tomorrow)
                for event in events:
                    event["_calendar"] = cal["name"]
                all_events.extend(events)
            except:
                continue
        
        # Sort by start time
        all_events.sort(key=lambda e: e.get("start", ""))
        
        # Group by calendar
        by_calendar = {}
        for event in all_events:
            cal_name = event.get("_calendar", "Unknown")
            if cal_name not in by_calendar:
                by_calendar[cal_name] = []
            by_calendar[cal_name].append(event)
        
        # Display as rich HTML
        cal_colors = {
            "Work": "#667eea",
            "Personal": "#48bb78",
            "Family": "#ed8936"
        }
        
        html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px 12px 0 0; text-align: center;">
        <h2 style="margin: 0; font-size: 28px; font-weight: 600;">{today.strftime('%A')}</h2>
        <p style="margin: 8px 0 0 0; font-size: 16px; opacity: 0.9;">{today.strftime('%B %d, %Y')}</p>
    </div>
    
    <div style="background: #ffffff; padding: 32px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
"""
        
        if not all_events:
            html += """
        <div style="text-align: center; padding: 48px; color: #718096;">
            <svg style="width: 64px; height: 64px; margin-bottom: 16px; opacity: 0.3;" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
            </svg>
            <p style="font-size: 18px; margin: 0;">No events today</p>
        </div>
"""
        else:
            for cal_name, events in by_calendar.items():
                color = cal_colors.get(cal_name, "#4a5568")
                html += f"""
        <div style="margin-bottom: 24px;">
            <h3 style="font-size: 14px; font-weight: 600; color: {color}; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 12px 0;">{cal_name}</h3>
"""
                for event in events:
                    start = event.get("start", "")
                    if len(start) > 11:
                        time_str = start[11:16]  # HH:MM
                    else:
                        time_str = "All Day"
                    title = event.get("title", "Untitled")
                    
                    html += f"""
            <div style="display: flex; align-items: start; padding: 12px; background: #f7fafc; border-left: 3px solid {color}; border-radius: 4px; margin-bottom: 8px;">
                <div style="min-width: 80px; font-weight: 600; color: {color}; font-size: 14px;">{time_str}</div>
                <div style="flex: 1; color: #2d3748; font-size: 15px;">{title}</div>
            </div>
"""
                html += """
        </div>
"""
        
        html += """
    </div>
</div>
"""
        print(html)
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

asyncio.run(main())
EOF
```

### week

Show this week's events from ALL of Charlie's calendars.

```bash
cd ~/Projects/m5-agents
python3 << 'EOF'
import asyncio
import sys
from datetime import datetime, timedelta
sys.path.insert(0, 'lib')
from icloud_calendar import list_calendars, get_events_range

async def main():
    try:
        cals = await list_calendars()
        all_cals = [c for c in cals]
        
        if not all_cals:
            print("No calendars found.")
            sys.exit(1)
        
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║                      THIS WEEK                            ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print()
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = today + timedelta(days=7)
        
        # Collect all events
        all_events = []
        for cal in all_cals:
            try:
                events = await get_events_range(cal["href"], today, week_end)
                for event in events:
                    event["_calendar"] = cal["name"]
                all_events.extend(events)
            except:
                continue
        
        if not all_events:
            print("  No events this week.")
            print()
            return
        
        all_events.sort(key=lambda e: e.get("start", ""))
        
        # Group by day
        by_day = {}
        for event in all_events:
            event_date = event.get("start", "")[:10]
            if event_date not in by_day:
                by_day[event_date] = []
            by_day[event_date].append(event)
        
        # Display by day
        for date_str in sorted(by_day.keys()):
            try:
                date_obj = datetime.fromisoformat(date_str)
                day_label = date_obj.strftime("%A, %B %d")
            except:
                day_label = date_str
            
            print(f"  {day_label.upper()}")
            
            events = by_day[date_str]
            for event in events:
                start = event.get("start", "")
                time_str = start[11:16] if len(start) > 11 else "All Day"
                title = event.get("title", "Untitled")
                cal = event.get("_calendar", "")
                
                print(f"    {time_str:<8} {title} ({cal})")
            print()
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

asyncio.run(main())
EOF
```

---

## Usage Examples

```bash
# Today's complete schedule
/charlie-calendar today

# This week's complete schedule
/charlie-calendar week

# Or ask naturally:
# "What's on my calendar today?"
# "Show me my schedule this week"
```

---

## Notes

- **Comprehensive:** Shows ALL calendars (personal, work, AND family)
- **Formatted:** Clean dashboard-style display with calendar labels
- **Read-only:** Can only READ events, not create/modify/delete
- **Grouped:** Events grouped by calendar (today) or by day (week)
- **Real-time:** Pulls live data from iCloud CalDAV

---

## Error Handling

- **Access Denied:** If user is not Charlie
- **Auth Failure:** If iCloud app-specific password is invalid
- **Network Error:** If iCloud CalDAV is unreachable
- **Calendar Errors:** Gracefully skips calendars that fail to load

All errors are logged with clear messages.
