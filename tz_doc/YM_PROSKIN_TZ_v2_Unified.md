# YM PROSKIN — Единое ТЗ v2.0 (Google Antigravity)

Версия: 2.0 · Дата: 2026-06-07 · Заменяет v1.0 · Парадигма: **Foundation-First**
Синтез: наш роадмап (v1.0) + ответ коллеги A (doc 12) + ответ коллеги B (doc 13).

---

## 0. Легенда пометок

`[ВХОД]` из ваших файлов · `[ФАКТ]` верифицировано источником · `[ВЕРИФ]` сверить с докой ·
`[РЕШЕНИЕ]` решено в этом ТЗ (конфликт снят) · `[НЕТ ДАННЫХ]` не экстраполируется.

---

## 1. Резюме и ключевое стратегическое решение

Проект — не «генератор слайдов», а **Presentation Intelligence Platform**: один раз собрать → верифицировать → построить граф знаний → многократно выводить в PPTX/PDF/HTML/статьи/лендинги.

**Стратегическое решение (вами одобрено): Foundation-First.**
Заморозить любую работу над PPTX/рендером. Сначала построить три фундаментальные сущности:
1. **Онтология + Схема** (что вообще существует в системе и как описывается).
2. **Граф знаний** (сущности → факты → доказательства → источники, через связи).
3. **Экосистема агентов** (роли + SKILL.md).

PPTX/PDF/HTML/Canva — это всего лишь форматы вывода, они подключаются после фундамента. Преждевременная работа над шаблонами = хаос данных через 2–3 месяца.

**Первый артефакт проекта: `ontology_v1.json`** (см. §5). До него агентов на сбор не запускать.

---

## 2. Разбор вкладов коллег (что взято / отклонено)

| Источник | Взято в ТЗ | Отклонено (причина) |
|---|---|---|
| **Коллега A** (doc 12) | Сильные системные промпты (EBM, «Тезис→Механизм→Источник», анти-вода); правило атомарности заголовка ≤50–60; дисклеймер+source_ref в метаданных слайда; читаемая группировка папок | `.ini`-конфиги агентов → **не формат Antigravity** (нужен SKILL.md); `theme_color`/hex захардкожен в каждом слайде → **ломает разделение контент/стиль**; только 3 агента → недостаточно для пайплайна |
| **Коллега B** (doc 13) | **Foundation-First / Schema-first / Knowledge Graph** (стратегический костяк, вами одобрен); `ontology_v1.json` как первый артефакт; 3-уровневая архитектура шаблонов Tokens→Components→Layouts; промежуточный формат-агностичный JSON слайда; роли 10 агентов; Ontology Manager (нормализация сущностей); skill-descriptor; tiers источников | Раздутое дерево (11 каталогов сразу) → **создавать поэтапно**; токен `#DDE6D5` → **выдуман**, перекрыт реальными `[ВХОД]`; Canva в экспорте → **облако, против принципа локальности**; запуск всех 10 агентов сразу → стадировать |
| **Наш v1.0** | Фактбаза Antigravity (Agent Skills, scopes, MCP); реальные дизайн-токены `[ВХОД]`; Zero Black/Arimo/радиусы; SKILL.md-формат; верифицированные команды find-skills; решение по рендеру (HTML→PDF канон + python-pptx); риск подмены Arimo; вывод «PDF-брендбук не парсить» | KB как просто файлы → **усилено до графа знаний** (по B) |

Снятые конфликты `[РЕШЕНИЕ]`: (1) цвет/шрифт **не хранится в slide-spec**, резолвится из токенов на рендере; (2) агенты — **SKILL.md**, не `.ini`; (3) знания — **граф (JSON-записи + индекс + связи)**, папки только для файлов; (4) дерево создаётся **поэтапно**; (5) токены — **только реальные из библиотеки** (§3.4).

---

## 3. Верифицированная фактбаза (сжато из v1.0)

### 3.1 Antigravity `[ФАКТ]`
Агентный IDE; агенты планируют/исполняют в редакторе, терминале, браузере; отдают артефакты. Поддержка стандарта **Agent Skills** (SKILL.md, progressive disclosure) с 2026-01-13 + **MCP**.

### 3.2 Scope скилов `[ФАКТ / ВЕРИФ пути]`
Workspace: `<repo>/.agent/skills/` · Global: `~/.gemini/antigravity/skills/`. Скил = папка + `SKILL.md` (+ скрипты). Переносим через GitHub. Существующие скилы (search/sort/review) переиспользуются. Точные пути сверить с докой при запуске. `[ВЕРИФ]`

### 3.3 find-skills + Skills CLI `[ФАКТ]`
```bash
npx skills add https://github.com/vercel-labs/skills --skill find-skills
npx skills find <query>            # поиск
npx skills add <owner/repo@skill> -g -y    # установка (-g global, -y без подтв.)
npx skills check && npx skills update      # обновления
npx skills init <name>             # создать свой
```
Качество: install ≥1K — норма, <100 — осторожно; источники `vercel-labs`/`anthropics`/`microsoft`. Полезное: `vercel-labs/agent-browser`, `anthropics/skills`, `obra/superpowers`, `anthropics/skill-creator`.

### 3.4 Реальные дизайн-токены `[ВХОД]` (перекрывают выдуманные у коллег)
```
--bg #F8F6F4 · --bg-alt #E6D2CA · --sage/--border #D7E0CE · --herbal #6D8470
--dark #2C3440 · --text #3D4A40 · warn #9E6A5A · focusRing rgba(109,132,112,.13)
Zero Black Policy (нет #000/#fff). Arimo 400/500/700, lh≥1.5, label +0.2em upper.
Radius: btn 8/12, card 16, badge 100. Шкала: Display52/H1 36/H2 26/H3 20/Body15 lh1.7.
```

---

## 4. Вектор проекта → `00_governance/AGENTS.md`

```markdown
# YM PROSKIN — Project Operating Rules (v2)

## Paradigm
Foundation-First. Build ontology + knowledge graph + agents BEFORE any render.
Slides/PPTX/PDF/HTML are output formats, not the product.

## Mission
Fact-verified cosmetology/dermatology knowledge platform. Audience: licensed
specialists. One graph -> many outputs.

## Hard rules
1. Evidence-based only. No claim enters the graph without source + evidence_level.
   D-level => never on a clinical slide. Doubt => discard.
2. Entities are normalized (retinol / retinoid / vitamin_a_derivative are NOT
   three entities). Ontology Manager owns canonical IDs.
3. Local-first. No clinical/patient data to cloud (no Canva export of such).
4. Separation: knowledge (graph) vs style (design tokens) vs render. slide-spec
   carries NO color/font; both resolved from design-tokens.json at render time.
5. Design invariants: tokens in §3.4 only. Zero Black. Arimo. lh>=1.5.
6. Reproducible & deterministic: output = f(graph, slide-spec, tokens).
7. Style of work: concise, no guessing, "insufficient data" when unknown, cite.

## Pipeline
discover -> collect -> extract -> dedup -> verify -> librarian/ontology -> graph
   (later) -> narrative -> architect -> build -> QA. Each stage logs to ops/logs.
```

---

## 5. ПЕРВЫЙ АРТЕФАКТ — `00_governance/ontology_v1.json`

Онтология фиксирует, какие объекты и связи существуют. До неё агенты не запускаются.

```json
{
  "version": "1.0",
  "entity_types": [
    "Ingredient", "Active", "Drug", "Disease", "Condition", "Procedure",
    "Device", "AnatomicalStructure", "Protocol", "Study", "Source",
    "Concept", "Fact", "Image", "Diagram", "Presentation", "Slide",
    "Layout", "Template"
  ],
  "relationship_types": [
    "is_a", "belongs_to", "part_of", "contains", "treats", "causes",
    "used_for", "contraindicated_for", "interacts_with", "supports",
    "contradicts", "references", "derived_from", "has_evidence", "related_to"
  ],
  "evidence_levels": {
    "A": "systematic review / meta-analysis / RCT",
    "B": "cohort / clinical guideline",
    "C": "expert consensus / case series",
    "D": "anecdotal / blog — rejected for clinical slides"
  },
  "source_tiers": {
    "A": ["PubMed","Cochrane","NIH","FDA","EMA","peer-reviewed journals"],
    "B": ["Wikipedia","Britannica","textbooks","INCI/CosIng","manufacturer docs"],
    "C": ["Reddit","professional forums","industry communities"],
    "D": ["general blogs / SEO — context only, never a fact source"]
  }
}
```

---

## 6. Схемы данных — `00_governance/schemas/`

**source.json**
```json
{"source_id":"SRC-0001","name":"","type":"PubMed","url":"","tier":"A",
 "pmid":"","doi":"","accessed":"2026-06-07"}
```
**entity.json**
```json
{"entity_id":"retinol","entity_type":"Ingredient","title":"Retinol",
 "aliases":["vitamin A","retinoid"],"belongs_to":["retinoids"],
 "used_for":["anti_aging","acne"],"contraindications":["pregnancy","lactation"],
 "tags":["collagen","cell_turnover"],"evidence_level":"A",
 "fact_ids":["fact_0001"],"updated":"2026-06-07"}
```
**fact.json**
```json
{"fact_id":"fact_0001","statement":"Retinol increases epidermal turnover",
 "entity_id":"retinol","confidence":0.95,"evidence_level":"A",
 "sources":["SRC-0001"],"contradictions":[],"verified_by":"verifier",
 "date":"2026-06-07"}
```
**relationship.json**
```json
{"rel_id":"rel_0001","from":"retinol","type":"belongs_to","to":"retinoids",
 "evidence_level":"A","sources":["SRC-0001"]}
```
**slide-spec.json** (формат-агностичный, БЕЗ цвета/шрифта)
```json
{"id":"deck01-s03","layout":"two_columns_image_left","section":"Ретиноиды",
 "title":"Механизм действия ретинола",
 "subtitle":"Влияние на эпидермис и дерму на клеточном уровне",
 "body":[{"type":"bullet","text":"Ускорение дифференцировки кератиноцитов"},
         {"type":"bullet","text":"Подавление металлопротеиназ"}],
 "media":{"type":"image","asset":"retinol_RAR_RXR.png","fit":"cover",
          "caption":"Связывание ретиноевой кислоты с RAR/RXR"},
 "components":{"alert":{"kind":"warning","title":"Противопоказание",
               "text":"Беременность, лактация"}},
 "disclaimers":["Только для практикующих специалистов","Требует SPF-защиты"],
 "source_refs":["retinol","fact_0001","SRC-0001"],"notes":""}
```
**skill.descriptor.json**
```json
{"skill_name":"","scope":"workspace|global","version":"","purpose":"",
 "input":"","output":"","dependencies":[]}
```
Правило: один и тот же `slide-spec` экспортируется в PPTX / PDF / HTML / Marp / Google Slides без изменений (цвет и шрифт берутся из токенов на рендере).

---

## 7. Граф знаний — модель хранения

Знания хранятся **как граф (JSON-записи + индекс + связи)**, не «как папки». Папки только организуют файлы.
- `03_knowledge_graph/entities/<entity_id>.json`
- `03_knowledge_graph/facts/<fact_id>.json`
- `03_knowledge_graph/relationships/<rel_id>.json`
- `03_knowledge_graph/sources.json` — реестр источников
- `03_knowledge_graph/graph_index.json` — плоский индекс для быстрого доступа агентами

Цепочка истины: `Entity → Fact → Evidence(level) → Source`. Все под git → трассируемость и откат.

---

## 8. Дерево папок (создавать поэтапно)

```
ym-proskin/
├── .agent/skills/                  # Antigravity workspace-скилы (реальные SKILL.md)  [Phase 0]
├── 00_governance/                  # [Phase 0]
│   ├── AGENTS.md
│   ├── ontology_v1.json            # ПЕРВЫЙ артефакт
│   ├── schemas/                    # entity/fact/source/relationship/slide-spec/skill
│   ├── prompts/                    # системные промпты агентов
│   └── naming.md
├── 01_collection/                  # [Phase 1] сырьё по tier источника
│   ├── tierA/  tierB/  tierC/
├── 02_processing/                  # [Phase 1-2] extraction/ dedup/ verify/ (рабочее)
├── 03_knowledge_graph/             # [Phase 1-2] entities/ facts/ relationships/ sources.json index
├── 04_design_system/               # [Phase 3 — заморожено сейчас]
│   ├── design-tokens.json (locked §3.4)  layouts.json  library/(pptx,pdf ref)
├── 05_content/                     # [Phase 3+] decks/  specs/
├── 06_render/                      # [Phase 4] html/  pptx_builder.py  out/
├── 07_skills_registry/             # манифесты/descriptor.json (реестр; файлы скилов — в .agent/skills)
├── 08_release/                     # утверждённые финалы
├── ops/logs/                       # трассировка, отчёты QA
└── 99_archive/
```
Сейчас (Phase 0) создаются только: `.agent/skills/`, `00_governance/`, `03_knowledge_graph/` (пустые подпапки), `ops/logs/`. Остальное — по мере фаз.

---

## 9. Экосистема агентов (10 ролей, стадированная активация) → SKILL.md

Активация Phase 0–2: A01–A07. Phase 3–4: A08–A10.

| # | Агент | Skill (SKILL.md) | Вход → Выход |
|---|---|---|---|
| A01 | Source Discovery | `source-discovery` | тема → список источников по tier |
| A02 | Source Collector | `research-collect` (+agent-browser) | источники → raw в 01_collection |
| A03 | Fact Extractor | `fact-extract` | документ → факты (statement+provenance) |
| A04 | Deduplicator | `dedupe-sort` | факты → без дублей (сильнейший evidence) |
| A05 | Fact Verifier | `source-verify` | факт → verified + evidence_level |
| A06 | Knowledge Librarian | `kb-graph` | verified → entities/facts/relationships |
| A07 | Ontology Manager | `ontology-guard` | граф → нормализованные канонические ID |
| A08 | Narrative Builder | `narrative-build` | тема+граф → сюжет (Проблема→Механизм→Решение→Результат) |
| A09 | Presentation Architect | `slide-spec-build` | нарратив+граф → slide-spec по layouts |
| A10 | QA Auditor | `qa-visual` | рендер → отчёт (overflow/контраст/Zero Black/дисклеймеры/источники) |

### Системные промпты (адаптированы из коллеги A, в `00_governance/prompts/`)

**A02 Collector**
> «Ты — научный сотрудник YM PROSKIN. Собираешь информацию только по доказательной медицине (EBM). Источники — рецензируемые (PubMed, Cochrane, NIH, FDA, EMA); блоговые/копирайтерские статьи игнорируешь. Формат записи: Тезис → Механизм действия → Источник (PMID/DOI). Запрещены размытые формулировки («полезно для кожи»). Пиши: «Стимулирует неоколлагенез через активацию фибробластов». Не утверждаешь — фиксируешь с провенансом в `01_collection/`».

**A05 Verifier**
> «Ты — главный редактор-верификатор YM PROSKIN. Берёшь сырьё, проверяешь: ≥2 независимых источника ИЛИ 1 peer-reviewed. Присваиваешь evidence_level A–D; D отбраковываешь для клинического контента. Сомнительный факт — удаляешь. Соответствие бренду: профессионализм, системность, доверие. Выход — verified-факты по схеме».

**A06/A07 Librarian + Ontology**
> «Ты — библиотекарь графа знаний. Раскладываешь верифицированные факты в entities/facts/relationships по `ontology_v1.json`. Нормализуешь сущности: retinol / retinoid / vitamin_a_derivative — одна сущность с aliases, не три. Любая новая категория — только согласно онтологии».

**A09 Architect**
> «Ты — UX-архитектор презентаций YM PROSKIN. Берёшь нарратив + факты из графа, раскладываешь по жёсткой сетке layout. Заголовок ≤50 символов (атомарность); излишек — в подзаголовок/тело. Выход — `slide-spec.json` с ID маски и контентом по блокам. Цвет/шрифт НЕ указываешь — они из токенов. Никакой воды».

---

## 10. Источники и протокол верификации (слитые tiers)

- **Tier A:** PubMed/MEDLINE, Cochrane, NIH, FDA, EMA, профильные журналы (JAAD, BJD, J. Cosmetic Dermatology), DermNet.
- **Tier B:** Wikipedia, Britannica, учебники, INCI/CosIng, документы производителей/регуляторов.
- **Tier C:** Reddit, проф. форумы, отраслевые сообщества — только темы/тренды, не источник факта.
- **Tier D:** общие блоги/SEO — контекст, никогда не факт.

Протокол (A05): клиническое утверждение → ≥2 независимых Tier A/B **или** 1 peer-reviewed; `evidence_level` A–D, D отбраковка; хранить `contradictions[]`; цитаты ≤15 слов, остальное — пересказ (копирайт + чистота графа).

---

## 11. Дизайн-система — 3 уровня (Phase 3, сейчас ЗАМОРОЖЕНО)

Уровень 1 **Tokens** (`design-tokens.json`, §3.4, locked) → Уровень 2 **Components** (Title, Subtitle, Card, Quote, Badge, Alert, Image, Timeline, Chart, Table, Progress, Glassmorphism — уже есть в библиотеке `[ВХОД]`) → Уровень 3 **Layouts**:
```
layout_001_cover · 002_two_columns_image_left · 003_four_cards · 004_timeline
005_image_focus · 006_comparison · 007_process · 008_statistics · 009_quote · 010_alert
```
Маски собираются из реальных компонентов библиотеки — новые не изобретать. Брендбук-PDF не парсить (растровый, 14 МБ; токены уже в PPTX дословно). Расхождение «чёрный фон логотипа» → закрепить `--dark #2C3440`. `[РЕШЕНИЕ]`

---

## 12. Рендер (Phase 4)

Один `slide-spec` → много форматов. Канон: **HTML/CSS→PDF** (дизайн-система CSS-родная, токены = CSS-переменные дословно). По запросу: **python-pptx** (редактируемый .pptx; риск подмены Arimo — встраивать/декларировать шрифт, проверять в QA `[ВХОД]`). Marp/Google Slides — опционально. Canva исключён (облако, против локальности `[РЕШЕНИЕ]`).

---

## 13. find-skills + слой обнаружения навыков (Phase 0)

Установить find-skills (§3.3). Сформировать `07_skills_registry/` с descriptor.json на каждый скил. Приоритетный поиск по категориям:
`scientific research`, `literature review`, `fact checking`, `source validation`, `browser automation`, `scraping`, `ontology`, `taxonomy`, `graph building`, `design systems`, `presentation design`, `csv/excel/json processing`, `review`, `consistency checking`, `hallucination detection`.

---

## 14. Роадмап (Foundation-First)

- **Phase 0 — Фундамент (текущий спринт):** `ontology_v1.json` → схемы (§6) → `AGENTS.md` → дерево Phase-0 → SKILL.md A01–A07 + системные промпты → установка find-skills → перенос скилов search/sort/review.
- **Phase 1 — Knowledge Collection:** наполнить tiers источников; A01→A02 «большой хапок» по ядру: анатомия кожи + активы (ретиноиды, AHA/BHA, витамин C, пептиды) → `01_collection/`.
- **Phase 2 — Knowledge Graph:** A03→A04→A05→A06/A07 → `03_knowledge_graph/` + index; нормализация онтологии.
- **Phase 3 — Presentation System:** разморозить `04_design_system` (tokens/components/layouts).
- **Phase 4 — Render:** A08→A09→A10; HTML→PDF (+python-pptx).
- **Phase 5 — Autonomous Pipeline:** Тема → A01…A10 → финал; регресс-проверка при смене токенов.

---

## 15. Рекомендации (приоритезированные)

1. Не трогать PPTX до завершения Phase 0–2. Фундамент = онтология + граф + агенты.
2. `ontology_v1.json` — собрать первым, до запуска любых агентов.
3. slide-spec — формат-агностичный, без цвета/шрифта (резолв из токенов).
4. Агенты — SKILL.md (Antigravity-native), не `.ini`.
5. Знания — граф (JSON+index), папки только для файлов.
6. Дерево — поэтапно; не плодить пустые каталоги.
7. QA-gate: клинический факт без `source_refs`/evidence ≥C блокирует релиз.
8. Ontology Manager обязателен с Phase 2 (иначе дубли сущностей).

## 16. Риски и митигации
- Дубли сущностей (retinol≠retinoid) → A07 Ontology Manager, канонические ID + aliases.
- Непроверенные мед-факты → протокол §10 + QA-gate.
- Подмена Arimo при .pptx → встраивать/декларировать, проверять. `[ВХОД]`
- Авторские права при сборе → пересказ, цитаты ≤15 слов, фиксировать источник.
- Дрейф путей/скилов Antigravity → сверка с докой. `[ВЕРИФ]`
- Over-engineering дерева → стадированное создание (§8).
- Конфиденциальность фото пациентов → локальный рендер, без Canva/облака.

## 17. Альтернативы
- Хранилище графа: JSON-файлы+git (выбрано) → при росте перейти на SQLite/JSONL или графовую БД.
- Контент-формат: формат-агностичный JSON (выбрано) vs Marp-MD (быстрее, слабее контроль сетки).
- Рендер: HTML→PDF (канон) vs python-pptx (редактируемость) vs Marp.
- Агенты: 10 ролей со стадированием (выбрано) vs 3 укрупнённых (быстрее старт, хуже масштаб).

## 18. [РЕШЕНИЕ] решено · [НЕТ ДАННЫХ] открыто
Решено: формат агентов (SKILL.md); цвет вне slide-spec; граф вместо папок; стадированное дерево; токены только реальные; Canva исключён; `--dark` вместо чёрного фона.
Открыто `[НЕТ ДАННЫХ]`: точные scope-пути Antigravity `[ВЕРИФ]`; файлы существующих скилов прошлого проекта (для маппинга на A01–A10); целевой формат финала (PDF/PPTX/оба); объём первого курса; конкретные «удалённые БД/библиотеки» с доступами.

---

### Источники внешних фактов
developers.googleblog.com (Antigravity) · codelabs.developers.google.com (Agent Skills) · vktr.com (поддержка стандарта, 2026-01-13) · vertu.com (scope-пути, сторонний) · skills.sh/vercel-labs/skills/find-skills (CLI).
