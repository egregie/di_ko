# WALKTHROUGH — phase-8.7b-grade-fix — 2026-06-12
status: done
scope: Закрыта системная дыра grade-гейта ("journal article"/"review" → A). Аудит всех 55 active фактов: 32 (58%) несли завышенный grade — исправлено downgrade-only. fact_0017 A→C + честная формулировка. Добавлен grade-чек в validate_graph. Это аудит доказательной базы графа — факты не удалялись, только переоценён уровень.

## files_changed
- `ops/scripts/lib/evidence.py` — НОВОЕ `derive_grade(pubtype, abstract)` (design-based: A=RCT/MA/SR, B=controlled-non-random/cohort, C=narrative-review/case/questionnaire/uncontrolled/in-vitro/unclear); `evidence_ok` переписан под derive_grade + принимает abstract. DEC-025.
- `ops/scripts/verify_gate.py` — передаёт abstract в evidence_ok (write-time grade-гейт честен).
- `ops/scripts/validate_graph.py` — секция 6: FAIL если evidence_level факта выше grade, поддержанного дизайном источника.
- `ops/scripts/one_time/grade_audit.py` — НОВОЕ: read-only аудит + `--apply` (downgrade-only, audit_flag).
- `03_knowledge_graph/facts/*.json` — 32 факта: evidence_level понижен до derived + `audit_flag=grade_corrected` + блок `grade_audit{prev,derived,signal}`.
- `03_knowledge_graph/facts/fact_0017.json` — A→C + формулировка: "Patient-reported significant improvement in acne in over 90% of patients using a glycolic+salicylic serum (uncontrolled questionnaire study, n=66)." (claim-support из кэша, judge НЕ перезапускался).
- `03_knowledge_graph/graph_index.json` — пересобран.
- `00_PROJECT_STATE/*` — decisions_log (DEC-025), known_problems (grade-дыра + UTF-8 ревизия), current_state, active_tasks.

## commands_run
- `python ops/scripts/one_time/grade_audit.py` — read-only: таблица 55 фактов (cur/new/delta/signal/pubtype); 32 downgrade.
- spot-check абстрактов fact_0007/0024/0044/0058/0019/0077 — подтвердил: in-vitro / pig-skin / narrative / retrospective, НЕ RCT (downgrade корректен).
- `python ops/scripts/one_time/grade_audit.py --apply` — применил 32 downgrade.
- negative-control: fact_0007 как «A» → grade-чек FAIL=True; как «C» → FAIL=False (чек живой, не no-op).
- `python ops/scripts/build_index.py` → 35/55/55; `python ops/scripts/validate_graph.py` (с grade-чеком) → **PASS**.

## acceptance
- Пункт 1 (fact_0017 A→C + рамка): PASS — grade C, формулировка с "patient-reported / uncontrolled / n=66", без judge-перезапуска.
- Пункт 2 (системный фикс дыры): PASS — "journal article"/narrative "review" больше НЕ дают A; derive_grade по pubtype+дизайну, без хардкода PMID; unclear→C консервативно.
- Пункт 3 (аудит по всем active): PASS — **32/55 (58%) завышены**. current A:48/B:7 → derived A:22/B:2/C:31. Полная таблица с delta выведена (сырой вывод), каждый downgrade показан, не молча.
- Пункт 4 (known_problems): PASS — grade-дыра (DEC-025) + UTF-8 ревизия ранее-отброшенных (DEC-024).
- Пункт 5 (build+validate с grade-чеком, сырой вывод): PASS — 35/55/55, validate PASS; negative-control доказал чек.

## deltas_vs_plan
- Downgrade-only: апселл (B→A у fact_0015 как meta-analysis) НЕ применялся — занижение безопаснее завышения; fact_0015 оставлен B.
- Grade C не исключает факт из деки (P001 запрещает только D); счёт pigmentation(8)/scarring(9) НЕ изменился — факты на месте, изменён только уровень. Пересчёт scarring/pigmentation не потребовался (fact_0017 P009-чист, не удалён).
- 31 факт теперь честно C (narrative review / case series / uncontrolled / in-vitro) — это реальное состояние доказательной базы, не деградация: дыра маскировала его как A.

## project_state_snapshot
phase: Phase 8.7b grade-fix — done
completed: [derive_grade + evidence_ok fix, verify_gate abstract pass-through, validate_graph grade-check, full 55-fact audit (32 corrected downgrade-only), fact_0017 A→C+reframe, DEC-025, known_problems UTF-8 revision note; graph 35/55/55 validate PASS]
in_progress: []
blocked: []
open_questions: [ревизия ранее-отброшенных rejected/ фактов с Unicode-цитатами через UTF-8-гейт (DEC-024); ~31 C-grade фактов фреймить как обзор/неконтролируемые при сборке деки]

## decisions_logged
- DEC-025: design-based grade derivation + validate grade-check; 32/55 фактов исправлено.

## next_recommended
- При сборке деки Постакне фреймить C-grade факты честно (обзор/неконтролируемое/самооценка), не как RCT.
- Опц.: прогнать rejected/ через UTF-8-гейт — возможны ранее false-dropped факты.
- Phase 8.4–8.6 (Slide Planning Engine) + 8.1 (каркасы заказчика) — для собственно деки.
