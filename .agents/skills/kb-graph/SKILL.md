---
name: kb-graph
description: |
  Integrate verified facts and entities into the Git-versioned JSON knowledge graph.
license: Apache-2.0
metadata:
  version: v1.0
  publisher: google
---

# Knowledge Graph Librarian Skill (A06)

This skill takes verified facts, entities, and relations, then integrates them into the canonical knowledge graph representation.

## Input
- Verified facts, sources, and entities.

## Output
- Updated files in `03_knowledge_graph/entities/`, `facts/`, and `relationships/`.
- Updated `03_knowledge_graph/graph_index.json` flat index.
- Updated `03_knowledge_graph/sources.json` registry.

## Operation Protocol
1. Map verified properties onto the existing entities or create new entity files if they don't exist.
2. Link facts to their primary entity IDs.
3. Write clean, formatted JSON files matching schemas.
4. Update `graph_index.json` to store a flat mapping of entities, facts, and relationships for fast access.

## Execution & Validation
Before writing any entities, facts, or relationships to the graph, execute the validator script to ensure conformity to the templates:
`python ops/scripts/validate_graph.py`
Any validation failure must halt the integration and reject the write.

## Caveman Mode
`ultra`


