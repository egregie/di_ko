# Next Steps

- **Phase 8 — Two-Stage Architecture (Antigravity → Claude Design) + Slide Planning Engine**
  ТЗ: `tz_doc/YM_PROSKIN_TZ_Phase8_TwoStage_SlidePlanning.md` (роадмап зафиксирован, DEC-017…DEC-020).
  - **8.0 DONE (2026-06-11)**: верификация `layouts.json` (геометрии нет — DEC-018), инвентаризация доноров (отсутствуют), закрытие конфликтов кросс-ревью, P021–P023, схема контракта, скилл `slide-plan`.
  - **8.1 [BLOCKED]**: утверждение заказчиком 2 каркасов + Layout Library v2 (bounds + relative_bounds + max_chars + зеркала). Ждёт: файлы `hd_1` + design concept от заказчика.
  - **8.2** (частично DONE): Placeholder Contract Layer — схема и правила готовы; эмиссия контракта на деку — вместе с 8.4.
  - **8.3**: `03_slide_taxonomy/slide_intents.json` — урезанная таксономия под пилотные деки (DEC-020).
  - **8.4**: `ops/scripts/slide_planner.py` — детерминированный селектор + slot-filling + composite IDs + attention inversion + clear_session.
  - **8.5**: Renderer refactor — relative→absolute, серые плашки с composite ID, миграция `[Placeholder]`-конвенции.
  - **8.6**: QA-гейты — scope 13–20 (P023), contract-гейты, bounds parity.
  - **8.7**: Пилот — Retinoids 13–20 слайдов → сбор знаний Постакне (≥8 фактов, P011) → дека Постакне → Claude Design Integration (Этап 2).
