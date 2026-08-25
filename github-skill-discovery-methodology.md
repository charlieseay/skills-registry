# GitHub Skill Discovery — Autonomous Methodology

**Category:** automation  
**Priority:** CRITICAL  
**Created:** 2026-08-20  
**For:** capability-gap-analyzer, competitive-skill-analyzer  
**Confidence triggers:** skill discovery, GitHub research, capability gaps, autonomous learning

---

## Purpose

This skill documents the methodology used in the 2026-08-20 manual skill discovery session so that `capability-gap-analyzer.py` and `competitive-skill-analyzer` can replicate it autonomously.

---

## The 5-Phase Process

### Phase 1: Internal Gap Analysis

**What:** Query knowledge bases to identify operational pain points

**How:**
```bash
# Query diagnostics KB for recurring issues
kb search "recurring issues repeated failures manual intervention" -n diagnostics -l 15

# Query runbooks KB for automation opportunities
kb search "automation gaps manual procedures operational toil" -n runbooks -l 15

# Query lessons KB for repeated patterns
kb search "lessons duplicate issues" -n lessons -l 15

# Query tools KB for capability gaps
kb search "limitations missing capabilities tool gaps" -n tools -l 15
```

**Output:** List of specific operational gaps with lesson IDs + frequency

**Example findings (2026-08-20):**
- 20+ duplicate task spawn lessons → task deduplication gap
- Sonique connector crashes → circuit breaker gap
- Bridge OOM kills → Docker health monitoring gap
- Stale container deployments → deployment verification gap

---

### Phase 2: GitHub Research (8 Domains)

**What:** Search GitHub for proven solutions to identified gaps

**Domains to research:**

1. **Docker & Container Management**
   - Search: "Docker health monitoring container restart OOM prevention production"
   - Target: >1K stars, active 2025-2026

2. **Task Queue & Orchestration**
   - Search: "task queue worker orchestration PostgreSQL retry patterns deduplication"
   - Look for: SKIP LOCKED patterns, deduplication strategies

3. **Agent Memory & Learning**
   - Search: "agent memory autonomous learning RAG lesson extraction LLM"
   - Filter: Research papers WITH code repos

4. **Security & Compliance**
   - Search: "automated security scanning secret detection OWASP compliance"
   - Essential: pre-push hooks, CI/CD integration

5. **Deployment Automation**
   - Search: "deployment automation health check zero downtime rollback"
   - Must have: health-gated deployments, auto-rollback

6. **Network Discovery**
   - Search: "network discovery service topology ARP nmap passive"
   - Prefer: Fast discovery methods

7. **Error Handling & Resilience**
   - Search: "circuit breaker retry resilience patterns Python TypeScript"
   - Need: Unified decorator/wrapper approaches

8. **Knowledge Base & RAG**
   - Search: "vector search knowledge graph semantic retrieval embedding"
   - Look for: Hybrid vector + graph approaches

**Search methodology:**
```bash
# Use WebSearch or AGY web_lookup
agy web_lookup "GitHub Docker health monitoring container restart OOM 2025 2026"

# Filter results:
# - GitHub repos only (github.com domain)
# - >1K stars preferred
# - Active maintenance (commits in last 6 months)
# - Production-ready (has releases, good docs)
```

---

### Phase 3: Gap Mapping & Prioritization

**What:** Map GitHub findings to internal gaps, prioritize by ROI

**Mapping template:**
```markdown
| Internal Gap | GitHub Solution | ROI | Effort |
|--------------|----------------|-----|--------|
| 20+ duplicate spawns | postgress_queue dedup | 10/10 | M |
| API failures | pyresilience | 9/10 | S |
| OOM kills | docker-autoheal | 8/10 | S |
```

**ROI calculation:**
- **High (9-10/10):** Solves 10+ documented lessons, affects multiple projects
- **Medium (6-8/10):** Solves 3-10 lessons, affects 1-2 projects
- **Low (3-5/10):** Nice-to-have, no documented lessons yet

**Effort estimation:**
- **S (Small):** < 1 day, add to existing config, minimal refactoring
- **M (Medium):** 1-3 days, schema changes, moderate refactoring
- **L (Large):** 1-2 weeks, new infrastructure, complex integration

**Priority formula:** `Priority = ROI / Effort`

---

### Phase 4: Skill Registration

**What:** Create skill files in `/Volumes/data/skills/`

**Skill file template:**
```markdown
# [Tool Name] — [One-Line Description]

**Category:** [infrastructure|security|task-queue|agent-learning|network|deployment]  
**Priority:** [CRITICAL|HIGH|MEDIUM|LOW|RESEARCH]  
**Created:** YYYY-MM-DD  
**Language:** [Python|Node.js|TypeScript|Shell|Language-agnostic]  
**Confidence triggers:** keyword1, keyword2, keyword3, use-case-phrases

**Source:** [GitHub URL] — [stars]K stars

## When to Use

Use this skill when:
- [Specific use case 1]
- [Specific use case 2]
- [Working on project X, feature Y]

**Anti-patterns this skill prevents:**
- [Lesson reference with ID]
- [Known gap from diagnostics KB]

---

## Quick Start

```bash
# Installation
[install command]
```

```[language]
# Minimal working example
[code snippet]
```

## Key Features

- **Feature 1** — What it does
- **Feature 2** — Why it matters
- **Feature 3** — How it helps

## Integration Pattern

[Language]-specific implementation for our stack:

```[language]
# Real integration example for our codebase
[code that fits our patterns]
```

**Complements:** `other-skill.md` (relationship)  
**Use case:** Specific service/project names

## References

- [Source repo](URL)
- [Alternative implementation](URL)
- [Lesson that triggered this](Projects/X/Lessons/Y.md)

---

**Last Updated:** YYYY-MM-DD  
**Confidence score:** 0.XX for "trigger phrase", "another phrase"
```

**Confidence triggers guidelines:**
- Include exact problem phrases from lessons
- Include tool/framework names
- Include use case descriptions
- Include project names where applicable
- Aim for 5-10 trigger phrases per skill

**File naming:**
- Use kebab-case: `tool-name-purpose.md`
- Be specific: `pg-boss-nodejs.md` not `job-queue.md`
- Include language when language-specific

---

### Phase 5: Validation & Documentation

**What:** Test discovery, document findings, measure impact

**Auto-discovery test:**
```bash
# Test that skills are discoverable
kb search "prevent duplicate tasks" -n skills -l 5
# Expected: task-deduplication.md with ≥0.7 confidence

kb search "API retry logic" -n skills -l 5
# Expected: circuit-breaker-resilience.md with ≥0.7 confidence
```

**If confidence < 0.7:** Enrich skill frontmatter with more trigger keywords

**Documentation outputs:**
1. **Gap analysis report** — Full research with 50+ repos, gap mapping, ROI
2. **Skills registered summary** — What was added, auto-discovery guide
3. **Decision log** — What wasn't registered and why

**Metrics to track:**
- Total repos analyzed
- Skills registered
- Coverage % of identified gaps
- Expected impact (% reduction in recurring issues)

---

## Autonomous Execution Guide

### For capability-gap-analyzer.py

**Current function:** Detect capability gaps from agent task outcomes

**New function:** Also search GitHub for solutions to detected gaps

**Integration:**
```python
def analyze_gaps():
    # Existing: Detect gaps from agent metrics
    gaps = detect_capability_gaps()
    
    # NEW: For each gap, search GitHub
    for gap in gaps:
        # Phase 1: Query KB for context
        context = query_kb(f"lessons {gap['issue_type']}")
        
        # Phase 2: GitHub research
        solutions = github_research(gap['issue_type'], context)
        
        # Phase 3: Prioritize by ROI
        ranked = prioritize_solutions(solutions, gap)
        
        # Phase 4: Register top solution as skill
        if ranked and ranked[0]['roi'] >= 7:
            register_skill(ranked[0], gap)
        
        # Phase 5: Create improvement task
        create_improvement_task(gap, ranked[0] if ranked else None)
```

**GitHub research function:**
```python
def github_research(issue_type: str, context: dict) -> list:
    """Search GitHub for solutions to issue_type"""
    # Use AGY or WebSearch
    query = f"GitHub {issue_type} solution production 2025 2026"
    results = web_lookup(query)
    
    # Filter: >1K stars, active, has code
    filtered = [r for r in results 
                if 'github.com' in r['url'] 
                and r.get('stars', 0) > 1000]
    
    return filtered[:10]  # Top 10 results
```

---

## Decision Matrix: Register vs Skip

### ✅ REGISTER when:
- **High ROI** (solves 3+ documented lessons)
- **Production-ready** (>1K stars, active maintenance, releases)
- **Implementation-ready** (has code, not just research papers)
- **Language match** (Python/Node.js/TypeScript for our stack)
- **Complementary** (fills a gap, not redundant with existing skills)

### ⚠️ CONDITIONAL when:
- **Alternative implementation** (register best one per language)
- **Research-level** (register summary skill, defer full implementation)
- **Niche use case** (check if any project actually needs it)

### ❌ SKIP when:
- **No code** (academic papers without implementations)
- **Wrong stack** (K8s when we're Docker Compose)
- **Redundant** (same pattern as existing skill)
- **Unmaintained** (no commits in 2+ years)
- **Too generic** (can't map to specific gap)

---

## Example: Full Workflow (2026-08-20 Session)

### Phase 1: Gap Analysis
```bash
kb search "duplicate tasks" -n diagnostics -l 10
# Found: 20+ lessons on duplicate task spawns
```

### Phase 2: GitHub Research
```bash
web_lookup "GitHub PostgreSQL task queue deduplication 2025"
# Found: postgress_queue (dedup_key pattern)
```

### Phase 3: Gap Mapping
```markdown
| Gap | Solution | ROI | Effort |
|-----|----------|-----|--------|
| 20+ duplicate spawns | postgress_queue | 10/10 | M |
```

### Phase 4: Skill Registration
```bash
# Created: /Volumes/data/skills/task-deduplication.md
# - 9KB comprehensive guide
# - SQL pattern + integration examples
# - Confidence triggers: "task queue", "duplicate tasks", "PostgreSQL"
```

### Phase 5: Validation
```bash
kb search "prevent duplicate tasks" -n skills -l 5
# Result: task-deduplication.md (0.95 confidence) ✅
```

---

## Success Criteria

After autonomous execution:

✅ Phase 1 complete → List of 5+ capability gaps with lesson references  
✅ Phase 2 complete → 10+ GitHub repos per gap domain  
✅ Phase 3 complete → Ranked list by ROI/effort  
✅ Phase 4 complete → Top 3-5 solutions registered as skills  
✅ Phase 5 complete → All skills test at ≥0.7 confidence  
✅ Documentation → Gap report + decision log generated  
✅ Tasks created → Improvement tasks for high-ROI patterns  

---

## Integration with Existing Agents

### capability-gap-analyzer (weekly)
**Add:** GitHub research step after gap detection  
**Output:** Skills registered + improvement tasks created

### competitive-skill-analyzer (daily)
**Add:** Proactive GitHub monitoring for new repos in our domains  
**Output:** Skills registered when new high-value tools emerge

### Workflow:
```
Weekly: capability-gap-analyzer
  → Detect gaps from agent outcomes
  → Search GitHub for solutions
  → Register top skills
  → Create improvement tasks

Daily: competitive-skill-analyzer
  → Monitor GitHub trending in our domains
  → Compare new tools to existing skills
  → Register if ROI > current solution
```

---

## Maintenance

**Skill updates:**
- Re-run GitHub research quarterly
- Update skills when better alternatives emerge
- Archive skills when tools are deprecated

**Confidence tuning:**
- Monitor skill invocation rates via compliance logs
- Add trigger keywords if invocation rate < 50%
- Refine examples if agents misuse skills

**Gap closure tracking:**
- Measure lesson recurrence rate post-skill-registration
- Expected: 80% reduction in recurring issues within 30 days
- If <50% reduction → investigate skill adoption or pattern effectiveness

---

## This Skill's Own Triggers

**Confidence triggers:** GitHub skill discovery, autonomous learning, capability gap analysis, competitive analysis, skill registration, research methodology

**Use when:**
- Building/updating capability-gap-analyzer
- Building/updating competitive-skill-analyzer
- Manual skill discovery session (like 2026-08-20)
- Training new autonomous agents
- Documenting research methodology

---

**Last Updated:** 2026-08-20  
**Confidence score:** 0.95 for "GitHub research", "skill discovery", "capability gaps"
