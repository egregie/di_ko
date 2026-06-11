# Postacne Knowledge Collection — Phase 8.7a — 2026-06-11

status: **partial / BLOCKED** (verification judge unavailable)

## Discovery (Block A) — DONE
- Live PubMed search via `collect_postacne_search.py` (hardened fetch: IPv4 force, ≤3 req/s, tool/email, logged).
- 10 clinical queries (PIH, PIE, atrophic scars × azelaic acid / retinoids / peels / niacinamide / microneedling / TCA CROSS / fractional laser / adapalene).
- 67 unique abstracts with text gathered → `.tmp/postacne_search.json` + `.tmp/postacne_search.md` (intermediates, gitignored).

## Candidates (Block B) — staged
- 12 candidates authored (`fact_0063`..`fact_0074`), each grounded in a specific live abstract; 12 sources registered (`SRC-A054`..`SRC-A065`, all PubMed tier-A).
- Ran each through `verify_gate.py --force-live`.

## Live gate result — BLOCKER hit
The grounded LLM-judge (Gemini) key returned **403 PERMISSION_DENIED — "API key was reported as leaked"**.
Root cause: the env `GEMINI_API_KEY` equals the key that was **hardcoded in `ops/scripts/lib/evidence.py`** (committed → flagged as leaked by Google). 403 does not trigger key rotation (only 429 does), so the judge fell back to NEEDS_MANUAL.

| Outcome | Count | Facts |
|---|---|---|
| Judge ran, SUPPORTED + grounded → clean write | 1 | fact_0070 (fractional picosecond laser ↓ PIH risk vs other fractional lasers) |
| Judge ran, SUPPORTED but **grounding guard** (no verbatim quote) → UNSUPPORTED → rejected | 2 | fact_0068, fact_0069 |
| Judge **blocked** (403) → NEEDS_MANUAL (abstract fetched, NOT judged) | 9 | fact_0063–0067, fact_0071–0074 |

**Honest accounting:** of the 3 candidates the judge actually evaluated, 1 passed (others failed the verbatim-quote grounding guard, working as designed). The remaining 9 are **unjudged**, not verified.

## Cleanup performed (P007/P013 — no unverified fact stays in graph)
- Removed the 9 NEEDS_MANUAL (unjudged) facts from `03_knowledge_graph/facts/`; they remain staged in `02_processing/verify/candidates/` for re-judging once a valid key is set.
- Kept `fact_0070` (genuinely judge-verified) + created entity `atrophic_acne_scars` (P008), linked.
- `fact_0068`/`fact_0069` remain in `02_processing/verify/rejected/`.
- Security: removed the leaked hardcoded key from `evidence.py`; judge now returns NEEDS_MANUAL cleanly when no key is configured.
- `build_index.py` → 26 entities / 38 facts / 49 relationships; `validate_graph.py` PASS.

## Deck-readiness (P011)
Postacne = **1 verified clean fact** → **NOT deck-ready** (need ≥8). Topic remains deferred.

## Unblock (requires user)
Set a valid, non-leaked `GEMINI_API_KEY` (env or a project `.env`). Then re-run:
`for n in 63..74: python ops/scripts/verify_gate.py 02_processing/verify/candidates/fact_00$n.json --force-live`
The 9 staged candidates + sources are ready; only the judge is missing. Expect historical 25–33% reject rate, so a second discovery round may be needed to clear ≥8.
