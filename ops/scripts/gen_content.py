"""
Phase 8.3 — generate deck content specs + provenance from the graph.

SOURCE OF TRUTH: factual block text is pulled from each fact's `statement` + `grade`
straight out of 03_knowledge_graph/facts/ — so every factual block is traceable to a
real fact_id with its real grade by construction (anti-fabrication, P018).
The author only writes neutral author-frame strings (titles, axis/category names,
transitions, interpretation framing) and the fact->slot mapping below.

A factual node may carry a `short` faithful paraphrase ONLY to fit a slot's max_chars
(TZ D3) — fidelity of `short` vs the fact statement is checked by the adversarial
verification pass (Block F). Out-of-scope this phase: id_graph/id_illustration stay
captioned plates (filled by the diagram engine later).

Emits: 04_design_system/deck_<id>_content.json, 04_design_system/deck_<id>_provenance.json
"""
import os, json, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DS = os.path.join(ROOT, "04_design_system")

# ── load graph facts (statement + grade) ────────────────────────────────────
FACTS = {}
for fp in glob.glob(os.path.join(ROOT, "03_knowledge_graph", "facts", "*.json")):
    d = json.load(open(fp, encoding="utf-8"))
    FACTS[d["fact_id"]] = {"statement": d["statement"], "grade": d.get("evidence_level"),
                           "verdict": d.get("audit_verdict")}
REJECTED = {os.path.basename(p)[:-5] for p in
            glob.glob(os.path.join(ROOT, "02_processing", "verify", "rejected", "*.json"))}

GRADE_LEVEL = {  # honest level frame per our derive_grade (DEC-025) definition
    "A": "РКИ / мета-анализ", "B": "контролируемое исслед.", "C": "обзор / огранич. данные",
}

# ── content-node builders (mini-DSL) ────────────────────────────────────────
def F(text, icon=None):            return {"kind": "frame", "text": text, **({"icon": icon} if icon else {})}
def FACT(fid, short=None, lead=None, icon=None):
    return {"kind": "fact", "fact_id": fid, **({"short": short} if short else {}),
            **({"lead": lead} if lead else {}), **({"icon": icon} if icon else {})}
def LIST(*nodes):                  return {"kind": "list", "items": list(nodes)}
def CARD(icon, label, node):       return {"kind": "card", "icon": icon, "label": label, "body": node}
def PLATE(purpose):                return {"kind": "plate", "purpose": purpose}
def LOGO(variant):                 return {"kind": "logo", "variant": variant}
def CAP(text):                     return {"kind": "caption", "text": text}

# ════════════════════════════════════════════════════════════════════════════
# POSTACNE (18)
# ════════════════════════════════════════════════════════════════════════════
POSTACNE = {
 1: {"deck_title": F("Постакне"), "subtitle": F("Доказательные протоколы коррекции · для специалистов"),
     "logo": LOGO("horizontal"), "cover_art": PLATE("обложка")},
 2: {"title": F("Постакне — это не один дефект, а четыре разных задачи"),
     "category_1": CARD("mini_14", "Пигментация", F("ПИГ — стойкие пятна после воспаления (PIH/PIE)")),
     "category_2": CARD("mini_15", "Сосудистый", F("Стойкая эритема — расширенные сосуды (PIE)")),
     "category_3": CARD("mini_16", "Рубцы", F("Атрофические рубцы — потеря дермального каркаса")),
     "category_4": CARD("mini_12", "Текстура", F("Неровность рельефа, поры, шероховатость"))},
 3: {"title": F("Как оценивать постакне: четыре оси разбора"),
     "param_1": CARD("mini_11", "Тип дефекта", F("Пигмент / сосуд / рубец / текстура — разные мишени")),
     "param_2": CARD("mini_09", "Глубина", F("Эпидермис или дерма — определяет выбор метода")),
     "param_3": CARD("mini_10", "Доказательность", F("Уровень данных под каждый метод (A/B/C)")),
     "param_4": CARD("mini_08", "Безопасность", F("Фототип, риск ПВГ, переносимость"))},
 4: {"part_label": F("Часть 1"), "section_title": F("Пигментация"),
     "section_subtitle": F("PIH и PIE: природа, активы, доказательная база"), "logo": LOGO("mark")},
 5: {"title": F("PIH и PIE — разная природа, разная тактика"),
     "anatomy": PLATE("схема: PIH (меланин) vs PIE (сосуд)"),
     "label_1": F("PIH — избыток меланина после воспаления", icon="mini_05"),
     "label_2": F("PIE — стойкое расширение сосудов, эритема", icon="mini_15"),
     "label_3": FACT("fact_0065", short="Обзор: при PIH сильнее всего доказаны ретиноиды и гидроксикислоты; обязателен SPF",
                     icon="mini_10")},
 6: {"title": F("Активы для пигментации × механизм"),
     "col_header": F("Актив → механизм действия (с уровнем доказательности)"),
     "row_1": FACT("fact_0034", short="Ниацинамид снижает гиперпигментацию, подавляя перенос меланосом в кератиноциты"),
     "row_2": FACT("fact_0063", short="Азелаиновая к-та 15%: улучшает поствоспалительную эритему и ПВГ при минимуме реакций"),
     "row_3": FACT("fact_0035", short="Ниацинамид 4% ≈ гидрохинон 4% при мелазме, но с меньшим числом побочных")},
 7: {"title": F("Ниацинамид · азелаиновая кислота · витамин C"),
     "table": PLATE("таблица сравнения активов"),
     "interp": LIST(F("Сравнение по силе доказательств и переносимости:"),
                    FACT("fact_0066", short="Ниацинамид: осветление за счёт блокады переноса меланосом"),
                    FACT("fact_0064", short="Азелаиновая к-та эффективнее плацебо при акне, розацеа, мелазме"),
                    FACT("fact_0021", short="Витамин C (L-аскорб.): синтез коллагена + защита от UV-фотоповреждения")),
     "grade_caption": CAP("Уровни: см. маркер A/B/C у каждого пункта")},
 8: {"title": F("Эффективность по пигментации: что показывают данные"),
     "chart": PLATE("график: эффективность активов при ПВГ"),
     "interp": LIST(F("Ключевые результаты:"),
                    FACT("fact_0035", short="Ниацинамид 4% сопоставим с гидрохиноном 4% при мелазме (меньше побочных)"),
                    FACT("fact_0036", short="Ниацинамид 2% и 5% достоверно снижают гиперпигментацию, повышают светлоту")),
     "source_caption": CAP("Маркер уровня доказательности — у каждого пункта")},
 9: {"part_label": F("Часть 2"), "section_title": F("Рубцы"),
     "section_subtitle": F("Атрофические рубцы: типы и выбор процедуры"), "logo": LOGO("mark")},
 10:{"title": F("Три типа атрофических рубцов"),
     "category_1": CARD("mini_16", "Ice-pick (сколотые)", F("Узкие, глубокие — точечное воздействие")),
     "category_2": CARD("mini_16", "Boxcar (прямоугольные)", F("Широкие, с чёткими краями")),
     "category_3": CARD("mini_17", "Rolling (закруглённые)", F("Волнообразные, фиброзные тяжи в дерме")),
     "category_4": PLATE("схема: типы рубцов в разрезе кожи")},
 11:{"title": F("Карта выбора процедуры по типу рубца"),
     "root": F("Тип рубца определяет метод первой линии"),
     "branch_1": LIST(F("Ice-pick →", icon="mini_20"),
                      FACT("fact_0073", short="CROSS с трихлоруксусной к-той: эффективен и хорошо переносится при ice-pick")),
     "branch_2": LIST(F("Boxcar / общие →", icon="mini_04"),
                      FACT("fact_0067", short="Микронидлинг (систем. обзор РКИ): эффективен и безопасен при атроф. рубцах"),
                      FACT("fact_0070", short="Фракц. пикосекундный лазер: эффект сопоставим, ниже риск ПВГ и боли")),
     "branch_3": LIST(F("Rolling →", icon="mini_19"),
                      FACT("fact_0077", short="Субцизия — самый частый метод при rolling-рубцах"),
                      FACT("fact_0079", short="Фракц. радиочастота предпочтительна у склонных к пигментации"))},
 12:{"title": F("Глубина воздействия процедур по слоям кожи"),
     "anatomy": PLATE("схема: глубина методов по слоям (эпидермис→дерма)"),
     "label_1": FACT("fact_0075", short="Субцизия — хирургическое рассечение тяжей в дерме", icon="mini_19"),
     "label_2": FACT("fact_0078", short="Абляционный фракц. CO₂-лазер — эффективен при атрофических рубцах", icon="mini_04"),
     "label_3": FACT("fact_0079", short="Фракц. RF — воздействие в дерме, выгоден при риске пигментации", icon="mini_07")},
 13:{"title": F("Субцизия · лазер · RF-микронидлинг"),
     "table": PLATE("таблица сравнения процедур"),
     "interp": LIST(F("Сильные стороны и доказательная база:"),
                    FACT("fact_0078", short="CO₂-лазер: выраженный эффект при атрофических рубцах"),
                    FACT("fact_0067", short="Микронидлинг: безопасен, хорошо переносится (обзор РКИ)"),
                    FACT("fact_0076", short="Субцизия: безопасный и эффективный метод при атроф. рубцах")),
     "grade_caption": CAP("Маркер уровня — у каждого пункта")},
 14:{"part_label": F("Часть 3"), "section_title": F("Текстура и протокол"),
     "section_subtitle": F("Кислоты, комбинации и порядок ведения"), "logo": LOGO("mark")},
 15:{"title": F("Система кислот для текстуры"),
     "param_1": CARD("mini_20", "Гликолевая (AHA)", FACT("fact_0072", short="Пилинг гликолевой 70% — альтернатива TCA при атроф. рубцах, меньше downtime")),
     "param_2": CARD("mini_20", "Салицил.+мандел.", FACT("fact_0050", short="Пилинг 20% салицил.+10% мандел. — при акне и постакне-гиперпигментации")),
     "param_3": CARD("mini_20", "Мандел. vs салицил.", FACT("fact_0041", short="45% мандел. ≈ 30% салицил. при акне, но с лучшим профилем безопасности")),
     "param_4": CARD("mini_01", "Принцип", F("Кислоты — поддержка текстуры и пигмента, не первая линия по рубцам"))},
 16:{"title": F("Комбинированный протокол постакне"),
     "track": PLATE("шкала: последовательность ведения"),
     "step_1": F("Стабилизация акне", icon="mini_02"),
     "step_2": FACT("fact_0071", short="Адапален 0.3%+БПО 2.5%: раннее лечение снижает число атрофических рубцов", icon="mini_18"),
     "step_3": F("Пигмент: активы + SPF", icon="mini_08"),
     "step_4": FACT("fact_0068", short="Комбинация микронидлинг+пилинг превосходит каждый метод по отдельности", icon="mini_04")},
 17:{"title": F("Сводка доказательной базы постакне"),
     "facts": LIST(F("Распределение уровней по графу постакне:"),
                   F("A (РКИ/мета-анализ): пигментация — ниацинамид, азелаин, обзор PIH; рубцы — микронидлинг, CO₂-лазер, пикосекунд, RF, адапален+БПО", icon="mini_10"),
                   F("B (контролируемые): CROSS-TCA при ice-pick", icon="mini_10"),
                   F("C (обзоры/огранич.): субцизия, ряд кислотных пилингов, отд. механизмы — подаются как ограниченные данные", icon="mini_11")),
     "grade_legend": CAP("Честная подача: C-уровень = обзор/неконтролируемое, не аксиома")},
 18:{"title": F("Итоговая карта решений"),
     "summary_1": F("Пигментация → ниацинамид / азелаин + обязательный SPF (есть A-данные)", icon="mini_14"),
     "summary_2": F("Рубцы → метод по типу: CROSS (ice-pick), микронидлинг/лазер (boxcar), субцизия/RF (rolling)", icon="mini_16"),
     "summary_3": F("Текстура → кислоты как поддержка; раннее лечение акне предотвращает рубцы", icon="mini_20"),
     "badge": LOGO("badge")},
}

# ════════════════════════════════════════════════════════════════════════════
# RETINOIDS (16)
# ════════════════════════════════════════════════════════════════════════════
RETINOIDS = {
 1: {"deck_title": F("Ретиноиды"), "subtitle": F("Класс, механизм и выбор · для специалистов"),
     "logo": LOGO("horizontal"), "cover_art": PLATE("обложка")},
 2: {"title": F("Какие бывают ретиноиды"),
     "category_1": CARD("mini_03", "Третиноин", F("Активная кислота — прямое действие на рецептор")),
     "category_2": CARD("mini_03", "Ретинол / ретинальдегид", F("Пердретиноиды — нужна конверсия в кислоту")),
     "category_3": CARD("mini_03", "Адапален", F("Синтетический, рецептор-селективный")),
     "category_4": CARD("mini_03", "Тазаротен", F("Синтетический, высокая активность"))},
 3: {"title": F("Четыре оси оценки ретиноида"),
     "param_1": CARD("mini_11", "Эффективность", F("Сила клинического эффекта по задаче")),
     "param_2": CARD("mini_01", "Раздражение", F("Переносимость, риск ретиноидного дерматита")),
     "param_3": CARD("mini_03", "Стабильность", F("Чувствительность к свету/окислению")),
     "param_4": CARD("mini_10", "Доказательность", F("Уровень данных (A/B/C)"))},
 4: {"part_label": F("Часть 1"), "section_title": F("Механизм"),
     "section_subtitle": F("Рецепторы, конверсия, эффект в дерме"), "logo": LOGO("mark")},
 5: {"title": F("Рецепторный механизм: RAR / RXR"),
     "anatomy": PLATE("схема: ретиноид → RAR/RXR → транскрипция"),
     "label_1": FACT("fact_0001", short="Ретиноиды регулируют транскрипцию генов через ядерные рецепторы RAR и RXR", icon="mini_03"),
     "label_2": F("Через рецептор меняется дифференцировка кератиноцитов", icon="mini_09"),
     "label_3": F("Эффект зависит от того, доходит ли молекула до кислоты", icon="mini_11")},
 6: {"title": F("Метаболическая конверсия пердретиноидов"),
     "track": PLATE("шкала: ретинол → ретинальдегид → кислота"),
     "step_1": F("Пердретиноид (ретинол)", icon="mini_18"),
     "step_2": FACT("fact_0011", short="Ретинальдегид: всего один шаг конверсии до активной кислоты в кератиноцитах"),
     "step_3": F("Ретиноевая кислота (активна)", icon="mini_03"),
     "step_4": FACT("fact_0004", short="Ретиноиды повышают синтез проколлагена → формирование коллагена в дерме")},
 7: {"part_label": F("Часть 2"), "section_title": F("Сравнение активов"),
     "section_subtitle": F("Рецепторный профиль и сила эффекта"), "logo": LOGO("mark")},
 8: {"title": F("Активы × свойства"),
     "col_header": F("Актив → рецептор / эффект (с уровнем доказательности)"),
     "row_1": FACT("fact_0009", short="Тазаротен селективно связывает рецепторы RAR-β и RAR-γ"),
     "row_2": FACT("fact_0007", short="Адапален селективно связывает рецепторы RAR-β и RAR-γ"),
     "row_3": FACT("fact_0010", short="Тазаротен 0.1% эффективен при фотоповреждении: морщины, гиперпигментация")},
 9: {"title": F("Третиноин · адапален · тазаротен"),
     "table": PLATE("таблица сравнения ретиноидов"),
     "interp": LIST(F("Профиль каждого актива:"),
                    FACT("fact_0005", short="Третиноин — золотой стандарт улучшения фотостарения кожи"),
                    FACT("fact_0007", short="Адапален — рецептор-селективный (RAR-β/γ)"),
                    FACT("fact_0010", short="Тазаротен 0.1% — эффект при фотоповреждении")),
     "grade_caption": CAP("Маркер уровня — у каждого пункта")},
 10:{"title": F("Эффективность: что показывают данные"),
     "chart": PLATE("график: эффективность ретиноидов"),
     "interp": LIST(F("Клинические результаты:"),
                    FACT("fact_0010", short="Тазаротен 0.1% эффективен при фотоповреждении (морщины, пигментация)"),
                    FACT("fact_0071", short="Адапален 0.3%+БПО снижает число атрофических рубцов при раннем лечении")),
     "source_caption": CAP("Маркер уровня доказательности — у каждого пункта")},
 11:{"part_label": F("Часть 3"), "section_title": F("Решения и применение"),
     "section_subtitle": F("Выбор по задаче, переносимость, безопасность"), "logo": LOGO("mark")},
 12:{"title": F("Выбор ретиноида по задаче"),
     "root": F("Задача определяет молекулу и силу"),
     "branch_1": LIST(F("Фотостарение →", icon="mini_03"),
                      FACT("fact_0005", short="Третиноин — золотой стандарт при фотостарении"),
                      FACT("fact_0010", short="Тазаротен 0.1% — при морщинах и пигментации")),
     "branch_2": LIST(F("Акне / рубцы →", icon="mini_02"),
                      FACT("fact_0007", short="Адапален — рецептор-селективный, базовый при акне"),
                      FACT("fact_0071", short="Адапален+БПО — раннее лечение снижает рубцы")),
     "branch_3": LIST(F("Переносимость →", icon="mini_01"),
                      F("Старт с пердретиноидов/низких концентраций, титрование частоты"))},
 13:{"title": F("Раздражение и адаптация"),
     "visual": PLATE("фото: реакция кожи / титрование"),
     "text": LIST(F("Тактика переносимости (организующая рамка, без претензии на клиническое доказательство):"),
                  F("Старт 2–3×/неделю, наращивание по переносимости"),
                  F("Буфер увлажняющим, избегать одновременных раздражающих кислот"),
                  F("Обязательный SPF — ретиноид повышает фоточувствительность"))},
 14:{"title": F("Противопоказания: категории"),
     "category_1": CARD("mini_08", "Беременность / лактация", FACT("fact_0015", short="Топические ретиноиды противопоказаны при беременности (тератогенный риск)")),
     "category_2": CARD("mini_01", "Барьерные нарушения", F("Активный дерматит, поврежденный барьер — отложить")),
     "category_3": CARD("mini_08", "Инсоляция / процедуры", F("Период активного солнца, сразу после агрессивных процедур")),
     "category_4": CARD("mini_11", "Совместимость", F("Осторожно с другими раздражающими активами"))},
 15:{"title": F("Сводка доказательной базы ретиноидов"),
     "facts": LIST(F("Распределение уровней по графу ретиноидов:"),
                   F("A (РКИ/др. сильные): тазаротен при фотоповреждении; адапален+БПО против рубцов", icon="mini_10"),
                   F("B (контролируемое): противопоказание при беременности", icon="mini_10"),
                   F("C (обзоры/механизм): RAR/RXR, конверсия, «золотой стандарт» — как механизм/обзор, не как РКИ-превосходство", icon="mini_11")),
     "grade_legend": CAP("Честная подача: механизм и «золотой стандарт» — C-уровень, не доказательство превосходства")},
 16:{"title": F("Итоговая карта решений"),
     "summary_1": F("Механизм → эффект через RAR/RXR; пердретиноидам нужна конверсия", icon="mini_03"),
     "summary_2": F("Выбор → фотостарение: третиноин/тазаротен; акне/рубцы: адапален(+БПО)", icon="mini_02"),
     "summary_3": F("Безопасность → титрование, SPF, противопоказание при беременности", icon="mini_08"),
     "badge": LOGO("badge")},
}

# ── resolve facts -> content.json + provenance.json ─────────────────────────
def resolve_node(node, prov, slide_n, slot_id):
    k = node.get("kind")
    if k == "fact":
        fid = node["fact_id"]
        f = FACTS.get(fid)
        if not f:
            raise SystemExit(f"slide {slide_n}/{slot_id}: unknown fact {fid}")
        text = node.get("short") or f["statement"]
        out = {"kind": "fact", "text": text, "fact_id": fid, "grade": f["grade"],
               "grade_level": GRADE_LEVEL.get(f["grade"], "")}
        if node.get("lead"): out["lead"] = node["lead"]
        if node.get("icon"): out["icon"] = node["icon"]
        prov.append({"slide": slide_n, "slot": slot_id, "block": "fact", "fact_id": fid,
                     "grade": f["grade"], "verdict": f["verdict"],
                     "quarantined": fid in REJECTED, "text": text})
        return out
    if k == "frame":
        prov.append({"slide": slide_n, "slot": slot_id, "block": "author_frame", "text": node["text"]})
        return node
    if k == "caption":
        prov.append({"slide": slide_n, "slot": slot_id, "block": "author_frame", "text": node["text"]})
        return node
    if k == "list":
        return {"kind": "list", "items": [resolve_node(n, prov, slide_n, slot_id) for n in node["items"]]}
    if k == "card":
        return {"kind": "card", "icon": node["icon"], "label": node["label"],
                "body": resolve_node(node["body"], prov, slide_n, slot_id)}
    if k in ("plate", "logo"):
        return node
    raise SystemExit(f"unknown node kind {k}")

def build(deck_id, template, title, spec):
    prov = []
    slides = []
    for n in sorted(spec):
        slots = {sid: resolve_node(node, prov, n, sid) for sid, node in spec[n].items()}
        slides.append({"n": n, "slots": slots})
    content = {"deck_id": deck_id, "template": template, "title": title, "slides": slides}
    json.dump(content, open(os.path.join(DS, f"{deck_id}_content.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump({"deck_id": deck_id, "blocks": prov},
              open(os.path.join(DS, f"{deck_id}_provenance.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    facts = [b for b in prov if b["block"] == "fact"]
    frames = [b for b in prov if b["block"] == "author_frame"]
    bad = [b for b in facts if b["quarantined"] or not b["grade"]]
    print(f"{deck_id}: {len(slides)} slides, {len(facts)} factual blocks, {len(frames)} author-frames, "
          f"quarantined/no-grade={len(bad)}")
    return content

build("deck_postacne_filled", "deck_template_postacne", "YM PROSKIN · Постакне", POSTACNE)
build("deck_retinoids_filled", "deck_template_retinoids", "YM PROSKIN · Ретиноиды", RETINOIDS)
