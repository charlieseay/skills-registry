---
name: quarterly-review
category: operations
description: Quarterly retrospective and planning session
triggers:
  patterns:
  - quarterly review
  - Q review
  - quarter retrospective
  contexts:
  - planning
  - retrospective
  - strategy
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when quarterly retrospective and planning session
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 120
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

# quarterly-review

Runs the quarterly infrastructure review process: assesses spend optimization and architecture improvements.

## Usage

`/quarterly-review` — runs for current quarter (auto-detects)  
`/quarterly-review 2026-Q3` — runs for specific quarter

## What it does

Orchestrates a two-part research process with parallel agents:

1. **Spend Optimization Research:** Reviews all spend tracking data to identify cost savings without capability loss
2. **Architecture Optimization Research:** Reviews infrastructure diagram and metrics to identify performance/reliability improvements without cost increase

Both agents run in parallel (background), then results are synthesized into an executive summary report.

## Output

**Report location:** `/Volumes/data/containers/filebrowser/data/reports/Lab/Quarterly Reviews/YYYY-QQ-Infrastructure-Review.html`

**Also creates:**
- Spend snapshot (JSON)
- Infrastructure snapshot (JSON)
- Metrics baseline (JSON)

Reports are automatically visible in Bridge at `https://bridge.seaynicroute.com/recap`

## Process

See full process documentation: `Projects/Lab/Infrastructure/Quarterly Infrastructure Review — Process.md`

## Implementation

**Step 1: Collect data**
- Snapshot current spend from Bridge API
- Snapshot infrastructure state (containers, services, agents)
- Gather prior quarter report (if exists) for comparison

**Step 2: Launch parallel research agents**
- Agent 1: Spend Optimization Researcher (NVIDIA-BAL or Bedrock)
- Agent 2: Architecture Optimization Researcher (NVIDIA-BAL or Bedrock)

**Step 3: Synthesize report**
- Agent 3: Scribe (write executive summary in dark dossier format)
- Generate HTML version for Bridge

**Step 4: Notify Charlie**
- Post to #helm with report link
- Add to Bridge alert panel

## Notes

- First run (Q3 2026) establishes baseline — no prior quarter to compare
- Subsequent runs show quarter-over-quarter changes
- Recommendations become tasks in helmsman.db when approved
- Implemented changes are measured and reported in next quarter's review
