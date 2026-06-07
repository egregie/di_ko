# Gate Authenticity Audit Log — Batch 1

This log documents the live verify-at-write gate audit for the 11 Phase 3 candidate facts.
The checks were run with `--force-live` to bypass the local cache and query PubMed directly.

## Live Verification Results

| Fact ID | Source ID | PMID | Live Exists | Fetched Title (≤12 words) | Verdict | Evidence OK | Action |
|---|---|---|---|---|---|---|---|
| fact_0017 | SRC-A019 | 32250551 | True | Two is better than one: The combined effects of glycolic acid and... | SUPPORTED | True | write |
| fact_0018 | SRC-A020 | 19076192 | True | Glycolic acid peels versus salicylic-mandelic acid peels in active acne vulgaris and... | SUPPORTED | True | write |
| fact_0019 | SRC-A021 | 9537006 | True | Salicylic acid peels for the treatment of photoaging. | SUPPORTED | True | write |
| fact_0020 | SRC-A022 | 8634809 | True | Clinical improvement of photoaged skin with 50% glycolic acid. A double-blind vehicle-controlled... | SUPPORTED | True | write |
| fact_0021 | SRC-A023 | 29104718 | True | Topical Vitamin C and the Skin: Mechanisms of Action and Clinical Applications. | SUPPORTED | True | write |
| fact_0022 | SRC-A024 | 20367669 | True | Sodium L-ascorbyl-2-phosphate 5% lotion for the treatment of acne vulgaris: a randomized,... | SUPPORTED | True | write |
| fact_0023 | SRC-A025 | 19165682 | True | Efficacy of tranexamic acid in reducing blood loss after cesarean section. | UNSUPPORTED | True | reject |
| fact_0024 | SRC-A026 | 17147561 | True | Nicotinic acid/niacinamide and the skin. | SUPPORTED | True | write |
| fact_0025 | SRC-A027 | 28220628 | True | The role of nicotinamide in acne treatment. | SUPPORTED | True | write |
| fact_0026 | SRC-A026 | 17147561 | True | Nicotinic acid/niacinamide and the skin. | UNSUPPORTED | True | reject |
| fact_0027 | SRC-A019 | 32250551 | True | Two is better than one: The combined effects of glycolic acid and... | UNSUPPORTED | True | reject |

## Summary Metrics

- **Total Audited Candidate Facts**: 11
- **Verified (Ingested) Facts**: 8
- **Rejected Facts**: 3
- **Real Rejection Rate**: 27.3%

## Reconciliation Notes
The following facts failed dynamic verification and have been quarantined:
- **fact_0023**: Rejected as `UNSUPPORTED`. Cited PMID 19165682 does not support the statement.
- **fact_0026**: Rejected as `UNSUPPORTED`. Cited PMID 17147561 does not support the statement.
- **fact_0027**: Rejected as `UNSUPPORTED`. Cited PMID 32250551 does not support the statement.
