# Scale Quality Report — Phase 4.2: Honest Backfill Ingestion Audit

## Per-Topic Rejection Rates (Phase 4.2 Backfill Candidates)
| Topic | Total Processed | Rejected | Rejection Rate | Status |
| --- | --- | --- | --- | --- |
| vitamin_c | 3 | 0 | 0.0% | PASS |
| niacinamide | 1 | 0 | 0.0% | PASS |
| exfoliants | 3 | 0 | 0.0% | PASS |

## Ingested Backfill Facts Details
| Fact ID | Topic | Statement | Verdict | Action |
| --- | --- | --- | --- | --- |
| fact_0044 | vitamin_c | topical L-ascorbic acid formulation requires a pH of less than 3.5 to achieve percutaneous absorption | SUPPORTED | WRITE |
| fact_0045 | vitamin_c | maximal percutaneous absorption of topical L-ascorbic acid occurs at a concentration of 20% | SUPPORTED | WRITE |
| fact_0046 | vitamin_c | topical L-ascorbic acid increases mRNA levels of collagen types I and iii in human skin in vivo | SUPPORTED | WRITE |
| fact_0047 | niacinamide | topical 5% niacinamide reduces fine lines, wrinkles, hyperpigmented spots, texture, red blotchiness, and yellowing in aging facial skin | SUPPORTED | WRITE |
| fact_0048 | exfoliants | topical alpha-hydroxy acids application to photoaged skin results in increased skin thickness, improved elastic fibers, and increased collagen density | SUPPORTED | WRITE |
| fact_0049 | exfoliants | salicylic acid acts as a desmolytic agent by disrupting cellular junctions to exfoliate the stratum corneum and possesses comedolytic properties useful for acne | SUPPORTED | WRITE |
| fact_0050 | exfoliants | topical 20% salicylic-10% mandelic acid combination peel is effective for the treatment of active acne and postacne hyperpigmentation in Asian skin | SUPPORTED | WRITE |

## Summary
All 7 candidate facts passed live verification through `verify_gate.py --force-live` and were successfully written to the active graph. 
All three thin topics now meet the deck-readiness threshold:
- **Vitamin C**: 8 verified facts (deck-ready)
- **Niacinamide**: 8 verified facts (deck-ready)
- **Exfoliants**: 8 verified facts (deck-ready)
