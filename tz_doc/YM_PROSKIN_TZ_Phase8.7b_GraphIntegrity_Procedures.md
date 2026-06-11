# ТЗ: Phase 8.7b — Целостность графа + Онтология процедур + Процедурный добор scarring

**Дата:** 2026-06-11
**Тег:** `phase-8.7b-integrity-procedures`
**Scope деки «Постакне»:** топика + процедуры (подтверждено заказчиком)
**Предусловие:** инвентаризация `postacne-inventory` выполнена (ground-truth получен)

---

## КОНТЕКСТ (ground-truth из инвентаризации, НЕ из устаревшего экспорта)

- Граф: **47 active фактов**. Постакне-домены уже населены: pigmentation 8 (deficit 0), scarring 7 (deficit 1 до P011 ≥8).
- Расхождение 42→36 **объяснено и закрыто** (−5 честных UNSUPPORTED на generalized gate: 0004/0006/0012/0017/0056; −1 ложный дроп fact_0025 от rate-limit, восстановлен `git checkout`). НЕ переоткрывать.
- **Обнаружены 2 реальных дефекта целостности** — блокируют чистый добор (см. Блок A).

Эта фаза — **groundwork для графа**. Деки/слайды НЕ создаются. Только граф + валидатор + онтология.

---

## БЛОК A — ЦЕЛОСТНОСТЬ ГРАФА (блокирующий; выполнять первым)

### A1. Broken fact-links: entity → quarantined fact
6 entity-файлов ссылаются на карантинные факты в своих `fact_ids`:

| Entity файл | Ссылка на quarantined fact |
|---|---|
| `retinoids.json` | fact_0004, fact_0006, fact_0012 |
| `retinol.json` | fact_0004 |
| `tretinoin.json` | fact_0006 |
| `retinaldehyde.json` | fact_0012 |
| `glycolic_acid.json` | fact_0017 |
| `exfoliants.json` | fact_0017 |

**Действие — для КАЖДОЙ ссылки, по порядку:**
1. Попытаться **восстановить факт** через гейт: переформулировать `statement` строго под реальный абстракт (raw fetch) → `verify_gate.py --force-live`. Если judge даёт SUPPORTED/WEAK с дословной цитатой из абстракта → факт возвращается в `facts/`, ссылка остаётся валидной.
2. Если восстановление не проходит (UNSUPPORTED) → **удалить fact_id из `fact_ids`** соответствующего entity. Факт остаётся в карантине.
3. [GUARD] НЕ подгонять statement под источник ради прохождения (анти-фабрикация P009). Честный UNSUPPORTED → удаление ссылки, не переписывание.
4. [ВЕРИФ] Показать для каждого: raw verdict judge + цитата (или её отсутствие), решение (restore/unlink).

### A2. Dangling relationships: relationship → missing entity
Связи указывают на несуществующие entity-файлы: `acne`, `photoaging`, `pregnancy`, `lactation`, `barrier`.

**Действие — классифицировать каждую отсутствующую сущность и разрешить:**
- `acne` → создать entity типа **clinical_condition** (предшествующее состояние; постакне-нарратив).
- `photoaging` → создать entity типа **clinical_condition**.
- `pregnancy`, `lactation` → создать entity типа **contraindication_context** (связаны с fact_0015 — противопоказание ретиноидов).
- `barrier` → проверить: это clinical_domain (барьерная функция) ИЛИ должна быть entity? Если только домен — **удалить связь** как ошибочную (домен ≠ узел). Показать решение.

[GUARD] Новые clinical_condition / contraindication_context entity создаются **без требования P011 ≥8** — это узлы-условия, не deck-ready темы. Зафиксировать в онтологии (см. Блок B), что P011-порог применяется только к topical_active / procedure темам, не к условиям-узлам.

### A3. Расширить валидатор
Дописать в `validate_graph.py` два детерминированных чека (сейчас отсутствуют — отсюда ложный PASS):
1. **FAIL**, если любой entity `fact_ids` ссылается на факт, физически лежащий в `02_processing/verify/rejected/`.
2. **FAIL**, если любая relationship `source`/`target` указывает на entity без файла в `entities/`.
[ВЕРИФ] Прогнать `validate_graph.py` ДО правок (показать новые FAIL) и ПОСЛЕ (PASS). Сырой вывод обоих прогонов.

---

## БЛОК B — ОНТОЛОГИЯ ПРОЦЕДУР (предусловие процедурного сбора)

### B1. Новый entity-тип `procedure` в `ontology_v1.json`
Топические активы имеют PubChem CID + molecule SVG (RDKit). Процедуры — нет. Добавить тип:

```
procedure:
  required: entity_id, type="procedure", name, mechanism, indication, evidence_level
  forbidden: pubchem_cid, molecule_svg  (процедура не молекула)
  evidence_level: enum [strong, moderate, limited]  (по доказательной базе)
  indication: список (atrophic_scars, rolling_scars, boxcar_scars, ice_pick_scars, PIE, PIH)
```

### B2. Diagram-маршрут процедур
[GUARD] Визуал процедур **НЕ через RDKit** (нет молекулы). Маршрут:
- `id_illustration` / `id_graph` для процедур → анатомические/механизм-схемы из **Servier Medical Art (CC-BY-4.0)** или source-grounded SVG (глубина воздействия по слоям кожи, схема субцизии).
- Гейт **P019** (provenance + license) применяется как есть. Атрибуция CC-BY обязательна.
- [GUARD] Запрещена prompt-генерация процедурного EBM-визуала (та же логика, что P021: научный визуал детерминированно/source-grounded, не из промпта).
- [ВЕРИФ] Прогнать diagram engine на ОДНОЙ процедурной схеме (например слои кожи + глубина фракц. лазера) — подтвердить, что `qa_svg_bounds` проходит и текст изолирован от графики (движок не тестировался вне молекул/рецепторных механизмов).

### B3. Зафиксировать P011-исключение
В `AGENTS.md`: P011 (deck-ready тема ≥8 фактов) применяется к темам типа `topical_active` и `procedure`. Узлы `clinical_condition` и `contraindication_context` — вспомогательные, порог не применяется.

---

## БЛОК C — ПРОЦЕДУРНЫЙ ДОБОР SCARRING (после A и B)

### C1. Цель
scarring: 7 → **≥8 active** с честным live-гейтом. Уровень детализации фактов — **обзорный**: механизм + эффективность + показание + уровень доказательности. БЕЗ клинических протоколов, параметров устройств, доз (образовательная дека, не методичка; обзорный уровень проще заземлить на абстракт).

### C2. Кандидаты (процедуры для атрофических постакне-рубцов)
Собрать кандидатов из (примерный пул, не лимит):
- субцизия (subcision) — rolling scars
- фракционный лазер (ablative CO2 / non-ablative Er:Glass) — atrophic scars
- микронидлинг (± RF) — atrophic scars
- TCA CROSS — ice-pick scars
- химический пилинг в кабинете (срединный) — texture/atrophic

[GUARD] Историч. rejection 25–33% → собрать **~5–6 кандидатов**, чтобы 3–4 прошли. НЕ останавливаться на ровно нужном числе — собрать с запасом, честно отбраковать.

### C3. Пайплайн (как Phase 6/8.7a)
1. Кандидаты → `verify_gate.py --force-live` (grounded judge: тезис + raw абстракт → verdict + дословная цитата).
2. SUPPORTED/WEAK → entity типа `procedure` (Блок B1) + relationships (procedure → indication clinical_condition).
3. UNSUPPORTED → карантин `rejected/`. [GUARD] 0% брака = красный флаг (P014).
4. `build_index.py` → `validate_graph.py` (с новыми чеками A3) PASS.
5. [ВЕРИФ] Показать raw verdict + цитату для КАЖДОГО кандидата (прошедшего и отбракованного).

### C4. Открытые из экспорта (закрыть попутно, связано с A2)
- **fact_0015 (беременность):** держится на Каплан-WEAK. Теперь есть entity `pregnancy` (A2) → подпереть источником, прямо поддерживающим противопоказание (тератогенность ретиноидов). Через гейт. Если источник не находится — оставить WEAK честно, audit_flag.
- **fact_0002 (третиноин связывается напрямую):** биологически верно, без источника → карантин. Найти источник через гейт ИЛИ оставить в карантине честно. НЕ восстанавливать без живой цитаты.

---

## DEFINITION OF DONE

- [ ] A1: все 6 broken fact-links разрешены (restore через гейт ИЛИ unlink), решение по каждому показано с raw verdict.
- [ ] A2: dangling entities созданы (clinical_condition / contraindication_context) ИЛИ связи удалены; `barrier` разобран.
- [ ] A3: `validate_graph.py` расширен 2 чеками; показан FAIL до / PASS после (сырой вывод).
- [ ] B1: тип `procedure` в `ontology_v1.json`.
- [ ] B2: diagram-маршрут процедур зафиксирован; engine прогнан на 1 процедурной схеме (qa_svg_bounds PASS).
- [ ] B3: P011-исключение в `AGENTS.md`.
- [ ] C1–C3: scarring ≥8 active; ~5–6 кандидатов собрано, честно отбраковано; raw verdict+цитата по каждому.
- [ ] C4: fact_0015 / fact_0002 разобраны через гейт (restore ИЛИ честный карантин).
- [ ] `build_index.py` + `validate_graph.py` финальный PASS (сырой вывод).
- [ ] walkthrough по шаблону `00_PROJECT_STATE/WALKTHROUGH_TEMPLATE.md`, тег `phase-8.7b-integrity-procedures`.
- [ ] Деки/слайды НЕ трогать (это graph-only фаза).

## КРАСНЫЕ ФЛАГИ (отклонить walkthrough если)
- «PASS» без сырого вывода judge и validate_graph.
- 0% rejection на процедурных кандидатах.
- Восстановление факта переписыванием statement под источник (фабрикация).
- Создание procedure entity с молекулой/CID.
- Любой слайд/дека тронуты в graph-only фазе.
