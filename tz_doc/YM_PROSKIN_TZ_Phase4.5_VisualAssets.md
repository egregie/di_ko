# YM PROSKIN — Phase 4.5: Visual Assets (Hybrid)

Версия: 1.0 · Дата: 2026-06-08 · Предыдущий: Phase 5.1 (принят, тег `phase-5.1-deck-integrity`).
Цель: заменить плейсхолдеры реальными визуальными ассетами по гибридной стратегии. Принцип:
**диаграмма — носитель доказательства, не украшение** → у каждого ассета обязательны
source-of-truth и чистая лицензия (аналог verify_gate для фактов).

> Свежей сессии: сначала прочитай `00_PROJECT_STATE/` и `AGENTS.md` (P001–P017), потом исполняй.

Scope этого спринта: **молекулы — на все 4 деки**; **механизмы/анатомия — пилот только на
ретиноидах** (остальные деки получают механизмы в follow-up 4.5b после валидации воркфлоу).

Легенда: `[GUARD]` · `[ВЕРИФ]` · `[НЕТ ДАННЫХ]`.

---

## Блок 0 — Governance
1. `P018 Слайд↔факт` (долг из 5.1 — записать в `AGENTS.md`): клинический тезис на слайде должен
   поддерживаться `statement` хотя бы одного процитированного факта; наличие `source_ref`
   недостаточно. (Сейчас правило только в `qa_deck.py` — закрепить как инвариант.)
2. `P019 Diagram-provenance + license-гейт`: ни один визуальный ассет не используется в деке без
   записи provenance, где есть:
   - `source_of_truth`: молекула → PubChem CID (+ канонический SMILES); механизм/анатомия → PMID/
     референс или Servier image ID;
   - `license`: разрешённая (own/generated · CC0 · CC-BY · public-domain). `[GUARD]` ЗАПРЕЩЕНО:
     CC-BY-SA (вирусный), NC (нет коммерции), BioRender без оплаченного Industry, «без явной лицензии».
   - `attribution`: для CC-BY — строка кредита, обязана попасть в выходной файл деки.
3. `DEC-015`: гибридная стратегия ассетов (генерация молекул / Servier CC-BY для биологии-анатомии
   / провенанс-гейт) зафиксирована.

Реестр: `04_design_system/assets/asset_provenance.json` (по ассету: id, type, path, source_of_truth,
license, attribution, generated_by/fetched_at).

---

## Блок A — Молекулы: генерация из проверенного SMILES (все деки)
1. Пайплайн `ops/scripts/gen_molecule.py` (постоянный, не one_time): вход — имя соединения →
   получить **PubChem CID + canonical SMILES** живым запросом (PUG REST), записать CID как
   source-of-truth → RDKit рендерит 2D SVG → стилизация под бренд (палитра, толщины, Zero Black).
   `[GUARD]` SMILES НЕ вводить из памяти — только из PubChem по CID (неверный SMILES = неверная
   молекула = дезинформация). Это verify-at-write для структур.
   `[GUARD]` Переиспользовать закалённый fetch (IPv4-force + UA + throttle из `evidence.py`).
   PubChem недоступен → `status: blocked`, не угадывать (P012).
2. Соединения (из графа): **ретиноиды** retinol, tretinoin, adapalene; **vitamin_c** L-ascorbic
   acid, sodium ascorbyl phosphate, magnesium ascorbyl phosphate, ascorbyl glucoside;
   **niacinamide**; **exfoliants** glycolic / lactic / mandelic / salicylic acid.
3. Выход: `04_design_system/assets/molecules/<compound>.svg` + запись provenance (CID, SMILES,
   license=generated/own).

Acceptance: каждая молекула — SVG из подтверждённого CID, с provenance; стиль соответствует бренду.

---

## Блок B — Механизмы/анатомия: пилот на ретиноидах
Нужны: схема **RAR/RXR** (механизм ретиноидов) и **слои кожи / эпидермальный turnover**.
1. Источник: **Servier Medical Art (CC-BY 4.0)** — киты «клетки/мембраны/рецепторы» и анатомия;
   коммерция и адаптация (перекрас/подписи под бренд) разрешены при атрибуции. Если точной схемы
   нет — собрать упрощённую **source-grounded SVG**.
2. `[GUARD]` **diagram↔факт:** каждый изображённый шаг механизма должен поддерживаться фактом
   графа (ретиноидные mechanism-факты). Нет факта на шаг — шаг не изображаем (или сперва собрать
   факт через гейт). Анатомия (слои кожи) — стабильное знание, допускается с референсом.
3. Записать provenance: Servier image ID + license `CC-BY-4.0` + строка attribution + поддерживающий PMID/факт.

Acceptance: схема RAR/RXR и слои кожи для ретиноидов готовы, с provenance и атрибуцией; шаги
механизма привязаны к фактам.

---

## Блок C — Интеграция в деки + рендер
1. **Ретиноиды v2:** заменить плейсхолдеры сгенерированными молекулами + пилотными механизм/
   анатомия-ассетами.
2. **Vit C / Niacinamide / Exfoliants:** заменить плейсхолдеры **сгенерированными молекулами**;
   механизм/анатомия остаются плейсхолдерами `[GUARD]` ЯВНО подписанными как placeholder (до 4.5b),
   не выдавать за реальные схемы.
3. Добавить в выход деки **строку/слайд атрибуции** для всех использованных CC-BY ассетов.
4. Перерендерить все деки (PDF+PPTX).

---

## Блок D — QA-расширение (license/provenance gate)
`qa_deck.py` (или `qa_assets.py`), на PDF и PPTX:
- `[GATE]` каждый используемый image-ассет имеет запись provenance с разрешённой лицензией +
  source-of-truth → иначе BLOCK;
- `[GATE]` CC-BY ассет → атрибуция присутствует в выходном файле → иначе BLOCK;
- молекула ссылается на записанный CID; пилотные механизм-схемы — diagram↔факт;
- оставшиеся плейсхолдеры явно помечены как placeholder;
- прежние проверки (Zero Black, Arimo, слайд↔факт P018) держатся.
Выход: `ops/logs/qa_assets_<deck>.md`.

---

## Definition of Done
- [ ] `P018`, `P019` в `AGENTS.md`; `DEC-015`; реестр `asset_provenance.json` заведён.
- [ ] `gen_molecule.py` работает; все 12 молекул — SVG из подтверждённых CID, с provenance, в бренде.
- [ ] Ретиноиды: RAR/RXR + слои кожи готовы (Servier CC-BY/source-grounded), provenance+attribution, diagram↔факт.
- [ ] Все 4 деки перерендерены (PDF+PPTX): молекулы реальные; механизмы — ретиноиды реальные,
      остальные явно-placeholder; атрибуция CC-BY в выходе.
- [ ] QA license/provenance-гейт зелёный; прежние проверки держатся; регресс ок.
- [ ] `walkthrough.md` по шаблону, честный `deltas_vs_plan` (P016); коммит + тег `phase-4.5-visual-assets`.

---

## НЕ трогать
- Граф фактов — только чтение/легальный сбор через гейт. `ontology_v1.json` — через A07.
- Механизмы для Vit C/Niacinamide/Exfoliants — follow-up `4.5b` после валидации воркфлоу.

## Открыто `[ВЕРИФ] / [НЕТ ДАННЫХ]`
- Доступность PubChem PUG REST с закалённым fetch (IPv4/UA). `[ВЕРИФ]`
- Наличие подходящих Servier-схем под RAR/RXR; иначе source-grounded SVG. `[НЕТ ДАННЫХ]`
- Формат атрибуции в деке (футер-кредит vs финальный слайд-источники) — выбрать единый.

---

### Выход
`walkthrough.md` по шаблону. В snapshot: число сгенерированных молекул (с CID), статус пилота
механизмов на ретиноидах, какие деки/слайды ещё на плейсхолдерах, статус license/provenance-гейта,
как оформлена атрибуция CC-BY.
