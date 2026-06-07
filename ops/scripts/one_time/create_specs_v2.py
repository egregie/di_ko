import os
import json

specs = [
    {
        "id": "deck_retinoids_v2-s01",
        "layout": "cover",
        "section": "Ретиноиды",
        "title": "YM PROSKIN · Ретиноиды v2",
        "subtitle": "Терапевтический профиль, механизмы действия и клинические протоколы",
        "body": [],
        "media": {
            "type": "image",
            "asset": "cover_placeholder.png",
            "fit": "cover",
            "caption": "Ретиноиды в дерматологии"
        },
        "components": {},
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": [],
        "notes": "Титульный слайд"
    },
    {
        "id": "deck_retinoids_v2-s02",
        "layout": "section_divider",
        "section": "Часть 1",
        "title": "Механизмы и Кинетика",
        "subtitle": "Клеточные рецепторы и пути метаболической конверсии",
        "body": [],
        "media": {},
        "components": {},
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": [],
        "notes": "Разделитель разделов"
    },
    {
        "id": "deck_retinoids_v2-s03",
        "layout": "quote_callout",
        "section": "Ретиноиды",
        "title": "Ядерные Рецепторы",
        "subtitle": "Основной путь транскрипции генов",
        "body": [
            {
                "type": "quote",
                "text": "Ретиноиды регулируют генную транскрипцию путем связывания с ядерными рецепторами RAR и RXR."
            }
        ],
        "media": {},
        "components": {},
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": ["fact_0001", "SRC-A009"],
        "notes": "Биологический механизм регуляции транскрипции генов"
    },
    {
        "id": "deck_retinoids_v2-s04",
        "layout": "timeline_protocol",
        "section": "Ретиноиды",
        "title": "Путь Метаболической Конверсии",
        "subtitle": "Каскад окисления ретиноидов в кератиноцитах",
        "body": [
            {
                "type": "step",
                "label": "Ретилпальмитат",
                "desc": "Слабый эфир, требует 3 шага конверсии до ретиноевой кислоты."
            },
            {
                "type": "step",
                "label": "Ретинол",
                "desc": "Стимулирует коллаген, требует 2 шага метаболического превращения."
            },
            {
                "type": "step",
                "label": "Ретинальдегид",
                "desc": "Высокоактивный ретиналь, требует всего 1 шаг конверсии."
            },
            {
                "type": "step",
                "label": "Ретиноевая кислота",
                "desc": "Активный третиноин, связывается напрямую с рецепторами."
            }
        ],
        "media": {},
        "components": {},
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": ["fact_0002", "fact_0004", "fact_0011"],
        "notes": "Путь превращения различных ретиноидов"
    },
    {
        "id": "deck_retinoids_v2-s05",
        "layout": "two_columns_image",
        "section": "Ретиноиды",
        "title": "Терапия Третиноином",
        "subtitle": "Клинические эффекты золотого стандарта коррекции",
        "body": [
            {
                "type": "bullet",
                "text": "Третиноин связывается напрямую с рецепторами rars без метаболической конверсии."
            },
            {
                "type": "bullet",
                "text": "Является золотым стандартом для клинического улучшения фотоповрежденной кожи."
            },
            {
                "type": "bullet",
                "text": "Нормализует дифференцировку кератиноцитов для предотвращения окклюзии фолликулов."
            }
        ],
        "media": {
            "type": "image",
            "asset": "tretinoin_media.png",
            "fit": "cover",
            "caption": "Эффект третиноина на эпидермис"
        },
        "components": {},
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": ["fact_0002", "fact_0005", "fact_0006"],
        "notes": "Эффекты третиноина при акне и старении"
    },
    {
        "id": "deck_retinoids_v2-s06",
        "layout": "comparison",
        "section": "Ретиноиды",
        "title": "Сравнение Селективных Форм",
        "subtitle": "Адапален против Тазаротена",
        "body": [
            {
                "type": "compare_left",
                "label": "Адапален",
                "text": "Селективно связывается с rar-beta и rar-gamma рецепторами, снижает риск раздражений."
            },
            {
                "type": "compare_right",
                "label": "Тазаротен",
                "text": "Связывается с rar-beta и rar-gamma, крем 0.1% клинически эффективен при фотоповреждении."
            }
        ],
        "media": {},
        "components": {},
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": ["fact_0007", "fact_0009", "fact_0010"],
        "notes": "Селективное действие ретиноидов"
    },
    {
        "id": "deck_retinoids_v2-s07",
        "layout": "three_cards",
        "section": "Ретиноиды",
        "title": "Безрецептурные Формы",
        "subtitle": "Биологическая активность ретинола, ретиналя и эфиров",
        "body": [
            {
                "type": "card",
                "title": "Ретинальдегид",
                "text": "Улучшает гидратацию и эластичность кожи, требует одного метаболического шага."
            },
            {
                "type": "card",
                "title": "Ретинол",
                "text": "Стимулирует синтез коллагена и ингибирует матриксные металлопротеиназы."
            },
            {
                "type": "card",
                "title": "Ретилпальмитат",
                "text": "Мягкая нано-форма, снижает воспалительные и невоспалительные акне-поражения."
            }
        ],
        "media": {},
        "components": {},
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": ["fact_0004", "fact_0011", "fact_0012", "fact_0014"],
        "notes": "Сравнение безрецептурных ретиноидов"
    },
    {
        "id": "deck_retinoids_v2-s08",
        "layout": "statistics",
        "section": "Ретиноиды",
        "title": "Клинические Метрики",
        "subtitle": "Параметры эффективности ретиноидов третьего поколения",
        "body": [
            {
                "type": "stat_item",
                "number": "0.1%",
                "label": "Тазаротен",
                "desc": "Концентрация крема, доказавшая эффективность при глубоких морщинах."
            },
            {
                "type": "stat_item",
                "number": "1 шаг",
                "label": "Ретинальдегид",
                "desc": "Конверсия до активной кислоты, минимизирует раздражения."
            },
            {
                "type": "stat_item",
                "number": "12 фкт",
                "label": "Проверенная база",
                "desc": "Клинически подтвержденных фактов в нашем графе ретиноидов."
            }
        ],
        "media": {},
        "components": {},
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": ["fact_0010", "fact_0011", "fact_0012"],
        "notes": "Показатели терапевтической эффективности"
    },
    {
        "id": "deck_retinoids_v2-s09",
        "layout": "contraindication_alert",
        "section": "Ретиноиды",
        "title": "Безопасность и Ограничения",
        "subtitle": "Меры предосторожности в клинической практике",
        "body": [],
        "media": {},
        "components": {
            "alert": {
                "title": "Абсолютное противопоказание: Беременность и лактация",
                "text": "Топические ретиноиды противопоказаны к применению в период беременности и лактации из-за потенциальных рисков системной тератогенности."
            }
        },
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": ["fact_0015", "SRC-A018"],
        "notes": "Слайд с предупреждением о противопоказании при беременности"
    },
    {
        "id": "deck_retinoids_v2-s10",
        "layout": "summary",
        "section": "Ретиноиды",
        "title": "Терапевтические Выводы",
        "subtitle": "Сводное резюме клинических рекомендаций по ретиноидам",
        "body": [
            {
                "type": "bullet",
                "text": "Назначение конкретного ретиноида определяется целями терапии и чувствительностью кожи."
            },
            {
                "type": "bullet",
                "text": "Селективные агонисты (адапален, тазаротен) предпочтительны при целевой монотерапии."
            },
            {
                "type": "bullet",
                "text": "Необходимо строго контролировать применение и исключать пациентов в группе риска."
            }
        ],
        "media": {},
        "components": {},
        "disclaimers": ["Только для практикующих специалистов"],
        "source_refs": ["fact_0001", "fact_0007", "fact_0015"],
        "notes": "Заключительные выводы и рекомендации"
    }
]

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    specs_dir = os.path.join(project_root, "05_content", "specs", "deck_retinoids_v2")
    os.makedirs(specs_dir, exist_ok=True)
    
    for s in specs:
        spec_path = os.path.join(specs_dir, f"{s['id']}.json")
        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2, ensure_ascii=False)
        print(f"Generated spec for {s['id']}")

if __name__ == "__main__":
    run()
