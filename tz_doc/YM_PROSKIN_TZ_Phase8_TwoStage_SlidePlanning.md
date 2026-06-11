# YM PROSKIN — Phase 8: Two-Stage Architecture (Antigravity → Claude Design) + Slide Planning Engine

Версия: 1.0 · Дата: 2026-06-11 · Предыдущий: `gate-generalized` + Phase 7.2 (Graph Integrity) + Brand Chrome Layer.
Источник: консолидация кросс-ревью Gemini×Grok + GPT-ревью (`YM_PROSKIN_SlidePlanning_Consolidated.md`),
сверенная с фактическим состоянием репозитория 2026-06-11.

> Свежей сессии: прочитай `00_PROJECT_STATE/` и `AGENTS.md`. Принципы P021–P023 и DEC-017…DEC-020 — действующие.

Легенда: `[GUARD]` — жёсткое правило · `[ВЕРИФ]` — требует проверки · `[BLOCKED]` — ждёт внешний вход.

---

## 0. Вердикт верификации входных допущений (выполнено 2026-06-11)

Кросс-ревью строилось на допущениях. Проверка по репозиторию:

| Допущение кросс-ревью | Факт в репо | Вердикт |
|---|---|---|
| «`layouts.json` = Template Library v1, 18 шаблонов с bounds» | [FACT] `04_design_system/layouts.json` = 10 layout'ов, **только name+description, без геометрии** | **ОПРОВЕРГНУТО** (GPT Ошибка №1 подтверждена) |
| «Донор `hd_1` доступен для парсинга» | [FACT] `hd_1`, `tpl1/tpl2`, `design concept`, `Постакне_nov20.pdf`, `Retinoid.pdf` в репо **отсутствуют** | **[BLOCKED]** — запросить файлы |
| «Баг: литерал `[Placeholder]` печатается на слайдах» | [FACT] Это действующая конвенция: `qa_deck.py:244` **требует** префикс `[Placeholder]` в caption | **НЕ БАГ** — конвенция, заменяется в 8.5 |
| «Footer-overlap» | [FACT] Текущие QA-гейты (bounds/overlap) проходят 100% на всех 5 деках | **НЕ ВОСПРОИЗВЕДЕНО** (устаревший экспорт) |
| «5 дек по 7–8 слайдов (scope-дрейф)» | [FACT] 5 активных дек (retinoids_v2, vitamin_c, niacinamide, exfoliants, peptides) по 7–10 слайдов | **ПОДТВЕРЖДЕНО** — все нарушат новый гейт 13–20 |
| «Постакне — следующая дека» | [FACT] В графе 0 фактов по постакне; P011 требует ≥8 верифицированных | **[BLOCKED]** — нужна фаза сбора знаний |

**Главный вывод:** Slide Planning Engine действительно недостающий слой, но строить его можно только
после (а) утверждения каркасов заказчиком и (б) создания геометрического слоя layouts v2.
Порядок GPT принят: **Contract → Approval/Geometry → Taxonomy → Planner → Renderer → Claude Design.**

---

## 1. Архитектура (принято, DEC-017)

### Этап 1 — Antigravity (этот репозиторий)
Выпускает **designer-ready PPTX**: структура, контент (верифицированный граф), композиция,
типографика, цветовая система, layout — полностью готовы. Все будущие визуалы существуют
только как **placeholder-блоки**: зарезервированные области с composite ID и промптом.

### Этап 2 — Claude Design
Получает PPTX + `placeholder_contract.json` и выполняет **только бинарную замену плашек**,
без изменения структуры/контента. Что и как заменять — определяет контракт, не интерпретация.

### `[GUARD]` Маршрутизация по типу placeholder (утверждено заказчиком проекта)

| Тип | Маршрут | Обоснование |
|---|---|---|
| `id_logo` | **Фиксированные брендовые SVG** из `04_design_system/assets/logo/` (logo_registry) | Лого не генерируются никогда |
| `id_illustration` | **Детерминированный движок** `gen_diagrams.py` (параметрика + source-grounded из графа) | P019/P020; prompt-генерация = регресс к фабрикации биологии |
| `id_graph` | **Детерминированный движок** (данные только из верифицированных фактов) | Числа/оси из графа, не из LLM |
| `id_img` | **Claude Design: генерация/сток** (lifestyle, упаковка, врач, кожа) | Декоративный слой; запись в `asset_provenance.json` обязательна (P019) |

Это закрывает конфликт §7.3 кросс-ревью: placeholder-архитектура Этапа 1 — да;
Этап-2 заполнение EBM-визуала через Claude Design — **нет**.

---

## 2. Контентные блоки (типографическая система слайда)

| Блок | Назначение | Требования |
|---|---|---|
| `display_h1` | Титул, крупные разделители | — |
| `h2` | Заголовок раздела/темы | ≤50 символов (атомарность, как у A09) |
| `h3` | Подзаголовок: модули, карточки, сравнения | — |
| `body` | Основной текст | line-height **1.7**, без перегруженных абзацев |
| `body_sm` | Описания, комментарии, подписи к изображениям | — |
| `caption` | Источники (PMID), служебные пометки, коды | коды — **monospace** |

Шрифт — Arimo (локальный, offline-first), палитра — `design-tokens.json`, Zero Black — без изменений.

---

## 3. Placeholder Contract Layer (DEC-017, схема создана)

Схема: `00_governance/schemas/placeholder_contract.json`. Один файл контракта на деку:
`05_content/contracts/<deck_id>_contract.json`.

Каждый placeholder:
- `placeholder_id` — **composite ID** `id_{type}_s{NN}_{slug}` (напр. `id_illustration_s04_moa`); формат в `naming.md` §1.6;
- `slide_id`, `type` (`img|graph|illustration|logo`), `route` (см. §1), `owner`;
- `bounds` (px, канва 1280×720) **и** `relative_bounds` (0.0–1.0) — px остаётся для обратной совместимости;
- `aspect_ratio`, `prompt{}` (title, style, composition, palette=tokens, labels, background);
- `source_refs[]` — для `graph`/`illustration` обязательны fact_id из активного графа (P018);
- `priority` (`required|optional`), `status` (`open|filled|rejected`).

`[GUARD]` Claude Design читает только контракт; placeholder без записи в контракте = QA FAIL.
`[GUARD]` `route` обязан соответствовать `type` по таблице §1 — расхождение = QA FAIL.

---

## 4. Slide Planning Engine (детерминизм, DEC-019)

```
Knowledge Graph
  → Content Generator (verify gate, лимиты символов)
  → Slide Intent Detection (rule-based: keyword + структурные метрики)
  → Template Selection Engine (slide_intents.json, детерминированно)
  → Slot Filling (bounds + relative_bounds + composite IDs + prompt)
  → PPTX/HTML Renderer (Arimo lh1.7 + серые плашки с composite ID)
  → QA (bounds/overlap/scope/contract)
  → Claude Design (Этап 2: бинарная замена по контракту, маршрутизация §1)
```

`[GUARD]` LLM **запрещён** для генерации и выбора композиции. Разрешён только выбор
`layout_id` из утверждённого пула + детерминированное дерево по `structural_metrics`
(text_nodes, lists_count, list_elements, has_visual, visual_type, visual_count).
`[GUARD]` Превышение `max_chars` слота = ошибка валидации на Этапе 1, **до** рендера.
Каскад выбора: `primary → secondary → layout_text_dense_fallback` (аварийный, без визуала).

**Attention Dynamics:** при повторе split-интента подряд — зеркалирование (Left-Visual ↔ Right-Visual),
глубина истории = 1; только для split-макетов (definition, mechanism, clinical), не для grid/timeline.
**Conditional routing — держать простым** (риск №4): пример — `protocol`: ≤5 шагов → timeline, >5 → serpentine.

---

## 5. Layout Library v2 (требования к `layouts.json`)

Текущие 10 описательных layout'ов — **не утверждены и без геометрии**. Цель v2:
- `id` с префиксом `layout_` (унификация; `tpl_` отклонён) + `alias` со старым именем (рендер не ломается);
- `blocks[]`: тип (§2), `bounds{x,y,w,h}` px **и** `relative_bounds` (px/1280 по X,W; px/720 по Y,H), `max_chars`;
- `placeholders[]`: id-шаблон, `allowed_types[]`, `aspect_ratio` (1:1 фото кожи, 16:9 график), bounds оба вида;
- `constraints[]`; канва 1280×720 (16:9); footer reserve `y=640..720`; margins 40px; safe-zone ≥1.5 см;
- зеркальные варианты `*_left/_right` для split-макетов;
- изоляция текст/графика обязательна.

`[GUARD]` Парсить геометрию доноров только из `hd_1` (одобренная переделка) + design concept.
`tpl1`/`tpl2` **не парсить** — грязная геометрия. `[BLOCKED]` — доноры не в репо.
`[GUARD]` Количество шаблонов — по факту нужд двух пилотных дек, НЕ «18 из обсуждения»
(GPT Ошибка №2: «существует в обсуждении» ≠ «утверждено»). Расширять по мере надобности.

---

## 6. Роадмап (зафиксирован, заменяет старый «Phase 8 — Advanced Custom Layouts»)

| Шаг | Содержание | Статус |
|---|---|---|
| **8.0** | Верификация `layouts.json` + инвентаризация доноров + закрытие конфликтов кросс-ревью | **DONE** (этот прогон, §0) |
| **8.1** | Утверждение заказчиком **2 каркасов** (композиция-only) + Layout Library v2 c геометрией (§5) | **[BLOCKED]**: нужны `hd_1` + design concept + утверждение |
| **8.2** | Placeholder Contract Layer: схема ✔, правило в AGENTS.md ✔ (P021); эмиссия контракта на деку — в 8.4 | Схема/правила **DONE**; эмиссия ждёт 8.4 |
| **8.3** | Slide Taxonomy **урезанная**: `03_slide_taxonomy/slide_intents.json` — только интенты двух пилотных дек (DEC-020) | Ждёт 8.1 |
| **8.4** | `ops/scripts/slide_planner.py` (SlidePlannerEngine): select_layout, generate_slide_spec, _validate_constraints, _apply_attention_dynamics, clear_session + эмиссия контракта | Ждёт 8.1+8.3 |
| **8.5** | Renderer refactor: relative→absolute (PPTX: X×13.333", Y×7.5"; 1px≈9525 EMU), серые плашки с composite ID; миграция конвенции `[Placeholder]`-caption в QA | Ждёт 8.4 |
| **8.6** | QA scope-гейт: **13–20 слайдов = жёсткий FAIL вне диапазона** (P023) — включается с первой деки нового пайплайна; contract-гейты (§3) | Ждёт 8.5 |
| **8.7** | Пилот: регенерация `deck_retinoids` (расширение до 13–20) → сбор знаний Постакне (P011: ≥8 фактов) → дека Постакне → Claude Design Integration (Этап 2) | Ждёт 8.6 |

`[GUARD]` Регресс на каждом шаге 8.4–8.7: существующие 5 дек рендерятся без сдвигов, пока не мигрированы.

---

## 7. QA-гейты Phase 8 (добавляются к существующим)

1. **Scope**: 13–20 слайдов на деку (FAIL вне диапазона) — с первой Phase-8 деки.
2. **Contract**: каждый placeholder на слайде имеет запись в контракте; `route`↔`type` соответствие; composite ID уникальны.
3. **Slots**: `max_chars` по каждому слоту; текст не выходит за bounds.
4. **Bounds parity**: `relative_bounds × канва == bounds` (допуск ±1px) — защита от рассинхрона двух систем координат.
5. **Provenance**: `id_img`, заполненные на Этапе 2, имеют запись в `asset_provenance.json` (P019).
6. Существующие: Zero Black, Arimo, slide-to-fact (P018), SVG bounds/overlap — без изменений.

---

## Definition of Done (Phase 8 целиком)
- [ ] Layout Library v2 с геометрией, каркасы утверждены заказчиком.
- [ ] `slide_intents.json` (урезанная таксономия) + `slide_planner.py` детерминированный, с тестами на интенты (supported/irrelevant/weak).
- [ ] Контракт эмитируется на деку; Claude Design-протокол чтения описан.
- [ ] Рендер рисует серые плашки с composite ID; relative→absolute без сдвигов (регресс на 5 деках).
- [ ] Пилотная дека 13–20 слайдов проходит все гейты §7.
- [ ] Этап 2 заполняет только `id_img` (+лого из реестра, диаграммы из движка); провенанс полный.
- [ ] `walkthrough.md` по шаблону на каждый подэтап; тег `phase-8-<step>`.

## НЕ трогать / отложено
- `[GUARD]` Существующие 5 дек и их QA не ломать до миграции (8.7+).
- `[GUARD]` Не строить «платформу на 1000 презентаций» (GPT Ошибка №3): таксономия только под реальные деки.
- `relative_bounds` внедрять параллельно px, переключение рендера — только в 8.5 с регрессом (риск №3).
- Консолидация 5 легаси-дек: решение отложено; новые деки идут через новый пайплайн, старые живут до миграции.

## Открыто `[ВЕРИФ]` / `[BLOCKED]`
- `[BLOCKED]` Донорские файлы: `hd_1` (имя файла, статус ревью ~80%), design concept — запросить у заказчика.
- `[BLOCKED]` Утверждение 2 каркасов заказчиком (предусловие 8.3+).
- `[ВЕРИФ]` Состав интентов пилотных дек — определить из контента, не из универсального списка 12.
- `[ВЕРИФ]` Постакне: объём сбора знаний до ≥8 верифицированных фактов (отдельное ТЗ).

---

### Выход
`walkthrough.md` на каждый подэтап: что внедрено, регресс существующих дек, честный `deltas_vs_plan`.
Финал Phase 8: designer-ready PPTX (Этап 1) + протокол Этапа 2 + пилот Retinoids/Постакне 13–20 слайдов.
