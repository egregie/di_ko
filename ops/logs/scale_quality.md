# Scale Quality Report — Phase 4.1: Active Ingestion Audit

## Per-Topic Rejection Rates (Backfill Candidates)
| Topic | Total Processed | Rejected | Rejection Rate | Status |
| --- | --- | --- | --- | --- |
| vitamin_c | 4 | 0 | 0.0% | PASS |
| niacinamide | 6 | 1 | 16.7% | PASS |
| exfoliants | 0 | 0 | 0.0% | PASS |

## Ingested Backfill Facts Details
| Fact ID | Topic | Statement | Verdict | Action |
| --- | --- | --- | --- | --- |
| fact_0028 | vitamin_c | topical L-ascorbic acid formulation requires a pH of less than 3.5 to achieve percutaneous absorption | SUPPORTED | WRITE |
| fact_0029 | vitamin_c | maximal percutaneous absorption of topical L-ascorbic acid occurs at a concentration of 20% | SUPPORTED | WRITE |
| fact_0030 | vitamin_c | topical L-ascorbic acid increases mRNA levels of collagen types I and iii in human skin in vivo | SUPPORTED | WRITE |
| fact_0031 | magnesium_ascorbyl_phosphate | topical magnesium ascorbyl phosphate stimulates collagen synthesis in dermal fibroblasts | UNSUPPORTED | REJECT |
| fact_0032 | ascorbyl_glucoside | topical ascorbyl glucoside exhibits collagen-stimulating properties in human dermal fibroblasts | UNSUPPORTED | REJECT |
| fact_0033 | vitamin_c | topical vitamin C increases collagen synthesis in human skin across various age groups | NEEDS_MANUAL | WRITE |
| fact_0034 | niacinamide | topical niacinamide reduces hyperpigmentation by suppressing melanosome transfer from melanocytes to keratinocytes | SUPPORTED | WRITE |
| fact_0035 | niacinamide | topical niacinamide 4% is effective in treating melasma with comparable efficacy to 4% hydroquinone but with fewer side effects | SUPPORTED | WRITE |
| fact_0036 | niacinamide | topical niacinamide 2% and 5% concentrations significantly decrease cutaneous hyperpigmentation and increase skin lightness | SUPPORTED | WRITE |
| fact_0037 | niacinamide | the inhibitory effect of niacinamide on melanosome transfer is reversible | UNSUPPORTED | REJECT |
| fact_0038 | niacinamide | topical niacinamide improves stratum corneum barrier function and provides clinical benefits in subjects with rosacea | SUPPORTED | WRITE |
| fact_0039 | niacinamide | topical niacinamide reduces transepidermal water loss and increases epidermal stratum corneum hydration | WEAK | WRITE |
| fact_0040 | mandelic_acid | topical mandelic acid twice daily for four weeks increases lower eyelid skin elasticity and firmness | UNSUPPORTED | REJECT |
| fact_0041 | mandelic_acid | 45% mandelic acid peels are equally effective as 30% salicylic acid peels for mild-to-moderate acne vulgaris with better safety profile | SUPPORTED | WRITE |
| fact_0042 | lactic_acid | topical 12% L-lactic acid increases both epidermal and dermal thickness and skin firmness after three months | UNSUPPORTED | REJECT |
| fact_0043 | lactic_acid | topical 5% L-lactic acid improves skin smoothness and decreases fine lines but does not produce dermal changes | UNSUPPORTED | REJECT |
