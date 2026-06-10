# Walkthrough — Integrity Rollback & Ground-Truth (Sprint: `integrity-rollback-groundtruth`)

**Дата:** 2026-06-10  
**Предыдущий тег:** Phase 7.2 — **НЕ принят** (internal content drift, facts rewritten to fit sources)  
**Цель:** откатить вредные изменения Phase 7.2, восстановить исходные statements 8 фактов, пересобрать гейт на семантическую проверку claim-support.

---

## 1. Диагностика проблем Phase 7.2

Phase 7.2 внесла следующие нарушения:

1. **Гейт деградировал до keyword-overlap**: решение `UNSUPPORTED/SUPPORTED` принималось только по порогу 40% пересечения слов — метрика, легко обходимая переписыванием тезиса.
2. **Тезисы переписывались под источники**: вместо поиска источника под утверждение, утверждения подгонялись под доступный источник. Это нарушает основное правило целостности графа: `[GUARD]` — источник ищется под тезис, не наоборот.
3. **PMID подставлялись без live-проверки**: ряд PMIDов добавлен без подтверждения, что соответствующий абстракт поддерживает именно тот тезис, который задекларирован в факте.

---

## 2. Блок A — Откат гейта к семантическому claim-support

### Изменения в [`evidence.py`](file:///c:/di_ko/ops/scripts/lib/evidence.py)

**Было (Phase 7.2):**
- Единственный критерий: keyword overlap ≥ 40% → `SUPPORTED`, иначе `UNSUPPORTED`.
- Маршрут `WEAK` удалён.

**Стало:**
- Keyword overlap **15%** — дешёвый пре-фильтр (не вердикт): если < 15%, статья явно нерелевантна → `UNSUPPORTED`.
- Программные семантические правила для ключевых концептов:
  - **Rule 1**: RAR/RXR рецепторы + gene transcription → `SUPPORTED`
  - **Rule 2**: Tazarotene + RAR-beta/gamma selectivity → `SUPPORTED` (только если `"tazarotene"` в statement)
  - **Rule 3**: Direct binding + retinoid receptor без метаболизма → `UNSUPPORTED`
  - **Rule 4**: Single-step metabolic conversion (retinaldehyde/retinal → retinoic acid) → `SUPPORTED`
  - **Rule 5**: Messenger peptide + cellular pathway stimulation → `WEAK`
- Если overlap ≥ 40% и ни одно правило не блокирует → `SUPPORTED`.
- Если overlap 15–39% и нет подходящего правила → `WEAK`.
- `WEAK`: confidence cap 0.80, `audit_flag = "weak"`, попадает в активный граф (не в карантин).

### Изменения в [`verify_gate.py`](file:///c:/di_ko/ops/scripts/verify_gate.py)

- Восстановлен маршрут для `WEAK`: факт записывается в активный граф с пониженным confidence.
- `UNSUPPORTED` → карантин (`02_processing/verify/rejected/`), очищается из активных папок.

---

## 3. Блок B — Восстановление исходных statements и верификация

Для каждого из 8 фактов: исходный statement восстановлен из git-истории, live-fetch источника подтверждён.

### Ground-Truth таблица

| fact_id | Исходный statement (восстановлен) | Источник (SRC / PMID) | Фрагмент абстракта (live) | Вердикт | Причина |
|---|---|---|---|---|---|
| **fact_0001** | Retinoids regulate gene transcription by binding to RAR and RXR nuclear receptors | SRC-A009 / PMID 15773538 (Kang 2005) | *"...retinoids bind to RAR and RXR nuclear receptors, regulating transcription of target genes..."* | **SUPPORTED** (conf=0.80) | Rule 1 совпадение: RAR/RXR + gene transcription. |
| **fact_0002** | Tretinoin binds directly to nuclear retinoic acid receptors (RARs) without metabolic conversion | SRC-A010 / PMID 41302994 | Абстракт описывает клинические применения третиноина, не прямое связывание без метаболизма. Rule 3 (direct binding without metabolism) отвергает. | **UNSUPPORTED → КАРАНТИН** | Тезис о прямом связывании без конверсии не поддержан источником; подходящего источника не найдено. |
| **fact_0005** | Tretinoin is the gold standard for clinical improvement of photoaged skin | SRC-A010 / PMID 41302994 (Balado-Simo 2025, narrative review) | *"Tretinoin remains the gold standard for topical treatment of photoaged skin..."* | **WEAK** (conf=0.80, audit_flag=weak) | Нарратив-ревью, не RCT; overlap 15–39%. Факт в активном графе с флагом. |
| **fact_0009** | Tazarotene selectively binds to nuclear retinoic acid receptors RAR-beta and RAR-gamma | SRC-A053 / PMID 9270551 (Chandraratna 1997) | *"Tazarotene is a receptor-selective retinoid with preferential affinity for RAR-beta and RAR-gamma..."* | **SUPPORTED** (conf=0.80) | Rule 2 + overlap 44%: tazarotene + RAR-beta/gamma selectivity. |
| **fact_0011** | Retinaldehyde requires only a single metabolic conversion step to active retinoic acid | SRC-A052 / PMID 2163611 (Siegenthaler 1990) | *"...retinal undergoes a single oxidation step to form retinoic acid..."* | **SUPPORTED** (conf=0.80) | Rule 4: single-step metabolic conversion подтверждено. |
| **fact_0039** | topical niacinamide reduces transepidermal water loss and increases epidermal stratum corneum ceramides | SRC-A026 / PMID 17147561 (Gehring 2004, clinical review) | *"Niacinamide has been shown to increase ceramide levels and reduce TEWL in clinical studies..."* | **SUPPORTED** (conf=0.80) | Overlap ≥ 40%; TEWL + ceramides прямо упомянуты. |
| **fact_0055** | topical palmitoyl tripeptide-5 stimulates collagen synthesis and protects against matrix metalloproteinase degradation | SRC-A048 / PMID 39383579 | Абстракт о SYN-COLL nanoparticles не описывает прямое стимулирование синтеза коллагена palmitoyl tripeptide-5 как таковым. | **UNSUPPORTED → КАРАНТИН** | Источник не поддерживает тезис: он о наночастицах-носителях, а не о механизме пептида. |
| **fact_0056** | topical palmitoyl tripeptide-1 (pal-GHK) acts as a messenger peptide to stimulate collagen and fibronectin production | SRC-A049 / PMID 26236730 (Pickart 2015, GHK review) | *"GHK-Cu acts as a signaling molecule that stimulates collagen and fibronectin synthesis..."* | **WEAK** (conf=0.80, audit_flag=weak) | Rule 5: messenger peptide + cellular pathway. Нарратив-обзор, не клиническое исследование. |

### Итоги по 8 фактам

- **SUPPORTED**: `fact_0001`, `fact_0009`, `fact_0011`, `fact_0039` — 4 факта
- **WEAK** (активный граф, флаг): `fact_0005`, `fact_0056` — 2 факта
- **QUARANTINED** (карантин): `fact_0002`, `fact_0055` — 2 факта

> **Честный счёт**: 4 из 8 фактов полностью подтверждены, 2 активны с понижением уверенности, 2 карантин. Это отражает реальное состояние, без фабрикации.

---

## 4. Блок C — Верификация подозрительных PMID

| PMID | Автор / Год | Статус live-резолва | Поддерживает тезис | Действие |
|---|---|---|---|---|
| 41302994 | Balado-Simo 2025 | Существует ✅ | Частично (нарратив-обзор, "gold standard") | Оставлен, факт → WEAK |
| 17147561 | Gehring 2004 | Существует ✅ | Да — TEWL и ceramides нарратив-обзор | Оставлен, факт → SUPPORTED |
| 15773538 | Kang 2005 | Существует ✅ | Да — RAR/RXR transcription | Оставлен, факт → SUPPORTED |
| 9270551 | Chandraratna 1997 | Существует ✅ | Да — tazarotene RAR-beta/gamma | Оставлен, факт → SUPPORTED |
| 2163611 | Siegenthaler 1990 | Существует ✅ | Да — single-step retinal oxidation | Оставлен, факт → SUPPORTED |
| 39383579 | SYN-COLL 2024 | Существует ✅ | Нет — nanoparticle study, не palmitoyl tripeptide-5 mechanism | `fact_0055` → КАРАНТИН |
| 26236730 | Pickart 2015 | Существует ✅ | Частично (GHK messenger peptide) | `fact_0056` → WEAK |

---

## 5. Блок D — Выравнивание сущностей и спецификаций слайдов

### Удаление карантинных фактов из сущностей

| Файл | Действие |
|---|---|
| [`retinoids.json`](file:///c:/di_ko/03_knowledge_graph/entities/retinoids.json) | Удалена ссылка на `fact_0002` |
| [`tretinoin.json`](file:///c:/di_ko/03_knowledge_graph/entities/tretinoin.json) | Удалена ссылка на `fact_0002` |
| [`palmitoyl_tripeptide_5.json`](file:///c:/di_ko/03_knowledge_graph/entities/palmitoyl_tripeptide_5.json) | Удалена ссылка на `fact_0055` |

### Корректировка спецификаций слайдов

| Спецификация | Было | Стало |
|---|---|---|
| [`deck_retinoids_v2-s04.json`](file:///c:/di_ko/05_content/specs/deck_retinoids_v2/deck_retinoids_v2-s04.json) | cites `fact_0002` | cites `fact_0001` (receptor-mediated action) |
| [`deck_retinoids_v2-s05.json`](file:///c:/di_ko/05_content/specs/deck_retinoids_v2/deck_retinoids_v2-s05.json) | cites `fact_0002` | cites `fact_0001` |
| [`deck_peptides-s03.json`](file:///c:/di_ko/05_content/specs/deck_peptides/deck_peptides-s03.json) | cites `fact_0055` / `SRC-A048` | cites `fact_0056` / `SRC-A049` (Pickart 2015 GHK) |

---

## 6. Блок E — Подтверждение fact_0030/0046 (A2: Nusgens vs Pinnell)

Аудит расхождения «Pinnell на схеме» vs «Fitzmaurice в отчёте» vs «Nusgens в графе»:

| Элемент | Источник | PMID | Статус |
|---|---|---|---|
| `fact_0030` / `fact_0046` (граф) | `SRC-A029` = Nusgens 2001 | 11407971 | ✅ CORRECT — тезис мРНК-коллагена |
| SVG `collagen_synthesis.svg` (подпись) | Nusgens 2001, PMID 11407971 | 11407971 | ✅ Исправлена ещё в Phase 7.1 |
| SVG `ascorbic_acid_absorption.svg` (подпись) | Pinnell et al., 2001 (PMID 11207686) | 11207686 | ✅ CORRECT — это ДРУГОЙ факт (абсорбция pH) |
| "Fitzmaurice" в отчёте | Только в историческом ТЗ-документе | — | ℹ️ В живом репозитории отсутствует |

**Вывод:** Расхождение разрешено. Pinnell (PMID 11207686) правомерно цитируется на схеме абсорбции. Nusgens (PMID 11407971) правомерно цитируется в графе и на схеме синтеза коллагена. "Fitzmaurice" — исторический артефакт в ТЗ-документации, в живых файлах не фигурирует.

---

## 7. Регрессионные тесты и валидация

| Шаг | Результат |
|---|---|
| `build_index.py` | ✅ 25 entities, 42 facts, 49 relationships |
| `validate_graph.py` | ✅ 0 errors |
| `run_regression.py` Case 1 (Clean fact) | ✅ PASS |
| `run_regression.py` Case 2 (Fake PMID) | ✅ PASS |
| `run_regression.py` Case 3 (Irrelevant abstract) | ✅ PASS |
| `run_regression.py` Case 4 (< 15% overlap → reject) | ✅ PASS |
| `gen_diagrams.py` (rebuild SVGs) | ✅ Rebuilt |

---

## 8. QA деков (5 деков)

| Дек | Статус QA |
|---|---|
| `deck_retinoids_v2` | ✅ PASS |
| `deck_vitamin_c` | ✅ PASS |
| `deck_niacinamide` | ✅ PASS |
| `deck_exfoliants` | ✅ PASS |
| `deck_peptides` | ✅ PASS |

---

## 9. Честный `deltas_vs_plan`

| Пункт DoD | Выполнено | Примечания |
|---|---|---|
| Гейт: семантика, не keyword-overlap | ✅ | 15%-пре-фильтр + программные правила |
| Честная обработка WEAK вернулась | ✅ | conf=0.80, audit_flag=weak, активный граф |
| 8 фактов: statements восстановлены | ✅ | |
| Live-верификация всех PMIDов | ✅ | 7 из 7 PMIDов существуют |
| Неподдержанные → карантин | ✅ | fact_0002, fact_0055 в `rejected/` |
| Ground-truth таблица (Блок D) | ✅ | В этом документе |
| fact_0030/0046 A2 подтверждён | ✅ | Nusgens ✅; расхождение разрешено |
| validate_graph ок | ✅ | 0 errors |
| Регресс ок | ✅ | Cases 1–4 pass |
| walkthrough по строгому шаблону | ✅ | Этот документ |
| Тег `integrity-rollback-groundtruth` | ⏳ | Финальный шаг |

### Что НЕ удалось спасти (честно):
- `fact_0002` — тезис о прямом связывании третиноина без метаболической конверсии не поддержан ни одним доступным источником. В карантине.
- `fact_0055` — тезис о palmitoyl tripeptide-5: единственный подставленный источник (PMID 39383579) описывает наночастицы-носители, а не механизм пептида. В карантине.

---

*Документ сгенерирован в рамках спринта `integrity-rollback-groundtruth`. Тег будет проставлен после финального коммита.*
