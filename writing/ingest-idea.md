---
name: ingest-idea
category: writing
description: Capture and structure new ideas into vault
triggers:
  patterns:
  - capture idea
  - new idea
  - ingest idea
  - save thought
  contexts:
  - ideation
  - knowledge capture
  - note-taking
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when capture and structure new ideas into vault
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 5
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

# Ingest Idea

Ingest a video or idea URL, fetch its transcript, run a full feasibility assessment, match to active projects, and create a task if buildable.

**Input:** `$ARGUMENTS` — a YouTube URL, or a topic/idea description if no URL

---

## Steps

### 1. Determine input type

- If `$ARGUMENTS` is a YouTube or video URL → transcript path
- If `$ARGUMENTS` is a text idea description (no URL) → skip transcript, go directly to assessment
- If `$ARGUMENTS` is empty → tell the user: "Provide a YouTube URL or idea description. Example: /ingest-idea https://youtu.be/abc123"

### 2. Fetch transcript (URL path only)

POST to the Video Idea Assessment Pipeline webhook:

```bash
curl -s -X POST http://localhost:5680/webhook/ingest-idea \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$ARGUMENTS\"}"
```

If the webhook returns a success response, report: "Helmsman is running the full assessment — result will appear in #helm within 90 seconds."

Then stop — the n8n pipeline handles the rest for the webhook path.

### 3. Direct assessment (text idea OR when Charlie says "you do it" / "full assessment")

When Charlie explicitly asks Claude or Helmsman to assess the idea (not just send to #helm), do the full assessment inline:

**3a. If URL provided, fetch transcript via Apify:**

```bash
APIFY_KEY=$(cat /Volumes/data/secrets/apify_api_key 2>/dev/null || echo "")
curl -s -X POST \
  "https://api.apify.com/v2/acts/streamers~youtube-transcript-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"videoUrl\": \"$ARGUMENTS\"}"
```

Join the `.text` fields from the returned segments into a single transcript string.

**3b. Fetch active projects from helmsman-db:**

```bash
curl -s "http://localhost:5682/projects" | python3 -c "
import json, sys
ps = json.load(sys.stdin)
active = [p.get('project', p.get('name','')) for p in ps if p.get('status') in ('live','active','active-dev','planned')]
print(', '.join(active[:20]))
"
```

**3c. Run assessment using Claude's own reasoning:**

With the transcript (or idea text) and the active project list in hand, perform this analysis:

1. **Idea summary** — 2-3 sentences: problem solved, who it's for, what's unique
2. **Feasibility** — high / medium / low, with one-sentence reason
3. **Build effort** — days / weeks / months, with one-sentence scope explanation
4. **Related projects** — which active Seaynic Labs projects this idea relates to, and how
5. **Recommended action** — build / investigate / bookmark / skip, with reason
6. **Task title** — if build or investigate: a 60-character task title

**3d. If recommended_action is "build" or "investigate", create a task:**

```bash
curl -s -X POST "http://localhost:5682/tasks" \
  -H "Content-Type: application/json" \
  -d "{
    \"task\": \"<task_title>\",
    \"owner\": \"CLAUDE\",
    \"project\": \"<first_related_project_or_Lab>\",
    \"effort\": \"<task_effort>\",
    \"brief_text\": \"## Goal\\nEvaluate and scope this idea for potential build.\\n\\n## Context\\nIdea: <idea_summary>\\n\\nFeasibility: <feasibility> — <feasibility_reason>\\n\\nBuild effort: <build_effort>\\n\\n## Steps\\n1. Research existing tools in this space\\n2. Define MVP scope\\n3. Estimate build time and dependencies\\n4. Write a one-page tech spec if viable\\n\\n## Research Questions\\nwhich curl\\n\\n## Verification\\n\`\`\`bash\\ncurl -s http://localhost:5682/tasks?owner=CLAUDE | python3 -m json.tool\\n\`\`\`\\n\\n## Success\\nTech spec written or decision documented: build vs skip.\\n\\n## Scope Boundary\\nDo not build. Assessment only.\"
  }"
```

### 4. Report findings

Present a structured assessment report:

```
## Idea Assessment

**Source:** <URL or "direct description">
**Idea:** <idea_summary>

**Feasibility:** <high|medium|low> — <reason>
**Build effort:** <days|weeks|months> — <reason>
**Action:** <build|investigate|bookmark|skip> — <reason>

**Related projects:** <list or "none">
**Project connection:** <how it relates, or "no direct match">

<if task created>
**Task created:** #<num> — <task_title> [<project>/<effort>]
<else>
**No task created** — <action> recommendation
```

---

## Routing note

- **"Send to Helm" / URL only** → use the webhook path (Step 2) — Helmsman handles it
- **"Full assessment" / "you assess it" / "what do you think"** → use the inline path (Step 3)
- **Both can run** — the webhook path also posts to #helm, so the team sees it either way
