Create a lightweight Architecture Decision Record (ADR) in a `Decisions/` folder.

## Usage
- `/decision-record` — prompts for a decision title interactively
- `/decision-record My Decision Title` — uses the provided title

## Steps

### 1. Gather inputs

If a decision title was provided as an argument, use it. Otherwise, ask:
> "What decision are you recording? (short title, e.g. 'Use Postgres over SQLite')"

Then ask:
> "Brief context — what situation or problem motivates this decision?"

Then ask:
> "Which project does this relate to? (optional — press enter to skip)"

### 2. Determine the ADR number

Look in the `Decisions/` folder relative to the current working directory. If the folder doesn't exist, this will be ADR-001.

If it does exist, scan all `.md` files for `adr_number:` in their frontmatter. Find the highest number and increment by 1. Pad to three digits (e.g., ADR-001, ADR-012, ADR-103).

### 3. Create the filename

Format: `YYYY-MM-DD-slugified-title.md`

Slugify rules:
- Lowercase the title
- Replace spaces with hyphens
- Remove any characters that aren't alphanumeric or hyphens
- Collapse multiple hyphens into one
- Trim leading/trailing hyphens

Example: `2026-03-12-use-postgres-over-sqlite.md`

### 4. Create the file

Create `Decisions/<filename>` with the following content. Replace `{{placeholders}}` with actual values.

```markdown
---
tags: [decision]
created: {{YYYY-MM-DD}}
updated: {{YYYY-MM-DD}}
status: proposed
adr_number: {{ADR-NNN}}
superseded_by:
project: {{project name or empty}}
---

# {{ADR-NNN}}: {{Decision Title}}

## Status

**Proposed** — {{YYYY-MM-DD}}

## Context

{{Brief context provided by the user. Write 2-3 sentences expanding on what they said — the situation, constraints, or forces at play.}}

## Decision

*What is the change being proposed or decided?*

## Consequences

### What becomes easier
-

### What becomes harder or riskier
-

## Alternatives Considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| | | | |
| | | | |

## Review Date

*When should this decision be revisited? (e.g., "After 6 months in production", "Before v2.0", "N/A")*
```

### 5. Report the result

Output:
- The absolute file path as a clickable link
- The ADR number assigned
- Reminder: "Fill in the Decision, Consequences, and Alternatives sections — the template has placeholders ready."

## Notes
- This skill is environment-agnostic — it works in any directory, any vault, any repo
- The `Decisions/` folder is always relative to the current working directory
- Create the `Decisions/` folder if it doesn't exist (`mkdir -p`)
- Use today's date for both `created` and `updated` frontmatter fields
- The `superseded_by` field is left empty — it gets filled in later if another ADR replaces this one
- Do NOT auto-open the file — just report the path

## Lessons

- **2026-06-15** — `intent_recorded_as_outcome_is_a_recurrin`: Intent-recorded-as-outcome is a recurring failure. Sonique 2026-06-11: a prior session recorded file rewrites as done but bash heredocs never hit disk (app still ran old code). Also: new .swift file on disk != compiled (needs pbxproj registration); new code path may be shadowed by an earlier router match (screenshot intent shadowed the agentic path — debug print never fired). ALWAYS: grep the expected symbol, prove with a build, trace where the request actually routes, commit immediately. Never sed-edit pbxproj (plutil round-trip + lint). [src: task-unknown]
