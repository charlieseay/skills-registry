# LightRAG — Knowledge Graph Extraction for RAG

**Category:** knowledge-base  
**Priority:** RESEARCH  
**Created:** 2026-08-20  
**Confidence triggers:** knowledge graph, RAG, LightRAG, entity extraction, graph database

**Source:** [HKUDS/LightRAG](https://github.com/hkuds/lightrag) — 10K stars, EMNLP 2025

## What It Does

Extracts knowledge graph from documents + combines with vector search for **hybrid retrieval**.

## Integration with open-notebook

```bash
pip install lightrag

# Our current: Vector-only
kb search "task queue deduplication" -n projects

# With LightRAG: Vector + Graph
# 1. Extract entities/relationships from vault notes
# 2. Build knowledge graph (lessons → agents → tasks)
# 3. Query: semantic search + graph traversal
```

## Setup

```python
from lightrag import LightRAG

# Initialize with documents
rag = LightRAG(
    working_dir="./kb_graph",
    llm_model="gpt-4o-mini"  # Or local model
)

# Index vault notes
rag.insert("content from Projects/")

# Query with graph context
result = rag.query(
    "How do we prevent duplicate tasks?",
    mode="hybrid"  # Vector + graph traversal
)
```

## Value Proposition

**Current (open-notebook):** Vector search → ranked passages  
**With LightRAG:** Vector search + entity linking → related concepts across domains

**Example:**
- Query: "duplicate tasks"
- Vector: Returns task-deduplication lessons
- Graph: Also surfaces bosun-proactive-audit (creates dupes) + helmsman-db (stores tasks)

**Gap closed:** Cross-domain knowledge synthesis

**Phase:** 2 (when we commit to agent memory evolution)
