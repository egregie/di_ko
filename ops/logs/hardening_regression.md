# Regression Test Log — Phase 2.5 (Collection Hardening)

This log documents the automated verification results of the gatekeeper script `verify_gate.py`.

## Case 1: Existing 12 Clean Facts
All 12 clean facts in the active knowledge graph must pass the gate successfully.

| Fact ID | Statement | Verdict | Evidence OK | Action | Status |
|---|---|---|---|---|---|
| fact_0001 | Retinoids regulate gene transcription by... | SUPPORTED | True | write | PASS |
| fact_0002 | Tretinoin binds directly to nuclear reti... | WEAK | True | write | PASS |
| fact_0004 | Retinol stimulates collagen synthesis an... | WEAK | True | write | PASS |
| fact_0005 | Tretinoin is the gold standard for clini... | SUPPORTED | True | write | PASS |
| fact_0006 | Tretinoin normalizes keratinocyte differ... | WEAK | True | write | PASS |
| fact_0007 | Adapalene selectively binds to retinoic ... | SUPPORTED | True | write | PASS |
| fact_0009 | Tazarotene selectively binds to nuclear ... | SUPPORTED | True | write | PASS |
| fact_0010 | Tazarotene 0.1% cream is effective for t... | SUPPORTED | True | write | PASS |
| fact_0011 | Retinaldehyde requires only a single met... | SUPPORTED | True | write | PASS |
| fact_0012 | Topical retinaldehyde improves skin hydr... | SUPPORTED | True | write | PASS |
| fact_0014 | Retinyl palmitate nano-formulation reduc... | SUPPORTED | True | write | PASS |
| fact_0015 | Topical retinoids are contraindicated du... | SUPPORTED | True | write | PASS |

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

