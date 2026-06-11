# WALKTHROUGH — phase-8.7a-postacne-knowledge — 2026-06-11
status: done
scope: Сбор знаний «Постакне» (граф-only). Discovery + живой grounded-гейт. Утёкший ключ судьи разблокирован свежим ключом (в gitignored .env). Итог — 10 верифицированных фактов (9 SUPPORTED + 1 WEAK), тема deck-ready (P011). Дека НЕ создавалась.

## files_changed
- `tz_doc/YM_PROSKIN_TZ_Phase8.7a_PostacneKnowledge.md` — [NEW] ТЗ фазы сбора.
- `ops/scripts/one_time/collect_postacne_search.py` — [NEW] Живой PubMed-поиск (закалённый fetch из evidence.py).
- `ops/scripts/one_time/author_postacne_candidates.py` — [NEW] Идемпотентная авторизация 12 кандидатов + 12 источников; 6 тезисов переформулированы под single-sentence grounding.
- `ops/scripts/lib/evidence.py` — [SECURITY] Удалён утёкший хардкод-ключ; `get_gemini_api_keys()` читает проектный `.env` первым, отбрасывает leaked-ключ, фолбэк на env/pharma_v2.
- `.env` — [NEW, gitignored] Свежий GEMINI_API_KEY (в репозиторий НЕ коммитится).
- `.gitignore` — добавлены `.tmp/` и `.env`.
- `03_knowledge_graph/facts/fact_0063..0068, 0070..0073.json` — [NEW] 10 верифицированных фактов постакне.
- `03_knowledge_graph/entities/azelaic_acid.json`, `post_inflammatory_hyperpigmentation.json`, `atrophic_acne_scars.json` — [NEW] 3 сущности.
- `03_knowledge_graph/entities/niacinamide.json, adapalene.json, glycolic_acid.json` — backlink fact_ids.
- `03_knowledge_graph/relationships/rel_0050..0053.json` — [NEW] 4 связи `treats`.
- `03_knowledge_graph/sources.json` — +12 источников tier-A (SRC-A054..A065).
- `02_processing/verify/candidates/fact_0063..0074.json` — кандидаты (источник истины для перепрогона).
- `ops/logs/postacne_collection.md` — [NEW] Полный лог (blocker → resolve, таблица фактов, инцидент regression).
- `00_PROJECT_STATE/*` — current_state, active_tasks, known_problems, walkthrough.

## commands_run
- `python ops/scripts/one_time/collect_postacne_search.py` — 67 абстрактов (live).
- `python ops/scripts/one_time/author_postacne_candidates.py` — 12 кандидатов / 72 источника.
- `python ops/scripts/verify_gate.py <fact_0063..0074> --force-live` — итог 9 SUPPORTED + 1 WEAK (+1 deferred quota, +1 rejected redundant).
- `git checkout HEAD -- 03_knowledge_graph/facts/` — восстановление fact_0025 (ложный дроп regression).
- `python ops/scripts/build_index.py` → 28/47/53; `python ops/scripts/validate_graph.py` → PASS.

## acceptance
- ≥8 чистых фактов (P011): PASS — 10 (9 SUPPORTED + 1 WEAK).
- Живой grounded-гейт, заземление на абстракт (дословная цитата): PASS — guard корректно отклонял stitched-цитаты; тезисы сужены под одно предложение.
- Источник↔тезис сверен (P018): PASS.
- Сущности/связи/индекс (P008): PASS — +3 сущности, +4 связи, validate PASS.
- Дека НЕ создавалась: PASS.
- Безопасность ключа: PASS — утёкший ключ убран из исходника, новый только в gitignored .env.

## deltas_vs_plan
- Первый прогон гейта заблокирован утёкшим ключом (захардкожен в evidence.py). Разблокировано свежим ключом от пользователя (.env, gitignored) + приоритет .env в загрузчике.
- Grounding-guard отклонял stitched-цитаты судьи → 6 тезисов переформулированы под одно contiguous-предложение (содержательно те же, заземление честное).
- `fact_0074` отложен (Gemini daily quota 429); `fact_0069` отклонён как избыточный (не переформулировал).
- ИНЦИДЕНТ: `run_regression.py` пере-верифицировал весь граф (cache) и ложно выбросил `fact_0025`; восстановлено `git checkout HEAD`. Полный regression при quota-лимите судьи больше не запускать (занесено в known_problems).

## project_state_snapshot
phase: Phase 8.7a (Postacne Knowledge Collection) — DONE
completed: [discovery 67 абстрактов; 10 верифицированных фактов постакне; 3 сущности + 4 связи; security-фикс ключа + .env-загрузчик; граф 28/47/53 validate PASS; Постакне deck-ready P011]
in_progress: []
blocked: [8.1 — донорские каркасы заказчика (независимо); дека постакне ждёт нового пайплайна 8.4–8.6]
open_questions: [re-judge fact_0074 после сброса quota; рефактор run_regression на изолированные фикстуры]

## decisions_logged
- (без новых DEC; security-фикс ключа, .env-приоритет, инцидент regression — в known_problems.md и postacne_collection.md)

## next_recommended
- Постакне готова к деке по графу; собственно дека — после Slide Planning Engine (8.4–8.6) и утверждения каркасов (8.1).
- Рефактор `run_regression.py` на изолированные фикстуры (не мутировать боевой граф).
- При желании — re-judge fact_0074 после сброса дневной quota.
