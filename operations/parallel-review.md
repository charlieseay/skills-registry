---
description: Multi-agent code review with confidence scoring
---

# Parallel Review

Launch 5 parallel specialist agents to review code changes from different angles, then score findings by confidence and filter to high-impact issues only.

## When to Use

- Comprehensive code review before merge
- Security audit of new feature
- Pre-deployment verification
- Finding hidden bugs across multiple dimensions

## How It Works

1. **Parallel Specialist Agents** — Launch 5 agents simultaneously:
   - **Agent 1: Security** — OWASP Top 10, injection, XSS, auth bypass, credential exposure
   - **Agent 2: Performance** — N+1 queries, missing indexes, cache opportunities, resource leaks
   - **Agent 3: Standards** — CLAUDE.md compliance, coding conventions, style guide adherence
   - **Agent 4: Historical Context** — git blame, previous bugs in this area, related PR comments
   - **Agent 5: Documentation** — code comments, README, API docs, changelog updates

2. **Confidence Scoring** — For each finding from step 1, launch a verification agent that scores 0-100:
   - **0-25:** False positive / pre-existing / would be caught by tooling
   - **25-50:** Possible issue, can't verify
   - **50-75:** Real but low impact
   - **75-100:** High impact, definitely fix

3. **Filter** — Only keep findings with confidence ≥ 80 AND impact ≥ medium

4. **Report** — Present filtered findings with evidence, file:line links, and recommendations

## Usage

```bash
# Review current branch changes
/parallel-review

# Review specific PR
/parallel-review <PR-number>

# Review specific files
/parallel-review src/auth.ts src/api.ts
```

## Output Format

Each finding includes:
- **Description** — What's wrong
- **Evidence** — File path, line numbers, code snippet
- **Confidence** — Score with reasoning
- **Impact** — critical/high/medium/low
- **Recommendation** — How to fix

## False Positive Checklist

Filters out:
- Pre-existing issues
- Issues linter/typechecker would catch
- Pedantic nitpicks
- Intentional changes
- Lines user didn't modify

## Implementation

Ask the user what to review (current diff, PR number, or specific files).

Then launch 5 parallel agents (use Sonnet or nvidia-agent) with prompts:

**Agent 1 (Security):**
> Review these changes for security vulnerabilities. Focus on: SQL injection, XSS, auth bypass, credential exposure, CSRF, insecure deserialization, XXE, path traversal. Return list of findings with file:line evidence.

**Agent 2 (Performance):**
> Review for performance issues: N+1 queries, missing database indexes, unbounded loops, memory leaks, missing cache opportunities, synchronous blocking in async code. Return findings with evidence.

**Agent 3 (Standards):**
> Review for compliance with CLAUDE.md and coding conventions. Check: naming patterns, error handling, logging, code organization, comment quality. Return findings with evidence.

**Agent 4 (Historical):**
> Run git blame on changed files. Check previous PRs that touched these files. Identify patterns: similar bugs fixed before, repeated issues, architectural decisions. Return findings with context.

**Agent 5 (Documentation):**
> Review documentation completeness: code comments for complex logic, README updates for new features, API doc updates, changelog entries. Return findings.

Once all 5 return, for each finding, launch a Haiku agent:

> Adversarially verify this finding. Try to REFUTE it. Score 0-100 based on: Is it real? Is it new? Is it important? Return score with reasoning.

Filter to findings ≥ 80, format as markdown report, present to user.

## Lessons

- **2026-06-15** — `task_completed__review_and_revise_brief`: Task completed: Review and revise brief for Task #1000457 [src: task-1000492]
- **2026-06-15** — `task_completed__review_task__1000467`: Task completed: Review task #1000467 [src: task-1000545]
- **2026-06-15** — `executor_timeout__420s____task_timed_out`: executor timeout (420s) — task timed out repeatedly, needs review [src: task-1000549]
- **2026-06-15** — `executor_timeout__420s____task_timed_out`: executor timeout (420s) — task timed out repeatedly, needs review [src: task-1000580]
- **2026-06-15** — `18_violations_found_and_written_to__tmp_`: 18 violations found and written to /tmp/hone-opener-violations.json [src: task-1000624]
- **2026-06-15** — `file_created_with_scored_table_and_top_3`: File created with scored table and top 3 revenue candidates identified. Task complete. [src: task-1000635]
- **2026-06-15** — `executor_timeout__1800s____task_timed_ou`: executor timeout (1800s) — task timed out repeatedly, needs review [src: task-1000719]
- **2026-06-15** — `task_completed__cve_fix__starlette_in_nv`: Task completed: CVE fix: starlette in nvidia-agent-svc (GHSA-86qp-5c8j-p5mr HIGH) [src: task-1000737]
- **2026-06-15** — `task_completed__review_and_revise_brief`: Task completed: Review and revise brief for classifying inactive n8n workflows (redispatch x2) [src: task-1000772]
- **2026-06-15** — `task_completed__review_and_revise_brief`: Task completed: Review and revise brief for Task #1000457 [src: task-1000492]
- **2026-06-15** — `task_completed__review_task__1000467`: Task completed: Review task #1000467 [src: task-1000545]
- **2026-06-15** — `executor_timeout__420s____task_timed_out`: executor timeout (420s) — task timed out repeatedly, needs review [src: task-1000549]
