# Known Problems & Blockers

- **RTK Hook Support**: Native Windows shell command intercept hooking has limited support compared to WSL. RTK remains fully functional for manual execution wrap (`rtk <cmd>`).
- **Quarantined Facts**: The following facts were quarantined during Phase 1.5 Evidence Audit due to lack of direct abstract support (UNSUPPORTED):
  - `fact_0003`: Retinol two-step oxidation (cites PMID 15773538, whose abstract lacks conversion details).
  - `fact_0008`: Adapalene lower irritation/photostability vs tretinoin (cites PMID 29494115, which is a general StatPearls overview lacking direct comparative details).
  - `fact_0013`: Retinyl palmitate stability & conversion (cites PMID 37927602, whose abstract lacks conversion steps).
  - `fact_0016`: Retinol localized irritation (cites PMID 15773538, whose abstract lacks adaptation irritation details).
- **Quarantined Facts (Phase 3.1)**:
  - `fact_0023`: SAP + Retinol synergy (cites PMID 19165682, which is actually about tranexamic acid for post-cesarean section bleeding).
  - `fact_0026`: Niacinamide + Retinoid synergy (cites PMID 17147561, which is a general Niacinamide review lacking retinoid tolerability details).
  - `fact_0027`: AHA + Retinoid irritation (cites PMID 32250551, which is about Glycolic/Salicylic acid combination and lacks retinoid reference).
- **Quarantined Facts (Phase 4.1 / 4.2)**:
  - `fact_0031`: Magnesium Ascorbyl Phosphate collagen stimulation (cites PMID 18505499, which is unsupported).
  - `fact_0032`: Ascorbyl Glucoside collagen properties (cites PMID 18505499, which is unsupported).
  - `fact_0033`: Vitamin C collagen synthesis across age groups (cites PMID 26327894, which is about menopausal symptoms).
  - `fact_0037`: Niacinamide melanosome transfer reversibility (cites PMID 16033423, which is unrelated/unsupported).
  - `fact_0040`: Mandelic Acid viscoelasticity (cites PMID 30513568, which is unrelated/unsupported).
  - `fact_0042`: Lactic Acid epidermal/dermal thickness (cites PMID 8854589, which is unrelated/unsupported).
  - `fact_0043`: Lactic Acid smoothness and fine lines (cites PMID 8854589, which is unrelated/unsupported).
- **Per-Topic Fact Shortfall**: Resolved. All thin topics (Vitamin C, Niacinamide, Exfoliants) have been backfilled to exactly 8 verified, clean facts each.
- **Phase 8 Blockers (registered 2026-06-11)**:
  - `layouts.json` has no geometry layer (10 descriptive entries only, no bounds/max_chars/placeholder slots) — blocks Slide Planning Engine (DEC-018).
  - Donor files absent from repo: `hd_1` (approved Postacne redesign, ~80% review), design concept, `Retinoid.pdf`, `Постакне_nov20.pdf` — required for Layout Library v2 geometry; request from client. `tpl1`/`tpl2` must NOT be parsed (dirty geometry).
  - Client approval of 2 layout carcasses pending — hard precondition for Phase 8.3+.
  - All 5 active decks are 7–10 slides and will fail the new P023 scope gate (13–20); gate applies only to Phase-8 pipeline decks until legacy migration.
  - Postacne topic: 0 facts in active graph; P011 requires ≥8 verified facts before its deck (separate collection TZ needed).
- **Stale-Export Artifacts (resolved as non-issues 2026-06-11)**: the cross-review's "literal `[Placeholder]` bug" is an enforced convention (`qa_deck.py` requires the prefix; superseded in Phase 8.5); "footer-overlap" not reproduced — current bounds/overlap QA passes 100% on all 5 decks.
- **Verification Judge Key (2026-06-11) — RESOLVED**: the original `GEMINI_API_KEY` was the key hardcoded in `evidence.py`, flagged by Google as leaked (403, no rotation since 403≠429). Removed the hardcoded key from source; user supplied a fresh key stored in gitignored `C:\di_ko\.env`; `get_gemini_api_keys()` now reads project `.env` first, drops the known-leaked key, then falls back to process env / pharma_v2. Judge operational again. NOTE: any committed Gemini key gets auto-flagged — keep keys only in gitignored `.env`.
- **Gemini quota / rate limit (updated 2026-06-12)**: the free-tier judge key enforces a tight per-minute rate limit (≈1 call per window) plus a daily cap. `evidence.py` now backs off on the 429 `retryDelay` (≤65s, 6 attempts) instead of bailing on the "PerDay" substring (DEC-023), so per-minute limits are waited out; once the daily cap is exhausted even backoff fails → NEEDS_MANUAL. Deferred on quota (re-judge when reset, or use a paid key): procedure candidates `fact_0076/0077/0079` (surplus — scarring deficit already closed by 0075+0078), `fact_0074` (azelaic tyrosinase), and C4 re-verify of `fact_0015`. Pace heavy batches.
- **run_regression.py is destructive to the live graph**: it re-verifies EVERY active fact (cache path) and rewrites their metadata; with imperfect judge cache it can false-drop a previously-verified fact (it dropped `fact_0025` on 2026-06-11, restored via `git checkout HEAD -- 03_knowledge_graph/facts/`). Do not run the full regression while the judge is quota-limited/unavailable. Candidate for a future fix: regression should operate on isolated fixtures, not mutate the real graph.





