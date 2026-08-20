---
description: Morning standup — vault scan, health check, executive summary
---

Run the morning standup routine:

1. Read the vault session-state memory file for handoff context
2. Run a service health check (mcp__claude_ai_claudecp__service_health_check)
3. Check n8n for failed executions in the last 24 hours
4. Scan all project notes for open bugs, features, and recent changes
5. Scan Ideas/ and Ideas/Opportunities/ for any new entries
6. Check git status across all tracked repos for uncommitted changes
7. Read `Projects/Master Task List.md` for all open items

## Output 1: Executive Summary HTML

Generate `project-status.html` and save to `/Volumes/data/containers/filebrowser/data/reports/project-status.html`.

This is the project executive summary. It covers:
- Infrastructure health (services up/down, any incidents)
- n8n status (failed workflows, error patterns)
- Open work by project (bugs, features, next steps)
- New ideas/opportunities since last session
- Recommended priorities for today

**Note:** The n8n "Project Status → Digest" workflow (`ivngL0ZO6pyFWOdk`) also generates this file at 6 AM CT. If the n8n version is fresh (updated today), skip regenerating and just verify it's current. If it's stale or missing data, regenerate.

## Output 2: Task List HTML

Generate `task-list.html` and save to `/Volumes/data/containers/filebrowser/data/reports/task-list.html`.

This is Charlie's personal action checklist. It must include:

1. **All open YOU tasks** from the Master Task List (items only Charlie can do)
2. **All open CHARLIE + CLAUDE split tasks** where Charlie's part is not done
3. **Pending approvals/reviews** — anything Claude built that's waiting for Charlie to test, approve, or deploy
4. **Content Factory items** where Charlie needs to act (test, approve, post manually)

### For each task, include:
- **Checkbox** (HTML `<input type="checkbox">`) — interactive, not just visual
- **Task title** with project label
- **Effort badge** (S/M/L/XL)
- **Why it matters** — one sentence on what it unblocks or why it's urgent
- **Step-by-step instructions** — exact commands, URLs to visit, files to edit, what to look for. Written so Charlie can complete the task without asking Claude for help.
- **Verification** — how to confirm it's done
- **Links** — to relevant vault notes, dashboards, or external URLs

### Styling

Match the existing report theme:
- Dark background: `#0A0B10`
- Card backgrounds: `#12141C` with `#1E2130` borders
- Font: Inter (body), JetBrains Mono (code/badges)
- Text: `#E2E4EA` primary, `#8B8FA3` secondary
- Accent colors: `#34D399` (green/done), `#FBBF24` (yellow/warning), `#F87171` (red/urgent), `#818CF8` (purple/info)
- Responsive, single-file (all CSS inline), no external dependencies
- Title includes the date and "Last updated" timestamp

### Ordering

1. Urgent / blocking items first
2. Then by effort (S first — quick wins before deep work)
3. Group by project when 2+ tasks share the same project

## Delivery

After generating both files, present Charlie with:
- Links to both reports at `https://reports.seaynicroute.com/`
- A 3-5 bullet summary of what's urgent today
- Flag anything that changed since yesterday
