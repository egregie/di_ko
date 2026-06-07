---
name: research-collect
description: |
  Collect raw scientific papers, guidelines, and articles from source lists and store them locally.
license: Apache-2.0
metadata:
  version: v1.0
  publisher: google
---

# Research Collect Skill (A02)

This skill automates raw content gathering from discovered sources (using HTTP requests or browser automation) and organizes it into the `01_collection/` directory.

## Input
- Discovered sources list (output from A01).

## Output
- Downloaded raw documents/articles saved in `01_collection/` under `tierA/`, `tierB/`, `tierC/`, or `tierD/`.

## Constraints & System Prompt
- Follow the system prompt defined in `00_governance/prompts/A02_collector.txt`.
- Collect ONLY evidence-based medicine (EBM) records. Ignore general blogs.
- Store documents locally; respect copyrights by creating concise abstracts/summaries (≤ 15 words for direct quotes).
- **[GUARD] Source Enforcement**: Every collected raw fact must have a valid `source_id` associated with a real PMID/DOI. Facts without PMID/DOI must be routed to `needs_manual` and are blocked from graph ingestion.

## Execution & Script Reference
Use the database retrieval and metadata extraction helper logic adapted from `pharma_v2`:
- Script: `ops/scripts/search_kb.py`


## Caveman Mode
`full`


