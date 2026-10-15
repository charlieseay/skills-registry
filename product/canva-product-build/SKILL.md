---
name: "canva-product-build"
description: "How to build and verify a Talos digital product (Instagram/social template bundle, printable, planner page set, sticker or label pack) using the Canva connector. Use when a task says 'in Canva', 'via Canva', 'Canva template/pack/bundle', or carries [needs:canva]. Covers the tool sequence, the rate budget, and the rule that a successful Canva job is not proof of a correct design."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["digital-product-playbook", "digital-product-quality-bar", "etsy-hero-image-generation", "product-quality-verify"]
---

# Canva Product Build

Canva is a claude.ai account connector (hosted MCP, tools named
`mcp__claude_ai_Canva__*`). Only the `claude_connectors` lane in
`agent_routing` can call it; a task reaches that lane when its text matches
`requires_connectors()` (say "in Canva", "Canva template", or `[needs:canva]`).
If you are on any other lane and cannot see Canva tools, stop and report
`NEEDS_CONNECTOR: canva` instead of faking output.

This is for **products Talos sells** (Etsy/Gumroad deliverables). It is not the
small-business social-campaign skill (`canva-creator`) and does not stage anything
in HubSpot.

## Sequence

1. **Phase 0 gate first.** No Canva call before the demand/saturation gate in
   `digital-product-playbook` has cleared. Canva work is cheap to start and
   expensive to throw away.
2. **Brand kit.** `list-brand-kits`, pick one, record its id in the product brief.
3. **Start from a template when one exists.** `search-brand-templates`, then
   `create-design-from-brand-template` (fill slots via `get-brand-template-dataset`).
   Otherwise `create-design` (or `generate-design` / `generate-design-structured`), then `create-design-from-candidate`
   for the chosen candidate.
4. **Refine** with `edit-design` (always confirm the edit transaction the way the
   tool describes) and `resize-design` for format variants.
5. **Export** with `get-export-formats` then `export-design`. PDF for printables,
   PNG for social and listing previews. Exports return URLs. The lane has no shell or
   file tools by design: report each export URL and design id in your output, and the
   caller downloads them with `agent_routing.download_export(url, dest)` (https, Canva
   hosts only) into `~/Projects/talos-tools/phase-1/<product>/`, alongside a `canva.json`
   of design ids so each design stays editable.

## Rules that prevent the known failures

- **`status: success` proves nothing about content.** A job with a stale or empty
  asset still succeeds and renders Canva's stock placeholder art. Every design must be exported and the
  rendered file inspected before it counts (rule: real viewer, not a CLI
  rasteriser; see `digital-product-quality-bar`).
- **Count slots against inputs.** A template with 3 image slots and 1 supplied image
  ships two placeholder graphics. List slots first; pick a single-slot template or
  report the gap.
- **Budget the calls.** About 5 API calls per design (create, edit, export, polling) and
  a 100/min ceiling per token. Plan `designs x 5`, pace in batches, and stop with
  partial results rather than looping on RATE_LIMIT.
- **Account state is shared.** Designs land in Charlie's real Canva account. Create a
  folder per product (`create-folder`) and `move-item-to-folder`; never edit or delete
  designs you did not create in this task.
- **Preview count.** The quality bar wants 10 listing previews; budget those exports up front.

## Output contract

Return: design ids, export URLs, and the call count used. Verification of the rendered
file happens after download, by the caller.

## Observed limits and the export contract (added 2026-10-07)

- **Canva has a credit quota with a cooldown.** A pilot that started six `create-design` jobs at once got one design; the other five failed immediately with `quota_cooldown: Credit quota cooldown is active`. Create designs **one at a time**, and on the first `quota_cooldown` stop, report `TASK_INCOMPLETE` with what exists, and do not retry in a loop. The cooldown length is not known.
- **The lane has no shell or files.** Give the task a line `EXPORT_DIR: ~/Projects/talos-tools/phase-1/<slug>/exports` in Context (only folders under talos-tools are honoured). For every exported file the agent prints one line `EXPORT: <name>.png <https url>`; the caller downloads them (Canva hosts only, redirects re-checked, 40 MB cap) and appends `DOWNLOADED:` lines.
- **Cleanup is manual.** The tool set has no delete, so every test design stays in the account. Put test work in one folder and tell the user the folder name.
- **Agents skipped the folder steps** in several runs. Make "create the folder", "move each design into it" and "report the folder id" explicit numbered steps, and check the reply for the id.
