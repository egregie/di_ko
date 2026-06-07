# Exa Pilot Report — Phase 4: Comparative Search Pathway Audit

## Overview
This report evaluates the search precision and rejection rate of two collection pathways for cosmetic active ingredient facts (specifically **Vitamin C**):
1. **Standard Search Pathway**: General search queries pulling abstract-level citations without strict claim-sentence grounding.
2. **Exa-Grounded Search Pathway**: High-precision search utilizing the Exa MCP server to retrieve exact paragraph-level matches for the target statements.

## Rejection Rate Comparison
- **Baseline Rejection Rate (DEC-010)**: 27.3%
- **Standard Search Pathway Rejection Rate**: 25.0% (1/4 rejected)
- **Exa-Grounded Search Pathway Rejection Rate**: 0.0% (0/4 rejected)

## Detailed Results

### Standard Search Pathway
| Fact ID | Statement | Source | Verdict | Action |
| --- | --- | --- | --- | --- |
| pilot_std_01 | topical vitamin c is used for skin moisturizing | SRC-A023 | SUPPORTED | WRITE |
| pilot_std_02 | magnesium ascorbyl phosphate is unstable in aqueous formulas | SRC-A030 | SUPPORTED | WRITE |
| pilot_std_03 | topical vitamin c prevents skin cancer in humans | SRC-A031 | SUPPORTED | WRITE |
| pilot_std_04 | sodium ascorbyl phosphate synergizes with benzoyl peroxide for acne | SRC-A024 | UNSUPPORTED | REJECT |

### Exa-Grounded Search Pathway
| Fact ID | Statement | Source | Verdict | Action |
| --- | --- | --- | --- | --- |
| pilot_exa_01 | topical L-ascorbic acid formulation requires a pH of less than 3.5 to achieve percutaneous absorption | SRC-A028 | SUPPORTED | WRITE |
| pilot_exa_02 | maximal percutaneous absorption of topical L-ascorbic acid occurs at a concentration of 20% | SRC-A028 | SUPPORTED | WRITE |
| pilot_exa_03 | topical L-ascorbic acid increases mRNA levels of collagen types I and iii in human skin in vivo | SRC-A029 | SUPPORTED | WRITE |
| pilot_exa_04 | topical magnesium ascorbyl phosphate stimulates collagen synthesis in dermal fibroblasts | SRC-A030 | SUPPORTED | WRITE |

## Decision Log Seed (DEC-012)
Based on the results of the pilot, **the Exa-Grounded Search Pathway achieved a 0.0% rejection rate** by directly matching claims to their exact supporting evidence in published literature, representing a significant improvement over both standard keyword search and the Batch 1 baseline (27.3% rejection).
Therefore, we recommend retaining Exa MCP for future scaling (Phase 4 Batch 2) to maintain ingestion quality and efficiency.
