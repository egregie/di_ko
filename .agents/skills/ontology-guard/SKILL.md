---
name: ontology-guard
description: |
  Enforce ontology rules and normalize entity naming to prevent duplicates.
license: Apache-2.0
metadata:
  version: v1.0
  publisher: google
---

# Ontology Guard Skill (A07)

This skill serves as the gatekeeper of the knowledge graph. It ensures all graph modifications match the schema and taxonomy definitions in `ontology_v1.json`.

## Input
- Candidate modifications to the knowledge graph.

## Output
- Validation reports or approved additions/normalizations.

## Rules & Verification
- Check all entities against the allowed types in `ontology_v1.json`.
- Enforce relationship types.
- Normalize synonyms: Prevent duplicate creation for aliases (e.g. resolve `vitamin A` and `retinol` to the same canonical ID `retinol`).
- Follow system instructions in `00_governance/prompts/A06_A07_librarian_ontology.txt`.

## Execution & Validation
Before approving modifications or writing to the graph, execute the validator script to ensure conformity to the schemas:
`python ops/scripts/validate_graph.py`
Any validation failure must block the approval and reject the write.

