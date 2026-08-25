# Agent Memory Patterns — Beyond RAG

**Category:** agent-learning  
**Priority:** RESEARCH  
**Created:** 2026-08-20  
**Confidence triggers:** agent memory, autonomous learning, RAG, lesson extraction, memory consolidation

**Source:** AtomMem, MAGMA, AgeMem (2026 research)

## Key Insight (2026)

> "Retrieval-augmented generation is a retrieval strategy, not a memory system. Agent memory requires admission, evolution, consolidation, forgetting, typed storage, and context-aware retrieval, while RAG addresses only the last item."

## Our Current Gap

✅ **Retrieval** — open-notebook (vector search)  
❌ **Admission** — No learned policy for what to remember  
❌ **Evolution** — Lessons don't auto-update agent behavior  
❌ **Consolidation** — No dedup or merging of similar lessons  
❌ **Forgetting** — No stale lesson cleanup  
❌ **Typed storage** — Flat KB, no entity graphs

## Patterns from 2026 Research

### 1. AtomMem — Learned Memory Policies

**Concept:** Decompose memory into atomic CRUD operations, learn via SFT + RL when to use them.

**Current Agent Learning System:** Rule-based (skill_updater.py)  
**Evolution path:** RL-learned admission policies

### 2. MAGMA — Multi-Graph Memory

**Concept:** Typed memory storage with graph relationships.

**Current:** File-based lessons  
**Evolution path:** Graph DB with entity linking (lessons → agents → tasks)

### 3. AgeMem/MemGPT — Tool-Based Memory

**Concept:** Expose memory ops as tools, model learns when to invoke.

**Integration:** Already have tool infrastructure, just need memory tools

## Action Items for Phase 2

1. Research LightRAG integration for knowledge graph layer
2. Prototype learned admission policy (what lessons to keep)
3. Add deduplication layer (merge similar lessons)
4. Build entity graph (cross-reference lessons/agents/tasks)

**References:**
- [VoltAgent/awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers)
- [tfatykhov/awesome-agent-memory](https://github.com/tfatykhov/awesome-agent-memory)
