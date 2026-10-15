---
name: brainstorm
category: research
description: "Structured brainstorming session with idea generation Modes: office-hours (six forcing questions before building anything)."
triggers:
  patterns:
  - brainstorm
  - ideate
  - generate ideas
  - creative session
  contexts:
  - ideation
  - planning
  - creativity
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when structured brainstorming session with idea generation
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 30
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

# Brainstorm — Multi-Agent Idea Analysis

Run an idea through 7 specialized AI agent personas for comprehensive, multi-perspective analysis.

## Usage

```
/brainstorm <idea>
/brainstorm <idea> --context "<additional context>"
```

## Examples

```
/brainstorm Build a voice-first task manager for ADHD users

/brainstorm "AI-powered personal finance coach" --context "Privacy-first, local-only data, subscription model"

/brainstorm Create a mobile app for tracking daily water intake
```

## What You Get

A comprehensive report combining perspectives from:

1. **The Visionary** — Creative, blue-sky possibilities
2. **The Practical Implementer** — Feasibility and execution plan
3. **The Skeptical Reviewer** — Risks and failure modes
4. **The UX Advocate** — User experience and accessibility
5. **The Financial Strategist** — ROI and cost structure
6. **The Red Teamer** — Strategic blindspots
7. **The Synthesizer** — Consolidated insights and recommendations

## Output Format

- **Executive Summary** — Quick verdict
- **Key Insights** — Top findings from each perspective
- **Synthesis & Tensions** — Where agents agree/diverge
- **Actionable Recommendations** — What to do next
- **Decision Framework** — Green/yellow/red lights

## How It Works

1. Skill parses your idea and optional context
2. POSTs to `brainstorm-agents-svc` at `http://localhost:5912/brainstorm`
3. The service runs 6 personas concurrently, then the Synthesizer
4. Full report returned to you
5. Session stored in Open-Notebook for reference

**Direct call** (the reliable path — no MCP round-trip):

```bash
curl -s -X POST http://localhost:5912/brainstorm \
  -H 'Content-Type: application/json' \
  -d '{"idea":"<the idea>","context":"<constraints, options, what you need decided>"}' \
  --max-time 900 -o /tmp/bs.json
```

Budget up to 15 minutes. The 70B personas are the slow ones.

Check it is up first: `curl -s localhost:5912/health`

## Architecture — NOT n8n (changed 2026)

This suite used to be described as an n8n workflow at
`localhost:5680/webhook/brainstorm`. **That path is dead** and the workflow was
never imported. Per `brainstorm-agents-svc/README.md`, it moved to its own
service because:

- n8n executes parallel branches **serially** — 6 agents took ~275s summed
- Bedrock needs SigV4 signing, impractical inside an n8n Code node
- `bedrock-claude-worker` (:5900) is single-flight and 503s on concurrent calls —
  it is Helmsman's task runner, not a general LLM proxy
- Ollama on shared hardware serializes heavy 14B calls (~400s under 6-way load)

Curling the old webhook returns HTTP 000. That is a stale doc, not a broken
capability — **probe :5912 before concluding the suite is down.**

## Provider routing

| Persona | Provider | Model |
|---|---|---|
| Visionary, Red Team | NVIDIA NIM | `meta/llama-3.1-70b-instruct` |
| Practical, Skeptical | NVIDIA NIM | `meta/llama-3.1-8b-instruct` |
| UX Advocate, Financial, Synthesizer | Bedrock | `us.anthropic.claude-haiku-4-5-...` |

Routing lives in `ROUTE` in `server.py`. Persona prompts/temperature/max_tokens
are read live from `Agents/Brainstorming/*.json` — editing a persona takes
effect on the next request, no restart.

## Single Agent Mode

To get just one perspective:

```
What would the Financial Strategist think about <idea>?
What's the UX Advocate's take on <idea>?
```

(Claude will auto-invoke `brainstorm_single` tool)

## Requirements

- ✅ `brainstorm-agents-svc` running on :5912 (launchd: `com.seayniclabs.brainstorm-agents-svc`)
- ✅ NVIDIA NIM key present (`/health` reports `nvidia_key: true`)
- ✅ Bedrock credentials for the Haiku personas

Restart it with:
```bash
launchctl load ~/Library/LaunchAgents/com.seayniclabs.brainstorm-agents-svc.plist
tail -f /tmp/brainstorm-svc.log
```

## Implementation

1. **Parse arguments** — extract the idea and optional `--context`
2. **POST to :5912/brainstorm** with `{idea, context?, session_id?}`
3. **Format the response** — lead with the synthesis, then the persona sections
4. **Error handling:**
   - Connection refused → the service is down; check launchctl and the log
   - Timeout → raise `--max-time`; 70B personas are slow under load
   - Partial failure → the response still carries the personas that answered;
     report which ones are missing rather than presenting a partial panel as complete

## Writing up the results

Give each persona its own voice. The value is in **disagreement between
perspectives** — where the Visionary and the Red Teamer conflict is the finding.
Collapsing seven views into one consensus paragraph throws away what you paid
for. Say which persona said what.

## Status

- ✅ Skill live
- ✅ brainstorm-agents-svc deployed (:5912), 7 personas loaded
- ✅ Sessions stored in the `brainstorming` open-notebook notebook
- ❌ n8n path retired — see Architecture above

## Notes

- First run may take 60-90 seconds (cold start + 7 agents)
- Subsequent runs faster (~30-45 seconds)
- All sessions stored for future reference
- Can search past sessions (future feature)

---

**Ready to use!** Just run `/brainstorm <your idea>` and wait for the multi-agent analysis.



## Mode: office-hours

YC office hours: six forcing questions before building anything.
Full procedure: `/Volumes/data/skills/_reference/brainstorm/office-hours.md`. Read it before running this mode.
