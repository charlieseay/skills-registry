---
name: clone
category: development
description: Clone a GitHub repository into ~/Projects/ using gh CLI
triggers:
  patterns:
  - clone repo
  - clone github
  - get repository
  contexts:
  - development
  - setup
  - onboarding
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when clone a github repository into ~/projects/ using gh cli
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 2
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Clone a GitHub repository into ~/Projects/ using the gh CLI.

## Usage
- `/clone owner/repo` — clones the repo into ~/Projects/repo
- `/clone owner/repo my-name` — clones into ~/Projects/my-name

## Steps

1. Parse the arguments: the first argument is the `owner/repo` (required), the second is an optional local directory name
2. Ensure `~/Projects/` exists: `mkdir -p ~/Projects`
3. Clone using gh: `gh repo clone <owner/repo> ~/Projects/<local-name>`
4. Report the clone location and the repo URL
5. If there is a README, read the first 30 lines and summarize what the project is

## Notes
- Default clone location is `~/Projects/` — always use this unless the user specifies otherwise
- Use `gh repo clone` (not `git clone`) so authentication is handled automatically
- If the clone fails because the directory already exists, tell the user and stop
