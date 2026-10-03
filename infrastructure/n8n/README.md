# n8n skills

Imported 2026-10-03 from https://github.com/czlonkowski/n8n-skills (verified
real: 6370 stars, 1+ year old, not an official n8n org repo -- a trusted
third-party community project). Relevant to orchestr8 (7 active workflows)
and the `n8nops` subagent.

Full 15-skill set imported (no overlap with anything we had): workflow
patterns, MCP tools, node configuration, JavaScript/Python code nodes,
expression syntax, validation, error handling, self-hosting, multi-instance,
subworkflows, agents, binary/data handling.

Each file individually grepped for prompt-injection/credential-exfil
patterns before import -- the only hits were a documented placeholder
`curl` example against `n8n.example.com` (not a real exfil target) and
JS regex `.exec()` calls (not shell execution). Clean.
