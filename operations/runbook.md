---
name: runbook
category: operations
description: Create operational runbook with procedures and rollback
triggers:
  patterns:
  - runbook
  - SOP
  - procedure
  - operational guide
  contexts:
  - operations
  - documentation
  - procedures
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when create operational runbook with procedures and rollback
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 30
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Generate an operational runbook note in the current working directory.

## Usage
- `/runbook service-name` — creates a runbook for the named service or process
- `/runbook` — prompts for the service/process name

## Steps

1. **Gather inputs.** If the service/process name was not passed as an argument, ask:
   > "What service or process is this runbook for?"

2. **Ask for a one-line description:**
   > "One-line summary of what this runbook covers?"

3. **Ask for the owner (optional):**
   > "Who owns this process? (name or team — press Enter to skip)"

   If skipped, use `TBD` as the owner value.

4. **Create the Runbooks folder** if it doesn't exist:
   ```bash
   mkdir -p "$(pwd)/Runbooks"
   ```

5. **Slugify the service name** for the filename: lowercase, replace spaces and special characters with hyphens, strip leading/trailing hyphens. Example: "Nginx Proxy Manager" → `runbook-nginx-proxy-manager.md`

6. **Write the file** at `Runbooks/runbook-<slug>.md` using the template below, filling in:
   - `service`: the original service/process name (not slugified)
   - `owner`: from step 3
   - `created` / `updated` / `last_verified`: today's date (YYYY-MM-DD)
   - The one-line description in the Overview section

7. **Report the file path** as a clickable markdown link. Do NOT auto-open the file.

## Template

```markdown
---
tags: [runbook]
created: <today>
updated: <today>
status: draft
service: <service name>
owner: <owner>
last_verified: <today>
review_cadence: quarterly
---

# Runbook: <Service Name>

## Overview

<one-line description from step 2>

**When to use this runbook:**
- <!-- List the situations that trigger this procedure -->

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Access | <!-- What accounts, roles, or permissions are needed --> |
| Tools | <!-- CLI tools, dashboards, or software required --> |
| Credentials | <!-- Where to find secrets — never the secrets themselves --> |

---

## Standard Operating Procedure

### Step 1: <!-- Step title -->

**Action:**
```bash
# command here
```

**Expected output:**
```
# what success looks like
```

**Verification:**
- <!-- How to confirm this step succeeded -->

---

### Step 2: <!-- Step title -->

**Action:**
```bash
# command here
```

**Expected output:**
```
# what success looks like
```

**Verification:**
- <!-- How to confirm this step succeeded -->

---

## Rollback

If the procedure needs to be undone, follow these steps in reverse order:

### Undo Step 2
```bash
# rollback command
```

### Undo Step 1
```bash
# rollback command
```

---

## Troubleshooting

### <!-- Failure mode 1 -->

- **Symptom:** <!-- What you observe -->
- **Cause:** <!-- Why it happens -->
- **Fix:** <!-- How to resolve it -->

### <!-- Failure mode 2 -->

- **Symptom:** <!-- What you observe -->
- **Cause:** <!-- Why it happens -->
- **Fix:** <!-- How to resolve it -->

---

## Escalation

| Order | Role | Contact Method | When to Escalate |
|-------|------|---------------|-----------------|
| 1 | <!-- Primary --> | <!-- Slack / email / phone --> | <!-- After what threshold --> |
| 2 | <!-- Secondary --> | <!-- Slack / email / phone --> | <!-- After what threshold --> |

**When escalating, include:**
- What was attempted (link to this runbook)
- Exact error messages or symptoms observed
- Timestamp of when the issue started

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| <today> | <!-- Author --> | Initial draft |
```

## Notes
- This skill works in any directory — it is not vault-specific
- The `Runbooks/` folder is created relative to the current working directory
- If the file already exists, warn the user and ask before overwriting
- Frontmatter follows the project's YAML frontmatter standard with runbook-specific fields added
- The `review_cadence` field defaults to `quarterly` — the user can change it after creation
- Steps in the SOP section always pair a command with expected output and a verification check

## Lessons

- **2026-06-15** — `w5_completed_manually_this_session___run`: W5 completed manually this session — runbooks written, n8n drill PASSED, commit 8b7814b. Closing stale workspace_busy entry. [src: task-1000560]
- **2026-06-15** — `w5_completed_manually_this_session___run`: W5 completed manually this session — runbooks written, n8n drill PASSED, commit 8b7814b. Closing stale workspace_busy entry. [src: task-1000560]
