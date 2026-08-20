---
skill: coach-loop
description: Active coaching loop - monitors team tasks, detects stalls, provides guidance
---

# Team Coaching Loop

Monitor active autonomous agent tasks, detect when they're stuck, and provide real-time coaching guidance.

## Loop Behavior

1. Check for active tasks (assigned but not shipped)
2. Detect stalled tasks (running > 10 min with no progress)
3. Provide pattern-based coaching:
   - Installation tasks: verify download URL first
   - SSH tasks: check network → keys → firewall
   - Hermes Desktop: likely needs manual download from releases
   - Research tasks: focus on finding ONE good source, not exhaustive research
4. Log guidance to /tmp/team-coach.log
5. Repeat every 5 minutes

## When to Use

- After dispatching complex L or XL tasks
- When agents are working on unfamiliar tools
- During autonomous overnight sessions
- When you want active supervision without micromanaging

## How It Works

The loop runs `/Users/charlieseay/.local/bin/team-coach` every 5 minutes via ScheduleWakeup. The script:
- Queries helmsman.db for active tasks
- Checks elapsed time since assignment
- Pattern-matches task titles to known failure modes
- Logs coaching guidance (agents don't read this yet - future: post to their context)

## Future Enhancement

When agents have a way to receive mid-task guidance (Slack channel? context injection?), the coach will post hints directly to them instead of just logging.

## Usage

```
/coach-loop
```

Starts the coaching loop. Run `/stop` to end it.
