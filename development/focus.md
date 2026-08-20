---
description: Set weekly focus schedule — assign projects to weekdays for better focus and ADHD management
---

# Weekly Focus Schedule

Set the weekly focus schedule to assign projects to specific weekdays. This helps manage context-switching and sets clear boundaries for daily work.

## Usage

```bash
/focus Mon=Bridge,Talos Tue=Sonique,ContentStudio Wed=Hone,Enchapter Thu=JobScout,Periscope Fri=IDEA
```

Or provide the schedule in natural language:
```
/focus Monday: Bridge and Talos, Tuesday: Sonique and Content Studio, ...
```

## Rules

- **ACTIVE projects** get Mon–Thu assignments (2hr target blocks)
- **IDEA/PLANNED projects** fill gaps and get Friday
- **Ops/finances/deadlines** auto-inject regardless of schedule
- **2-hour blocks are targets**, not caps — work can run over
- Schedule persists for the full week, overrides tracked automatically

## What Happens

1. Creates/updates the active weekly schedule in helmsman.db
2. Bridge Portfolio displays "This Week's Focus" with your schedule
3. Actual work time is tracked against the schedule
4. Off-schedule work is flagged as "override" but not blocked
5. End-of-day adherence summary shows on-schedule % and overrides

## Schedule Format

The skill accepts flexible input:
- `Day=Project1,Project2` (comma-separated, no spaces in project names)
- Full weekday names or 3-letter abbreviations (Mon/Monday both work)
- Multiple formats: `Mon=X,Y` or `Monday: X and Y` or `mon X Y`

Project names are matched against your Portfolio projects (case-insensitive).

## Week Boundaries

Schedule runs Monday–Sunday by default. The skill auto-calculates the Monday of the current week as `week_start`.

If you need to set a future week's schedule:
```
/focus --week 2026-06-08 Mon=Bridge Tue=Sonique ...
```

## Examples

```bash
# Typical week
/focus Mon=Bridge,Talos Tue=Sonique,ContentStudio Wed=Hone,Enchapter Thu=JobScout,Periscope Fri=IDEA

# Crunch week (focus on one project)
/focus Mon=Bridge Tue=Bridge Wed=Bridge Thu=Bridge Fri=IDEA

# Natural language
/focus Monday and Tuesday: Bridge. Wednesday: Hone and Enchapter. Thursday: Periscope. Friday: backlog.
```

## Notes

- **You set the schedule** — the system doesn't auto-propose yet
- **Live tracking** — tracer_spans + task_queue data feed actual work hours
- **Overrides are logged**, not blocked — you retain full autonomy
- **One active schedule** — setting a new schedule deactivates the previous one

---

**Implementation:** POST to `http://localhost:5682/schedules` with parsed week_start + schedule JSON.
