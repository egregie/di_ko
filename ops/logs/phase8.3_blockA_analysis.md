# Phase 8.3 — Block A: Reference analysis + asset inventory

> Read-only. Reference = STYLE of placement, not approved content template (old/ref decks are drafts, deprecated). Grade count = **A:21 / B:3 / C:31** (real, from disk).

## A1 — Visual-language patterns (from 3 reference decks + old decks)

Reference decks (`postakne model create 2/3/4.pdf`, NotebookLM-generated, 14–15 slides) — borrow LAYOUT/DENSITY/PLACEMENT only, NOT font (they use a serif; brand = Arimo per design-tokens).

| Pattern | Observed | Where to apply |
|---|---|---|
| Background line-art behind text | faint botanical + molecule/hexagon outlines in corners, low opacity, under text | C2 bg-molecule 35% on light text-heavy slides (title, section, text content) |
| Two-zone content | heading top; text left (paragraph + bold-lead bullets); visuals right (diagram + photo grid) | B1_split, B3_anatomy, reworked C1/C3 |
| Bold-lead bullets | "Причина: …", "Процесс: …", "Результат: …" (lead word bold, then explanation) | body lists on Knowledge/Authority slides |
| Category grid w/ circular icons | 2×2 / 3-col cells = circular sage icon + bold label + body | A1 classification cells, reworked A2 framework cells (use mini-SVGs as icons) |
| 3-column visual classification | Ice-pick / Boxcar / Rolling, each label + diagram | A1 scar-types slide |
| Warning / scope pill | sage/terracotta pill + ⚠️ icon at bottom: scope/safety caveat | grade-level framing, contraindications, "вне компетенций" notes |
| Palette | sage greens, warm beige, terracotta accents | already = design-tokens (bg/sage/herbal/bgAlt/warn) |
| Density | content slides are text-rich (paragraph + 3-item list + 2 visual panels) | reworked C1/C3 add interpretation text beside a smaller plate |

## A2 — Mini-SVG inventory (`design/svg_mini/` → recolored to `04_design_system/assets/mini/`)

All 21 had `fill="#000000"` → recolored to `currentColor` (0 residual black). Line-icon style, Postacne-themed.

| File | Depicts | Type | Suggested use |
|---|---|---|---|
| mini_01 | droplet + shield | accent | barrier / protection / serum safety |
| mini_02 | cross + bacteria | category | acne / medical treatment |
| mini_03 | arrows + DNA | mechanism | cell turnover / conversion |
| mini_04 | hand + resurfacing tool | procedure | resurfacing / abrasion |
| mini_05 | cell w/ dots (melanocyte) | mechanism | pigment cell / melanosome |
| mini_06 | tangled fibers | mechanism | collagen / scar fibrosis |
| mini_07 | syringe + tools | category | procedure toolkit |
| mini_08 | sun + shield+check | accent | photoprotection / SPF |
| mini_09 | skin + follicle cross-section | anatomy | skin layers |
| mini_10 | document + magnifier | icon | evidence / study (Evidence Summary, sources) |
| mini_11 | magnifier | accent | analysis / detail / assessment |
| mini_12 | skin layer + bumps | anatomy | texture / surface |
| mini_13 | skin wave + dots | anatomy | texture / surface |
| mini_14 | circle + spots | category | pigmentation / pores |
| mini_15 | branching | category | vascular / erythema (PIE) |
| mini_16 | skin + depression (boxcar) | anatomy | atrophic scar type |
| mini_17 | skin + wavy depression (rolling) | anatomy | rolling scar type |
| mini_18 | cream tube | icon | topical application |
| mini_19 | scalpel + dashed line | procedure | subcision / surgical |
| mini_20 | flask + droplet | icon | formulation / chemical peel |
| mini_21 | multi-icon set | composite | mechanism legend / multi-factor |

[GUARD] Mini-SVGs are decorative-structural — they NEVER carry a factual assertion (do not replace id_illustration/id_graph). Combined with text (bullet markers, category-card icons, dividers).

## A3 — Slide → fact_id → grade map (drives Block D)

Author-frame = structural (titles, category names, axis names, transitions) — NO factual claim, no grade. Factual cells trace to fact_id + grade.

### Postacne (18)
| # | layout | theme | fact_ids (grade) | author-frame? |
|---|---|---|---|---|
| 1 | D1_title | title | — | frame |
| 2 | A1_classification | постакне → 4 категории | — (categories = organizing frame) | frame |
| 3 | A2_framework | как оценивать постакне | — (axes = frame) | frame |
| 4 | D2_section | Ч.1 Пигментация | — | frame |
| 5 | B3_anatomy | PIH vs PIE | fact_0065(A) | + frame (PIE nature) |
| 6 | A4_matrix | активы пигментации × механизм | 0034(A),0066(A),0063(A),0074(C),0035(A),0036(A) | grid frame + facts |
| 7 | C1_comparison | ниацинамид/азелаин/вит C | 0035(A),0066(A),0063(A),0064(A),0021(C) | facts |
| 8 | C3_research_chart | эффективность пигментации | 0035(A),0036(A),0065(A) | facts + chart slot |
| 9 | D2_section | Ч.2 Рубцы | — | frame |
| 10 | A1_classification | типы атрофических рубцов (+illustration) | — (ice-pick/boxcar/rolling = anatomical frame) | frame |
| 11 | A3_decision_map | выбор процедуры по типу рубца | 0073(B),0077(C),0078(A),0067(A),0079(A),0070(A) | frame map + facts |
| 12 | B3_anatomy | глубина процедур по слоям | 0075(C),0078(A),0079(A) | frame (depth) + facts |
| 13 | C1_comparison | субцизия/лазер/RF | 0075(C),0076(C),0077(C),0078(A),0079(A),0067(A),0070(A) | facts |
| 14 | D2_section | Ч.3 Текстура и протокол | — | frame |
| 15 | A2_framework | система кислот для текстуры | 0072(C),0050(C),0018(C),0019(C),0041(A),0068(C) | facts in cells |
| 16 | B2_process | комбинированный протокол | 0071(A),0068(C) | frame (sequence) + facts |
| 17 | C2_evidence_summary | сводка + grade | ALL postacne facts (grade distribution) | facts |
| 18 | D3_closing | итоговая карта | — | frame |

### Retinoids (16)
| # | layout | theme | fact_ids (grade) | author-frame? |
|---|---|---|---|---|
| 1 | D1_title | title | — | frame |
| 2 | A1_classification | какие бывают ретиноиды | — (types = frame) | frame |
| 3 | A2_framework | 4 оси оценки | — (axes = frame) | frame |
| 4 | D2_section | Ч.1 Механизм | — | frame |
| 5 | B3_anatomy | RAR/RXR механизм | 0001(C) | + frame |
| 6 | B2_process | метаболическая конверсия | 0011(C),0004(C) | frame + facts |
| 7 | D2_section | Ч.2 Сравнение | — | frame |
| 8 | A4_matrix | активы × свойства | 0009(C),0007(C),0001(C),0010(A),0005(C) | grid frame + facts |
| 9 | C1_comparison | третиноин/адапален/тазаротен | 0005(C),0007(C),0009(C),0010(A) | facts |
| 10 | C3_research_chart | эффективность данные | 0010(A),0071(A) | facts + chart slot |
| 11 | D2_section | Ч.3 Решения | — | frame |
| 12 | A3_decision_map | выбор ретиноида по задаче | 0010(A),0005(C),0007(C),0071(A) | frame map + facts |
| 13 | B1_split | раздражение и адаптация | ⚠️ **NO direct graph fact** (irritation fact was quarantined) | **frame only — titration guidance, NO efficacy claim** |
| 14 | A1_classification | противопоказания | 0015(B) | frame + pregnancy fact |
| 15 | C2_evidence_summary | сводка + grade | ALL retinoid facts (grade distribution) | facts |
| 16 | D3_closing | итоговая карта | — | frame |

**Flagged (A3 GUARD):** Retinoids s13 has no supporting graph fact → author frame only (no fabricated efficacy). Many retinoid mechanism facts are grade C (mechanism / "gold standard") → must be framed honestly, not as proof of clinical superiority.
