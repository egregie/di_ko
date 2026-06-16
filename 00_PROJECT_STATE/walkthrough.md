# WALKTHROUGH — phase-8.2-authority-layouts — 2026-06-15
status: done
scope: Expert-Authority Layout System (13 layout'ов в 4 класса) + 2 deck-каркаса (Ретиноиды 16, Постакне 18), отрендеренные ПУСТЫМИ (placeholder-плашки + бренд-хром) в реальный PDF для утверждения заказчицей. 3 клиентских лого интегрированы (Zero Black). Граф НЕ тронут. Подход: геометрия из существующего визуального языка v2 + брендбук-токены (не из донора hd_1 — 8.1 остался заблокирован, здесь он не нужен).

## files_changed
- `04_design_system/assets/logo/ym_proskin_{mark,badge,horizontal}.svg` — клиентские 002/004/005, перекрашены `#000000`→`currentColor` (+ дефолт `color="#2C3440"`); 0 остаточного black.
- `04_design_system/assets/logo/deprecated/` — старые рисованные mark/badge/horizontal (НЕ затёрты, заархивированы; descriptor оставлен — нужен legacy-рендерам).
- `04_design_system/assets/logo/logo_registry.json` — 3 клиентских лого (viewBox 654×597 / 1125×867 / 1230×469), цвет-токены по контексту, маршрутизация (mark→футер, horizontal→титул, badge→закрытие); descriptor помечен legacy.
- `04_design_system/assets/asset_provenance.json` — 3 записи лого: client-provided, license own/client (P019).
- `04_design_system/layouts_v2.json` — НОВОЕ: 13 layout'ов, 4 класса, slot-геометрия (bounds@1280×720 + relative_bounds + constraints), footer_band, anti_fabrication policy, наследует placeholder_contract.
- `04_design_system/deck_templates.json` — НОВОЕ: 2 каркаса (retinoids 16, postacne 18), последовательность layout'ов + per-slide placeholder-назначения, БЕЗ контента.
- `ops/scripts/gen_layouts_v2.py` — НОВОЕ: генератор геометрии (bounds авторские, relative авто → parity гарантирован) + встроенный sanity-репорт.
- `ops/scripts/render_carcass.py` — НОВОЕ: пустой каркас → HTML (sage-плашки `type · purpose`, текст-заглушки по block_type, реальные лого, бренд-футер).
- `ops/scripts/validate_layouts.py` — НОВОЕ гейт: canvas / footer-band / routing / max_chars / parity / overlap / deck-ref / литерал `[Placeholder]` / Zero-Black в рендере.
- `ops/scripts/compile_pdf.js` — добавлены опц. argv ширина/высота (обратно совместимо; дефолт 1024×576) → рендер каркасов 1280×720.
- `ops/scripts/one_time/shot_carcass.js` — QA-хелпер скриншотов слайдов.
- `06_render/out/deck_template_{retinoids,postacne}.{html,pdf}` — пустые каркасы (16 и 18 слайдов).
- `00_PROJECT_STATE/*` + `00_governance` — decisions_log (DEC-026), current_state, active_tasks, HANDOFF_SNAPSHOT.

## commands_run
- `python ops/scripts/gen_layouts_v2.py` — 13 layout'ов, sanity-репорт: все слоты в canvas, без захода в футер.
- `python ops/scripts/render_carcass.py --deck deck_template_retinoids|postacne` — HTML 16 и 18 слайдов @1280×720.
- `node ops/scripts/compile_pdf.js deck_template_* 1280 720` — оба PDF собраны (реальные пути в 06_render/out/).
- визуальная проверка всех 13 архетипов layout (скриншоты A1/A2/A3/A4/B1/B2/B3/C1/C2/C3/D1/D2/D3): лого рендерятся (не black), sage-плашки с `type · purpose` (НЕ литерал `[Placeholder]`), футер на контент/закрытии и отсутствует на титул/раздел, без overlap. Найден и исправлен 1 overlap (D1 deck_title↔cover_art).
- `python ops/scripts/validate_layouts.py` → **PASS** (сырой вывод: 13 layouts, 2 decks, all checks OK).
- negative-control: инъекция `[Placeholder]` в HTML → validate FAIL (exit 1); re-render → PASS (exit 0). Чек живой.
- `python ops/scripts/validate_graph.py` → **PASS** (граф не тронут — регресс-чек).

## acceptance
- A1 (3 лого перекрашены, 0 остаточного #000, брендовые имена, старые в deprecated): PASS.
- A2–A3 (logo_registry + provenance; маршрутизация титул/футер/закрытие): PASS.
- B (4 класса, 13 layout'ов; анти-фабрикация зафиксирована — `cell_provenance_required` + anti_fabrication policy в layouts_v2): PASS.
- C (2 deck_template: 16 и 18, оба 13–20, Authority ведут каждую часть): PASS.
- D1 (layouts_v2.json со slot-геометрией, наследует placeholder_contract): PASS.
- D2 (deck_templates.json без контента): PASS.
- D3 (оба каркаса в реальном PDF; серые/sage-плашки с типом, НЕ литерал `[Placeholder]`; бренд-хром; футер без overlap; Zero Black): PASS.
- E (validate_layouts PASS сырой вывод; validate_graph остался PASS): PASS.
- DEC-026 + walkthrough + тег: DEC и walkthrough — done; git commit+tag — предложен, ждёт подтверждения.

## deltas_vs_plan
- Геометрия взята из визуального языка v2 + брендбук-токенов (как разрешает §4 D1), НЕ из донора hd_1: hd_1 в репо отсутствует (8.1 BLOCKED), а 8.2 его не требует. Красный флаг «геометрия из головы» не нарушен — источник реальный (design-tokens + рендер v2).
- §3 prose-композиция (Authority 6/7 и т.п.) расходится с собственной таблицей ТЗ на ±1; композиция явно НЕ-гейт («ориентир»). Взята авторитетная таблица: retinoids A5/K3/E3/T5, postacne A6/K3/E4/T5.
- Два слайда специализируют тип placeholder поверх дефолта layout (retinoids s13 B1 visual→id_img «кожа-фото»; postacne s10 A1 category_4→id_illustration «типы рубцов») — через per-deck contract-модель (Phase 8.0), геометрия не меняется.
- Канвас 1280×720 (ТЗ §4 D1 + placeholder_contract). Legacy-рендер render_deck.py остаётся 1024×576 — не трогался.
- Прим.: grade-профиль ТЗ-преамбулы «A:22/B:2/C:31» по диску = A:21/B:3/C:31 (graph-вопрос 8.7b, зафиксирован в HANDOFF_SNAPSHOT). На 8.2 не влияет — каркасы без контента/grade.

## project_state_snapshot
phase: Phase 8.2 authority-layouts — done
completed: [3 client logos integrated (Zero Black), logo_registry+provenance, layouts_v2.json (13 layouts/4 classes/geometry/anti-fab), deck_templates.json (16+18 carcasses), gen_layouts_v2.py, render_carcass.py, validate_layouts.py (negative-control proven), compile_pdf.js dims, both empty carcasses → real PDF, DEC-026; graph untouched validate_graph PASS]
in_progress: []
blocked: [8.1 Layout Library from donor hd_1 — superseded by 8.2's brand-layer approach for the carcass purpose; client APPROVAL of the 2 carcasses still pending]
open_questions: [заказчица утверждает 2 каркаса (по PDF) ДО наполнения; content-fill (8.4–8.6) обязан соблюсти cell_provenance_required; диаграммный движок наполняет id_illustration/id_graph из графа]

## decisions_logged
- DEC-026: Expert-Authority Layout System + Layout Library v2 geometry; 13 layouts/4 classes; anti-fabrication encoded; 2 carcasses rendered empty to PDF; validate_layouts gate.

## next_recommended
- Показать заказчице оба PDF (`06_render/out/deck_template_retinoids.pdf`, `deck_template_postacne.pdf`); получить утверждение/правки 2 каркасов.
- После утверждения: Phase 8.4–8.6 (slide_planner.py — детерминированный slot-filling из графа, соблюдая cell_provenance_required) → дека Постакне.
- Git: commit + tag `phase-8.2-authority-layouts` (по подтверждению).
