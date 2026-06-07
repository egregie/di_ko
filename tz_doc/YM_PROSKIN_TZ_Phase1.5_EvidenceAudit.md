# YM PROSKIN — Phase 1.5: Evidence Audit (Ground-Truth Gate)

Версия: 1.0 · Дата: 2026-06-07 · Предыдущий: Phase 1 (структурно принят, тег `phase-1-retinoids`).
Цель: проверить, что 16 фактов пилота опираются на **реальные** источники, которые
**действительно подтверждают** утверждение и соответствуют присвоенному evidence_level.
Это блокирующий гейт. Дизайн/рендер остаются заморожены до его прохождения.

Легенда: `[ФАКТ]` · `[ВЕРИФ]` · `[GUARD]` жёсткое ограничение.

---

## Почему этот спринт, а не дизайн
- `validate_graph.py` проверяет структуру, НЕ факт. «0 ошибок» ≠ «PMID существует и
  подтверждает claim».
- Риск: выдуманный/чужой PMID → авторитетная дезинформация → наследуется всеми слайдами.
- Принцип P007 (нет факта без источника) сейчас декларирован, но не проверяется машинно.
- Пилот вскрыл слепое пятно пайплайна; чиним на 16 фактах, до масштабирования.

Carry-forward закрыт: RTK-хук активен (`rtk git/gain` работают). Записать в `lessons.md`.

---

## Блок A — `ops/scripts/verify_sources.py` (существование источника)
Для каждого источника из `sources.json`, имеющего `pmid` или `doi`, обратиться к живому API
и подтвердить существование + получить заголовок (и абстракт, если есть).

Эндпоинты `[ФАКТ, ВЕРИФ лимитов]`:
- PubMed esummary: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<PMID>&retmode=json`
- PubMed abstract: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=<PMID>&rettype=abstract&retmode=text`
- DOI (Crossref): `https://api.crossref.org/works/<DOI>`
- Лимит без API-ключа ~3 req/s (с ключом выше) — троттлить. `[ВЕРИФ]`

Скелет (реализовать, не сжимать вывод RTK на этом скрипте):
```python
import json, time, urllib.request, urllib.parse, pathlib
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
def pmid_summary(pmid):
    url = f"{EUTILS}/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    with urllib.request.urlopen(url, timeout=20) as r:
        data = json.load(r)
    rec = data.get("result", {}).get(str(pmid))
    return {"exists": bool(rec and not rec.get("error")),
            "title": (rec or {}).get("title", ""),
            "pubtype": (rec or {}).get("pubtype", [])}
# для каждого source: вызвать, троттлить time.sleep(0.34), записать результат
```
Выход: `ops/logs/source_check_phase1.json` — по каждому источнику `{source_id, pmid/doi,
exists, title, pubtype}`.

Acceptance: каждый источник с PMID/DOI имеет запись exists=true|false + title.

---

## Блок B — Claim-support проверка (заземление на абстракт)
Для каждого факта `fact_0001..0016`:
1. Взять его `sources[]`; подтянуть title/abstract из результатов Блока A (efetch).
2. Агент (A05 source-verify, режим full — детали важны) читает **фактический абстракт** и
   выносит вердикт по `statement`:
   - `SUPPORTED` — абстракт прямо подтверждает;
   - `WEAK` — косвенно/частично;
   - `UNSUPPORTED` — не подтверждает/противоречит;
   - `SOURCE_NOT_FOUND` — источник не существует (Блок A exists=false).
3. Проверить соответствие `evidence_level`: meta/RCT→A, cohort/guideline→B, consensus/case→C.
   Если pubtype не бьётся с уровнем — флаг `EVIDENCE_MISMATCH`.

`[GUARD]` Вердикт основывать ТОЛЬКО на полученном тексте абстракта, не на памяти модели.
Если абстракт недоступен (книга/гайдлайн без PMID) — вердикт `NEEDS_MANUAL`, не угадывать.

Выход: `ops/logs/evidence_audit_phase1.md` — таблица:
`fact_id | claim(≤12 слов) | source_id | exists | verdict | evidence_ok`.

---

## Блок C — Карантин и пересборка
1. Факты с `SOURCE_NOT_FOUND` или `UNSUPPORTED` → переместить из `03_knowledge_graph/facts/`
   в `02_processing/verify/rejected/`; удалить связанные relationships; записать причину в
   `known_problems.md`.
2. `WEAK` / `EVIDENCE_MISMATCH` → оставить, но понизить/исправить `evidence_level` или
   `confidence`; зафиксировать правку.
3. `NEEDS_MANUAL` → оставить с пометкой в файле факта `"status":"needs_manual"`; в граф для
   рендера такие не отдавать (фильтр в retriever позже).
4. Пересобрать индекс: `python ops/scripts/build_index.py`.
5. Перевалидировать: `python ops/scripts/validate_graph.py` (0 ошибок).
6. Перепроверить ретривал: `retriever.py "retinol" --limit 10` → подграф без удалённых фактов.

---

## Блок D — Онтологический спот-чек (A07)
Подтвердить нормализацию: tretinoin = ATRA (один объект с aliases), нет дублей одного
соединения; класс Retinoids — родитель для всех шести. Расхождения — исправить через A07,
записать DEC при изменении правила.

---

## Блок E — Definition of Done (количественно)
- [ ] `source_check_phase1.json`: у каждого источника зафиксировано exists=true|false.
- [ ] `evidence_audit_phase1.md`: у каждого из 16 фактов есть verdict, заземлённый на абстракт.
- [ ] В графе НЕ осталось фактов с `SOURCE_NOT_FOUND` или `UNSUPPORTED`.
- [ ] `WEAK`/`EVIDENCE_MISMATCH` исправлены или помечены; `NEEDS_MANUAL` помечены.
- [ ] Индекс пересобран; `validate_graph.py` 0 ошибок; retriever возвращает очищенный подграф.
- [ ] Онтология нормализована (Блок D).
- [ ] Итоговые счётчики (всего / supported / weak / rejected / needs_manual) — в `walkthrough.md`.
- [ ] Коммит + тег `phase-1.5-audit`.

---

## Блок F — `[GUARD]` и копирайт
- Никаких «вероятно корректно»: PMID не получен → FAIL, не пропускать.
- Абстракты не складывать в граф целиком. Хранить пересказ; цитата ≤15 слов; провенанс.
- Не добивать число фактов: если после карантина осталось <15 — это нормально, зафиксировать
  реальное число и причину. Качество важнее количества (P007).

---

## НЕ трогать
- `04_design_system`, `05_content`, рендер/PPTX — заморожено ДО прохождения этого гейта.
- Другие темы (кислоты, пептиды) — не собирать.

## Открыто `[ВЕРИФ] / [НЕТ ДАННЫХ]`
- Нужен ли NCBI API-ключ для приемлемой скорости (без ключа ~3 req/s — на 16 фактах хватает).
- Источники-гайдлайны/книги без PMID: верифицировать по DOI/издателю либо `NEEDS_MANUAL`,
  не помечать автоматически как FAIL.

---

### Выход
Завершить `walkthrough.md` строго по `WALKTHROUGH_TEMPLATE.md`. В `project_state_snapshot`
обязательно отразить счётчики аудита и список карантина (если есть).
