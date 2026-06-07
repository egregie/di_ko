# YM PROSKIN — Phase 2.5: Collection Hardening

Версия: 1.0 · Дата: 2026-06-07 · Предыдущий: Phase 2 (срез принят, тег `phase-2-pilot-deck`).
Цель: превратить пост-фактум аудит (Phase 1.5) в **автоматический гейт на этапе записи**.
После этого спринта факт физически не может попасть в граф без подтверждённого,
поддерживающего источника. Это разблокирует масштабирование сбора (Phase 3).

Легенда: `[GUARD]` жёсткое ограничение · `[ВЕРИФ]` · `[НЕТ ДАННЫХ]`.

---

## Зачем
- Аудит вскрыл 25% брака (4/16) + 19% weak в Phase 1. Это дефект A02/A05, не разовая случайность.
- Сейчас проверка источника — отдельный ручной спринт. На тысячах фактов это не масштабируется.
- Нужно: сверка существования источника + claim-support встроены в пайплайн и срабатывают
  автоматически до записи в `03_knowledge_graph/facts/`.

---

## Блок 0 — Процессные правила (в `AGENTS.md`)
1. **P009 Verify-at-Write:** факт пишется в граф только после авто-проверки A05 (источник
   существует + абстракт поддерживает + evidence_level бьётся с pubtype). Fabricated/недоступный
   PMID = авто-reject.
2. **Скрипты постоянны:** пайплайн-скрипты живут в `ops/scripts/` и привязаны к SKILL.md
   соответствующей роли. `[GUARD]` Запрещено удалять рабочие скрипты после прогона
   (нарушение P006). Разовые миграции — в `ops/scripts/one_time/` с пометкой, не удаляются.

---

## Блок A — Вынести проверку в модуль
1. Рефактор `verify_sources.py` → переиспользуемый модуль `ops/scripts/lib/evidence.py`:
   - `check_source(pmid|doi) -> {exists, title, pubtype, abstract}` (eutils/Crossref, кэш+троттлинг);
   - `assess_claim(statement, abstract) -> verdict {SUPPORTED|WEAK|UNSUPPORTED|NEEDS_MANUAL}`
     (заземление ТОЛЬКО на текст абстракта);
   - `evidence_ok(level, pubtype) -> bool` (meta/RCT→A, cohort/guideline→B, consensus/case→C).
2. Кэш ответов eutils в `ops/cache/eutils/<pmid>.json` — не дёргать API повторно.

`[ВЕРИФ]` Лимит eutils без ключа ~3 req/s; при масштабе — добавить API-ключ. `[НЕТ ДАННЫХ]` ключ.

---

## Блок B — Встроить в A05 source-verify (гейт записи)
1. `ops/scripts/verify_gate.py`: вход — кандидат-факт (statement, sources, evidence_level);
   выход — `{verdict, evidence_ok}` + решение write|reject|needs_manual.
2. Правило `[GUARD]`:
   - `SOURCE_NOT_FOUND` или `UNSUPPORTED` → **reject** (в `02_processing/verify/rejected/`, не в граф);
   - `WEAK` → write с `confidence≤0.80` + флаг;
   - `NEEDS_MANUAL` → write с `"status":"needs_manual"` (ретривер для рендера такие не отдаёт);
   - `SUPPORTED` + `evidence_ok` → write.
3. Привязать `verify_gate.py` в `.agents/skills/source-verify/SKILL.md` (секция Execution):
   ни один факт не уходит в A06 kb-graph без прохождения гейта.

---

## Блок C — Подпереть A02 research-collect
1. `[GUARD]` Каждый собранный сырой факт обязан нести реальный PMID/DOI на этапе сбора.
   Нет идентификатора → не превращается в факт, уходит в `needs_manual`, не в граф.
2. Обновить `.agents/skills/research-collect/SKILL.md`: формат сырья включает обязательное поле
   `source_id` с PMID/DOI; запрет «голых» утверждений без источника.

---

## Блок D — Регресс-тест (доказать, что гейт автоматический)
1. Прогнать `verify_gate.py` по существующим 12 чистым фактам → все write/passthrough (регресс
   не сломан).
2. Подложить **намеренно битый** факт с выдуманным PMID (напр. `99999999`) → гейт обязан вернуть
   `SOURCE_NOT_FOUND` → reject **без участия человека**. Затем удалить тестовый факт из rejected.
3. Подложить факт с реальным PMID, но не относящимся к claim → ожидается `UNSUPPORTED` → reject.
Зафиксировать результаты в `ops/logs/hardening_regression.md`.

---

## Блок E — Definition of Done
- [ ] `lib/evidence.py` + `verify_gate.py` созданы; кэш и троттлинг работают.
- [ ] `verify_gate.py` привязан в SKILL.md A05; A02 требует PMID/DOI на сборе.
- [ ] Регресс: 12 чистых фактов проходят; битый PMID авто-reject; нерелевантный источник reject.
- [ ] `hardening_regression.md` с результатами 3 тестов.
- [ ] `P009 Verify-at-Write` и правило «скрипты не удалять» в `AGENTS.md`.
- [ ] `validate_graph.py` 0 ошибок; граф не изменился по составу (12 фактов).
- [ ] `walkthrough.md` по шаблону; коммит + тег `phase-2.5-hardening`.

---

## Блок F — Хвост по QA (из замечаний к Phase 2)
1. Восстановить `qa_audit.py` как **постоянный** скрипт `ops/scripts/qa_deck.py`, привязать к
   будущему A10; не удалять.
2. Добавить в него проверку реального применения шрифта: рендер слайда в PNG + детект, что
   текст отрисован Arimo (а не fallback). Если офлайн-вебфонт не грузится — встроить Arimo
   локально (ttf в `04_design_system/fonts/`). `[ВЕРИФ]`

---

## После Phase 2.5 (план, не для этого спринта)
- **Phase 3 — Scale Collection:** расширить граф на новые темы (AHA/BHA, витамин C, пептиды,
  аппараты) — теперь безопасно, гейт ловит брак автоматически.
- **Full Design System:** остальные layouts/компоненты, python-pptx как второй рендер.

## НЕ трогать
- Новые темы сбора (до Phase 3). `ontology_v1.json` — только через A07.

---

### Выход
Завершить `walkthrough.md` строго по `WALKTHROUGH_TEMPLATE.md`. В snapshot отразить результаты
регресс-теста (3 кейса: clean/fake-pmid/irrelevant) и состав графа после прогона.
