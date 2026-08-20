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
2. Invokes MCP `brainstorm` tool
3. MCP server triggers n8n workflow
4. n8n routes idea to all 7 agents in parallel (30-60 seconds)
5. Synthesizer combines outputs
6. Full report returned to you
7. Session stored in Open-Notebook for reference

## Single Agent Mode

To get just one perspective:

```
What would the Financial Strategist think about <idea>?
What's the UX Advocate's take on <idea>?
```

(Claude will auto-invoke `brainstorm_single` tool)

## Requirements

- ✅ MCP server configured (automatic)
- ⏳ n8n workflow imported (manual step)
- ✅ nvidia-agent-svc running
- ✅ Ollama running on ThinkPad

## Implementation

The skill does the following:

1. **Parse arguments:**
   - Extract idea from user input
   - Extract optional `--context` flag

2. **Invoke MCP tool:**
   ```python
   # MCP brainstorm tool auto-invoked when skill is run
   # Tool makes HTTP POST to: http://localhost:5680/webhook/brainstorm
   ```

3. **Format response:**
   - Present synthesis in readable format
   - Include session ID
   - Link to full report in Open-Notebook (when available)

4. **Error handling:**
   - If n8n workflow not found → Show helpful setup message
   - If timeout → Explain workflow is still processing
   - If partial agent failure → Show available perspectives

## Status

- ✅ Skill created
- ✅ MCP server deployed
- ⏳ n8n workflow (ready for import)
- ⏳ Open-Notebook integration (future)

## Notes

- First run may take 60-90 seconds (cold start + 7 agents)
- Subsequent runs faster (~30-45 seconds)
- All sessions stored for future reference
- Can search past sessions (future feature)

---

**Ready to use!** Just run `/brainstorm <your idea>` and wait for the multi-agent analysis.
