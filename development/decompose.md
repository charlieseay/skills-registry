---
name: decompose
category: development
description: Decompose large tasks into smaller, manageable subtasks
triggers:
  patterns:
  - decompose
  - break down
  - split task
  - subtasks
  contexts:
  - planning
  - project management
  - task breakdown
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when decompose large tasks into smaller, manageable subtasks
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 10
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

# Decompose Task Skill

Manually decompose a large task into phase-linked subtasks.

## Usage

```bash
/decompose <task-num>
/decompose <brief-file>
```

## What it does

1. Analyzes task complexity using brief_analyzer.py (6 signals)
2. Calls POST /tasks/:num/decompose endpoint
3. Reports phase breakdown
4. Shows phase task numbers with dependencies

## Examples

```bash
# Decompose existing task
/decompose 1013932

# Decompose from brief file
/decompose /tmp/task-brief.md
```

## When to use

- Task timed out (30 min) → decompose before retry
- L/XL effort task → decompose upfront
- Multi-step brief (>3 numbered steps) → decompose for visibility
- Task has >4KB brief → likely needs decomposition

## Output

Reports:
- Complexity signals detected
- Confidence score (0.0-1.0)
- Number of phases created
- Phase task numbers (#1014877, #1014878, etc.)
- Dependencies (blocked_by relationships)

---

## Implementation

**INPUT:** Task number or brief file path

**PROCESS:**

1. If task number → fetch from helmsman-db
2. If file path → read brief from disk
3. Call POST /tasks/:num/decompose
4. Parse response
5. Display phase breakdown

**OUTPUT:** Phase summary + task links
