# Regression Test Log — Phase 2.5 (Collection Hardening)

This log documents the automated verification results of the gatekeeper script `verify_gate.py`.

## Case 1: Existing 12 Clean Facts
All 12 clean facts in the active knowledge graph must pass the gate successfully.

| Fact ID | Statement | Verdict | Evidence OK | Action | Status |
|---|---|---|---|---|---|
| fact_0001 | Retinoids regulate gene transcription by... | WEAK | True | write | PASS |
| fact_0005 | Tretinoin is the gold standard for clini... | WEAK | True | write | PASS |
| fact_0007 | Adapalene selectively binds to retinoic ... | SUPPORTED | True | write | PASS |
| fact_0009 | Tazarotene selectively binds to nuclear ... | SUPPORTED | True | write | PASS |
| fact_0010 | Tazarotene 0.1% cream is effective for t... | NEEDS_MANUAL | True | write | PASS |
| fact_0011 | Retinaldehyde requires only a single met... | WEAK | True | write | PASS |
| fact_0014 | Retinyl palmitate nano-formulation reduc... | NEEDS_MANUAL | True | write | PASS |
| fact_0015 | Topical retinoids are contraindicated du... | WEAK | True | write | PASS |
| fact_0018 | salicylic-mandelic acid peels are effect... | NEEDS_MANUAL | True | write | PASS |
| fact_0019 | topical 30% salicylic acid peels reduce ... | NEEDS_MANUAL | True | write | PASS |
| fact_0020 | glycolic acid peels clinical application... | NEEDS_MANUAL | True | write | PASS |
| fact_0021 | topical l-ascorbic acid promotes collage... | NEEDS_MANUAL | True | write | PASS |
| fact_0022 | topical 5% sodium ascorbyl phosphate lot... | NEEDS_MANUAL | True | write | PASS |
| fact_0024 | topical niacinamide enhances ceramide sy... | NEEDS_MANUAL | True | write | PASS |
| fact_0028 | topical L-ascorbic acid formulation requ... | NEEDS_MANUAL | True | write | PASS |
| fact_0029 | maximal percutaneous absorption of topic... | NEEDS_MANUAL | True | write | PASS |
| fact_0030 | topical L-ascorbic acid increases mRNA l... | NEEDS_MANUAL | True | write | PASS |
| fact_0034 | topical niacinamide reduces hyperpigment... | NEEDS_MANUAL | True | write | PASS |
| fact_0035 | topical niacinamide 4% is effective in t... | NEEDS_MANUAL | True | write | PASS |
| fact_0036 | topical niacinamide 2% and 5% concentrat... | NEEDS_MANUAL | True | write | PASS |
| fact_0038 | topical niacinamide improves stratum cor... | NEEDS_MANUAL | True | write | PASS |
| fact_0039 | topical niacinamide reduces transepiderm... | SUPPORTED | True | write | PASS |
| fact_0041 | 45% mandelic acid peels are equally effe... | NEEDS_MANUAL | True | write | PASS |
| fact_0044 | topical L-ascorbic acid formulation requ... | NEEDS_MANUAL | True | write | PASS |
| fact_0045 | maximal percutaneous absorption of topic... | NEEDS_MANUAL | True | write | PASS |
| fact_0046 | topical L-ascorbic acid increases mRNA l... | NEEDS_MANUAL | True | write | PASS |
| fact_0047 | topical 5% niacinamide reduces fine line... | NEEDS_MANUAL | True | write | PASS |
| fact_0048 | topical alpha-hydroxy acids application ... | NEEDS_MANUAL | True | write | PASS |
| fact_0049 | salicylic acid acts as a desmolytic agen... | NEEDS_MANUAL | True | write | PASS |
| fact_0050 | topical 20% salicylic-10% mandelic acid ... | NEEDS_MANUAL | True | write | PASS |
| fact_0051 | topical palmitoyl pentapeptide-4 (pal-KT... | NEEDS_MANUAL | True | write | PASS |
| fact_0052 | topical copper tripeptide-1 (GHK-Cu) sti... | NEEDS_MANUAL | True | write | PASS |
| fact_0053 | topical GHK-Cu peptide regulates gene ex... | NEEDS_MANUAL | True | write | PASS |
| fact_0054 | topical acetyl hexapeptide-8 (Argireline... | NEEDS_MANUAL | True | write | PASS |
| fact_0057 | topical palmitoyl tripeptide-38 formulat... | NEEDS_MANUAL | True | write | PASS |
| fact_0058 | topical acetyl tetrapeptide-5 has protec... | NEEDS_MANUAL | True | write | PASS |
| fact_0063 | 15% azelaic acid gel effectively improve... | SUPPORTED | True | write | PASS |
| fact_0064 | Azelaic acid is more effective than vehi... | SUPPORTED | True | write | PASS |
| fact_0065 | In a systematic review of topical treatm... | SUPPORTED | True | write | PASS |
| fact_0066 | Niacinamide is an effective skin lighten... | SUPPORTED | True | write | PASS |
| fact_0067 | A systematic review of randomized contro... | SUPPORTED | True | write | PASS |
| fact_0068 | Combined microneedling and chemical peel... | WEAK | True | write | PASS |
| fact_0070 | Meta-analysis found fractional picosecon... | SUPPORTED | True | write | PASS |
| fact_0071 | Long-term treatment with adapalene 0.3 p... | SUPPORTED | True | write | PASS |
| fact_0072 | A 70% glycolic acid peel is an effective... | SUPPORTED | True | write | PASS |
| fact_0073 | The chemical reconstruction of skin scar... | SUPPORTED | True | write | PASS |

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

## Case 4: Marginally Weak Claim
A candidate fact with a real PMID but weak claim alignment (overlap < 15%) must be automatically rejected under the pre-filter gate.

- Candidate Fact ID: `fact_weak_mismatch`
- Exit Code: `1` (Expected: non-zero)
- Output Verdict: `UNSUPPORTED` (Expected: `UNSUPPORTED`)
- Routing Action: `reject` (Expected: `reject`)
- In Rejected Folder: `True` (Expected: `True`)
- **Status**: PASS

## Case 5: Grounded Supported Fact
A new out-of-sample fact with a relevant abstract that is supported directly must return `SUPPORTED` or `WEAK`.

- Candidate Fact ID: `fact_grounded_supported`
- Exit Code: `0` (Expected: 0)
- Output Verdict: `SUPPORTED` (Expected: `SUPPORTED` or `WEAK`)
- Routing Action: `write` (Expected: `write`)
- In Active Folder: `True` (Expected: `True`)
- **Status**: PASS

## Case 6: Grounded Weak Fact
A new out-of-sample fact with a review abstract supporting it indirectly must return `WEAK`.

- Candidate Fact ID: `fact_grounded_weak`
- Exit Code: `0` (Expected: 0)
- Output Verdict: `WEAK` (Expected: `WEAK`)
- Routing Action: `write` (Expected: `write`)
- In Active Folder: `True` (Expected: `True`)
- **Status**: PASS

## Case 7: Grounded Unsupported Fact
A new out-of-sample fact with keyword overlap but unsupported claim must return `UNSUPPORTED`.

- Candidate Fact ID: `fact_grounded_unsupported`
- Exit Code: `1` (Expected: non-zero)
- Output Verdict: `UNSUPPORTED` (Expected: `UNSUPPORTED`)
- Routing Action: `reject` (Expected: `reject`)
- In Rejected Folder: `True` (Expected: `True`)
- **Status**: PASS

