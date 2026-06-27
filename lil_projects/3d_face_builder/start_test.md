ГПТ 
Короткий ответ: нет, они не вспомнили все лучшие современные движки и инструменты. Даже близко.

Но что важно: это не недостаток анализа, а следствие того, что все трое (я, Gemini, Grok) обсуждали архитектуру вокруг MediaPipe-пайплайна, а не делали полноценный технологический аудит рынка CV/3D Reconstruction на 2025-2026 год.

Поэтому я бы разделил задачу на две части:

Часть 1. Что из ваших обсуждений нужно оставить

После объединения всех замечаний я бы оставил примерно 90% следующего.

Оставить обязательно
Архитектурный каркас
Input
↓
Preprocess
↓
Landmarks
↓
Scale Estimation
↓
Canonical Face Reconstruction
↓
Accessory Generator
↓
Mesh Processing
↓
QA / Confidence
↓
Export

Это сейчас самый здравый вариант.

Canonical Base Mesh

Это центральная идея проекта.

Не:

Фото
→ генерируем меш

А:

Фото
→ landmarks
→ деформируем эталонную голову

Это остается.

Confidence Score

Обязательно.

Я бы даже расширил.

Не один score.

А:

{
  "photo_quality": 0.91,
  "landmark_quality": 0.95,
  "scale_quality": 0.84,
  "reconstruction_quality": 0.79,
  "mesh_quality": 0.97,
  "final_confidence": 0.88
}
Generator Layer

Gemini и Grok абсолютно правы.

Это отдельная подсистема.

Не смешивать с mesh processing.

Pipeline Config

Да.

Сначала:

pipeline_config.json

Потом всё остальное.

Это SSOT.

Часть 2. Что я бы изменил даже после Gemini и Grok
Убрал бы Knowledge Graph

Сейчас это выглядит как наследие SVG Builder.

Для MVP пользы почти нет.

Я бы заменил на:

artifact registry

Простой реестр артефактов.

Убрал бы Markdown Passports

Лучше:

JSON

или

Pydantic Models

Markdown красиво.

Но автоматизация хуже.

Не делал бы ставку на Iris

Тут Gemini немного переоценивает.

Проблема:

11.7 ± 0.5 мм

это уже почти:

±4%

ошибки.

Плюс:

разрешение фото
размытие
угол головы
качество сегментации

Я бы использовал иерархию:

User Measurement
↓
Reference Object
↓
IPD
↓
Iris
↓
Fallback

а не наоборот.

Самое главное

Теперь самое интересное.

Нет, вы не обсудили лучшие движки 2025-2026

Вы обсуждали только:

MediaPipe
DensePose
TPS
RBF
Open3D
Trimesh

Это лишь маленькая часть рынка.

Что бы я добавил в исследование
CV Layer

Вместо только MediaPipe изучить:

MediaPipe Face Landmarker

Текущий кандидат №1.

Оставить.

InsightFace

Очень сильный кандидат.

Плюсы:

face alignment
face parsing
pose estimation

Иногда стабильнее MediaPipe.

Face Alignment Network (FAN)

До сих пор используется в исследовательских пайплайнах.

Особенно для реконструкции.

Face Reconstruction Layer

Вот здесь главный пробел.

FLAME

Самый важный кандидат.

FLAME

Если бы я выбирал одну технологию для проекта — это был бы FLAME.

Почему?

Потому что:

MediaPipe
=
landmarks

FLAME
=
параметрическая голова

Вместо собственного basemesh.

DECA

DECA

Очень интересный вариант.

Позволяет восстановить форму лица намного лучше обычного MediaPipe.

EMOCA

EMOCA

Современное развитие DECA.

Depth Estimation

Вы вообще не обсуждали этот слой.

А зря.

Depth Anything V2

Depth Anything V2

Сейчас один из лучших depth-моделей.

Я бы обязательно тестировал.

Metric3D

Metric3D

Интересен именно для получения метрической глубины.

Mesh Processing
Open3D

Оставить.

Trimesh

Оставить.

PyMeshLab

PyMeshLab

Очень рекомендую добавить.

Дает:

remesh
decimation
cleanup
repair
MeshLab Engine

Очень полезен для repair.

Boolean Operations

Вот тут ещё одна ловушка.

Trimesh часто ломается.

Я бы изучил:

Blender Geometry Nodes

Blender

через headless режим.

Очень надежно.

OpenCascade

Open CASCADE Technology

если проект уйдет в инженерную геометрию.

Что бы я дал Клоду как финальное направление

Если убрать всё лишнее, то стек 2026 года выглядит так:

CV
────────────────────

MediaPipe Face Landmarker
InsightFace

Reconstruction
────────────────────

FLAME
DECA
EMOCA

Depth
────────────────────

Depth Anything V2
Metric3D

Geometry
────────────────────

Open3D
Trimesh
PyMeshLab

Boolean
────────────────────

Blender Headless

Validation
────────────────────

Pydantic
JSON Schema

Export
────────────────────

3MF
GLB
STL
OBJ

Самый важный вывод после прочтения Gemini и Grok:

Они очень хорошо оптимизировали первоначальную архитектуру, но всё ещё мыслят в парадигме "MediaPipe → TPS → Mesh".

Если ты начинаешь проект с нуля в 2026 году, то я бы заставил Claude провести отдельный deep research именно по связке:

FLAME
vs
DECA
vs
EMOCA
vs
MediaPipe-only

для задач:
- маски
- очки
- украшения
- плотная посадка на лицо
- 3D печать

Потому что именно здесь находится потенциальный скачок качества на порядок, а не в выборе между очередным TPS и RBF-интерполятором.

вот коментарий к твоему ответу: подумай и прийми решение что внедрить в твоей ответ
учти все идеи и предложения, проанализируй, определи и оставь для нас самое лучшее со всех этих идей, примерь к проекту. 

 Ещё раз повтори, действительно ли мои коллеги смогли вспомнить все лучшие новейшие движки для этого процессора, препроцессоры, модули оптического зрения, скилы-агенты, плагины, тулзы разные, которые можно будет внедрить и использовать в моём проекте. Притом учти, что я буду работать над проектом в ПК-версии приложения Cloud Code. ответ дай в виде детального проработанного тз для клода.

Твой коллега правильно поставил вопрос. В моем прошлом ответе я перечислил сильные технологии, но не принял финальное архитектурное решение под твои реальные ограничения:

локальная разработка;
Cloud Code Desktop;
RTX 2060 8GB;
Python-first стек;
детерминированный pipeline;
производство 3D-моделей под печать;
отсутствие гарантированных LiDAR/TrueDepth данных;
необходимость дальнейшего масштабирования.

После объединения всех обсуждений (Gemini + Grok + мой анализ) я бы изменил первоначальную рекомендацию.

ГЛАВНЫЙ ВЫВОД

Нет.

Коллеги НЕ вспомнили все лучшие современные движки и инструменты.

Но.

Они вспомнили примерно 70-80% того, что реально пригодится для MVP и первой production-версии.

Самое важное, что отсутствует:

Face Reconstruction
FLAME
DECA
EMOCA
Depth
Depth Anything V2
Metric3D
Mesh Processing
PyMeshLab
Blender Headless Geometry Processing
Quality Estimation
BRISQUE
NIMA
Face Quality Assessment модели
Face Parsing
InsightFace
BiSeNet Face Parsing

Именно эти компоненты я бы заставил Claude исследовать отдельно.

САМОЕ ВАЖНОЕ РЕШЕНИЕ

После всех обсуждений я бы НЕ строил проект вокруг:

MediaPipe
→ TPS
→ Export

Это уже выглядит как архитектура 2022-2023.

Я бы строил вокруг:

MediaPipe
+
FLAME
+
Depth Anything V2
+
Accessory Generator
+
PyMeshLab
+
Blender Headless

Это гораздо ближе к современному стеку 2026.

ЧТО ОСТАВИТЬ ИЗ ВСЕХ ВЕРСИЙ
Оставляем
MediaPipe Face Landmarker

Причина:

быстрый
бесплатный
стабильный
работает локально
хорошо интегрируется
Canonical Face Mesh

Обязательно.

Но лучше:

FLAME

чем самодельный BaseMesh.

Scale Estimation Layer

Обязательно.

Иерархия:

User Override
↓
Reference Object
↓
IPD
↓
Iris
↓
Fallback
Confidence Layer

Обязательно.

Причем многокомпонентный.

Accessory Generator

Обязательно.

Отдельный слой.

Guard Rails

Обязательно.

Artifact Registry

Оставить.

ЧТО ВЫКИНУТЬ
DensePose

Удалить.

Detectron2

Удалить.

Full Body CV

Удалить.

Самодельный Knowledge Graph

Для MVP удалить.

Заменить:

Artifact Registry
Markdown Passports

Заменить:

JSON
+
Pydantic
ЧТО ДОБАВИТЬ ОБЯЗАТЕЛЬНО
Face Quality Agent

Проверяет:

размытие
засветы
угол головы
окклюзии
очки
волосы

Если качество низкое:

reject

до запуска pipeline.

Reconstruction Agent

Сравнивает:

MediaPipe only
vs
FLAME fit
vs
Depth fit

и выбирает лучший вариант.

Mesh Repair Agent

Использует:

PyMeshLab

для ремонта.

Boolean Agent

Использует:

Blender Headless

а не Trimesh.

ЧТО Я БЫ ВЫБРАЛ ДЛЯ RTX2060

Вот здесь самое важное.

Не использовать

EMOCA

для постоянного pipeline.

Слишком тяжелая.

Не использовать

полноценные нейронные реконструкторы головы.

Использовать

MediaPipe

FLAME

Depth Anything V2

по требованию.

Это оптимальный баланс:

качество
/
скорость
/
VRAM
ФИНАЛЬНАЯ АРХИТЕКТУРА ДЛЯ ПРОЕКТА
INPUT
│
├── Photo Quality Agent
│
├── Preprocessing Agent
│    ├── Crop
│    ├── Alignment
│    ├── Exposure Normalize
│    └── Lens Distortion Compensation
│
├── Landmark Agent
│    ├── MediaPipe Face Landmarker
│    └── Iris Extraction
│
├── Scale Agent
│    ├── User Override
│    ├── Reference Object
│    ├── IPD
│    ├── Iris
│    └── Fallback
│
├── Face Reconstruction Agent
│    ├── FLAME Fit
│    ├── Landmark Projection
│    └── Depth Fusion
│
├── Accessory Generator Agent
│    ├── Mask
│    ├── Glasses
│    ├── Jewelry
│    └── Helmet
│
├── Mesh Processing Agent
│    ├── Thickness
│    ├── Remesh
│    ├── Smoothing
│    └── Decimation
│
├── Boolean Agent
│    └── Blender Headless
│
├── Mesh Repair Agent
│    └── PyMeshLab
│
├── QA Agent
│    ├── Watertight
│    ├── Self Intersection
│    ├── Printer Bounds
│    ├── Confidence
│    └── Quarantine
│
└── Export Agent
     ├── 3MF
     ├── STL
     ├── GLB
     └── OBJ
ТЗ ДЛЯ CLAUDE (что исследовать)

PROJECT: 3D_FACE_BUILDER

OBJECTIVE

Perform a deep technical research and architecture audit for a local-first 3D face reconstruction and accessory generation pipeline intended for 3D printing.

HARD CONSTRAINTS

Development environment: Cloud Code Desktop
Language: Python 3.11+
GPU: RTX 2060 8GB
Local execution preferred
Deterministic pipeline
Physical output accuracy is more important than visual realism
Input is usually a single RGB photo
Optional future support for multiple photos
Output formats: 3MF, STL, OBJ, GLB
Maximum build volume: 350x350x350 mm

RESEARCH TASKS

Evaluate and compare:
MediaPipe Face Landmarker
FLAME
DECA
EMOCA
InsightFace
Depth Anything V2
Metric3D

For:

reconstruction accuracy
runtime speed
VRAM usage
robustness
local deployment complexity
suitability for 3D printing
Determine optimal reconstruction pipeline under RTX2060 constraints.
Determine whether FLAME should replace a custom Canonical Base Mesh.
Evaluate hybrid reconstruction:

MediaPipe + FLAME
MediaPipe + Depth Anything
MediaPipe + FLAME + Depth Fusion

Research best mesh repair stack:
Trimesh
Open3D
PyMeshLab
Blender Headless
OpenCascade
Design agent architecture:
Photo Quality Agent
Landmark Agent
Scale Agent
Reconstruction Agent
Accessory Generator Agent
Mesh Processing Agent
Boolean Agent
Mesh Repair Agent
QA Agent
Export Agent
Produce final recommendations with:
architecture diagrams
module contracts
dependency matrix
performance estimates
VRAM estimates
implementation roadmap
risk matrix
MVP scope
production scope

DELIVERABLE

Produce a final architecture recommendation optimized specifically for RTX2060 8GB and Cloud Code Desktop development environment.

Если бы проект запускался завтра, я бы начинал не с AGENTS.md и не с генераторов масок, а с проверки одной гипотезы:

MediaPipe + FLAME + пользовательская калибровка масштаба против MediaPipe-only.

От результата этого сравнения зависит примерно 50% всей дальнейшей архитектуры проекта.

ГРОК
**Финальный вердикт по логике, архитектуре и структуре проекта**

**Общая логика проекта — правильная и перспективная (8.5/10).**  
Все обсуждения (Gemini, GPT, мои предыдущие) сходятся в ключевом: **деформация параметрического/канонического Base Mesh** намного лучше генерации меша "с нуля" из одного фото. Это промышленный подход, минимизирующий артефакты и обеспечивающий анатомическую правдоподобность.

**Архитектура после синтеза всех идей — гибридная и реалистичная для твоих ограничений (RTX 2060 8GB, Cloud Code Desktop, Python, локальный запуск, 3D-печать).**  
- **Не чистый MediaPipe+TSP** (устаревает).  
- **Не тяжёлый DECA/EMOCA** в основном пайплайне (VRAM).  
- **Оптимально**: MediaPipe Face Landmarker + FLAME (как основной Canonical Mesh) + Depth Anything V2 (опционально для улучшения Z и перспективы) + PyMeshLab + Blender Headless для обработки.  
Это даёт **скачок качества** по сравнению с исходным ТЗ, при сохранении производительности.

**Структура проекта** — упростить (убрать Knowledge Graph и Markdown passports для MVP). Оставить чёткую иерархию папок с акцентом на `00_governance`, `ops/scripts` (агенты) и artifact registry (JSON + Pydantic).

**Коллеги вспомнили ~75-80% лучших инструментов.**  
Отсутствовали/недооценены: FLAME (лучший для parametric head), DECA/EMOCA (детали), Depth Anything V2 / Metric3D (метрическая глубина), PyMeshLab + Blender Headless (repair & boolean). Они перечислены в GPT-анализе и подтверждены актуальным состоянием на 2026 год. Я интегрировал всё лучшее.

### Детальное ТЗ для Claude (Opus / Sonnet) в Cloud Code

**Скопируй это полностью в новый чат с Claude в Cloud Code Desktop.**

---

**PROJECT: 3d_face_builder**  
**Версия ТЗ: 1.0 (Синтез Gemini + GPT + Grok, оптимизировано под RTX 2060 8GB)**  
**Дата: Июнь 2026**  
**Цель:** Создать детерминированный, локальный Python-конвейер генерации непланарной 3D-геометрии (маски, очки, украшения, шлемы) для 3D-печати из одного RGB-фото с акцентом на физическую точность посадки.

#### Жёсткие ограничения
- **Окружение:** Cloud Code Desktop, Python 3.11+, RTX 2060 8GB VRAM.
- **Input:** Преимущественно одно RGB-фото (фас/полупрофиль). Опционально — несколько фото в будущем.
- **Output:** Манifoldный, watertight меш в единицах миллиметров, bounds ≤ 350×350×350 мм. Форматы: 3MF (приоритет), STL, OBJ, GLB.
- **Требования:** Локальный запуск без интернета после установки. Минимизировать VRAM. Детерминированность (seed + config). Точность для печати > визуального реализма.
- **Не использовать:** DensePose, Detectron2, тяжёлые EMOCA/DECA в основном пайплайне.

#### Финальная архитектура пайплайна (агенты)

```
Input Raster
    ↓
1. Photo Quality Agent          → reject / score (blur, pose, lighting, occlusions)
    ↓
2. Preprocessing Agent          → crop, align, undistort (barrel + perspective)
    ↓
3. Landmark Agent               → MediaPipe Face Landmarker (478 pts + Iris)
    ↓
4. Scale Estimation Agent       → User > Reference Object > IPD > Iris > Fallback
    ↓
5. Face Reconstruction Agent    → FLAME fit (primary) + MediaPipe projection + optional Depth Anything V2 fusion
    ↓
6. Accessory Generator Agent    → parametric (mask/glasses/jewelry/helmet) по Vertex ID FLAME
    ↓
7. Mesh Processing Agent        → non-planar thickness (normal displacement), remesh, smooth, decimate
    ↓
8. Boolean & Repair Agent       → Blender Headless (boolean) + PyMeshLab (repair)
    ↓
9. QA / Confidence Agent        → multi-component score + guard rails + quarantine
    ↓
10. Export Agent                → 3MF with metadata
```

#### Технологический стек (рекомендованный)

**CV / Landmarks:**
- MediaPipe Face Landmarker (основной, быстрый, локальный).

**Reconstruction (Canonical):**
- FLAME (PyTorch версия) — основной parametric head model. Заменяет самодельный Base Mesh.

**Depth (опционально):**
- Depth Anything V2 (для Z-улучшения и perspective).

**Mesh Processing:**
- trimesh + Open3D (базовые операции).
- PyMeshLab (remesh, cleanup, repair).
- Blender Python (headless) — boolean operations (надёжнее Trimesh).

**Другое:**
- numpy, scipy (TPS/RBF как fallback).
- pydantic + jsonschema.
- trimesh / pyvista для валидации.

#### Структура папок проекта (финальная)

```
c:\3d_face_builder\
├── 00_governance\
│   ├── pipeline_config.json          # SSOT
│   ├── AGENTS.md                     # Контракты
│   └── schemas\                      # JSON schemas
├── 01_input_raster\
├── 02_processing\
│   ├── landmarks\
│   ├── depth_maps\                   # optional
│   └── preprocessed\
├── 03_artifacts\                     # JSON registry вместо KG
├── 04_passports\                     # JSON + Markdown summary
├── 05_output_mesh\
│   ├── staging\
│   └── quarantine\
├── 06_archive\
└── ops\
    ├── scripts\                      # один файл = один Agent
    ├── logs\
    └── tests\
```

#### pipeline_config.json (ключевые секции)

Включи:
- `reconstruction`: {"primary": "flame", "fallback": "mediapipe_tps", "enable_depth_fusion": false}
- `scale_hierarchy`: ["user", "reference", "ipd", "iris", "default"]
- `gates`: MIN_CONFIDENCE, MAX_BOUNDS, WATERTIGHT и т.д.
- `vrame_optimization`: flags для моделей.

#### Задачи для Claude (приоритет по порядку)

1. **Исследовать и предложить конкретные реализации** (с примерами кода/установки для RTX 2060):
   - FLAME integration (PyTorch) + fitting к MediaPipe landmarks.
   - Depth Anything V2 (лёгкий вариант).
   - Hybrid reconstruction pipeline.
   - PyMeshLab + Blender headless examples для repair/boolean.

2. **Написать**:
   - Полный `pipeline_config.json` с комментариями.
   - `AGENTS.md` с Input/Output/Responsibility для каждого агента.
   - Skeleton для первых 4 скриптов: `photo_quality.py`, `extract_landmarks.py`, `scale_estimation.py`, `flame_reconstruction.py`.

3. **Создать**:
   - Risk matrix и roadmap (MVP → Production).
   - Performance/VRAM estimates.
   - Тесты на edge-кейсах (плохое освещение, поворот головы, селфи-дисторсия).

4. **Рекомендации по Accessory Generator** (начать с маски: parametric offset + normal displacement + boolean difference от FLAME head).

**MVP Scope (первые 2-3 недели):**
- MediaPipe + Scale + простой FLAME fit + non-planar thickness + basic QA + Export.
- Одна accessory type (mask).

**Доставь результат поэтапно:** сначала config + AGENTS.md, потом код первых агентов.

---

Это ТЗ готово к копированию. Оно синтезирует всё лучшее, учитывает твои ограничения и даёт чёткий путь вперёд.

Хочешь, я сразу напишу `pipeline_config.json` здесь, или начинаем реализацию какого-то скрипта? Готов продолжить.

ГЕМИНИ
ФИНАЛЬНЫЙ ВЕРДИКТ
Логика конвейера
Успешно. Переход от парадигмы «MediaPipe → TPS → Mesh» к связке «MediaPipe + FLAME + Depth Anything V2» ликвидирует фундаментальный недостаток монокулярной реконструкции — статистически усредненную («плоскую») координату Z. Использование параметрической топологии FLAME, обученной на реальных 3D-сканах, гарантирует анатомическую корректность меша, предотвращая появление неестественных изломов геометрии.

Архитектура
Успешно. Исключение DensePose и Detectron2 снижает риски падения по памяти (OOM) на видеокарте RTX 2060 (8 ГБ VRAM) до нуля, освобождая ресурс под инференс моделей глубины. Замена булевого ядра Trimesh на детерминированный Blender Headless (Exact Engine) устраняет проблему негерметичных ребер (non-manifold) и вырожденных треугольников при вычитании геометрии лица из заготовки аксессуара. Иерархия масштабирования (Scale Hierarchy) обеспечивает производственную точность для 3D-печати.

Структура проекта
Успешно. Полная преемственность с базовым конвейером svg_builder. Отказ от тяжелого Knowledge Graph и Markdown-паспортов в пользу Pydantic-моделей и JSON Artifact Registry упрощает автоматизацию и ускоряет валидацию на локальном узле.

ТЕХНИЧЕСКОЕ ЗАДАНИЕ ДЛЯ CLAUDE (OPUS/SONNET) В CLOUD CODE
Резюме
Цель проекта: Разработка локального автоматизированного Python-конвейера c:\3d_face_builder для генерации непланарной (объемной) 3D-геометрии масок, очков и украшений под физическую 3D-печать (ограничение области сборки: 350×350×350 мм) по одной растровой фотографии.
Аппаратный стек: ПК, GPU RTX 2060 (8 ГБ VRAM), Python 3.11+, среда разработки — Cloud Code Desktop IDE.

Детализация
1. Архитектура 10-модульного конвейера (Агенты)
Photo Quality Agent (preflight_check.py): Входной фильтр. Оценка размытия (дисперсия Лапласиана), детекция перекрытия лица (волосы, посторонние предметы), расчет углов поворота головы (Yaw, Pitch, Roll). Порог отсечения: Confidence<0.85.

Preprocessing Agent (preflight_crop.py): Автокроп, нормализация экспозиции. Чтение EXIF метаданных. Применение инверсной радиальной дисторсии (Undistort) для компенсации искажений селфи-камер (~24-28 мм).

Landmark Agent (extract_landmarks.py): Инференс MediaPipe Face Landmarker в локальном режиме. Экстракция 478 плотных 3D-ориентиров (включая контуры радужной оболочки глаз). Сериализация в JSON.

Scale Agent (scale_estimation.py): Вычисление коэффициента px_to_mm. Строгая реализация иерархии:

User Manual Input→Reference Card Detection→Calculated IPD→Iris Diameter (11.7 mm)→Fallback
Face Reconstruction Agent (fit_flame.py): Подгонка (Fitting) параметров формы (β) и выражений (ψ) параметрической модели FLAME под извлеченные ориентиры MediaPipe с использованием оптимизатора scipy.optimize. Опциональное наложение карты относительной глубины из Depth Anything V2.

Accessory Generator Agent (generate_accessory.py): Загрузка 3D-шаблона изделия. Привязка геометрии к жестким топологическим индексам вершин (Vertex IDs) канонической сетки FLAME (переносица, скулы, контур глаз).

Mesh Processing Agent (apply_thickness.py): Расчет локальных векторов нормалей деформированного лица. Непланарное смещение вершин (Displacement) заготовки аксессуара наружу по формуле:

V 
new
​
 =V 
i
​
 +(N 
i
​
 ×thickness_mm)
Применение алгоритмов ремешинга и сглаживания (Laplacian Smoothing).

Boolean Agent (blender_boolean.py): Запуск Blender в headless-режиме (blender --background --python). Выполнение операции Boolean Difference (Exact Engine) между заготовкой аксессуара и деформированным мешем лица для формирования идеальной посадочной поверхности.

Mesh Repair Agent (pymeshlab_repair.py): Автоматическое закрытие отверстий, удаление изолированных вырожденных треугольников с нулевым объемом посредством PyMeshLab.

QA Agent (validate_3d_mesh.py): Финальный релиз-гейт. Проверка на герметичность (mesh.is_watertight), отсутствие самопересечений, валидация физических габаритов (≤350 мм). Вычисление многокомпонентного Confidence Score.

2. Структура папок проекта
Plaintext
c:\3d_face_builder\
├── 00_governance\
│   ├── pipeline_config.json        # Единый источник истины (SSOT)
│   ├── AGENTS.md                   # Протоколы и контракты обмена данными агентов
│   └── schemas\
│       ├── landmark_artifact_v1.schema.json
│       └── mesh_3d_artifact_v1.schema.json
├── 01_input_raster\                # Исходные изображения лиц (masks, glasses, jewelry)
├── 02_processing\
│   ├── landmarks\                  # Выходные JSON-координаты MediaPipe
│   └── undistorted\                # Растры с компенсированной дисторсией линз
├── 03_artifact_registry\           # MVP-реестр артефактов в формате JSON (вместо KG)
├── 04_passports\                   # Автоматические JSON-паспорта объектов (вместо MD)
├── 05_output_mesh\                 # Релизные меши миллиметрового диапазона (.3MF)
│   ├── staging\                    # Промежуточные заготовки булевых операций (Git-ignored)
│   └── quarantine\                 # Отбракованные негерметичные сетки или меши > 350 мм
├── 06_archive\                     # Архив успешно обработанных сессий
└── ops\
    ├── scripts\
    │   ├── preflight_crop.py
    │   ├── extract_landmarks.py
    │   ├── scale_estimation.py
    │   ├── fit_flame.py
    │   ├── generate_accessory.py
    │   ├── apply_thickness.py
    │   ├── blender_boolean.py
    │   ├── pymeshlab_repair.py
    │   └── validate_3d_mesh.py
    ├── logs\
    │   └── agent_trace.jsonl       # Пошаговый трейсинг времени и VRAM
    └── tests\
3. Конфигурация Единого Источника Истины (00_governance/pipeline_config.json)
JSON
{
  "config_version": "1.0",
  "spec_version": "1.0-3d-flame",
  "engine": {
    "cv_landmark_extractor": "mediapipe.face_mesh",
    "parametric_reconstructor": "flame_model_2020",
    "depth_enhancer": "depth_anything_v2_vits",
    "boolean_backend": "blender_headless_exact",
    "repair_backend": "pymeshlab"
  },
  "scale_calibration": {
    "strategy_hierarchy": [
      "user_override_mm",
      "reference_marker_id1_mm",
      "interpupillary_distance_mm",
      "iris_diameter_reference_mm"
    ],
    "default_ipd_mm": 63.5,
    "iris_diameter_reference_mm": 11.7
  },
  "lens_compensation": {
    "assume_focal_length_mm": 28.0,
    "auto_exif_extraction": true
  },
  "vram_management": {
    "max_allowed_vram_mb": 7168,
    "force_cpu_fallback_for_depth": false,
    "clear_cuda_cache_after_each_stage": true
  },
  "release_gates": {
    "min_photo_quality_score": 0.85,
    "min_total_confidence_score": 0.80,
    "mesh_validation": {
      "requires_watertight": true,
      "requires_winding_consistent": true,
      "allow_self_intersections": false,
      "min_wall_thickness_mm": 1.5,
      "max_physical_bounds_mm": [350.0, 350.0, 350.0]
    }
  }
}
Рекомендации по реализации в Cloud Code
Локальный вызов Blender Headless: Не импортируйте bpy напрямую в основной пайплайн Python (это требует сборки Blender как python-модуля, что усложняет переносимость). Используйте CLI-вызов через subprocess:

Python
subprocess.run(["blender", "--background", "--python", "ops/scripts/blender_boolean.py", "--", input_args], check=True)
Управление VRAM (RTX 2060 8GB): Для исключения OOM-ошибок при совместной работе MediaPipe и Depth Anything V2, инициализируйте очистку контекста CUDA после каждого этапа. Используйте легковесную версию модели глубины DepthAnythingV2-ViT-Small (размер файла ~90MB, потребление VRAM < 1.5 ГБ).

Изоляция параметрических генераторов: Модуль generate_accessory.py должен быть построен на системе плагинов. Каждый плагин жестко завязан на неизменяемые ID вершин маски FLAME.

Риски и их смягчение
Риск: Нарушение манифолдности при непланарном смещении. На участках с высокой кривизной (крылья носа) смещение по нормалям может вызвать самопересечение треугольников.

Смягчение: Внедрить в apply_thickness.py операцию проверки знака скалярного произведения нормалей соседних граней до и после смещения. При инверсии — применять локальное сглаживание Лапласа.

Риск: Отсутствие EXIF данных в растре.

Смягчение: При отсутствии EXIF скрипт автоматически откатывается на дефолтное фокусное расстояние в 28 мм (базовое фокусное расстояние камер современных смартфонов) и фиксирует штрафной коэффициент в confidence_score.

Альтернативы
Технологический узел	Выбранное решение (ТЗ)	Альтернатива для MVP	Причина выбора решения (ТЗ)
Базовый меш лица	Параметрическая модель FLAME	Самодельный средний Base Mesh	FLAME исключает анатомически невозможные деформации сетки.
Булево ядро	Blender Headless (Exact)	Trimesh Boolean (OpenCASCADE)	Blender гарантирует герметичность стыков без генерации дыр в сетке.
Паспорт объекта	Строгий JSON (Pydantic)	Markdown файлы	JSON обеспечивает мгновенную машиночитаемость без парсинга регулярными выражениями.
План запуска проекта (Implementation Roadmap)
Шаг 1: Развертывание структуры папок и инициализация 00_governance/pipeline_config.json.

Шаг 2: Написание скрипта ops/scripts/extract_landmarks.py (MediaPipe Face Mesh локально).

Шаг 3: Реализация математики подгонки FLAME под извлеченные ориентиры в ops/scripts/fit_flame.py.

Спецификация подготовлена. Задача полностью детерминирована. Начните генерацию кода со Шага 1 и Шага 2.