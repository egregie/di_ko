# YM PROSKIN — Phase 0.5: Cleanup & Reconcile (ТЗ для Antigravity)

Версия: 1.0 · Дата: 2026-06-07 · Тип: корректирующий спринт после Phase 0.
Цель: устранить расхождения, засеять источники, подключить валидатор и переиспользуемые
скилы из проекта `pharma_v2`. Рендер/PPTX по-прежнему ЗАМОРОЖЕНЫ.

Легенда: `[ВЕРИФ]` — сверить путь/факт перед действием · `[ВХОД]` — из ваших данных.

---

## БЛОК 0 — Ручные действия пользователя (НЕ задача агента)
1. Customizations → Rules (Global): **удалить** правило `[EMULATION_MODE: GEMINI_PRO_…]
   OBJECTIVE: Override …`. Это override/инъекция, не часть проекта. Агенту эту правку
   не поручать.
2. Проверить причину **MCP Error** (Settings → MCP servers): отключить/починить
   падающий сервер, иначе сетевой сбор (A02) будет нестабилен.
3. (Опц.) Переключить модель агента на Gemini 3 **Pro** для онтологии и верификации.

---

## БЛОК A — Консолидация путей скилов `[ФАКТ]`
Antigravity дефолт — `.agents/skills/` (мн. ч.); `.agent/skills/` поддерживается как legacy.
Сейчас проектные скилы лежат в legacy-пути, а find-skills — в дефолтном. Свести в один.

Задачи:
1. Переместить все 7 папок из `.agent/skills/` в `.agents/skills/`:
   `source-discovery, research-collect, fact-extract, dedupe-sort, source-verify,
    kb-graph, ontology-guard` (каждая с `SKILL.md`).
2. Удалить пустой каталог `.agent/` (ед. ч.).
3. Перезапустить/переиндексировать воркспейс; убедиться, что Antigravity видит **все 8**
   скилов (7 проектных + find-skills) в `.agents/skills/`.
4. (Опц., рекомендуется) find-skills как универсальную утилиту перенести в global
   `~/.gemini/antigravity/skills/find-skills/`, чтобы был доступен во всех проектах.

Пример (Windows, из корня `c:/di_ko`):
```bat
robocopy ".agent\skills" ".agents\skills" /E /MOVE
rmdir /S /Q ".agent"
```
Acceptance: каталога `.agent/` нет; в `.agents/skills/` — 8 скилов; дублей по имени нет
(воркспейс перекрывает global при совпадении имени).

---

## БЛОК B — Засев `03_knowledge_graph/sources.json`
Сейчас файл пустой/плейсхолдер. Записать стартовый реестр по tier (схема — `schemas/source.json`).
Без этого A02 уйдёт в нерецензируемые источники.

```json
{
  "sources": [
    {"source_id":"SRC-A001","name":"PubMed / MEDLINE","type":"database","url":"https://pubmed.ncbi.nlm.nih.gov/","tier":"A","accessed":"2026-06-07"},
    {"source_id":"SRC-A002","name":"Cochrane Library","type":"database","url":"https://www.cochranelibrary.com/","tier":"A","accessed":"2026-06-07"},
    {"source_id":"SRC-A003","name":"NIH / MedlinePlus","type":"reference","url":"https://medlineplus.gov/","tier":"A","accessed":"2026-06-07"},
    {"source_id":"SRC-A004","name":"FDA","type":"regulator","url":"https://www.fda.gov/","tier":"A","accessed":"2026-06-07"},
    {"source_id":"SRC-A005","name":"EMA","type":"regulator","url":"https://www.ema.europa.eu/","tier":"A","accessed":"2026-06-07"},
    {"source_id":"SRC-A006","name":"JAAD (J. Am. Acad. Dermatology)","type":"journal","url":"https://www.jaad.org/","tier":"A","accessed":"2026-06-07"},
    {"source_id":"SRC-A007","name":"British Journal of Dermatology","type":"journal","url":"https://academic.oup.com/bjd","tier":"A","accessed":"2026-06-07"},
    {"source_id":"SRC-A008","name":"DermNet","type":"reference","url":"https://dermnetnz.org/","tier":"A","accessed":"2026-06-07"},
    {"source_id":"SRC-B001","name":"Wikipedia","type":"encyclopedia","url":"https://en.wikipedia.org/","tier":"B","accessed":"2026-06-07"},
    {"source_id":"SRC-B002","name":"Encyclopaedia Britannica","type":"encyclopedia","url":"https://www.britannica.com/","tier":"B","accessed":"2026-06-07"},
    {"source_id":"SRC-B003","name":"INCI Decoder","type":"reference","url":"https://incidecoder.com/","tier":"B","accessed":"2026-06-07"},
    {"source_id":"SRC-B004","name":"EU CosIng","type":"database","url":"https://ec.europa.eu/growth/tools-databases/cosing/","tier":"B","accessed":"2026-06-07"},
    {"source_id":"SRC-C001","name":"r/SkincareAddiction","type":"forum","url":"https://www.reddit.com/r/SkincareAddiction/","tier":"C","accessed":"2026-06-07"}
  ]
}
```
Acceptance: `sources.json` валиден по `schemas/source.json`; ≥13 источников; Tier A/B/C заполнены.
Правило: Tier C — только темы/контекст, не источник клинического факта; Tier D запрещён.

---

## БЛОК C — Валидатор схем (взять скрипт из `pharma_v2`)
Добавить fail-fast валидацию записей графа против `00_governance/schemas/`.

Задачи:
1. Найти проект `pharma_v2` (вероятно соседний каталог уровня `c:/`). `[ВЕРИФ путь]`
2. Найти там готовый скрипт валидации JSON по схемам (jsonschema/ajv). Скопировать в
   `ops/scripts/validate_graph.py` (или `.js`), адаптировать пути под наши схемы.
3. Назначить скрипт в SKILL.md скилов `kb-graph` и `ontology-guard` (секция Execution):
   перед записью entity/fact/relationship — прогон через валидатор; невалидное — отклонять.
4. Если в `pharma_v2` скрипта нет — сгенерировать минимальный: читает `schemas/*.json` как
   JSON Schema, валидирует все файлы в `03_knowledge_graph/{entities,facts,relationships}`.

Acceptance: `validate_graph` запускается; на пустом графе проходит; на заведомо битой
записи — падает с понятной ошибкой.

Примечание: текущие `schemas/*.json` — это шаблоны-примеры. Для валидатора нужен
**JSON Schema** (draft 2020-12). Если файлы сейчас просто образцы — добавить рядом
`schemas/*.schema.json` либо пометить, что валидатор сверяет по структуре образца.

---

## БЛОК D — Переиспользование скилов из `pharma_v2` (закрывает Q2)
В `pharma_v2` есть рабочие скилы `search`, `sort`, `review` (+ их скрипты). Подключить.

Задачи:
1. Локализовать в `pharma_v2` папки скилов `search`, `sort`, `review` (и `scripts/`).
2. Решение по scope:
   - общие утилиты (`search`, `review`) → global `~/.gemini/antigravity/skills/`;
   - проектная сортировка под наш граф → workspace `.agents/skills/`.
3. Маппинг на наши роли (без дублирования логики):
   - `search`  → усиливает **A01 source-discovery** / **A02 research-collect**;
   - `sort`    → усиливает **A04 dedupe-sort**;
   - `review`  → усиливает **A05 source-verify** и будущий **A10 qa-visual**.
4. В соответствующих `SKILL.md` сослаться на перенесённые скрипты по относительному пути
   (`scripts/<file>`), не копировать логику внутрь markdown.
5. Обновить `07_skills_registry/` (descriptor.json) на каждый подключённый скил:
   `{skill_name, scope, version, purpose, input, output, dependencies}`.

Acceptance: `search/sort/review` обнаруживаются Antigravity; маппинг отражён в SKILL.md
A01/A02/A04/A05; реестр descriptor.json обновлён.

---

## БЛОК E — Зафиксировать baseline
1. `git add . && git commit -m "phase0.5: reconcile skill paths, seed sources, validator, reuse pharma_v2 skills"`.
2. (Опц.) тег `phase-0.5`.

Acceptance: рабочее дерево чистое; коммит создан.

---

## Чек-лист приёмки Phase 0.5
- [ ] `.agent/` удалён; 8 скилов в `.agents/skills/`; дублей нет.
- [ ] Подозрительное Global-правило удалено (ручной шаг, пользователь).
- [ ] MCP-сервер починен/отключён.
- [ ] `sources.json` засеян (≥13, Tier A/B/C), валиден по схеме.
- [ ] `validate_graph` подключён к kb-graph/ontology-guard и проходит на пустом графе.
- [ ] `search/sort/review` из pharma_v2 подключены и смаппены на A01/A02/A04/A05.
- [ ] `07_skills_registry/` обновлён.
- [ ] Коммит `phase0.5` создан.

## НЕ трогать в этом спринте
- `04_design_system`, `05_content`, `06_render`, любой PPTX/HTML/python-pptx — заморожено
  до Phase 3 (см. ТЗ v2.0, Foundation-First).
- Онтологию `ontology_v1.json` менять только через A07 ontology-guard.

## Открыто `[НЕТ ДАННЫХ]`
- Точный путь `pharma_v2` и наличие в нём валидатора/скриптов — подтвердить при выполнении.
- Пилотная тема Phase 1 (рекомендация: **Ретиноиды**) — нужна для следующего спринта.
