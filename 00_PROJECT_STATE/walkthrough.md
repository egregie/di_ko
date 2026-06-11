# WALKTHROUGH — phase-8.0-twostage-groundwork — 2026-06-11
status: done
scope: Интеграция консолидированного кросс-ревью (Gemini×Grok+GPT) о двухэтапной архитектуре (Antigravity → Claude Design): верификация входных допущений по репо, закрытие конфликтов, фиксация роадмапа Phase 8, регистрация принципов P021–P023 и решений DEC-017…DEC-020, схема placeholder-контракта, обновление агента A09 и скиллов.

## files_changed
- `tz_doc/YM_PROSKIN_TZ_Phase8_TwoStage_SlidePlanning.md` — [NEW] ТЗ Phase 8: вердикт верификации допущений, архитектура, контракт, роадмап 8.0–8.7, QA-гейты.
- `00_governance/schemas/placeholder_contract.json` — [NEW] Схема контракта плейсхолдеров (composite ID, bounds+relative_bounds, prompt, routing_rules, source_refs).
- `00_governance/AGENTS.md` — Добавлена секция Two-Stage Render Architecture + принципы P021 (контракт и маршрутизация), P022 (детерминированный slot-filling), P023 (scope 13–20).
- `00_governance/naming.md` — §1.6 Placeholder ID (`id_{type}_s{NN}_{slug}`), §1.7 Layout ID (`layout_*`, зеркала `_left/_right`, alias для v1-имён).
- `00_governance/prompts/A09_architect.txt` — Архитектор переведён на slot-filling из утверждённого пула, эмиссию контракта, лимиты max_chars, scope 13–20.
- `.agents/skills/slide-plan/SKILL.md` — [NEW] Скилл Slide Planning Engine (протокол: intent → deterministic select → slots → contract).
- `07_skills_registry/slide-plan.json` — [NEW] Регистрация скилла.
- `00_PROJECT_STATE/decisions_log.md` — DEC-017…DEC-020.
- `00_PROJECT_STATE/next_steps.md` — Старый «Phase 8 — Advanced Custom Layouts» заменён роадмапом двухэтапной архитектуры.
- `00_PROJECT_STATE/known_problems.md` — Блокеры Phase 8 (нет геометрии в layouts.json, нет доноров, нет утверждения каркасов, легаси-деки <13 слайдов, Постакне 0 фактов) + закрытые «не-проблемы» из устаревшего экспорта.
- `00_PROJECT_STATE/current_state.md` — Метаданные → Phase 8; бэкфилл дрейфа (7.1, 7.2, integrity-rollback, gate-generalization, brand chrome из git-истории); запись Phase 8.0.
- `00_PROJECT_STATE/active_tasks.md` — 5 закрытых задач 8.0 + 10 задач 8.1–8.7.

## commands_run
- Чтение/аудит: `layouts.json` (10 layout'ов, только name+description), grep доноров `hd_1|tpl1|tpl2|Постакне` (в репо отсутствуют), grep `[Placeholder]` (конвенция qa_deck.py:244, не баг) — состояние-changing команд нет, только записи файлов выше.
- `python ops/scripts/validate_graph.py` — PASS (граф не затронут, регресс-контроль).

## acceptance
- Допущения кросс-ревью верифицированы по диску (layouts.json, доноры, баги рендера): PASS
- Конфликт §7.3 (Claude Design vs EBM-провенанс) закрыт маршрутизацией по типу placeholder (DEC-017/P021): PASS
- Роадмап зафиксирован (ТЗ + next_steps, порядок GPT: Contract → Approval → Taxonomy → Planner → Renderer → Claude Design): PASS
- Агенты/скиллы/воркфлоу обновлены (A09, slide-plan, AGENTS.md pipeline): PASS
- Код не написан преждевременно (GPT Ошибка №2): slide_planner.py/slide_intents.json/layouts v2 отложены до утверждения каркасов: PASS
- Существующие 5 дек и их QA не затронуты: PASS

## deltas_vs_plan
- Кросс-ревью считало layouts.json готовой библиотекой (18 шаблонов с bounds) — опровергнуто аудитом (10 описательных). Роадмап сдвинут: геометрия строится в 8.1, а не «уже есть».
- «Баг литерала [Placeholder]» и «footer-overlap» из устаревшего экспорта не воспроизведены — исключены из роадмапа как баги; конвенция мигрирует в 8.5.
- «Консолидация в 2 деки» не выполнена как разрушение 5 легаси-дек: пилоты нового пайплайна = Retinoids-расширение + Постакне; легаси живут до миграции (DEC-020).
- slide_intents.json и зеркальные layout'ы НЕ созданы в этом прогоне (по плану §9 они после утверждения каркасов) — отражено в роадмапе.

## project_state_snapshot
phase: Phase 8.0 (Two-Stage Architecture — Groundwork)
completed: [верификация допущений, DEC-017…020, P021–P023, схема контракта, naming §1.6/1.7, скилл slide-plan, промпт A09, роадмап, бэкфилл current_state]
in_progress: []
blocked: [8.1: донорские файлы hd_1 + design concept от заказчика; утверждение 2 каркасов заказчиком]
open_questions: [состав интентов пилотных дек (из контента, не из 12 универсальных); объём сбора знаний Постакне до ≥8 фактов; судьба 5 легаси-дек после миграции]

## decisions_logged
- DEC-017: Двухэтапная архитектура принята; маршрутизация placeholder по типу (logo→SVG-реестр, illustration/graph→детерминированный движок, img→генерация/сток) — закрывает конфликт с EBM-провенансом.
- DEC-018: Аудит layouts.json — Template Library v1 не существует (10 описательных layout'ов без геометрии); утверждение каркасов = предусловие Planning Engine.
- DEC-019: Детерминированный slide planning — LLM запрещён для выбора композиции; dual-хранение bounds px + relative.
- DEC-020: Анти-переусложнение — урезанная таксономия под пилотные деки; scope-гейт 13–20 (P023) с первой Phase-8 деки; [Placeholder]-литерал = конвенция, не баг.

## next_recommended
- Запросить у заказчика донорские файлы (`hd_1`, design concept) и утверждение 2 каркасов — единственный блокер 8.1.
- Параллельно (не блокируется): отдельное ТЗ на сбор знаний «Постакне» до ≥8 верифицированных фактов (P011) — длинный lead time из-за live-верификации.
- После разблокировки 8.1: Layout Library v2 → slide_intents.json (урезанная) → slide_planner.py, строго в этом порядке.
