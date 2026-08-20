---
name: meeting-notes
category: operations
description: Structured meeting notes with decisions and action items
triggers:
  patterns:
  - meeting notes
  - notes
  - meeting minutes
  - capture meeting
  contexts:
  - meetings
  - documentation
  - collaboration
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when structured meeting notes with decisions and action items
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 10
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Create structured meeting notes in the current vault or working directory.

## Usage
- `/meeting-notes` — prompts for a meeting title
- `/meeting-notes Weekly Sync` — creates notes with the given title

## Steps

1. **Get the meeting title.** If a title was passed as an argument, use it. If not, ask the user for one before proceeding.

2. **Ask for attendees.** Prompt: "Who attended? (comma-separated names)" — collect the response as a list.

3. **Ask for project (optional).** Prompt: "Which project does this relate to? (press Enter to skip)" — if the user provides one, include it in frontmatter. If skipped, omit the `project:` field.

4. **Create the `Meeting Notes/` directory** in the current working directory if it doesn't already exist:
   ```bash
   mkdir -p "Meeting Notes"
   ```

5. **Generate the filename.** Format: `YYYY-MM-DD-slugified-title.md`
   - Use today's date
   - Slugify the title: lowercase, replace spaces with hyphens, strip non-alphanumeric characters (keep hyphens), collapse multiple hyphens
   - Example: "Weekly Sync" on 2026-03-12 → `2026-03-12-weekly-sync.md`

6. **Write the note** to `Meeting Notes/<filename>` with the template below, filling in:
   - Today's date for `created` and `updated`
   - The attendees list from step 2 (as a YAML array)
   - The project name from step 3 (if provided)
   - The meeting title as the H1 heading

7. **Report the result.** Output the absolute file path so the user can open it.

## Note Template

```markdown
---
tags: [meeting]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
attendees: [Name One, Name Two]
project: Project Name
---

# Meeting Title

## Context

<!-- 1-2 sentences: what is this meeting about and why is it happening now? -->

## Decisions

<!-- Each decision gets a bullet with a rationale line -->
- **Decision:** [what was decided]
  - *Rationale:* [why this was chosen]

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| | | | Open |

## Discussion Notes

<!-- Freeform notes from the meeting -->

## Follow-up

<!-- What needs to happen before or at the next meeting? -->
```

## Rules
- If no project was given, omit the `project:` line from frontmatter entirely — do not leave it blank
- Attendees should be formatted as a YAML flow sequence: `[Alice, Bob, Charlie]`
- Do not auto-open the file — just report the path
- This skill is environment-agnostic: it uses the current working directory, not a hardcoded vault path
- If a file with the same name already exists, warn the user and ask before overwriting

## Lessons

- **2026-06-16** — `notes-scattered-need-canonical`: Each project needs ONE canonical note; others link to it, never duplicate. Scattered notes cause stale/wrong info + slow lookups. The housekeeper must enforce this. _(context: Bridge notes split across 5+ locations this session caused exactly the stale-info problem Charlie flagged. Housekeeper isn't keeping notes organized.)_ [src: session/2026-06-16-housekeeper]
