# YM PROSKIN — Project Operating Rules (v2)

## Paradigm
Foundation-First. Build ontology + knowledge graph + agents BEFORE any render.
Slides/PPTX/PDF/HTML are output formats, not the product.

## Mission
Fact-verified cosmetology/dermatology knowledge platform. Audience: licensed
specialists. One graph -> many outputs.

## Hard rules
1. Evidence-based only. No claim enters the graph without source + evidence_level.
   D-level => never on a clinical slide. Doubt => discard.
2. Entities are normalized (retinol / retinoid / vitamin_a_derivative are NOT
   three entities). Ontology Manager owns canonical IDs.
3. Local-first. No clinical/patient data to cloud (no Canva export of such).
4. Separation: knowledge (graph) vs style (design tokens) vs render. slide-spec
   carries NO color/font; both resolved from design-tokens.json at render time.
5. Design invariants: tokens in §3.4 only. Zero Black. Arimo. lh>=1.5.
6. Reproducible & deterministic: output = f(graph, slide-spec, tokens).
7. Style of work: concise, no guessing, "insufficient data" when unknown, cite.

## Pipeline
discover -> collect -> extract -> dedup -> verify -> librarian/ontology -> graph
   (later) -> narrative -> architect -> build -> QA. Each stage logs to ops/logs.
