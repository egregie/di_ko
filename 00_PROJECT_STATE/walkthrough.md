# WALKTHROUGH — phase-8.7b-integrity-procedures — 2026-06-12
status: done
scope: Целостность графа (A) + онтология процедур и diagram-маршрут (B) + процедурный добор scarring (C) выполнены. Дефицит scarring закрыт (7→9, ≥8 P011) двумя верифицированными процедурными фактами; 3 избыточных кандидата отложены на quota. C4 разобран честно. Деки/слайды не трогались (graph-only).

## files_changed
- `ops/scripts/validate_graph.py` — A3: +2 чека (entity.fact_ids→rejected = FAIL; relationship from/to→missing entity = FAIL). DEC-021.
- `03_knowledge_graph/entities/retinoids.json, retinol.json, tretinoin.json, retinaldehyde.json, glycolic_acid.json, exfoliants.json` — A1: отвязаны 8 broken fact-links (0004/0006/0012/0017).
- `03_knowledge_graph/entities/acne.json, photoaging.json` — [NEW] A2: clinical_condition.
- `03_knowledge_graph/entities/pregnancy.json, lactation.json` — [NEW] A2: contraindication_context.
- `03_knowledge_graph/relationships/rel_0042.json` — A2: УДАЛЁН (niacinamide→barrier = домен, не узел).
- `00_governance/ontology_v1.json` — B1: тип `procedure` (+clinical_condition, contraindication_context) + procedure-схема (forbidden cid/molecule, evidence strong/moderate/limited) + p011_scope. v1.0→1.1. DEC-022.
- `00_governance/AGENTS.md` — B3: P011-исключение (порог только для topical_active/procedure).
- `ops/scripts/one_time/gen_procedure_diagram.py` + `04_design_system/assets/mechanisms/procedure_depth_skin_layers.svg` — B2: engine на процедурной схеме, qa_svg_bounds PASS.
- `04_design_system/assets/asset_provenance.json` — B2: provenance схемы (generated/own, P019).
- `ops/scripts/one_time/collect_procedure_search.py` + `author_procedure_candidates.py` — C2: discovery + стейджинг 5 кандидатов.
- `03_knowledge_graph/facts/fact_0075.json, fact_0078.json` — [NEW] C: верифицированы SUPPORTED (subcision, fractional CO2 laser).
- `03_knowledge_graph/entities/subcision.json, fractional_laser.json` — [NEW] C: procedure entities (P008).
- `03_knowledge_graph/relationships/rel_0054.json, rel_0055.json` — [NEW] C: procedure -treats-> atrophic_acne_scars.
- `02_processing/verify/candidates/fact_0075..0079.json` — staged; 0076/0077/0079 ждут судью (quota).
- `03_knowledge_graph/sources.json` — +5 источников tier-A (SRC-A066..A070).
- `ops/scripts/lib/evidence.py` — DEC-023: backoff по retryDelay (≤65s, 6 попыток) вместо bail на "PerDay".
- `00_PROJECT_STATE/*`, `00_governance/...` — состояние, решения.

## commands_run
- `python ops/scripts/validate_graph.py` — ДО фиксов: FAIL (8 broken links + 29 dangling rels, сырой вывод показан). ПОСЛЕ: PASS.
- `verify_gate fact_0004 --force-live` → UNSUPPORTED (abstract: procollagen да, MMP нет — цитата/reason показаны) → unlink.
- `verify_gate fact_0017 --force-live` → judge SUPPORTED, grounding-guard отклонил stitched-цитату → UNSUPPORTED → unlink.
- `verify_gate fact_0006/0012 --force-live` → 429 (quota) → NEEDS_MANUAL → возврат в карантин + unlink.
- `gen_procedure_diagram.py` → qa_svg_bounds PASS.
- `collect_procedure_search.py` → 26 абстрактов (live NCBI).
- `verify_gate fact_0075 --force-live` → SUPPORTED, quote "Subcision is a surgical technique for managing atrophic acne scars." → write.
- `verify_gate fact_0078 --force-live` → SUPPORTED, quote "Ablative fractional carbon dioxide laser is an effective therapy for the treatment of acne scars." → write.
- `verify_gate fact_0076/0077/0079 --force-live` (backoff 48–60s ×5–6) → 429 daily exhausted → NEEDS_MANUAL → удалены из графа, staged.
- `build_index.py` → 34 entities / 49 facts / 54 rels; `validate_graph.py` → PASS.

## acceptance
- A1 (6 broken fact-links): PASS — все 8 ссылок разрешены (unlink); raw verdict по каждому факту показан.
- A2 (dangling entities): PASS — acne/photoaging (clinical_condition), pregnancy/lactation (contraindication_context); barrier-связь удалена.
- A3 (валидатор +2 чека, FAIL до / PASS после): PASS — сырой вывод обоих прогонов.
- B1 (procedure в онтологии): PASS. B2 (diagram-маршрут + engine, qa_svg_bounds): PASS. B3 (P011-исключение): PASS.
- C1–C3 (scarring ≥8): PASS — дефицит закрыт (baseline 7 → 9) двумя SUPPORTED процедурными фактами с дословными цитатами (fact_0075, fact_0078); создано 2 procedure entities + 2 treats-связи. 5 кандидатов собрано (запас); 3 (0076/0077/0079) отложены на quota — НЕ в графе, raw NEEDS_MANUAL показан.
- C4: PASS (честная развязка) — fact_0015 остаётся WEAK (re-verify отложен на quota; entity pregnancy теперь существует, связи валидны); fact_0002 остаётся в карантине (UNSUPPORTED, ни на что не ссылается).
- Деки/слайды не трогались: PASS.

## deltas_vs_plan
- A1: ни один факт не восстановлен — честные UNSUPPORTED (0004 MMP-часть не в абстракте; 0017 grounding-fail на сшитой цитате) и quota-NEEDS_MANUAL (0006/0012). Реформулировать-восстановить нельзя без чистого прохода гейта → backlog. P009 не нарушен (statement не переписывался под источник).
- C: собрано 5 кандидатов (запас по TZ). 2 прошли SUPPORTED → дефицит scarring закрыт. 3 (subcision×2 surplus, RF) отложены на дневной quota Gemini — НЕ оставлены в графе как verified (P007/P013). Rejection rate по 5 НЕ установлен (3 deferred, не judged) — честно отмечено; красный флаг «0% rejection» не применим (deferred ≠ passed).
- C4: оба факта разобраны честным бездействием (TZ допускает «оставить WEAK/карантин честно»); живой re-verify fact_0015 невозможен (quota).
- Инфраструктурный фикс evidence.py backoff (DEC-023) — вне исходного плана, по D3 (root cause квота-сбоев).

## project_state_snapshot
phase: Phase 8.7b (Graph Integrity + Procedure Ontology) — done
completed: [A1 unlinks, A2 condition/contraindication nodes + barrier removed, A3 validator hardened (FAIL→PASS), B1 procedure type, B2 diagram route+engine, B3 P011 scope, C scarring deficit closed (2 procedure facts + entities + rels), C4 honest resolution, evidence.py backoff fix; graph 34/49/54 validate PASS]
in_progress: []
blocked: []
open_questions: [re-judge surplus fact_0076/0077/0079 + fact_0074 + C4 re-verify fact_0015 when Gemini quota resets / paid key; backlog restore fact_0004(procollagen)/0017 via single-sentence reformulation]

## decisions_logged
- DEC-021: validator hardening (broken fact-link + dangling relationship checks).
- DEC-022: procedure ontology (type + schema; forbidden cid/molecule; P011 scope).
- DEC-023: judge backoff on 429 retryDelay instead of daily-bail.

## next_recommended
- При сбросе quota: verify_gate на staged 0076/0077/0079 (+ создать radiofrequency_microneedling если 0079 пройдёт); закрыть fact_0074; re-verify fact_0015 на источнике тератогенности.
- Двухэтапный пайплайн (8.4–8.6) + утверждение каркасов (8.1) — для собственно деки Постакне (топика+процедуры теперь deck-ready по графу).
