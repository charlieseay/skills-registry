---
name: "web-design-guidelines"
description: "Review UI code for compliance with Vercel's Web Interface Guidelines — 100+ rules covering accessibility, performance, and UX. Use when asked to 'review my UI', 'check accessibility', 'audit design', 'review UX', or 'check my site against best practices'. Always fetches the current guidelines at run time rather than relying on a cached copy, so it stays current as Vercel updates the rule set."
category: "development"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["taste", "image-to-code"]
  source: "https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md (Vercel, official). Vendored 2026-09-26 for fleet-wide use per Charlie's request. Guidelines themselves come from vercel-labs/web-interface-guidelines."
---

# Web Interface Guidelines

> Vendored from [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) for fleet-wide use — any agent with a fetch/WebFetch-equivalent tool can run this, not just Claude Code.

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt the user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review — do not rely on a memorized or cached copy, since Vercel updates the rule set independently of this skill file:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use whatever fetch tool your runtime provides (Claude Code/Claude: WebFetch; other agents: an equivalent HTTP GET) to retrieve the latest rules. The fetched content contains all the rules and the output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above.
2. Read the specified files.
3. Apply all rules from the fetched guidelines.
4. Output findings using the format specified in the guidelines.

If no files are specified, ask the user which files to review.
