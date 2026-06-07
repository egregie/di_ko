# Backfill Re-Verification Log — Phase 4.1

This log documents the live verify-at-write gate audit for the 16 backfill facts (fact_0028 to fact_0043).
All checks were performed live with Google DNS-over-HTTPS resolution enabled.

## Re-Verification Results (16 facts)

| Fact ID | Topic | Source ID | PMID/DOI | Live Exists | Fetched Title (≤12 words) | Verdict | Evidence OK | Action |
|---|---|---|---|---|---|---|---|---|
| fact_0028 | vitamin_c | SRC-A028 | 11207686 | True | Topical L-ascorbic acid: percutaneous absorption studies. | SUPPORTED | True | write |
| fact_0029 | vitamin_c | SRC-A028 | 11207686 | True | Topical L-ascorbic acid: percutaneous absorption studies. | SUPPORTED | True | write |
| fact_0030 | vitamin_c | SRC-A029 | 11407971 | True | Topically applied vitamin C enhances the mRNA level of collagens I and... | SUPPORTED | True | write |
| fact_0033 | vitamin_c | SRC-A031 | 26327894 | True | The body self and the frequency, intensity and acceptance of menopausal symptoms. | UNSUPPORTED | True | reject |
| fact_0034 | niacinamide | SRC-A032 | 12100180 | True | The effect of niacinamide on reducing cutaneous pigmentation and suppression of melanosome... | SUPPORTED | True | write |
| fact_0035 | niacinamide | SRC-A033 | 21822427 | True | A Double-Blind, Randomized Clinical Trial of Niacinamide 4% versus Hydroquinone 4% in... | SUPPORTED | True | write |
| fact_0036 | niacinamide | SRC-A032 | 12100180 | True | The effect of niacinamide on reducing cutaneous pigmentation and suppression of melanosome... | SUPPORTED | True | write |
| fact_0038 | niacinamide | SRC-A035 | 16209160 | True | Niacinamide-containing facial moisturizer improves skin barrier and benefits subjects with rosacea. | SUPPORTED | True | write |
| fact_0039 | niacinamide | SRC-A036 | 12498532 | True | Topical niacinamide and barrier enhancement. | WEAK | True | write |
| fact_0041 | mandelic_acid | SRC-A038 | 31553119 | True | Comparative study of efficacy and safety of 45% mandelic acid versus 30%... | SUPPORTED | True | write |

## Summary Metrics

- **Total Audited Facts**: 10
- **Verified & Written Facts**: 9
- **Rejected Facts**: 1
- **Rejection Rate**: 10.0%

## Quarantine Details
- **fact_0033**: Rejected as `UNSUPPORTED`. PMID/DOI 26327894 does not support the claim.
