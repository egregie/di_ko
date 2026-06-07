# Regression Test Log — Phase 2.5 (Collection Hardening)

This log documents the automated verification results of the gatekeeper script `verify_gate.py`.

## Case 1: Existing 12 Clean Facts
All 12 clean facts in the active knowledge graph must pass the gate successfully.

| Fact ID | Statement | Verdict | Evidence OK | Action | Status |
|---|---|---|---|---|---|
| fact_0001 | Retinoids regulate gene transcription by... | WEAK | True | write | PASS |
| fact_0002 | Tretinoin binds directly to nuclear reti... | WEAK | True | write | PASS |
| fact_0004 | Retinol stimulates collagen synthesis an... | SUPPORTED | True | write | PASS |
| fact_0005 | Tretinoin is the gold standard for clini... | WEAK | True | write | PASS |
| fact_0006 | Tretinoin normalizes keratinocyte differ... | SUPPORTED | True | write | PASS |
| fact_0007 | Adapalene selectively binds to retinoic ... | SUPPORTED | True | write | PASS |
| fact_0009 | Tazarotene selectively binds to nuclear ... | WEAK | True | write | PASS |
| fact_0010 | Tazarotene 0.1% cream is effective for t... | SUPPORTED | True | write | PASS |
| fact_0011 | Retinaldehyde requires only a single met... | WEAK | True | write | PASS |
| fact_0012 | Topical retinaldehyde improves skin hydr... | SUPPORTED | True | write | PASS |
| fact_0014 | Retinyl palmitate nano-formulation reduc... | SUPPORTED | True | write | PASS |
| fact_0015 | Topical retinoids are contraindicated du... | SUPPORTED | True | write | PASS |
| fact_0017 | glycolic acid and salicylic acid combina... | SUPPORTED | True | write | PASS |
| fact_0018 | salicylic-mandelic acid peels are effect... | SUPPORTED | True | write | PASS |
| fact_0019 | topical 30% salicylic acid peels reduce ... | SUPPORTED | True | write | PASS |
| fact_0020 | glycolic acid peels clinical application... | SUPPORTED | True | write | PASS |
| fact_0021 | topical l-ascorbic acid promotes collage... | SUPPORTED | True | write | PASS |
| fact_0022 | topical 5% sodium ascorbyl phosphate lot... | SUPPORTED | True | write | PASS |
| fact_0024 | topical niacinamide enhances ceramide sy... | SUPPORTED | True | write | PASS |
| fact_0025 | topical niacinamide reduces inflammatory... | SUPPORTED | True | write | PASS |
| fact_0028 | topical L-ascorbic acid formulation requ... | SUPPORTED | True | write | PASS |
| fact_0029 | maximal percutaneous absorption of topic... | SUPPORTED | True | write | PASS |
| fact_0030 | topical L-ascorbic acid increases mRNA l... | SUPPORTED | True | write | PASS |
| fact_0034 | topical niacinamide reduces hyperpigment... | SUPPORTED | True | write | PASS |
| fact_0035 | topical niacinamide 4% is effective in t... | SUPPORTED | True | write | PASS |
| fact_0036 | topical niacinamide 2% and 5% concentrat... | SUPPORTED | True | write | PASS |
| fact_0038 | topical niacinamide improves stratum cor... | SUPPORTED | True | write | PASS |
| fact_0039 | topical niacinamide reduces transepiderm... | WEAK | True | write | PASS |
| fact_0041 | 45% mandelic acid peels are equally effe... | SUPPORTED | True | write | PASS |

**Case 1 Result**: SUCCESS

## Case 2: Fabricated PMID 99999999
A candidate fact referencing a non-existent PMID must be automatically rejected with verdict `SOURCE_NOT_FOUND`.

- Candidate Fact ID: `fact_fake_pmid`
- Exit Code: `1` (Expected: non-zero)
- Output Verdict: `SOURCE_NOT_FOUND` (Expected: `SOURCE_NOT_FOUND`)
- Routing Action: `reject` (Expected: `reject`)
- In Rejected Folder: `True` (Expected: `True`)
- **Status**: PASS

## Case 3: Real PMID but Irrelevant Claim
A candidate fact with a real PMID but unrelated statement must be automatically rejected with verdict `UNSUPPORTED`.

- Candidate Fact ID: `fact_irrelevant`
- Exit Code: `1` (Expected: non-zero)
- Output Verdict: `UNSUPPORTED` (Expected: `UNSUPPORTED`)
- Routing Action: `reject` (Expected: `reject`)
- In Rejected Folder: `True` (Expected: `True`)
- **Status**: PASS

