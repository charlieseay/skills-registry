# GitHub awesome-copilot (selected skills)

Imported 2026-10-03 from https://github.com/github/awesome-copilot (verified
real: official `github` GitHub org, 39.6K stars). Note: despite living under
the official org, content is explicitly community-contributed, not
GitHub-authored -- the repo's own description says so. Reviewed each file
individually before import rather than trusting the org alone.

The skills.sh listing's "gh-cli" (22K installs) did not actually exist in
this repo under that name -- most of the 426 skills here are Azure/Microsoft-
focused and off-target for our stack. Only imported the 5 that are genuinely
relevant:

- `mcp-security-audit` — audit .mcp.json configs for hardcoded secrets, shell
  injection, unpinned versions. Directly useful: we run dozens of MCP servers.
- `mcp-implementation-security-review` — reviewing an MCP server's own
  implementation for command injection / dynamic eval vulnerabilities.
- `postgresql-optimization` / `postgresql-code-review` — relevant since
  helmsman-db and Bridge both run Postgres.
- `security-review` — general review skill.

Each file individually grepped for prompt-injection/credential-exfil
patterns before import; clean (the only hits were the skills' own
pattern-matching code for detecting those exact attacks).
