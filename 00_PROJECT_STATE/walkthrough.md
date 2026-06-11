# WALKTHROUGH — phase-8.7b-integrity-procedures — 2026-06-11
status: partial
scope: Целостность графа (Блок A) + онтология процедур и diagram-маршрут (Блок B) выполнены полностью. Процедурный добор scarring (Блок C) и разбор fact_0015/0002 (C4) — BLOCKED на дневной quota Gemini-судьи; discovery выполнен, 5 кандидатов застейджены к верификации. Деки/слайды не трогались (graph-only).

## files_changed
- `ops/scripts/validate_graph.py` — A3: +2 детерминированных чека (entity.fact_ids → quarantined fact = FAIL; relationship from/to → missing entity = FAIL).
- `03_knowledge_graph/entities/retinoids.json, retinol.json, tretinoin.json, retinaldehyde.json, glycolic_acid.json, exfoliants.json` — A1: отвязаны 8 broken fact-links (0004/0006/0012/0017).
- `03_knowledge_graph/entities/acne.json, photoaging.json` — [NEW] A2: clinical_condition.
- `03_knowledge_graph/entities/pregnancy.json, lactation.json` — [NEW] A2: contraindication_context.
- `03_knowledge_graph/relationships/rel_0042.json` — A2: УДАЛЁН (niacinamide→barrier; barrier = домен-функция, не узел).
- `00_governance/ontology_v1.json` — B1: тип `procedure` (+ clinical_condition, contraindication_context) + procedure-схема (forbidden pubchem_cid/molecule_svg) + p011_scope. v1.0→1.1.
- `00_governance/AGENTS.md` — B3: P011-исключение (порог ≥8 только для topical_active/procedure; condition/contraindication_context — exempt).
- `ops/scripts/one_time/gen_procedure_diagram.py` — [NEW] B2: прогон diagram engine на процедурной схеме.
- `04_design_system/assets/mechanisms/procedure_depth_skin_layers.svg` — [NEW] B2: процедурная схема (слои кожи + глубина), qa_svg_bounds PASS.
- `04_design_system/assets/asset_provenance.json` — B2: provenance процедурной схемы (generated/own, P019).
- `ops/scripts/one_time/collect_procedure_search.py` — [NEW] C2: live PubMed discovery процедур.
- `ops/scripts/one_time/author_procedure_candidates.py` — [NEW] C2: стейджинг 5 кандидатов (subcision×3, fractional CO2, fractional RF).
- `02_processing/verify/candidates/fact_0075..0079.json` — [NEW] застейджены (НЕ в графе; ждут судью).
- `02_processing/verify/rejected/fact_0006.json, fact_0012.json` — возвращены в карантин (quota→NEEDS_MANUAL, не верифицированы).
- `03_knowledge_graph/sources.json` — +5 источников tier-A (SRC-A066..A070).
- `00_PROJECT_STATE/*` — current_state, active_tasks, known_problems, walkthrough.

## commands_run
- `python ops/scripts/validate_graph.py` — ДО фиксов: FAIL (8 broken links + 29 dangling rels — сырой вывод показан). ПОСЛЕ: PASS.
- `python ops/scripts/verify_gate.py 02_processing/verify/rejected/fact_0004.json --force-live` — judge UNSUPPORTED (abstract поддерживает procollagen, НЕ MMP — сырая цитата/reason показаны).
- `python ops/scripts/verify_gate.py .../fact_0017.json --force-live` — judge SUPPORTED, но grounding-guard отклонил stitched-цитату → gate UNSUPPORTED.
- `python ops/scripts/verify_gate.py .../fact_0006.json|fact_0012.json --force-live` — 429 RESOURCE_EXHAUSTED (PerDay) → NEEDS_MANUAL (НЕ верифицировано).
- `python ops/scripts/one_time/gen_procedure_diagram.py` — qa_svg_bounds: PASS.
- `python ops/scripts/one_time/collect_procedure_search.py` — 26 абстрактов (live).
- `python ops/scripts/one_time/author_procedure_candidates.py` — 5 кандидатов застейджены.
- `python ops/scripts/build_index.py` → 32 entities / 47 facts / 52 rels; `validate_graph.py` → PASS.

## acceptance
- A1 (6 broken fact-links): PASS — все разрешены. raw verdict: fact_0004 UNSUPPORTED (procollagen да / MMP нет); fact_0017 SUPPORTED→grounding-fail→UNSUPPORTED; fact_0006/0012 quota→NEEDS_MANUAL→возврат в карантин. Все 8 ссылок отвязаны.
- A2 (dangling entities): PASS — acne/photoaging (clinical_condition), pregnancy/lactation (contraindication_context) созданы; barrier-связь удалена (домен).
- A3 (валидатор +2 чека, FAIL до / PASS после): PASS — сырой вывод обоих прогонов показан.
- B1 (тип procedure в онтологии): PASS.
- B2 (diagram-маршрут + engine на 1 процедурной схеме): PASS — qa_svg_bounds PASS, текст изолирован, provenance записан.
- B3 (P011-исключение в AGENTS.md): PASS.
- C1–C3 (scarring ≥8): **FAIL/BLOCKED** — discovery выполнен, 5 кандидатов застейджены, но верификация невозможна (Gemini daily quota 429). scarring остаётся 7.
- C4 (fact_0015/0002 через гейт): **BLOCKED** — нужен судья (quota).
- Деки/слайды не трогались: PASS.

## deltas_vs_plan
- A1: ни один факт не восстановлен. fact_0004 — честный UNSUPPORTED (MMP-часть не в абстракте); fact_0017 — судья SUPPORTED, но grounding-guard отклонил сшитую цитату (корректно). fact_0006/0012 — судья недоступен (quota), возвращены в карантин, НЕ восстановлены. Реформулировать-и-восстановить нельзя без чистого прохода гейта (quota) — отложено в backlog (НЕ переписывал statement под источник, P009).
- Block C verification + C4 заблокированы дневной quota Gemini (429 PerDay, подтверждено дважды). Discovery (NCBI) не заблокирован → выполнен; 5 кандидатов застейджены к мгновенной верификации после сброса quota. Процедурные entity НЕ создавались (P008: только под прошедшие факты).
- Сканирование чужих .env на ключи — не выполнялось.

## project_state_snapshot
phase: Phase 8.7b (Graph Integrity + Procedure Ontology) — partial
completed: [A1 broken-links resolved, A2 condition/contraindication nodes + barrier removed, A3 validator hardened (FAIL→PASS), B1 procedure type, B2 diagram route+engine proof, B3 P011 scope; graph 32/47/52 validate PASS]
in_progress: []
blocked: [C1-C3 scarring procedural verification (Gemini daily quota); C4 fact_0015/0002 restore (quota)]
open_questions: [после сброса quota: verify fact_0075-0079 (procedure scarring) + создать procedure entities; восстановить ли fact_0004(procollagen)/0017 реформуляцией под одно предложение]

## decisions_logged
- DEC-021: Graph-integrity validator hardening — entity.fact_ids не должны указывать на quarantined facts; relationship from/to обязаны указывать на существующий entity-файл. Оба = FAIL в validate_graph.py.
- DEC-022: Онтология процедур — тип `procedure` (forbidden pubchem_cid/molecule_svg; visual route = source-grounded/Servier CC-BY, не prompt-gen). P011 ≥8 применяется к topical_active/procedure; clinical_condition/contraindication_context — exempt.

## next_recommended
- После сброса дневной quota Gemini (или платный ключ): `verify_gate --force-live` на fact_0075-0079 → создать procedure entities (subcision/fractional_laser/radiofrequency_microneedling) + treats-связи → scarring ≥8.
- C4: прогнать fact_0015 (источник тератогенности ретиноидов) и fact_0002 через гейт.
- Backlog: реформулировать fact_0004 (procollagen) и fact_0017 (single-sentence) и восстановить через гейт.
