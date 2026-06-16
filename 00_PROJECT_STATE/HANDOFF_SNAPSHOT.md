# HANDOFF SNAPSHOT — YM PROSKIN

> Канонический ground-truth для передачи в новый чат. Обновлять при каждом изменении графа.
> Проверено по файлам, не по пересказу. Последняя сверка: **2026-06-15** (Phase 8.2 closed).

## Phase 8.2 (Authority Layouts) — DONE 2026-06-15
- Design-system фаза, **граф НЕ тронут** (validate_graph PASS). DEC-026.
- `04_design_system/layouts_v2.json` (13 layouts / 4 класса), `deck_templates.json` (Ретиноиды 16, Постакне 18), `gen_layouts_v2.py`, `render_carcass.py`, `validate_layouts.py` (negative-control proven).
- 3 клиентских лого интегрированы (Zero Black; старые в `assets/logo/deprecated/`).
- Оба ПУСТЫХ каркаса отрендерены в PDF: `06_render/out/deck_template_{retinoids,postacne}.pdf`.
- **Next: заказчица утверждает 2 каркаса (по PDF) → Slide Planning 8.4–8.6.**

## Состояние графа (сверено с диска + graph_index.json)

| Метрика | Значение | Источник истины |
|---|---|---|
| Entities | **35** | `03_knowledge_graph/entities/*.json` |
| Facts (active) | **55** | `03_knowledge_graph/facts/*.json` |
| Relationships | **55** | `03_knowledge_graph/relationships/*.json` |
| Quarantine (rejected) | **28** | `02_processing/verify/rejected/*.json` |
| validate_graph.py | **PASS** | schema + cache-provenance + cross-ref + grade-consistency |
| graph_index.json | актуален (35/55/55) | `ops/scripts/build_index.py` |

## Grade-профиль (EBM evidence_level) — СВЕРЕНО

**A: 21 · B: 3 · C: 31** (сумма 55).

> ⚠️ Ревью Phase 8.7b называло «A:22 / B:2 / C:31». По файлам — **A:21 / B:3 / C:31**.
> Расхождение в один факт: `fact_0020` (glycolic_acid) имеет grade **B**, а не A.
> Три B-факта: `fact_0015` (retinoids, WEAK), `fact_0020` (glycolic_acid, NEEDS_MANUAL), `fact_0073` (atrophic_acne_scars, SUPPORTED).

## Claim-support verdict — НЕ равномерен по графу

| Verdict | Кол-во | Что значит |
|---|---|---|
| SUPPORTED | 18 | grounded-судья подтвердил claim↔abstract |
| WEAK | 7 | grounded-судья: слабая поддержка |
| **NEEDS_MANUAL** | **30** | grounded-судья НЕ подтверждал; прошли только старый `evidence_ok`-гейт |

- **«validate PASS» ≠ «все 55 grounded-верифицированы».** Валидатор не гейтит по `audit_verdict`.
- 25 фактов имеют grounded-вердикт; **30 — нет** (все 30 несут `evidence_ok=true`, т.е. источник/абстракт проверены старым гейтом до появления grounded-судьи).
- **30 NEEDS_MANUAL — это легаси-топики уже отрендеренных дек**: niacinamide (7), vitamin_c (7), peptides (6), exfoliants (3), salicylic (2), + tazarotene/retinyl_palmitate/mandelic/glycolic/SAP/glycolic_acid.
- **Фундамент Постакне (pigmentation 8 + scarring 9 = 17) — это и есть свежесудимый grounded-набор** (SUPPORTED/WEAK). Постакне deck-ready по факту, не на словах.

## Scope графа
Топик-деки (Retinoids, Vitamin C, Niacinamide, Exfoliants, Peptides) + Постакне (pigmentation + scarring) + процедуры (subcision, fractional_laser, radiofrequency_microneedling).

## Критический путь
- **8.2 DONE**: 2 каркаса отрендерены пустыми в PDF (см. выше). Геометрия взята из визуального языка v2 + брендбук-токенов — донор `hd_1` для каркасов НЕ понадобился, 8.1-блокер обойдён для этой цели.
- **[PENDING CLIENT]**: заказчица утверждает 2 каркаса по PDF (или даёт правки). Это гейт перед наполнением.
- **8.3–8.6**: Slide Planning Engine (детерминированный slot-filling, P022) — кода намеренно нет, ждёт утверждения каркасов. Наполнение обязано соблюсти `cell_provenance_required` (anti-fabrication из layouts_v2).
- **8.7**: сборка 2 дек на пайплайне (наполнение каркасов фактами графа через диаграммный движок).
- _8.1 (Layout Library из донора hd_1): для целей каркасов **снят 8.2**; если позже понадобится точная геометрия из реального hd_1 — донор по-прежнему отсутствует, `tpl1/tpl2` НЕ парсить._

## Бэклог (не блокеры)
1. **Grade-рамка в деке → поднять в QA-гейт деки** (rec #1): C-факт на слайде обязан нести маркер уровня доказательности; C-факт без рамки = FAIL. Зашить при Slide Planning (8.4–8.6).
2. **Ревизия rejected/ через UTF-8-гейт** (rec #2, DEC-024): часть из 28 карантинных могла быть ложно сброшена крашем кодировки до фикса; прогнать заново.
3. **Решение по 30 NEEDS_MANUAL легаси-фактам**: либо прогнать через grounded-судью (нужна квота Gemini), либо явно зафиксировать, что легаси-деки верифицированы старым `evidence_ok`-гейтом, и подавать соответственно.

## Источники истины (читать ИХ, не пересказы)
- `00_PROJECT_STATE/current_state.md` — полный лог фаз
- `00_PROJECT_STATE/known_problems.md` — блокеры/решённые проблемы
- `00_PROJECT_STATE/active_tasks.md` — чек-лист задач
- `00_governance/decisions_log.md` — DEC-021…DEC-025
- этот файл — числовой снимок для передачи

## Ключевые решения (свежие)
- **DEC-021** broken-link + dangling-rel чеки в validate_graph
- **DEC-022** procedure entity-type (без pubchem/svg-gen)
- **DEC-023** judge backoff чтит 429 retryDelay
- **DEC-024** UTF-8 stdout в verify_gate (краш маскировал вердикты как NEEDS_MANUAL)
- **DEC-025** `derive_grade` по дизайну + grade-consistency чек (закрыта grade-инфляция)
