# Scale Quality Metrics — Batch 1

This log documents the ingestion quality metrics and rejection rates for the three cosmetic topics added during Phase 3 (Batch 1).

## Ingestion Metrics

| Topic | Candidate Facts | Verified Facts | Rejected Facts | Rejection Rate | Status |
|---|---|---|---|---|---|
| **Exfoliants** (AHA/BHA) | 4 | 4 | 0 | 0.0% | PASS |
| **Vitamin C** & Derivatives | 3 | 3 | 0 | 0.0% | PASS |
| **Niacinamide** | 3 | 3 | 0 | 0.0% | PASS |
| **Cross-Topic Interactions** | 1 | 1 | 0 | 0.0% | PASS |
| **Total** | **11** | **11** | **0** | **0.0%** | **PASS** |

## Quality & Reject Analysis

- **Verification Gate**: 100% of candidate facts passed through the automated verify-at-write gate keeper `verify_gate.py` with the verdict `SUPPORTED` and `evidence_ok` equal to `true`.
- **Rejection Rate Trigger**: Rejection rates for all topics are well below the critical threshold (>30%), indicating high-quality source alignment.
- **Ontology Alignment**: 0 duplicate entities created. Canonical naming was strictly enforced (e.g., L-ascorbic acid / Vitamin C aliases mapped to `vitamin_c`, and niacinamide / vitamin B3 aliases mapped to `niacinamide`).
