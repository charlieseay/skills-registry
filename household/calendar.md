---
name: household-calendar
description: Shared family calendar for Charlie and Becki's household
trigger_patterns: family calendar|household calendar|family schedule|our calendar
contexts: calendar, household, shared
access: [charlie, becki]
success_indicators: family events listed, household schedule shown
---

# household-calendar

**Shared Family Calendar**

**Access:** Both Charlie and Becki  
**Data Source:** iCloud CalDAV "Family" calendar  
**Purpose:** Shared household events, kids' activities, family appointments

---

## Access Control

Before running ANY command, verify the user:

```python
import os
user = os.getenv("SKILL_INVOKING_USER", "unknown")
if user not in ["charlie", "becki"]:
    print(f"ERROR: Access denied. Household calendar is only accessible to Charlie and Becki.")
    print(f"User '{user}' does not have access to family calendar data.")
    exit(1)
```

---

## Commands

### today

Show today's family events.

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
        
        # Filter to Family calendar only
        family_cal = next((c for c in cals if c["name"].lower() == "family"), None)
        
        if not family_cal:
            print("Family calendar not found.")
            sys.exit(1)
        
        today = datetime.now()
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today_start + timedelta(days=1)
        
        try:
            all_events = await get_events_range(family_cal["href"], today_start, tomorrow)
        except:
            all_events = []
        
        all_events.sort(key=lambda e: e.get("start", ""))
        
        html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%); color: white; padding: 24px; border-radius: 12px 12px 0 0; text-align: center;">
        <h2 style="margin: 0; font-size: 28px; font-weight: 600;">Family Calendar</h2>
        <p style="margin: 8px 0 0 0; font-size: 16px; opacity: 0.9;">{today.strftime('%A, %B %d, %Y')}</p>
    </div>
    
    <div style="background: #ffffff; padding: 32px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
"""
        
        if not all_events:
            html += """
        <div style="text-align: center; padding: 48px; color: #718096;">
            <svg style="width: 64px; height: 64px; margin-bottom: 16px; opacity: 0.3;" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
            </svg>
            <p style="font-size: 18px; margin: 0;">No family events today</p>
        </div>
"""
        else:
            for event in all_events:
                start = event.get("start", "")
                if len(start) > 11:
                    time_str = start[11:16]  # HH:MM
                else:
                    time_str = "All Day"
                title = event.get("title", "Untitled")
                
                html += f"""
        <div style="display: flex; align-items: start; padding: 12px; background: #fff5f0; border-left: 3px solid #ed8936; border-radius: 4px; margin-bottom: 8px;">
            <div style="min-width: 80px; font-weight: 600; color: #ed8936; font-size: 14px;">{time_str}</div>
            <div style="flex: 1; color: #2d3748; font-size: 15px;">{title}</div>
        </div>
"""
        
        html += """
    </div>
</div>
"""
        print(html)
            
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

asyncio.run(main())
EOF
```

### week

Show this week's family events.

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
        family_cal = next((c for c in cals if c["name"].lower() == "family"), None)
        
        if not family_cal:
            print("Family calendar not found.")
            sys.exit(1)
        
        print("Family Calendar - This Week")
        print()
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = today + timedelta(days=7)
        
        try:
            all_events = await get_events_range(family_cal["href"], today, week_end)
        except:
            print("No family events this week.")
            return
        
        if not all_events:
            print("No family events this week.")
            return
        
        all_events.sort(key=lambda e: e.get("start", ""))
        
        current_day = None
        for event in all_events:
            event_date = event.get("start", "")[:10]
            event_time = event.get("start", "")[11:16] if len(event.get("start", "")) > 11 else "All Day"
            title = event.get("title", "Untitled")
            
            if event_date != current_day:
                if current_day is not None:
                    print()
                try:
                    date_obj = datetime.fromisoformat(event_date)
                    print(f"{date_obj.strftime('%A, %B %d')}:")
                except:
                    print(f"{event_date}:")
                current_day = event_date
            
            print(f"  {event_time} - {title}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

asyncio.run(main())
EOF
```

---

## Usage Examples

```bash
# Today's family schedule
/household-calendar today

# This week's family schedule
/household-calendar week
```

---

## Notes

- **Shared Access:** Both Charlie and Becki can view household calendar
- **Read-only:** Can only READ events, not create/modify/delete
- **Calendar Name:** Uses iCloud "Family" calendar specifically
- **Privacy:** Does NOT show Charlie's work calendar or Becki's work calendar
- **Credentials:** Uses shared iCloud access (cseay@live.com)

---

## Error Handling

- **Access Denied:** If user is not Charlie or Becki
- **No Calendar Found:** If "Family" calendar doesn't exist
- **Auth Failure:** If iCloud credentials are invalid
- **Network Error:** If iCloud CalDAV is unreachable

All errors are logged with clear messages.
