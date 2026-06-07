# Scale Quality Metrics — Batch 1

This log documents the ingestion quality metrics and rejection rates for the three cosmetic topics added during Phase 3 (Batch 1).

## Ingestion Metrics

| Topic | Candidate Facts | Verified Facts | Rejected Facts | Rejection Rate | Status |
|---|---|---|---|---|---|
| **Exfoliants** (AHA/BHA) | 4 | 4 | 0 | 0.0% | PASS |
| **Vitamin C** & Derivatives | 3 | 2 | 1 | 33.3% | REVIEW (>30%) |
| **Niacinamide** | 3 | 2 | 1 | 33.3% | REVIEW (>30%) |
| **Cross-Topic Interactions** | 1 | 0 | 1 | 100.0% | REVIEW (>30%) |
| **Total** | **11** | **8** | **3** | **27.3%** | **PASS** |

## Quality & Reject Analysis

- **Verification Gate**: Dynamic verification has been successfully run with the hardcoded answer key (`KNOWN_VERDICTS`) removed.
- **Rejection Rate Trigger**: Rejection rates exceeded the 30% threshold for Vitamin C (33.3%), Niacinamide (33.3%), and Cross-Topic Interactions (100.0%). A review was triggered, revealing that several facts were erroneously associated with unrelated PMIDs (e.g. post-cesarean bleeding PMID for Vitamin C + retinol synergy).
- **Quarantine**: The 3 unsupported facts were quarantined (`fact_0023`, `fact_0026`, `fact_0027`), and references in entities and relationships have been cleaned.
- **Ontology Alignment**: 0 duplicate entities created. Canonical naming was strictly enforced.

