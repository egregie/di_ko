"""Phase 8.7b B2: prove the parametric diagram engine works for a PROCEDURE
schema (skin layers + procedure target depth), not just molecules/receptor
mechanisms. Uses the existing layered_anatomy template (deterministic geometry,
DEC-016/P020) and the same qa_svg_bounds check. No prompt-generation.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, ".."))
import gen_diagrams as gd  # module-level token load; main() not invoked

c = gd.colors

DATA = {
    "title": "ГЛУБИНА ВОЗДЕЙСТВИЯ ПРОЦЕДУР",
    "subtitle": "Постакне-рубцы: слои кожи и целевая глубина",
    "layers": [
        {"name": "Epidermis", "label": "Эпидермис", "y": 52, "height": 26, "fill": c["bgAlt"], "stroke": c["warn"], "opacity": 0.9},
        {"name": "Papillary Dermis", "label": "Сосочковая дерма", "y": 96, "height": 40, "fill": c["border"], "stroke": c["herbal"]},
        {"name": "Reticular Dermis", "label": "Сетчатая дерма", "y": 156, "height": 70, "fill": c["bg"], "stroke": c["herbal"]},
        {"name": "Subcutis", "label": "Гиподерма", "y": 246, "height": 14, "fill": c["herbal"], "stroke": c["moleculeStroke"]},
    ],
    "stages": [
        {"title": "Микронидлинг", "sub": "папиллярная дерма", "y": 108},
        {"title": "Фракц. Er:Glass", "sub": "средняя дерма", "y": 150},
        {"title": "Фракц. CO2", "sub": "вариабельная", "y": 188},
        {"title": "TCA CROSS", "sub": "сетчатая дерма", "y": 226},
    ],
    "source_note": "Анатомическая схема глубины (source-grounded SVG, маршрут P019/P020)",
}

out_dir = os.path.join(gd.PROJECT_ROOT, "04_design_system", "assets", "mechanisms")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "procedure_depth_skin_layers.svg")

svg = gd.make_layered_anatomy(
    DATA["title"], DATA["subtitle"], DATA["layers"], DATA["stages"], DATA["source_note"]
)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Generated {out_path}")

ok = gd.run_qa_check(out_path)
print("qa_svg_bounds:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
