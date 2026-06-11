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

## Two-Stage Render Architecture (Phase 8+, DEC-017)
Stage 1 (Antigravity, this repo): graph -> content -> slide planning (intent ->
deterministic layout select -> slot fill) -> designer-ready PPTX/HTML where ALL
visuals exist only as placeholder blocks (composite IDs, grey plates) + emitted
`placeholder_contract.json` per deck. Stage 2 (Claude Design): binary replacement
of placeholders strictly per contract; structure/content untouched.
Placeholder routing by type: id_logo -> fixed brand SVG (logo registry);
id_illustration / id_graph -> deterministic diagram engine (source-grounded from
active graph, NEVER prompt-generated); id_img -> generation/stock (provenance required).

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
- **P012 External Dependency Blocked Policy**: The absence or unreachability of any required external resource (e.g. an API endpoint, API credentials, or network connection) MUST block the task execution and mark the walkthrough status as `blocked`. Substituting missing dependencies with simulated, mocked, or handwritten dummy data is strictly forbidden and constitutes a quality violation.
- **P013 Transparent Status Reporting**: The status reported in walkthroughs must strictly represent reality. If any fallbacks, overrides, or blocks occur during execution, they must be documented in `deltas_vs_plan` and the status must be reported as `partial` or `blocked`. Marking simulated runs as `PASS` or `done` is prohibited.
- **P014 Dynamic Caching Provenance**: All cache entries inside the verification cache must be written exclusively by the live fetcher path. The manual fabrication, editing, or seed authoring of cache files or verdicts is prohibited. Fact nodes referencing the cache are dynamically validated against the cache's cryptographic hash and live-fetch provenance.
- **P016 Deltas-Honesty**: deltas_vs_plan must document any unplanned edits, deletions, renaming, index recompiles, or out-of-spec alterations. Setting it to None is only permitted if execution matches the plan exactly.
- **P017 Confidence-Semantics**: The confidence field in facts is not consumed. It must be marked as reserved/unused in schemas, bypassed in validator, and documented in DEC-014.
- **P018 Slide-Fact Alignment**: A clinical claim/thesis on a slide must be supported by the `statement` of at least one cited fact in the active graph; simply having a source_ref reference is insufficient.
- **P019 Diagram Provenance**: No visual asset can be used in a deck without a logged record in `asset_provenance.json` detailing its source of truth, license type, and attribution credit (if CC-BY). Permitted licenses: own/generated, CC0, CC-BY, public-domain. Forbidden licenses: CC-BY-SA, NC, BioRender without industry license, and unknown/undeclared licenses.
- **P020 Diagram-engine**: (a) diagram carries only short labels (≤4 words, ≤6 labels total / ≤3 key bullets); all prose resides in the slide body, not in the illustration; (b) diagram geometry is calculated dynamically via template/tokens and not positioned manually; (c) no diagram is saved or integrated without passing the deterministic bounds check.
- **P021 Placeholder Contract & Routing**: Stage 1 never embeds final visuals; every visual area is a placeholder block with a composite ID (`id_{type}_s{NN}_{slug}`, naming.md §1.6) registered in the deck's `placeholder_contract.json` (schema in `00_governance/schemas/`). Stage 2 fills strictly by contract routing: `id_logo`→logo registry SVG; `id_illustration`/`id_graph`→deterministic diagram engine grounded in active graph facts (P018/P019/P020 apply); `id_img`→generation/stock with mandatory `asset_provenance.json` entry. A placeholder without a contract entry, or with a `route` mismatching its `type`, is a QA FAIL. Prompt-generation of EBM visuals (mechanisms, anatomy, charts, numbers) is forbidden.
- **P022 Deterministic Slot-Filling**: LLM is forbidden to generate or choose slide composition. Layout selection is rule-based only: intent (rule-based detection) → decision tree over structural metrics → `layout_id` from the approved pool in `layouts.json`; fallback cascade primary → secondary → `layout_text_dense_fallback`. Content fills fixed slots; exceeding a slot's `max_chars` is a Stage-1 validation error (fail fast, before render). Geometry is stored as `bounds` (px, 1280×720) plus `relative_bounds` (0.0–1.0); both must stay in parity (±1px).
- **P023 Deck Scope Gate**: a deck contains 13–20 slides; fewer than 13 or more than 20 is a hard QA FAIL. Effective for every deck produced by the Phase-8 pipeline; legacy decks (7–10 slides) remain valid only until their migration.





## Walkthrough Standards
По завершении любого ТЗ создавать/обновлять walkthrough.md строго по WALKTHROUGH_TEMPLATE.md. Никакого свободного текста вне секций. Это интерфейс к внешнему ревьюеру.
