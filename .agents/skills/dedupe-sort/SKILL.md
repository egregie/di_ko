---
name: dedupe-sort
description: |
  Deduplicate and sort extracted claims, keeping the highest evidence-level details.
license: Apache-2.0
metadata:
  version: v1.0
  publisher: google
---

# Deduplicate & Sort Skill (A04)

This skill consolidates draft fact JSON files from the processing area. It merges overlapping or identical claims and filters them based on source quality.

## Input
- Draft JSON facts in `02_processing/`.

## Output
- Deduplicated, sorted list of candidate facts in `02_processing/`.

## Logic Rules
- If multiple entries affirm the same claim, merge them.
- Retain the source with the highest tier (e.g. prioritize Tier A over Tier B).
- Keep track of contradictory evidence and store it in the `contradictions[]` array.

## Execution & Script Reference
To execute deduplication and sorting, run the automated script:
`python ops/scripts/dedupe_sort.py`

## Caveman Mode
`ultra`


