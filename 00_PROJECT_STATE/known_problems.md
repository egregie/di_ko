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
- **Quarantined Facts (Phase 4.1)**:
  - `fact_0031`: Magnesium Ascorbyl Phosphate collagen stimulation (cites PMID 18505499, which is unsupported).
  - `fact_0032`: Ascorbyl Glucoside collagen properties (cites PMID 18505499, which is unsupported).
  - `fact_0037`: Niacinamide melanosome transfer reversibility (cites PMID 16033423, which is unrelated/unsupported).
  - `fact_0040`: Mandelic Acid viscoelasticity (cites PMID 30513568, which is unrelated/unsupported).
  - `fact_0042`: Lactic Acid epidermal/dermal thickness (cites PMID 8854589, which is unrelated/unsupported).
  - `fact_0043`: Lactic Acid smoothness and fine lines (cites PMID 8854589, which is unrelated/unsupported).
- **Per-Topic Fact Shortfall (Phase 4.1)**:
  - Vitamin C (6 verified facts), Niacinamide (7 verified facts), and Exfoliants (5 verified facts) are below the target deck-readiness threshold of ≥8 verified facts per topic. These topics remain non-deck-ready (P011) and their slide decks are deferred until more facts can be ingested under a live verification gate.



