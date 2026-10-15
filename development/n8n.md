---
name: n8n
category: development
description: Work with n8n workflows (debug, create, deploy)
triggers:
  patterns:
  - n8n
  - workflow
  - automation
  - n8n workflow
  contexts:
  - automation
  - integration
  - workflows
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when work with n8n workflows (debug, create, deploy)
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 30
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Manage n8n workflows from the command line — list, backup, health check, test, logs, and status control.

## Usage
- `/n8n list` — list all workflows with active/inactive status and last execution
- `/n8n backup [workflow_id]` — export workflow JSON to vault backup folder
- `/n8n health` — check failed executions, summarize errors, alert count
- `/n8n test [workflow_id]` — manual trigger and wait for result
- `/n8n logs [workflow_id]` — recent execution history with errors
- `/n8n status [workflow_id] [on|off]` — activate/deactivate a workflow and verify

If no action is provided, default to `list`.

## MCP Tools

All operations use the Vault MCP n8n tools:

| Action | MCP Tool |
|--------|----------|
| List workflows | `mcp__claude_ai_claudecp__n8n_list_workflows` |
| Get workflow detail | `mcp__claude_ai_claudecp__n8n_get_workflow` |
| Failed executions | `mcp__claude_ai_claudecp__n8n_failed_executions` |
| Execute workflow | `mcp__claude_ai_claudecp__n8n_execute_workflow` |
| Execution history | `mcp__claude_ai_claudecp__n8n_workflow_executions` |
| Execution detail | `mcp__claude_ai_claudecp__n8n_execution_detail` |
| Activate workflow | `mcp__claude_ai_claudecp__n8n_activate_workflow` |
| Deactivate workflow | `mcp__claude_ai_claudecp__n8n_deactivate_workflow` |
| Status summary | `mcp__claude_ai_claudecp__n8n_status_summary` |

---

## Action: `list`

1. Call `n8n_list_workflows`
2. Present results as a table:

| ID | Name | Active | Last Execution | Last Status |
|----|------|--------|----------------|-------------|

Sort by name. Show "never" if no executions exist.

---

## Action: `backup [workflow_id]`

Exports workflow JSON for version-controlled backup.

**Backup directory:** `Projects/Lab/Apps/n8n-backups/` in the vault (`/path/to/your/obsidian/vault/Projects/Lab/Apps/n8n-backups/`)

**If `workflow_id` is provided:**
1. Call `n8n_get_workflow` with the ID
2. Save the full JSON response to `<backup_dir>/<workflow_name>__rl.json` (replace spaces with underscores in filename, append `__rl` suffix per n8n operations runbook convention)
3. Report the saved file path and size

**If no `workflow_id` (backup all):**
1. Call `n8n_list_workflows` to get all workflow IDs
2. For each workflow, call `n8n_get_workflow` and save JSON using the same naming convention
3. Report total workflows backed up and total size

After backup, remind the user to run `/checkpoint` to push backups to the n8n-workflow-backups repo.

---

## Action: `health`

Runs a health audit of the n8n instance.

1. Call `n8n_status_summary` for an overview (active/inactive counts, execution stats)
2. Call `n8n_failed_executions` to get recent failures
3. Summarize in a structured report:

**n8n Health Report**

| Metric | Value |
|--------|-------|
| Total workflows | # |
| Active | # |
| Inactive | # |
| Failed executions (recent) | # |

**Failed Executions:**
For each failure, show:
- Workflow name and ID
- When it failed
- Error message (first line / summary)
- Which node failed

Group failures by workflow if multiple failures exist for the same workflow.

**Important:** n8n only stores error executions (`EXECUTIONS_DATA_SAVE_ON_SUCCESS=none`). The absence of execution records for a workflow means it has been succeeding, not that it hasn't run.

If there are 5+ failures for a single workflow, flag it as needing attention.

---

## Action: `test [workflow_id]`

Manually triggers a workflow and reports the result.

1. Confirm the workflow exists by calling `n8n_get_workflow` — show the name and current active status
2. Call `n8n_execute_workflow` with the workflow ID
3. Wait for the result
4. Report:
   - Execution ID
   - Status (success/error)
   - Duration
   - If error: the failing node and error message
   - If success: summary of output data (first 500 chars if large)

**Warning:** Some workflows have side effects (send emails, post to APIs, update databases). Before executing, tell the user which workflow they're about to trigger and what it does (based on the workflow name and nodes). Let them confirm unless the workflow name is clearly safe (e.g., health check, status report).

---

## Action: `logs [workflow_id]`

Shows recent execution history for a specific workflow.

1. Call `n8n_workflow_executions` with the workflow ID
2. Present as a table:

| Execution ID | Started | Finished | Status | Error |
|-------------|---------|----------|--------|-------|

3. If any execution has errors, call `n8n_execution_detail` for the most recent failed one and show:
   - Which node failed
   - Full error message
   - Input data to the failing node (if available)

Show up to 10 most recent executions. If there are no executions, explain that n8n only stores error executions — no records means the workflow has been succeeding.

---

## Action: `status [workflow_id] [on|off]`

Activates or deactivates a workflow.

1. Call `n8n_get_workflow` to confirm current state — show the name and current active/inactive status
2. If the requested state matches the current state, report "already [active/inactive]" and stop
3. If changing state:
   - `on` → call `n8n_activate_workflow`
   - `off` → call `n8n_deactivate_workflow`
4. After the API call, verify by calling `n8n_get_workflow` again to confirm the state changed
5. Report the result

**Post-change note:** If a workflow with cron/schedule triggers was activated, remind the user that n8n may need a container restart to re-register cron triggers:
> After activating a scheduled workflow via API, run `docker restart n8n` to ensure cron triggers are registered.

---

## Key Rules

These rules come from the n8n operations runbook and must always be followed:

1. **n8n only stores error executions** — `EXECUTIONS_DATA_SAVE_ON_SUCCESS=none` is set. No execution records = workflow is succeeding.
2. **Code nodes v2 use `jsCode`** — never use the `code` field for typeVersion 2 Code nodes.
3. **Restart after API updates** — after activating/deactivating workflows via API, cron triggers may not re-register until the n8n container is restarted.
4. **`__rl` suffix for backup files** — all workflow JSON exports use the `__rl` naming convention.
5. **Follow Post-Fix Verification Protocol** — fix, verify via execution, then update the registry note.
6. **Build/fix one node at a time** — when modifying workflows, change one node and verify before moving to the next.
7. **Registry is the source of truth** — the annotated registry at `Projects/Lab/Apps/n8n Workflow Registry.md` documents what each workflow does and its current state.

## Notes
- n8n instance: `https://[your-n8n-url]` (port 5678)
- Workflow backups repo: `/path/to/n8n/backups` (https://github.com/[your-username]/[your-n8n-backups])
- Vault backup path: `Projects/Lab/Apps/n8n-backups/` in your vault
- The n8nOps agent definition at `Agents/n8nOps.md` has additional operational context — read it for complex troubleshooting
