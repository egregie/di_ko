# Known Problems & Blockers

- **RTK Hook Support**: Native Windows shell command intercept hooking has limited support compared to WSL. RTK remains fully functional for manual execution wrap (`rtk <cmd>`).
- **Quarantined Facts**: The following facts were quarantined during Phase 1.5 Evidence Audit due to lack of direct abstract support (UNSUPPORTED):
  - `fact_0003`: Retinol two-step oxidation (cites PMID 15773538, whose abstract lacks conversion details).
  - `fact_0008`: Adapalene lower irritation/photostability vs tretinoin (cites PMID 29494115, which is a general StatPearls overview lacking direct comparative details).
  - `fact_0013`: Retinyl palmitate stability & conversion (cites PMID 37927602, whose abstract lacks conversion steps).
  - `fact_0016`: Retinol localized irritation (cites PMID 15773538, whose abstract lacks adaptation irritation details).
