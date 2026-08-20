---
name: checkpoint
category: development
description: Checkpoint skill
triggers:
  patterns:
  - checkpoint
  contexts:
  - development
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when checkpoint skill
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 15
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Create a Git checkpoint — stage and commit changes across all tracked repos, then push to GitHub.

## Quick Start

**BEFORE running checkpoint, enforce the golden rules:**

1. **Query the rules** — open-notebook is the knowledge base now:
   ```bash
   kb search "golden rules" -n rules -l 10
   kb search "standing rules" -n rules -l 10
   ```
   (helmsman `curl -s "http://localhost:5682/rules?tier=golden"` still works and
   remains the write path for the registry itself; `kb` is how you READ.)

2. **Documentation-First check** — if any work this session touched platform/API code, verify the session consulted official docs (Golden Rule #3)

Then invoke the checkpoint-v2 script with the user's arguments:

```bash
/Users/charlieseay/Projects/claude-config/bin/checkpoint-v2 ${ARGS}
```

Where `${ARGS}` is:
- Empty for auto-generated messages
- `--dry-run` for preview mode
- `"commit message"` for custom message

The script handles everything: parallel scanning, conditional builds, PDF regeneration, summary artifact.

## What checkpoint-v2 Does

1. **Parallel dirty check** — scans all 59 repos simultaneously using `git status --porcelain`
2. **Skip unchanged** — only processes repos with actual changes
3. **Progress reporting** — shows "Processing N/M repos"
4. **Background builds** — runs npm/xcodebuild/docker in background, reports at end
5. **Conditional tasks:**
   - Task audit (only if vault Projects/ changed)
   - Agent config sync (only if CLAUDE.md/GEMINI.md changed)
   - Master project updates (only if substantial project work)
   - PDF regeneration (only if Standards/ or tracked docs changed)
   - Cloudflare deploy (only if charlieseay.com/enchapter-site + build flag)
6. **Summary artifact** — writes JSON to `/tmp/checkpoint-summary-$$.json` with timing/stats
7. **Smart cleanup** — removes temp files older than 1 day

## Performance

- **Before:** 60-90s for 5-10 changed repos (serial scanning, blocking builds)
- **After:** 5-10s for 5-10 changed repos (parallel scanning, background builds)
- **Speedup:** 10-20x faster

## Exit Behavior

After checkpoint completes, the skill should report the summary and then **continue with whatever work was in progress** — checkpoint is a save point, not a stopping point. Do not wait for user confirmation to resume.

## Environment detection

This skill works from **both** the Mac and the code-server container. Detect the environment first:

- **Mac (macOS):** paths start with `/Users/charlieseay/`
- **code-server container (Linux):** paths start with `/config/workspace/`

Check: if `/config/workspace` exists, use container paths. Otherwise, use Mac paths.

## Repos to checkpoint

| Repo | Mac Path | Container Path | What it tracks |
|------|----------|----------------|----------------|
| ~~SeaynicNet vault~~ | — | — | **NOT git-backed (2026-06-24). iCloud Sync is the backup.** Git commits conflict with Docker VirtioFS — containers (vault-mcp) bind-mount the vault incl. `.git`, blocking `index.lock` creation. Do NOT checkpoint the vault to GitHub. |
| charlieseay.com | `/Users/charlieseay/Projects/charlieseay.com` | `/config/workspace/Projects/charlieseay.com` | Full Astro site source |
| Enchapter | `/Users/charlieseay/Projects/StoryChat` | `/config/workspace/Projects/StoryChat` | Full iOS app source (Xcode project folder stays as StoryChat) |
| Enchapter Site | `/Users/charlieseay/Projects/enchapter-site` | `/config/workspace/Projects/enchapter-site` | Product page (static Astro site) |
| Hone | `/Users/charlieseay/Projects/hone` | `/config/workspace/Projects/hone` | Self-assessment platform (Astro site) |
| Enchapter API | `/Users/charlieseay/Projects/enchapter-api` | `/config/workspace/Projects/enchapter-api` | Proxy API server (Hono/Node.js) |
| Claude Config | `/Users/charlieseay/Projects/claude-config` | `/config/workspace/Projects/claude-config` | Skills, hooks, and settings for Claude Code portability |
| REACT Pro | `/Users/charlieseay/Projects/reactpro` | `/config/workspace/Projects/reactpro` | Business website (static Astro site) |
| E2E Tests | `/Users/charlieseay/Projects/e2e-tests` | `/config/workspace/Projects/e2e-tests` | Playwright browser tests & screenshot automation |
| JobAid | `/Users/charlieseay/Projects/jobaid` | `/config/workspace/Projects/jobaid` | Resume tailoring tool (Node.js + Anthropic SDK) |
| Claude Context | `/Users/charlieseay/Projects/claude-context` | `/config/workspace/Projects/claude-context` | Portable Claude context — personas, agents, working patterns |
| Stripe MCP | `/Users/charlieseay/Projects/stripe-mcp` | `/config/workspace/Projects/stripe-mcp` | Read-only Stripe MCP server (Python / FastMCP) |
| Sextant | `/Users/charlieseay/Projects/sextant` | `/config/workspace/Projects/sextant` | Vision-augmented browser automation (Python + Playwright + NVIDIA vision) — Phase 1 scaffold; no remote yet |
| Bridge | `/Users/charlieseay/Projects/bridge` | `/config/workspace/Projects/bridge` | Helmsman command center dashboard (SvelteKit + Hono, port 8116) |
| Content Studio | `/Users/charlieseay/Projects/content-studio` | `/config/workspace/Projects/content-studio` | Content pipeline app (Bun/Hono, port 3600) |
| Seaynic Labs Store | `/Users/charlieseay/Projects/seayniclabs-store` | `/config/workspace/Projects/seayniclabs-store` | Product store (Astro SSR + Stripe + Authentik) |
| Bearing | `/Users/charlieseay/Projects/bearing` | `/config/workspace/Projects/bearing` | Intelligent model router MCP server (Python/FastMCP) |
| Reckoner | `/Users/charlieseay/Projects/reckoner` | `/config/workspace/Projects/reckoner` | Local-first AI chat VSCode extension (Ollama + MCP + Bearing) |
| Prompt Library | `/Users/charlieseay/Projects/prompt-library` | `/config/workspace/Projects/prompt-library` | Reverse-engineered prompt library (136 prompts) |
| Enchapter Kokoro | `/Users/charlieseay/Projects/enchapter-kokoro` | `/config/workspace/Projects/enchapter-kokoro` | Fly.io config for Piper TTS cluster |
| QA Runner | `/Users/charlieseay/Projects/qa-runner` | `/config/workspace/Projects/qa-runner` | Playwright QA suite + Ledger reporter (Mac only — no container path) |
| QA Hands | `/Users/charlieseay/Projects/qa-hands` | `/config/workspace/Projects/qa-hands` | Vision-driven QA orchestrator + LedgerOrchestrator hook (Mac only) |
| Ledger | `/Users/charlieseay/Projects/ledger` | `/config/workspace/Projects/ledger` | Shared Ledger pipeline: export.py + annotate.py (Mac only) |
| Sonique iOS | `/Users/charlieseay/Projects/sonique-ios` | — | SwiftUI voice assistant client for CAAL (Mac only) |
| Sonique Mac | `/Users/charlieseay/Projects/sonique-mac` | — | macOS menu bar app for Sonique (Mac only) |
| CAAL | `/Users/charlieseay/Projects/cael` | — | Core voice agent backend (Next.js + Python + LiveKit) |
| TC Platform Build 0 | `/Users/charlieseay/Projects/tc-platform-build0` | — | TC automation platform master template (Mac only) |
| TC Platform Onboarding | `/Users/charlieseay/Projects/tc-platform-onboarding` | — | Client onboarding wizard — Astro + Cloudflare Pages (Mac only) |
| TC Platform Control | `/Users/charlieseay/Projects/tc-platform-control` | — | Control plane — heartbeat receiver, provisioning, Grafana (Mac only) |
| Centaur Tools | `/Users/charlieseay/Projects/centaur-tools` | — | Playwright/browser automation for Fiverr, Upwork, Freelancer session management (Mac only) |
| Jackel | `/Users/charlieseay/Projects/jackel` | `/config/workspace/Projects/jackel` | OSINT investigation dashboard for licensed private investigators (FastAPI + Next.js, Docker) |
| Weft Playwright | `/Users/charlieseay/Projects/weft-playwright` | — | Playwright session capture for Weft — Fiverr, Upwork, Freelancer (Mac only) |
| StdOut | `/Users/charlieseay/Projects/stdout` | `/config/workspace/Projects/stdout` | Self-hosted infrastructure monitoring with AI diagnosis (Astro + SQLite + Observatory AI toolbox) |
| StdOut Site | `/Users/charlieseay/Projects/stdout-site` | `/config/workspace/Projects/stdout-site` | Product page + community library host for StdOut + Windlass (Astro SSR + SQLite, port 8114) |
| StdOut Satellite | `/Users/charlieseay/Projects/stdout-satellite` | `/config/workspace/Projects/stdout-satellite` | Lightweight Go agent that reports system metrics to a StdOut instance |
| nvidia-agent-svc | `/Users/charlieseay/Projects/nvidia-agent-svc` | — | Agentic task runner using NVIDIA NIM tool calling (FastAPI, port 5901, Mac only) |
| aider-svc | `/Users/charlieseay/Projects/aider-svc` | — | Headless aider task runner using Gemini 2.5 Pro (FastAPI, port 5902, Mac only) |
| seaynic-support-inbound | `/Users/charlieseay/Projects/seaynic-support-inbound` | — | Cloudflare Worker — receives mail to support@seayniclabs.com, parses SEAYNIC_ROUTING, POSTs to n8n (Mac only) |
| seaynic-support-lib | `/Users/charlieseay/Projects/seaynic-support-lib` | — | Shared Python helper for sending to support@ with mandatory SEAYNIC_ROUTING block (Mac only) |
| support-responder-svc | `/Users/charlieseay/Projects/support-responder-svc` | — | Polls Helmsman for support tasks, drafts replies via Bedrock Haiku, sends via Resend (FastAPI + launchd, port 5910, Mac only) |
| b3ck-agents | `/Users/charlieseay/Projects/b3ck-agents` | — | B3CK's autonomous agents — tech catalog scanner + tech-kb staleness checker (Mac only) |
| helmsman-db | `/Users/charlieseay/Projects/helmsman-db` | — | Helmsman task DB REST service (server.py, port 5682, Mac only) |
| talos | `/Users/charlieseay/Projects/talos` | — | Talos freelance bidding automation — workers, workflows, inbound email (Mac only) |
| real-estate-mcp | `/Users/charlieseay/Projects/real-estate-mcp` | — | FollowUp Boss CRM MCP server (8 tools — TypeScript, stdio; Mac only). Remote: https://github.com/charlieseay/real-estate-mcp |
| homeassistant-mcp-server | `/Users/charlieseay/Projects/homeassistant-mcp-server` | — | Home Assistant MCP server (Life360 + UGREEN NAS, Python/FastMCP; Mac only). Remote: https://github.com/charlieseay/homeassistant-mcp-server |

## Pre-commit build verification

Before committing, check for build flag files in `/tmp/claude-build-flags/`. These are set automatically by the PostToolUse hook when project files are edited.

For each flag file that exists:
- `hone` → run `npm run build` in the hone repo
- `enchapter` → run `xcodebuild` for StoryChat (if applicable)
- `enchapter-api` → run `docker compose build` in the enchapter-api repo (rebuilds container image)

If a build **fails**, stop and report the error. Do not commit broken code.

After a successful build, remove the flag file: `rm /tmp/claude-build-flags/<name>`

If no flag files exist, skip the build step.

## Cloudflare Pages deployments

**Skip condition:** Only run if `charlieseay.com` or `enchapter-site` had changes AND their build flag exists.

These repos are hosted on Cloudflare Pages (direct upload, not GitHub-triggered). After pushing to GitHub, deploy the built `dist/` to Pages using wrangler:

| Repo | Pages project name | Deploy command |
|------|--------------------|---------------|
| charlieseay.com | `charlieseay` | `cd ~/Projects/charlieseay.com && npm run build && CLOUDFLARE_API_TOKEN=$(cat /Volumes/data/secrets/cloudflare_management_token) CLOUDFLARE_ACCOUNT_ID=b1b2b942d6d2f2df8e21f4c48f4d37c5 npx wrangler pages deploy dist --project-name=charlieseay --branch=main --commit-dirty=true` |
| enchapter-site | `enchapter-site` | `cd ~/Projects/enchapter-site && npm run build && CLOUDFLARE_API_TOKEN=$(cat /Volumes/data/secrets/cloudflare_management_token) CLOUDFLARE_ACCOUNT_ID=b1b2b942d6d2f2df8e21f4c48f4d37c5 npx wrangler pages deploy dist --project-name=enchapter-site --branch=main --commit-dirty=true` |

**When to deploy:** Only when the build flag exists for the repo (same as other build verification). If the flag file triggers a build, also deploy to Pages after the build succeeds.

## Steps

For **each repo**, independently:

1. Run `git status` to see what has changed
2. If there are no changes in that repo, skip it — do not create an empty commit
3. Stage all changes: `git add -A`
4. If a message was provided as an argument, use it for both repos. Otherwise, write a short message appropriate to what changed in that repo.
5. Commit with the message, appending the Co-Authored-By trailer:
   ```
   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   ```
6. Push to origin: `git push`

## Write the checkpoint to open-notebook

After committing, publish what changed so the KB reflects reality. This is where
we put things now — a checkpoint that only lands in git is invisible to every
agent that searches.

```bash
# Per project with substantial work this session:
kb write -n projects -t "<Project> HANDOFF" -f "Projects/<Project>/HANDOFF.md"

# Session summary (upserts by title, so re-running the same day updates it):
kb write -n projects -t "Session $(date +%Y-%m-%d) — <focus>" --text "$(cat <<'EOF'
## Shipped
- ...
## Decisions
- ...
## Open
- ...
EOF
)"
```

`kb write` upserts by title and credential-scrubs every body, refusing anything
still secret-shaped. Skip it only if the session produced no durable change.

## Note consolidation

**Note:** `vault-housekeep.py` runs automatically every Saturday 08:00 CT via launchd. Checkpoint does NOT run it — the scheduled job handles vault hygiene independently.

Checkpoint only commits the auto-fixes that vault-housekeep made during its scheduled run (if any uncommitted changes exist in `Projects/Lab/Housekeeping/`).

## Task audit

**Skip condition:** Only run if vault `Projects/` folder had changes this session.

After committing, audit the vault bug/feature tracker to make sure it's complete and current. The tracker is the **single source of truth** for "what's left to do" across all projects.

### How to audit

1. **Scan all project notes** (`Projects/*/`) for open items — look for:
   - Unchecked `- [ ]` items in Planning/Phase sections
   - Items mentioned as "next" or "TODO" or "deferred" or "pending" in Issues & Resolutions
   - Any work discussed in the current session that was deferred or left incomplete

2. **Scan all existing ticket files** (`Projects/*/Bugs/*.md` and `Projects/*/Features/*.md`) — check that:
   - Every ticket's `status` frontmatter matches reality (e.g., if something was fixed this session, update to `resolved`/`closed`)
   - No tickets are stale or orphaned

3. **Compare and fill gaps:**
   - If an open item exists in a project note but has no corresponding ticket file → create the ticket
   - If a ticket exists but isn't referenced in the project note's tracking list → add the wikilink
   - If work was done this session that resolves a ticket → update the ticket status and add resolution details

4. **Report** what was added, updated, or is still open — so the user has a clean snapshot.

### Ticket format

Use the vault templates:
- **Bugs:** `Projects/<project>/Bugs/<Title>.md` — use `Bug Report.md` template frontmatter
- **Features:** `Projects/<project>/Features/<Title>.md` — use `Feature Request.md` template frontmatter

Every ticket must be referenced in its project note's "Bug & Feature Tracking" section as a bullet using standard markdown links (not wikilinks — wikilinks don't render in the browser): `- **P#** [Title](Type/Title%20Name.md) — Status`

### Skip conditions

- If no project-related work was done in this session (e.g., only vault note edits), skip the audit
- If the session was trivial (single typo fix, etc.), skip the audit

## Agent Configuration Sync

**Skip condition:** Only run if `CLAUDE.md` or `GEMINI.md` (vault or global) changed this session.

Before updating project files, check if any agent configuration files (CLAUDE.md, GEMINI.md) have new rules, directives, or objectives that need to be synced.

**Files to check:**
- Vault: `CLAUDE.md` (project-specific instructions)
- Global: `~/.claude/CLAUDE.md` (user's global instructions)
- Vault: `GEMINI.md` (Gemini-specific instructions, if it exists)
- Global: `~/.gemini/GEMINI.md` (Gemini's global context, if it exists)

**Sync process:**

1. **Compare vault vs global:** If vault CLAUDE.md has rules that aren't in ~/.claude/CLAUDE.md (or vice versa), identify which is newer
2. **Merge bidirectionally:**
   - New routing rules, standards, or standing instructions → copy to both
   - Project-specific context (repos, URLs, current work) → keep in vault only
   - Personal preferences (name, role, communication style) → keep in global only
3. **Update timestamps:** Set `updated` date in frontmatter when changes are synced
4. **Log what was synced:** Report which rules/sections were added to which file

**Skip conditions:**
- No changes to CLAUDE.md or GEMINI.md this session
- Files already in sync (no new rules/directives)

**Example sync:**
```
Vault CLAUDE.md added new routing rule: "All TC Platform work routes to Claude Code"
→ Copied to ~/.claude/CLAUDE.md so all agents see it

~/.claude/CLAUDE.md updated communication preference: "Call me Charlie, not 'user'"
→ Copied to vault CLAUDE.md for consistency
```

## Master Project File Update

**Skip condition:** Only run if this session did substantial work on a specific project (not just vault organization, memory updates, or cross-project changes).

After agent config sync and task audit, update or create the master project file for any project that had significant work this session.

**Location:** `Projects/<project>/<project>.md` (e.g., `Projects/REACT Pro/REACT Pro.md`)

**Template** (create if doesn't exist):
```markdown
---
tags: [project, <slug>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active | archived | on-hold
---

# Project Name

## Overview
Brief description of what this project is and its purpose.

## Current State
What's deployed, what's working, what's blocked.

## Last Session (YYYY-MM-DD)
- **Operator:** Claude Code / Gemini / Agent name
- **Work completed:** Bullet list of what shipped
- **Decisions made:** Key architectural or design choices
- **Issues discovered:** Problems found but not yet fixed
- **Next actions:** What should happen next

## Active Work
Current sprint/phase items:
- [ ] Task 1
- [ ] Task 2

## Key Files & Resources
- Production URL: ...
- Repo: ...
- Deployment docs: ...
- Related projects: ...
```

### Update process

1. **Determine if update needed:** Only update if this session did substantial work on a specific project (not just vault organization or memory updates)

2. **Read existing file** (if it exists) to preserve Overview, Current State, Active Work, and Key Files sections

3. **Add new "Last Session" entry** at the top of the Last Session section (push previous sessions down, keep last 5 sessions max)

4. **Update frontmatter `updated` field** to today's date

5. **Update Current State** based on what shipped this session

6. **Conflict detection:** If file was modified since session start, merge manually:
   - Keep existing Overview, Active Work, Key Files (don't overwrite)
   - Prepend new Last Session entry (don't replace other agents' entries)
   - Update Current State only if it's stale

### What to include in Last Session

- **Operator:** The AI that did the work (Claude Code, Gemini CLI, nvidia-agent, etc.)
- **Work completed:** Specific deliverables — features shipped, bugs fixed, deployments made
- **Decisions made:** Architectural choices, design patterns adopted, tech stack decisions
- **Issues discovered:** Bugs found, blockers identified, edge cases uncovered
- **Next actions:** Clear next steps for whoever picks this up

### Skip conditions

- No substantial project work this session (only docs, memory, or vault organization)
- Session was purely research or exploration with no deliverables
- Multi-project session with no clear primary project

### Example Last Session entry

```markdown
## Last Session (2026-06-08)
- **Operator:** Claude Code (Claude Sonnet 4.6)
- **Work completed:**
  - Complete agent onboarding flow (tool selection → OAuth → completion)
  - Add/Edit/Delete agent functionality
  - OAuth sync system with manual refresh button
  - Service-focused messaging throughout
- **Decisions made:**
  - OAuth credentials live in vault DB, admin panel syncs via /health endpoint
  - Template variables for all cross-service URLs (no hardcoding)
  - Agents table + clients table both updated on agent creation (FK requirement)
- **Issues discovered:**
  - OAuth sync doesn't auto-refresh on page load (debounce too aggressive)
  - Frontend cache requires hard refresh after deployment
- **Next actions:**
  - Verify sync button works after hard refresh
  - Wire up email sending via Resend
  - Add Microsoft 365 + CRM OAuth flows
```

## PDF regeneration

**Skip condition:** Only run if any files in `Standards/` or tracked project docs changed this session.

After committing, check if any tracked Markdown files were changed that have corresponding PDFs in the reports directory at `/Volumes/data/containers/filebrowser/data/reports/`.

### Tracked document folders and their PDF output mapping

| Source folder | Reports subfolder |
|--------------|-------------------|
| `Standards/*.md` | `Standards/` |
| `Projects/Business/*.md` | `Business/` |
| `Projects/Hone/Tech Spec.md`, `Projects/Hone/Test Plan.md` | `Hone/` |
| `Projects/Enchapter/Tech Spec.md`, `Projects/Enchapter/Test Plan.md` | `Enchapter/` |
| `Projects/charlieseay.com/Tech Spec.md` | `charlieseay.com/` |
| `Projects/Lab/Apps/ElevenLabs Setup.md` | `Lab/` |

### How to regenerate

For each changed `.md` file that has a PDF mapping above:

1. Run `/pdf <path-to-md-file>` (which uses the PDF skill pipeline: strip frontmatter → render Mermaid → convert to HTML → Chrome headless PDF)
2. The PDF skill already saves to the correct reports directory
3. Report which PDFs were regenerated

### Skip conditions

- If no tracked documents changed, skip PDF regeneration
- If running from the code-server container, skip (no Chrome available)

## Temp file cleanup

After all other steps, clean up any temporary files created during the session:

```bash
# Remove Claude session temp files
rm -f /tmp/claude-*.html /tmp/claude-*.py /tmp/claude-*.json
rm -f /tmp/mermaid_*.mmd /tmp/mermaid_*.png
rm -f /tmp/batch_pdf.py
rm -f /tmp/project-showcase-mockups.html
rm -f /tmp/*.html  # HTML intermediates from PDF pipeline
```

Only delete files that match known Claude session patterns — do NOT `rm -rf /tmp/*`.

Report how many temp files were cleaned up.

## Report

After processing all repos, report:
- Which repos had changes and were committed
- Which repos were skipped (no changes)
- Commit hash, message, and files changed for each committed repo
- **Agent config sync:** rules/directives synced between vault and global configs (or "no changes")
- **Task audit results:** new tickets created, tickets updated, total open items by project
- **Master project files updated:** which project master files were updated with this session's work
- **PDFs regenerated:** which reports were updated (or "none" if no tracked docs changed)
- **Temp files cleaned:** count of files removed from /tmp

## After Checkpoint: Auto-Resume

**CRITICAL**: After completing the checkpoint report, **immediately resume the work that was interrupted**. The checkpoint is a save point, not a stopping point.

If there is an active TodoWrite list with pending tasks:
1. Check which task was `in_progress` before the checkpoint
2. Resume that task without asking permission
3. If no task was in_progress, start the next `pending` task

If you were in the middle of implementing a feature:
1. Continue from where you left off
2. Reference the last commit message to understand context
3. Pick up the next logical step

**Do NOT**:
- Wait for user confirmation to continue
- Ask "should I continue?"
- Stop after reporting the checkpoint
- Require the user to tell you to resume

The checkpoint should be invisible to the user's workflow — save, report briefly, continue working.

## Notes
- **First step**: run `ls /config/workspace 2>/dev/null` to detect if you're in the container. Use the matching path column from the table above.
- On Mac, always use the full absolute path for the vault repo — the path contains spaces
- The vault repo only tracks `Projects/` — the rest is gitignored; iCloud is the source of truth for everything else
- charlieseay.com repo: https://github.com/charlieseay/charlieseay.com (private)
- SeaynicNet vault repo: https://github.com/charlieseay/seaynicnet (private)
- Enchapter repo: https://github.com/charlieseay/storychat (private) — GitHub repo name stays `storychat`; rename via GitHub settings when ready
- Hone repo: https://github.com/charlieseay/hone (private)
- Enchapter Site repo: https://github.com/charlieseay/enchapter-site (private)
- Enchapter API repo: https://github.com/charlieseay/enchapter-api (private)
- Claude Config repo: https://github.com/charlieseay/claude-config (private)
- REACT Pro repo: https://github.com/charlieseay/reactpro (private)
- E2E Tests repo: https://github.com/charlieseay/e2e-tests (private)
- JobAid repo: https://github.com/charlieseay/jobaid (private)
- Claude Context repo: https://github.com/charlieseay/claude-context (private)
- Stripe MCP repo: https://github.com/charlieseay/stripe-mcp (private)
- Command Center repo: https://github.com/charlieseay/command-center (private)
- The Bridge repo: https://github.com/charlieseay/bridge (private)
- Content Studio repo: https://github.com/charlieseay/content-studio (private)
- Seaynic Labs Store repo: https://github.com/charlieseay/seayniclabs-store (private)
- Bearing repo: https://github.com/charlieseay/bearing (private)
- Reckoner repo: https://github.com/charlieseay/reckoner (private)
- Prompt Library repo: https://github.com/charlieseay/prompt-library (private)
- Enchapter Kokoro repo: https://github.com/charlieseay/enchapter-kokoro (private)
- QA Runner repo: https://github.com/charlieseay/qa-runner (private)
- QA Hands repo: https://github.com/charlieseay/qa-hands (private)
- Ledger repo: https://github.com/charlieseay/ledger (private)
- Sonique iOS repo: https://github.com/charlieseay/sonique-ios (public)
- Sonique Mac repo: https://github.com/charlieseay/sonique-mac (private)
- CAAL repo: https://github.com/charlieseay/cael (private — fork of CoreWorxLab/CAAL)
- TC Platform Build 0 repo: https://github.com/seayniclabs/tc-platform-build0 (private)
- TC Platform Onboarding repo: https://github.com/seayniclabs/tc-platform-onboarding (private)
- TC Platform Control repo: https://github.com/seayniclabs/tc-platform-control (private)
- Centaur Tools repo: https://github.com/seayniclabs/centaur-tools (private)
- Jackel repo: https://github.com/seayniclabs/jackel (private)
- Weft Playwright repo: https://github.com/seayniclabs/weft-playwright (private)
- StdOut repo: https://github.com/seayniclabs/stdout (public)
- StdOut Site repo: https://github.com/seayniclabs/stdout-site (public)
- StdOut Satellite repo: https://github.com/seayniclabs/stdout-satellite (private)
- nvidia-agent-svc repo: https://github.com/charlieseay/nvidia-agent-svc (private)
- aider-svc repo: https://github.com/charlieseay/aider-svc (private)
- seaynic-support-inbound repo: https://github.com/seayniclabs/seaynic-support-inbound (private)
- seaynic-support-lib repo: https://github.com/seayniclabs/seaynic-support-lib (private)
- support-responder-svc repo: https://github.com/seayniclabs/support-responder-svc (private)
- b3ck-agents repo: https://github.com/charlieseay/b3ck-agents (private) — versioned 2026-08-18; previously ran in production with no repo
- helmsman-db repo: https://github.com/charlieseay/helmsman-db (private)
- talos repo: https://github.com/charlieseay/talos (private)

## Lessons

- **2026-06-15** — `drill_passed_clean__commit_8b7814b__3_ru`: Drill passed clean. Commit 8b7814b. 3 runbooks created. n8n create-export-delete-restore-verify cycle passed. 122 baseline preserved. [src: task-1000561]
- **2026-06-15** — `18_guides_rewritten__commit_f3fab80__pus`: 18 guides rewritten, commit f3fab80, pushed to main. All first body lines now follow voice rules — concrete, topic-specific, zero Most/Many/question openers. [src: task-1000625]
- **2026-06-15** — `work_already_complete___commit_3b197f3_r`: Work already complete — commit 3b197f3 raised timeout 420→1800s (2026-05-26 05:52:48) [src: task-1000598]
- **2026-06-15** — `task_completed__cve_fix__gitpython_in_st`: Task completed: CVE fix: gitpython in stripe-mcp (CVE-2026-42215 (+CVE-2026-42215, CVE-2026-42284, CVE-2026-44244, GHSA-mv93-w799-cj2w) HIGH) [src: task-1000722]
