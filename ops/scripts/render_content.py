"""
Phase 8.3 — render a FILLED deck (content + visual layer) to HTML, then compile_pdf.js -> PDF.

Consumes: deck_<id>_content.json (graph-traced text + author frames) + layouts_v2.json
(geometry) + deck_templates.json (class/theme) + design-tokens + logos + mini-SVGs.

Visual layer:
  - mini-SVGs as bullet/card icons (decorative; never carry a fact)
  - bg-molecule (svg_logo_bg) faint behind text-heavy slides only (C2 rule), under text
  - logo presence logic (C3): title=horizontal, section=mark, content=footer mark, closing=badge
  - grade chip on every factual block (A/B/C + honest level frame) — D2 grade-honesty

Usage: python render_content.py --deck deck_postacne_filled
"""
import os, json, re, argparse

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--deck", required=True); args = ap.parse_args()
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    ds = os.path.join(root, "04_design_system")
    C = json.load(open(os.path.join(ds, "design-tokens.json"), encoding="utf-8"))
    tokens = C; C = C["color"]; T = tokens["type"]; F = tokens["font"]; R = tokens["radius"]
    layouts = {l["layout_id"]: l for l in json.load(open(os.path.join(ds, "layouts_v2.json"), encoding="utf-8"))["layouts"]}
    templates = json.load(open(os.path.join(ds, "deck_templates.json"), encoding="utf-8"))
    content = json.load(open(os.path.join(ds, f"{args['deck'] if isinstance(args,dict) else args.deck}_content.json"), encoding="utf-8"))
    deck_id = content["deck_id"]
    tmpl = next(d for d in templates["decks"] if d["deck_id"] == content["template"])
    meta = {s["n"]: s for s in tmpl["slides"]}

    logo_dir = os.path.join(ds, "assets", "logo"); mini_dir = os.path.join(ds, "assets", "mini")
    def load_svg(path, fallback_color):
        try: s = open(path, encoding="utf-8").read().strip()
        except Exception: return ""
        s = re.sub(r'\s(width|height)="[^"]*"', '', s)
        if "preserveAspectRatio" not in s: s = s.replace("<svg ", '<svg preserveAspectRatio="xMidYMid meet" ', 1)
        s = re.sub(r'(<svg[^>]*?)\scolor="[^"]*"', rf'\1 color="{fallback_color}"', s, count=1)
        return s
    LOGO = {v: load_svg(os.path.join(logo_dir, f"ym_proskin_{v}.svg"), C["dark"]) for v in ("mark","horizontal","badge","bg")}
    MINI = {}
    for fn in os.listdir(mini_dir):
        if fn.endswith(".svg"):
            key = fn.replace("svg_postakne_", "").replace(".svg", "")  # mini_05
            MINI[key] = load_svg(os.path.join(mini_dir, fn), C["herbal"])

    W, H = 1280, 720
    PLATE_LAYOUTS = {"B1_split","B2_process","B3_anatomy","C1_comparison","C3_research_chart"}
    NO_BG = PLATE_LAYOUTS | {"D2_section", "D1_title", "D3_closing"}  # bg-molecule only on pure-text Authority/Evidence slides
    BG_OPACITY = 0.14   # readability prioritized over effect (TZ C2 GUARD); refs show faint art
    def esc(t): return (t or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

    GRADE_CLASS = {"A": "g-a", "B": "g-b", "C": "g-c"}
    def chip(node):
        g = node.get("grade"); lvl = node.get("grade_level", "")
        if not g: return ""
        return f'<span class="chip {GRADE_CLASS.get(g,"g-c")}">{g}</span><span class="chip-lvl">{esc(lvl)}</span>'
    def mini(key):
        return f'<span class="mini">{MINI.get(key,"")}</span>' if key else ""

    def render_inline(node):
        """frame/fact -> a paragraph-ish chunk (used inside list items / labels / standalone text)."""
        k = node["kind"]
        if k == "fact":
            lead = f'<b>{esc(node["lead"])}: </b>' if node.get("lead") else ""
            return f'{mini(node.get("icon"))}<span class="txt">{lead}{esc(node["text"])} {chip(node)}</span>'
        # frame / caption
        return f'{mini(node.get("icon"))}<span class="txt">{esc(node["text"])}</span>'

    def render_slot(sid, node, block_type):
        k = node["kind"]
        if k == "logo":
            return f'<div class="logo-slot">{LOGO.get(node["variant"],"")}</div>'
        if k == "plate":
            return f'<div class="ph-plate"><span class="ph-cap">{esc(node["purpose"])}</span></div>'
        if k == "list":
            lis = "".join(f'<li>{render_inline(it)}</li>' for it in node["items"])
            return f'<ul class="clist">{lis}</ul>'
        if k == "card":
            return (f'<div class="card"><div class="card-ico">{MINI.get(node["icon"],"")}</div>'
                    f'<div class="card-lbl">{esc(node["label"])}</div>'
                    f'<div class="card-body">{render_inline(node["body"])}</div></div>')
        # frame / fact / caption -> styled by block_type
        cls = {"display_h1":"t-display","h2":"t-h2","h3":"t-h3","caption":"t-cap"}.get(block_type, "t-body")
        return f'<div class="textblock {cls}">{render_inline(node)}</div>'

    slides_html = []
    for s in content["slides"]:
        n = s["n"]; m = meta[n]; lid = m["layout_id"]; klass = m["class"]; theme = m.get("theme","")
        L = layouts[lid]; bt = {sl["slot_id"]: sl["block_type"] for sl in L["slots"]}
        is_frame_slide = lid in ("D1_title","D2_section")
        bg = C["bgAlt"] if is_frame_slide else C["bg"]
        parts = []
        if lid not in NO_BG:
            parts.append(f'<div class="bg-mol" style="opacity:{BG_OPACITY}">{LOGO["bg"]}</div>')
        parts.append(f'<div class="rubric"><span class="rubric-class">{klass.upper()} · {esc(L["name"])}</span>'
                     f'<span class="rubric-theme">{esc(theme)}</span></div>')
        parts.append(f'<div class="corner-tag">#{n:02d} · {lid}</div>')
        for sl in L["slots"]:
            sid = sl["slot_id"]
            if sid == "rubric_label": continue
            b = sl["bounds"]; style = f'left:{b["x"]}px;top:{b["y"]}px;width:{b["w"]}px;height:{b["h"]}px;'
            node = s["slots"].get(sid)
            if node is None:
                # unfilled placeholder slot -> labeled plate (out-of-scope content this phase)
                if sl["kind"] == "placeholder" and sid != "rubric_label":
                    inner = f'<div class="ph-plate"><span class="ph-cap">{sl["block_type"]}</span></div>'
                    parts.append(f'<div class="slot" style="{style}">{inner}</div>')
                continue
            parts.append(f'<div class="slot" style="{style}">{render_slot(sid, node, bt.get(sid,"body"))}</div>')
        if L.get("footer_reserved"):
            parts.append(f'<div class="footer"><span class="f-mark">{LOGO["mark"]}</span>'
                         f'<span class="f-word">YM PROSKIN · только для специалистов</span>'
                         f'<span class="f-num">{n:02d} / {tmpl["slide_count"]:02d}</span></div>')
        slides_html.append(f'<section class="slide" style="background:{bg}">{"".join(parts)}</section>')

    html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>{esc(content['title'])}</title>
<style>
@font-face {{ font-family:'{F["family"]}'; font-style:normal; font-weight:100 900;
  src:url('../../04_design_system/fonts/Arimo[wght].ttf') format('truetype'); }}
:root{{ --bg:{C["bg"]};--bgAlt:{C["bgAlt"]};--sage:{C["sage"]};--herbal:{C["herbal"]};
  --dark:{C["dark"]};--text:{C["text"]};--border:{C["border"]};--warn:{C["warn"]}; }}
*{{box-sizing:border-box;}}
body{{margin:0;background:var(--dark);font-family:'{F["family"]}',sans-serif;color:var(--text);}}
.slide{{position:relative;width:{W}px;height:{H}px;overflow:hidden;margin:0 auto 18px;}}
@media print{{ .slide{{margin:0;page-break-after:always;}} }}
.bg-mol{{position:absolute;right:-120px;top:50%;transform:translateY(-50%);width:620px;height:620px;color:var(--sage);z-index:0;pointer-events:none;}}
.bg-mol svg{{width:100%;height:100%;}}
.slot{{position:absolute;z-index:2;}}
.rubric{{position:absolute;left:64px;top:30px;display:flex;flex-direction:column;gap:4px;max-width:900px;z-index:3;}}
.rubric-class{{font-size:{T["label"]}px;color:var(--herbal);text-transform:uppercase;letter-spacing:0.2em;font-weight:700;}}
.rubric-theme{{font-size:{T["bodySm"]}px;color:var(--dark);font-weight:700;}}
.corner-tag{{position:absolute;right:64px;top:34px;font-size:{T["caption"]}px;color:var(--herbal);letter-spacing:0.12em;opacity:0.75;z-index:3;}}
.textblock{{width:100%;height:100%;display:flex;flex-direction:column;justify-content:center;}}
.t-display{{font-size:{T["display"]}px;font-weight:700;color:var(--dark);line-height:1.1;}}
.t-h2{{font-size:{T["h2"]}px;font-weight:700;color:var(--dark);line-height:1.2;justify-content:flex-start;}}
.t-h3{{font-size:{T["h3"]}px;font-weight:700;color:var(--herbal);}}
.t-body{{font-size:{T["body"]}px;color:var(--text);line-height:1.5;justify-content:flex-start;}}
.t-cap{{font-size:{T["caption"]}px;color:var(--herbal);font-weight:500;}}
.txt{{display:inline;}}
.clist{{margin:0;padding:0;list-style:none;font-size:{T["bodySm"]}px;color:var(--text);line-height:1.45;}}
.clist li{{margin-bottom:10px;display:flex;gap:8px;align-items:flex-start;}}
.mini{{display:inline-flex;width:18px;height:18px;flex-shrink:0;color:var(--herbal);vertical-align:middle;margin-right:6px;}}
.mini svg{{width:100%;height:100%;}}
.card{{width:100%;height:100%;background:var(--bg);border:1px solid var(--border);border-radius:{R["card"]}px;padding:20px 22px;display:flex;flex-direction:column;gap:8px;}}
.card-ico{{width:40px;height:40px;border-radius:50%;background:var(--sage);color:var(--dark);display:flex;align-items:center;justify-content:center;}}
.card-ico svg{{width:24px;height:24px;}}
.card-lbl{{font-size:{T["h3"]}px;font-weight:700;color:var(--dark);}}
.card-body{{font-size:{T["bodySm"]}px;color:var(--text);line-height:1.45;}}
.chip{{display:inline-block;font-size:10px;font-weight:700;color:var(--bg);border-radius:10px;padding:1px 7px;margin-left:4px;vertical-align:middle;}}
.g-a{{background:var(--herbal);}} .g-b{{background:#8AA08C;}} .g-c{{background:#B9A78F;}}
.chip-lvl{{font-size:10px;color:var(--herbal);margin-left:4px;font-style:italic;}}
.ph-plate{{width:100%;height:100%;background:var(--sage);border:1px solid var(--border);border-radius:{R["card"]}px;display:flex;align-items:center;justify-content:center;text-align:center;padding:10px;}}
.ph-cap{{font-size:{T["bodySm"]}px;color:var(--dark);font-weight:700;letter-spacing:0.04em;text-transform:uppercase;word-break:break-word;}}
.logo-slot{{width:100%;height:100%;}} .logo-slot svg{{width:100%;height:100%;color:var(--dark);}}
.footer{{position:absolute;left:0;right:0;bottom:0;height:58px;display:flex;align-items:center;padding:0 48px;border-top:1px solid var(--sage);z-index:3;background:transparent;}}
.f-mark{{display:inline-flex;height:26px;width:26px;color:var(--herbal);flex-shrink:0;}} .f-mark svg{{height:100%;width:auto;}}
.f-word{{flex:1;margin-left:10px;font-size:{T["caption"]}px;font-weight:700;color:var(--text);text-transform:uppercase;letter-spacing:0.2em;}}
.f-num{{font-size:{T["caption"]}px;color:var(--herbal);font-weight:500;}}
</style></head><body>{"".join(slides_html)}</body></html>"""
    out = os.path.join(root, "06_render", "out", f"{deck_id}.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"wrote {out} ({len(content['slides'])} slides)")

if __name__ == "__main__":
    main()
