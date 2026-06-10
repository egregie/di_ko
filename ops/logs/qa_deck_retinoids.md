# QA Audit Report — Phase 3.5: Design System & Dual Render

**Overall Audit Status**: FAIL

## PDF / HTML Render Audit
- **Status**: FAIL

### Errors
- GATE BLOCK: Placeholder asset 'cover_placeholder.png' caption 'Ретиноиды в дерматологии' in slide 'deck_retinoids-s01.json' must start with '[Placeholder]'.
- GATE BLOCK: Asset 'formula_placeholder.png' used in slide 'deck_retinoids-s02.json' is NOT registered in asset_provenance.json.
- GATE BLOCK: Asset 'mechanism_placeholder.png' used in slide 'deck_retinoids-s03.json' is NOT registered in asset_provenance.json.
- GATE BLOCK: Asset 'ingredients_placeholder.png' used in slide 'deck_retinoids-s04.json' is NOT registered in asset_provenance.json.
- GATE BLOCK: Asset 'clinical_placeholder.png' used in slide 'deck_retinoids-s05.json' is NOT registered in asset_provenance.json.
- GATE BLOCK: Asset 'warning_placeholder.png' used in slide 'deck_retinoids-s06.json' is NOT registered in asset_provenance.json.
- Claim Validation failed in slide 'deck_retinoids-s06.json': Slide contains 'Safety/Tolerability' clinical claim, but none of the cited facts ['retinoids', 'fact_0015', 'SRC-A018'] contain supporting keywords ['безопас', 'safe'].
- GATE BLOCK: Asset 'summary_placeholder.png' used in slide 'deck_retinoids-s07.json' is NOT registered in asset_provenance.json.

## PPTX (PowerPoint) Render Audit
- **Status**: FAIL

### Errors
- GATE BLOCK: Placeholder asset 'cover_placeholder.png' caption 'Ретиноиды в дерматологии' in slide 'deck_retinoids-s01.json' must start with '[Placeholder]'.
- GATE BLOCK: Asset 'formula_placeholder.png' used in slide 'deck_retinoids-s02.json' is NOT registered in asset_provenance.json.
- GATE BLOCK: Asset 'mechanism_placeholder.png' used in slide 'deck_retinoids-s03.json' is NOT registered in asset_provenance.json.
- GATE BLOCK: Asset 'ingredients_placeholder.png' used in slide 'deck_retinoids-s04.json' is NOT registered in asset_provenance.json.
- GATE BLOCK: Asset 'clinical_placeholder.png' used in slide 'deck_retinoids-s05.json' is NOT registered in asset_provenance.json.
- GATE BLOCK: Asset 'warning_placeholder.png' used in slide 'deck_retinoids-s06.json' is NOT registered in asset_provenance.json.
- Claim Validation failed in slide 'deck_retinoids-s06.json': Slide contains 'Safety/Tolerability' clinical claim, but none of the cited facts ['retinoids', 'fact_0015', 'SRC-A018'] contain supporting keywords ['безопас', 'safe'].
- GATE BLOCK: Asset 'summary_placeholder.png' used in slide 'deck_retinoids-s07.json' is NOT registered in asset_provenance.json.

## Warnings
- No warnings.

## Checked Invariants
- Zero Black Policy: PASS
- Arimo font defined in tokens: PASS
- Safety slide present: PASS
- Pregnancy slide present (when required): PASS
- Playwright Font Load (Online): PASS
- Playwright Font Load (Offline): PASS
- PPTX Element Font Check (Arimo): PASS
- Total slides checked: 7
