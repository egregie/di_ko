# YM PROSKIN — Phase 0.7: Operating & Cognitive Layer (ТЗ для Antigravity)

Версия: 1.0 · Дата: 2026-06-07 · Предыдущий: Phase 0.5 (принят, тег `phase-0.5`).
Цель: установить операционный слой (токен-дисциплина, краткость по режимам, постоянная
память) ДО массового сбора данных. Рендер/PPTX и сбор данных (Phase 1) — НЕ в этом спринте.

Легенда: `[ФАКТ]` верифицировано · `[ВЕРИФ]` сверить при выполнении · `[НЕТ ДАННЫХ]`.

---

## Резюме и важная коррекция терминов

Phase 0.5 закрыта: 8 скилов в `.agents/skills/`, валидатор подключён, логика pharma_v2
портирована, тег `phase-0.5`.

Коррекция (важно, иначе будет ложное ожидание):
- **RTK (Rust Token Killer)** `[ФАКТ]` — CLI-прокси, сжимает **вывод shell-команд** (git/тесты/
  find/grep) до контекста, 60–90% экономии, хук переписывает `cmd` → `rtk cmd`. Это **не**
  про базу знаний.
- «Context Manager / Retriever» из ответа коллеги — **отдельный слой ретривала по графу**
  (агент получает 20–50 релевантных узлов, не всю базу). Полезен, но это **не RTK**.
- В этом ТЗ они разведены: Блок A = RTK (CLI), Блок B = слой ретривала (наш).

---

## БЛОК A — RTK: сжатие CLI-вывода `[ФАКТ + ВЕРИФ установки]`
Репозиторий `rtk-ai/rtk`, open-source, single-binary Rust, конфиг `~/.config/rtk/config.toml`.

Задачи:
1. Установить RTK. Порядок попыток (Windows нативно может потребовать WSL/Cargo):
   - Homebrew/curl-installer (если есть); иначе `cargo install` (нужен Rust toolchain);
   - проверить наличие пребилт-бинаря под Windows. `[ВЕРИФ]`
2. Подключить к Antigravity. Прямой init для Antigravity не подтверждён `[ВЕРИФ]`:
   - если есть per-agent init (как для Claude Code/Gemini CLI) — использовать его;
   - иначе общий Bash/PreToolUse-хук, переписывающий шумные команды в `rtk <cmd>`.
3. Настроить `config.toml`: исключения, tee-mode для восстановления при падении тестов,
   per-project фильтры. Не сжимать вывод валидатора схем (нужны полные ошибки).
4. Зафиксировать факт установки в `00_PROJECT_STATE/decisions_log.md`.

Acceptance: `rtk gain` показывает ненулевую экономию на тестовой команде (`git status`/`find`);
вывод `validate_graph.py` НЕ сжимается. Если интеграция с Antigravity не подтверждена —
зафиксировать в `known_problems.md` и оставить RTK для ручного `rtk <cmd>`.

---

## БЛОК B — Слой ретривала (наш «Context Manager», не RTK)
Цель: агент получает только релевантные узлы графа, а не всю базу. Сейчас граф почти пуст —
строим **интерфейс/скелет**, наполнение работает само по мере роста графа.

Задачи:
1. `ops/scripts/retriever.py` — на входе: запрос/тема + лимит N (дефолт 30); на выходе:
   список узлов из `03_knowledge_graph/` (entities/facts/relationships), отсортированных по
   релевантности и evidence_level, обрезанный по N. Источник индекса — `graph_index.json`.
   Базовый матчинг: по тегам/aliases/entity_type (без тяжёлых эмбеддингов на старте).
2. `ops/scripts/context_builder.py` — берёт вывод retriever и собирает компактный
   контекст-пакет (только нужные поля: statement, evidence_level, sources) под бюджет токенов.
3. Политика в `AGENTS.md`: агенты A02/A03/A05/A06/A09 обращаются к графу ТОЛЬКО через
   retriever→context_builder, не читают каталоги целиком. Дефолтный бюджет: 20–50 узлов.
4. Переиспользовать `search_kb.py` (из pharma_v2) как движок матчинга, если применимо.

Acceptance: `retriever.py "retinol" --limit 5` возвращает ≤5 узлов в валидном JSON (на пустом
графе — пустой список без ошибки); `context_builder.py` отдаёт пакет с усечёнными полями.

---

## БЛОК C — Caveman: краткость по режимам `[ФАКТ]`
Скил `JuliusBrussee/caveman`. Режимы lite/full/ultra (`/caveman <mode>`); режет только выход,
не reasoning; есть exit-исключение для деструктивных операций.

Задачи:
1. Установить глобально: `npx skills add https://github.com/JuliusBrussee/caveman --skill caveman`.
2. НЕ включать ultra глобально (потеря деталей в research). Назначить режимы по ролям в
   соответствующих `SKILL.md`:
   - **Verbose (детали важны) → `/caveman off` или `full`:** A01 source-discovery,
     A02 research-collect, A03 fact-extract, A05 source-verify.
   - **Terse (механика/структура) → `/caveman ultra`:** A04 dedupe-sort, A06 kb-graph,
     A07 ontology-guard, A09 architect (Phase 3), A10 QA (Phase 4).
   - **A08 narrative (Phase 3) → `full`** (нужен связный текст).
3. Прописать в `AGENTS.md`: режим Caveman — атрибут роли; деструктивные операции всегда
   разворачиваются в полный текст (consent), независимо от режима.

Acceptance: установлен; в SKILL.md каждой активной роли (A01–A07) указан режим; деструктивное
действие не сокращается.

---

## БЛОК D — Persistent Memory (метод Карпатого)
Создать `00_PROJECT_STATE/` — снимок проекта, переживающий рестарт IDE.

Файлы:
```
00_PROJECT_STATE/
├── current_state.md      # где проект сейчас (фаза, что готово)
├── active_tasks.md       # что в работе
├── next_steps.md         # что дальше
├── known_problems.md     # блокеры/баги/неподтверждённое
├── decisions_log.md      # журнал решений: DEC-xxx — решение — причина — дата
└── memory/
    ├── failures.md       # что пробовали и почему не сработало
    └── lessons.md        # выводы (что работает лучше)
```
Правила (в `AGENTS.md`):
1. Каждый агент в конце задачи дописывает: completed / in_progress / blocked / next_step
   (формат YAML-блока, см. ниже) в `current_state.md` + `active_tasks.md`.
2. Каждый агент в начале задачи читает `00_PROJECT_STATE/*` — это его «рабочая память».
3. Любое архитектурное решение → запись `DEC-xxx` в `decisions_log.md` (почему JSON, почему
   Arimo, почему граф, почему не Notion и т.д.).
4. Любая неудачная попытка → `memory/failures.md` (чтобы не повторять).

Формат записи агента:
```yaml
date: 2026-06-07
agent: ontology_manager
completed: [created ingredient taxonomy, merged duplicates]
in_progress: [device taxonomy]
blocked: [missing FDA data]
next_step: [collect device classifications]
```
Acceptance: папка и 7 файлов созданы и заполнены текущим состоянием (Phase 0.7); в
`decisions_log.md` есть стартовые DEC-записи (граф-first, токены, RTK, Caveman).

---

## БЛОК E — Принципы проекта → `AGENTS.md`
Зафиксировать как раздел `## Principles`:
```
P001 Schema First
P002 Knowledge Graph Before Templates
P003 Context Discipline — RTK сжимает CLI-вывод; Retriever отдаёт агенту только 20–50
     релевантных узлов графа, не всю базу
P004 Concise by Mode — Caveman ultra для production-ролей, off/full для research-ролей
P005 Persistent Working Memory — 00_PROJECT_STATE поддерживается каждым агентом
P006 Every Agent Leaves Logs (ops/logs + PROJECT_STATE)
P007 No Fact Without Source (evidence_level, ≥2 источника или 1 peer-reviewed)
P008 No Entity Without Ontology (через A07 ontology-guard)
```
Acceptance: раздел присутствует в `AGENTS.md`.

---

## БЛОК F — Стандарт Walkthrough «под Claude» (ключевое)
Каждый ТЗ агент завершает файлом `walkthrough.md` СТРОГО по шаблону ниже. Цель — плотный,
машиночитаемый снимок, который внешний аналитик (Claude) парсит за один проход без
довывода контекста. Стиль — terse (Caveman-совместимый), без вступлений и постскриптумов.

Шаблон (сохранить как `00_PROJECT_STATE/WALKTHROUGH_TEMPLATE.md` и использовать всегда):
```markdown
# WALKTHROUGH — <phase_id> — <YYYY-MM-DD>
status: done | partial | blocked
scope: <одна строка>

## files_changed        # путь — назначение в 1 строку
- <path> — <purpose>

## commands_run          # только state-changing/ключевые
- <cmd> — <result 1 строка>

## acceptance            # критерий: PASS|FAIL [+заметка]
- <criterion>: PASS|FAIL

## deltas_vs_plan         # отличия от ТЗ и причина (пусто, если нет)
- <delta> — <reason>

## project_state_snapshot # зеркало 00_PROJECT_STATE
phase: <id>
completed: [...]
in_progress: [...]
blocked: [...]
open_questions: [...]

## decisions_logged       # новые DEC за этот прогон
- DEC-<n>: <решение> — <причина>

## next_recommended       # 1–3 пункта, предложение агента
- <item>
```
Правило в `AGENTS.md`: «По завершении любого ТЗ создавать/обновлять `walkthrough.md` строго
по `WALKTHROUGH_TEMPLATE.md`. Никакого свободного текста вне секций. Это интерфейс к внешнему
ревьюеру».

Acceptance: шаблон сохранён; правило добавлено; данный спринт завершается walkthrough по
шаблону.

---

## БЛОК G — Baseline
`git add . && git commit -m "phase0.7: operating layer (RTK, retriever, caveman, project-state, principles, walkthrough standard)"; git tag phase-0.7`

---

## Чек-лист приёмки Phase 0.7
- [ ] RTK установлен; `rtk gain` ненулевой; вывод валидатора не сжимается (или проблема в known_problems).
- [ ] `retriever.py` + `context_builder.py` работают на пустом графе без ошибок.
- [ ] Caveman установлен; режимы проставлены в SKILL.md A01–A07; деструктив не сокращается.
- [ ] `00_PROJECT_STATE/` (7 файлов) создан и заполнен; стартовые DEC внесены.
- [ ] Раздел `## Principles` (P001–P008) в `AGENTS.md`.
- [ ] `WALKTHROUGH_TEMPLATE.md` сохранён; правило в `AGENTS.md`.
- [ ] Коммит+тег `phase-0.7`.
- [ ] `walkthrough.md` этого спринта написан по шаблону.

## НЕ трогать
- Сбор данных (Phase 1), `04_design_system`, рендер/PPTX — заморожено.
- `ontology_v1.json` — только через A07.

## Открыто `[НЕТ ДАННЫХ] / [ВЕРИФ]`
- Поддержка RTK именно в Antigravity и способ установки на нативном Windows. `[ВЕРИФ]`
- Пилотная тема Phase 1 (рекомендация: **Ретиноиды**) — нужна для следующего ТЗ.
- Нужен ли ретриверу семантический поиск (эмбеддинги) или хватит тег-матчинга — решить по
  росту графа.

---

### Источники внешних фактов
github.com/JuliusBrussee/caveman, skillsllm.com (Caveman: режимы, output-only) ·
github.com/rtk-ai/rtk, pyshine.com, everydev.ai (RTK: CLI-прокси, хук, config.toml).
