---
name: "credential-and-tool-verification"
description: "Before relying on any external tool/API/connector to fix a real problem (a broken delivery link, a blocked publish, an integration Charlie says is 'connected'), verify it is actually usable from the execution context you're running in, not just that it exists or was authorized somewhere. Use this whenever a fix plan depends on a named tool/connector/MCP server/API you haven't personally called yet in this exact session or worker process, whenever Charlie says a service is 'connected' or 'set up', or before telling Charlie a problem 'can't be fixed via API' — that claim needs proof, not assumption."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["talos-product-launch-audit", "state-reconciliation", "etsy-api"]
---

# Credential and Tool Verification

**Fleet-wide skill.** A tool or connector being "authorized," "connected," or
"available" in one place does not mean it is callable from where you're
actually running. This gap has real cost: work stalls, or worse, an agent
tells Charlie something "can't be done via API" when it was never actually
checked.

## Why this exists

On 2026-09-29, mid-investigation into a broken Etsy product (10 Canva
template links all returning 403), Charlie asked "you have the Canva MCP,
right?" A `claude.ai Canva` connector did show as configured. Charlie then
authorized it via claude.ai connector settings. A tool search for Canva
capabilities afterward found **zero actual Canva tools** — the connector
showed as authorized but exposed nothing callable in that session. Separately,
and more importantly: even if it had worked, that authorization is scoped to
one interactive session's claude.ai login. It does nothing for Talos's own
background workers (`nvidia-agent`, `cursor-worker`, Bedrock), which
authenticate through entirely separate credentials in
`/Volumes/data/secrets/` — a session-level OAuth connector can never reach
them. Two independent, stackable failure modes, both invisible until someone
actually tried to call the tool.

## The two checks, always in this order

### 1. Is the tool actually callable from where you're running RIGHT NOW?

Don't infer this from:
- A connector/integration showing "authorized" or "connected" in a settings
  UI or a system list.
- A prior session, a different agent, or a different execution context
  having used it successfully.
- The tool's *name* sounding right (a "Canva" connector can expose zero
  Canva-specific tools if its scope or the underlying MCP server doesn't
  provide them — verify by actually listing/searching for the specific
  capability you need, not the connector's existence).

Do this instead: actually invoke a search/list/discovery call for the
specific capability (e.g. `ToolSearch` for a tool name, a direct API health
check, a `--help`/`list` command against a CLI) **before** building a fix
plan around it. If nothing real surfaces, the tool is not available here,
full stop — regardless of what a settings page claims.

### 2. If it IS callable here, does it also reach the OTHER execution context that needs it?

This is the check most often skipped. A credential/connector authorized in
**your current interactive session** does not automatically propagate to:
- A background worker process (Talos's `nvidia-agent`, `cursor-worker`,
  Bedrock lanes) — these authenticate independently, typically via API
  keys/service credentials in `/Volumes/data/secrets/`, not session OAuth.
- A different agent's own session (Gemini, aider, another Claude Code
  instance) — same boundary.
- A scheduled/cron job or launchd service — same boundary again.

**Ask explicitly: who needs this capability?** If the answer is "an
autonomous background process, not just me right now," a session-scoped
connector is close to useless — what's needed is a durable, portable
credential (an actual API key/OAuth client ID+secret pair) stored in
`/Volumes/data/secrets/<name>` per this fleet's standard pattern (see
`etsy-api` skill's credential section for the canonical example: app
key/secret + a refreshable token pair, with a reusable helper module other
agents import rather than each re-implementing OAuth). Setting this up
almost always requires a human to complete an account-owner step (register
a developer app, click through an OAuth consent screen once) — that's not a
failure of the fix, it's a legitimate one-time cost to pay before the
capability becomes durably available to the fleet.

## Before declaring "this can't be fixed via API"

This is a high-cost false claim — it can cause a real, fixable problem to
sit broken (see `talos-product-launch-audit`'s external-link-verification
pattern, where a customer-facing broken link is active revenue/reputation
risk). Before making this claim:

1. Confirm you actually tried calling the relevant API/tool per check #1
   above — not that you assumed based on general knowledge of the platform.
2. Check whether a parallel precedent already exists in another skill (e.g.
   Notion's Share-to-Web action has no API — documented in
   `digital-product-quality-bar`'s Notion Marketplace section; this is a
   real, previously-confirmed limitation worth citing rather than
   re-discovering). A platform's publish/share action frequently has no API
   surface even when its read/create/update actions do — this is a common
   enough pattern across Notion, Canva, and similar tools that it's worth
   checking as a first hypothesis, not a last resort.
3. If genuinely no API path exists, say so plainly and name the exact manual
   step a human needs to take (e.g. "click Share on these 10 specific Canva
   design URLs") — don't leave it vague, and don't attempt to fabricate a
   workaround that doesn't actually solve the problem.

## Quick reference

| Question | How to actually answer it |
|---|---|
| Is this tool available to me right now? | Call `ToolSearch` (or the tool's own discovery/health call) for the specific capability — not the connector name |
| Does Charlie saying "X is connected" mean I can use X? | No — it means X is connected to Charlie's account/session. Verify separately whether YOUR execution context can reach it |
| Will authorizing this connector help Talos's background workers? | Almost never — those need their own credential in `/Volumes/data/secrets/`, set up separately |
| Can I fix this via the platform's API? | Only if you've actually called it successfully — check for a known "no API for this action" precedent first (Notion Share, Canva Share/Publish) |
