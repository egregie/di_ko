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

## Principles
- **P001 Schema First**: Data model templates dictate integration properties.
- **P002 Knowledge Graph Before Templates**: Database and index creation take priority over slide templates.
- **P003 Context Discipline**: RTK compresses CLI-proxy output; the Retriever returns only 20–50 relevant nodes from the graph index, preventing large-scale DB reading overhead.
- **P004 Concise by Mode**: Enable Caveman ultra mode for production integration roles and off/full mode for research/verification roles.
- **P005 Persistent Working Memory**: Every agent reads and maintains project metadata records under `00_PROJECT_STATE/`.
- **P006 Every Agent Leaves Logs**: Track processes under `ops/logs/` and update project state log.
- **P007 No Fact Without Source**: Facts require an evidence_level and at least 2 independent sources or 1 peer-reviewed journal reference.
- **P008 No Entity Without Ontology**: Canonical definitions and aliases must conform to `ontology_v1.json` via the ontology-guard agent.
- **P009 Verify-at-Write**: Facts are written to the graph only after automated verification (source existence, abstract support, and evidence level alignment). Fabricated or unreachable sources are automatically rejected.
- **P010 Script Permanence**: Pipeline scripts reside in `ops/scripts/` and must be registered in their respective SKILL.md. Deleting working scripts is prohibited. One-time migrations go to `ops/scripts/one_time/`.
- **P011 Deck Readiness**: A cosmetic topic qualifies for a presentation slide deck only when it has at least 8 verified, clean facts in the active knowledge graph. Presentations for topics below this threshold are deferred until more facts are ingested under the verification gate.


## Walkthrough Standards
По завершении любого ТЗ создавать/обновлять walkthrough.md строго по WALKTHROUGH_TEMPLATE.md. Никакого свободного текста вне секций. Это интерфейс к внешнему ревьюеру.


