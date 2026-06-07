---
name: source-discovery
description: |
  Discover scientific and secondary sources for a given cosmetology/dermatology topic, filtering by source tier.
license: Apache-2.0
metadata:
  version: v1.0
  publisher: google
---

# Source Discovery Skill (A01)

This skill searches and lists references for target topics within cosmetology and dermatology, classifying results into specific tiers:
- **Tier A**: Peer-reviewed (PubMed, Cochrane, NIH, FDA, EMA)
- **Tier B**: Textbooks, INCI/CosIng, manufacturer docs, Wikipedia
- **Tier C**: Professional forums, Reddit (context/trends only)
- **Tier D**: General blogs / SEO (rejected for fact sourcing)

## Input
- Cosmetology/dermatology topic or keyword (e.g., "Retinol mechanism", "AHA vs BHA").

## Output
- List of source objects matching the `source.json` schema layout.

## Procedure
1. Search databases (PubMed, clinical trials, or web search) for the topic.
2. Filter out non-EBM/unverified blog posts.
3. Group findings by Tier A, B, C, D.
4. Record URL, accessed date, PMID/DOI, and author info.

## Execution & Script Reference
Use the database search logic adapted from `pharma_v2`:
- Script: `ops/scripts/search_kb.py`

## Caveman Mode
`full`


