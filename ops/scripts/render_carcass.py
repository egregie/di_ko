"""
Phase 8.2 — render an EMPTY deck carcass to HTML (then compile_pdf.js -> PDF).

Reads layouts_v2.json (geometry) + deck_templates.json (sequence) + design-tokens
+ brand logos. Emits a structural skeleton for client approval:
  - placeholder slots  -> sage plate, caption "type · purpose"  (NOT literal [Placeholder])
  - text slots         -> outlined stub labeled by block_type, no real content
  - id_logo slots      -> real recolored brand SVG (horizontal / badge)
  - brand chrome footer -> mark + wordmark + slide number + hairline (footer_reserved layouts)
Zero Black: only design-token colors; client logos already recolored to currentColor.

Usage: python render_carcass.py --deck deck_template_retinoids
"""
import os, json, re, argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True, help="deck_id in deck_templates.json")
    args = ap.parse_args()

    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    ds = os.path.join(root, "04_design_system")
    tokens = json.load(open(os.path.join(ds, "design-tokens.json"), encoding="utf-8"))
    layouts_doc = json.load(open(os.path.join(ds, "layouts_v2.json"), encoding="utf-8"))
    templates = json.load(open(os.path.join(ds, "deck_templates.json"), encoding="utf-8"))
    C = tokens["color"]; T = tokens["type"]; F = tokens["font"]; R = tokens["radius"]

    W = layouts_doc["canvas"]["w"]; H = layouts_doc["canvas"]["h"]
    FB = layouts_doc["footer_band"]
    lay = {l["layout_id"]: l for l in layouts_doc["layouts"]}

    deck = next((d for d in templates["decks"] if d["deck_id"] == args.deck), None)
    if not deck:
        raise SystemExit(f"deck '{args.deck}' not found in deck_templates.json")

    logo_dir = os.path.join(ds, "assets", "logo")
    def load_logo(variant):
        path = os.path.join(logo_dir, f"ym_proskin_{variant}.svg")
        try:
            s = open(path, encoding="utf-8").read().strip()
        except Exception:
            return ""
        s = re.sub(r'\s(width|height)="[^"]*"', '', s)          # let CSS size it
        if "preserveAspectRatio" not in s:
            s = s.replace("<svg ", '<svg preserveAspectRatio="xMidYMid meet" ', 1)
        s = re.sub(r'(<svg[^>]*?)\scolor="[^"]*"', rf'\1 color="{C["dark"]}"', s, count=1)
        return s

    mark_svg = load_logo("mark")
    LOGO = {"horizontal": load_logo("horizontal"), "badge": load_logo("badge"), "mark": mark_svg}

    PH_PLATE = {"id_illustration", "id_graph", "id_img"}

    def esc(t): return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    slides_html = []
    for sl in deck["slides"]:
        L = lay.get(sl["layout_id"])
        if not L:
            raise SystemExit(f"layout '{sl['layout_id']}' (slide {sl['n']}) missing in layouts_v2.json")
        klass = L["class"]
        ph_map = sl.get("placeholders", {})
        is_frame = sl["layout_id"] in ("D1_title", "D2_section")   # bgAlt, no footer
        bg = C["bgAlt"] if is_frame else C["bg"]

        parts = []
        # top rubric: CLASS · layout name  +  slide theme
        parts.append(
            f'<div class="rubric"><span class="rubric-class">{klass.upper()} · {esc(L["name"])}</span>'
            f'<span class="rubric-theme">{esc(sl.get("theme",""))}</span></div>')
        # corner navigation tag
        parts.append(f'<div class="corner-tag">#{sl["n"]:02d} · {sl["layout_id"]}</div>')

        for s in L["slots"]:
            sid = s["slot_id"]; bt = s["block_type"]; b = s["bounds"]
            assign = ph_map.get(sid, {})
            eff_type = assign.get("type", bt)   # per-slide override (e.g. id_illustration->id_img)
            style = (f'left:{b["x"]}px;top:{b["y"]}px;width:{b["w"]}px;height:{b["h"]}px;')

            if sid == "rubric_label":
                continue  # represented by the top rubric band

            if eff_type == "id_logo":
                variant = assign.get("variant", "mark")
                svg = LOGO.get(variant, "")
                parts.append(f'<div class="slot logo-slot" style="{style}">{svg}</div>')
            elif eff_type in PH_PLATE:
                purpose = assign.get("purpose", "")
                cap = f'{eff_type}' + (f' · {esc(purpose)}' if purpose else '')
                parts.append(
                    f'<div class="slot ph-plate" style="{style}"><span class="ph-cap">{cap}</span></div>')
            else:
                # text stub: show block_type, no real content
                parts.append(
                    f'<div class="slot text-stub" style="{style}"><span class="stub-lbl">{bt}</span></div>')

        # brand chrome footer
        if L.get("footer_reserved"):
            parts.append(
                f'<div class="footer">'
                f'<span class="f-mark">{mark_svg}</span>'
                f'<span class="f-word">YM PROSKIN · только для специалистов</span>'
                f'<span class="f-num">{sl["n"]:02d} / {deck["slide_count"]:02d}</span>'
                f'</div>')

        slides_html.append(f'<section class="slide" style="background:{bg}">{"".join(parts)}</section>')

    html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<title>YM PROSKIN — carcass — {deck['deck_id']}</title>
<style>
@font-face {{ font-family:'{F["family"]}'; font-style:normal; font-weight:100 900;
  src:url('../../04_design_system/fonts/Arimo[wght].ttf') format('truetype'); }}
:root{{ --bg:{C["bg"]}; --bgAlt:{C["bgAlt"]}; --sage:{C["sage"]}; --herbal:{C["herbal"]};
  --dark:{C["dark"]}; --text:{C["text"]}; --border:{C["border"]}; }}
*{{box-sizing:border-box;}}
body{{margin:0;background:var(--dark);font-family:'{F["family"]}',sans-serif;color:var(--text);}}
.slide{{position:relative;width:{W}px;height:{H}px;overflow:hidden;margin:0 auto 18px;}}
@media print{{ .slide{{margin:0;page-break-after:always;}} }}
.slot{{position:absolute;}}
.text-stub{{border:1px dashed var(--herbal);border-radius:{R["btn"]}px;
  display:flex;align-items:center;justify-content:center;opacity:0.65;}}
.stub-lbl{{font-size:{T["caption"]}px;color:var(--herbal);text-transform:uppercase;
  letter-spacing:0.18em;font-weight:500;}}
.ph-plate{{background:var(--sage);border:1px solid var(--border);border-radius:{R["card"]}px;
  display:flex;align-items:center;justify-content:center;text-align:center;padding:10px;}}
.ph-cap{{font-size:{T["bodySm"]}px;color:var(--dark);font-weight:700;letter-spacing:0.04em;
  text-transform:uppercase;word-break:break-word;}}
.logo-slot svg{{width:100%;height:100%;color:var(--dark);}}
.rubric{{position:absolute;left:64px;top:32px;display:flex;flex-direction:column;gap:4px;max-width:880px;}}
.rubric-class{{font-size:{T["label"]}px;color:var(--herbal);text-transform:uppercase;
  letter-spacing:0.2em;font-weight:700;}}
.rubric-theme{{font-size:{T["bodySm"]}px;color:var(--dark);font-weight:500;}}
.corner-tag{{position:absolute;right:64px;top:34px;font-size:{T["caption"]}px;color:var(--herbal);
  letter-spacing:0.12em;font-weight:500;opacity:0.8;}}
.footer{{position:absolute;left:0;right:0;bottom:0;height:{FB["h"]}px;display:flex;align-items:center;
  padding:0 48px;border-top:1px solid var(--sage);}}
.f-mark{{display:inline-flex;height:26px;width:26px;color:var(--herbal);flex-shrink:0;}}
.f-mark svg{{height:100%;width:auto;color:var(--herbal);}}
.f-word{{flex:1;margin-left:10px;font-size:{T["caption"]}px;font-weight:700;color:var(--text);
  text-transform:uppercase;letter-spacing:0.2em;}}
.f-num{{font-size:{T["caption"]}px;color:var(--herbal);font-weight:500;}}
</style></head><body>{"".join(slides_html)}</body></html>"""

    out = os.path.join(root, "06_render", "templates", f"{deck['deck_id']}.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"wrote {out}  ({len(deck['slides'])} slides, {W}x{H})")

if __name__ == "__main__":
    main()
