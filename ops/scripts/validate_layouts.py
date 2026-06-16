"""
Phase 8.2 — validate_layouts.py
Gate for the Authority Layout System (layouts_v2.json + deck_templates.json + rendered carcasses).

FAIL if:
  - a slot lies outside the canvas
  - a placeholder slot has no routing type (route)
  - a deck template has <13 or >20 slots
  - a content slot enters the reserved footer band (footer_reserved layouts)
  - a text slot has no max_chars constraint
  - the rendered carcass HTML contains the literal "[Placeholder]" (old defect)
  - (integrity) a deck references a missing layout_id or a placeholder slot_id absent from its layout
  - (overlap) two slots in the same layout overlap
  - (zero-black) rendered HTML contains a forbidden #000000/#FFFFFF token
"""
import os, json, re, sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ds = os.path.join(root, "04_design_system")
out_dir = os.path.join(root, "06_render", "out")

errors = []

layouts_doc = json.load(open(os.path.join(ds, "layouts_v2.json"), encoding="utf-8"))
templates = json.load(open(os.path.join(ds, "deck_templates.json"), encoding="utf-8"))
W = layouts_doc["canvas"]["w"]; H = layouts_doc["canvas"]["h"]
FOOTER_Y = layouts_doc["footer_band"]["y"]
lay = {l["layout_id"]: l for l in layouts_doc["layouts"]}

def rects_overlap(a, b):
    return not (a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"]
                or a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"])

# ── per-layout slot checks ───────────────────────────────────────────────────
for lid, L in lay.items():
    slots = L["slots"]
    for s in slots:
        b = s["bounds"]; sid = s["slot_id"]
        if b["x"] < 0 or b["y"] < 0 or b["x"] + b["w"] > W or b["y"] + b["h"] > H:
            errors.append(f"[canvas] {lid}.{sid} out of canvas {b}")
        if s["kind"] == "placeholder" and not s.get("route"):
            errors.append(f"[routing] {lid}.{sid} placeholder has no route")
        if s["kind"] == "content" and "max_chars" not in s.get("constraints", {}):
            errors.append(f"[max_chars] {lid}.{sid} text slot has no max_chars")
        if L.get("footer_reserved") and b["y"] + b["h"] > FOOTER_Y:
            errors.append(f"[footer] {lid}.{sid} enters reserved footer band (y+h={b['y']+b['h']} > {FOOTER_Y})")
        # bounds/relative parity
        rb = s["relative_bounds"]
        for k, denom in (("x", W), ("y", H), ("w", W), ("h", H)):
            if abs(rb[k] - b[k] / denom) > 0.005:
                errors.append(f"[parity] {lid}.{sid} relative_bounds.{k}={rb[k]} != {b[k]}/{denom}")
    # overlap (pairwise within layout)
    for i in range(len(slots)):
        for j in range(i + 1, len(slots)):
            if rects_overlap(slots[i]["bounds"], slots[j]["bounds"]):
                errors.append(f"[overlap] {lid}: {slots[i]['slot_id']} overlaps {slots[j]['slot_id']}")

# ── deck template checks ─────────────────────────────────────────────────────
for d in templates["decks"]:
    n = len(d["slides"])
    if n < 13 or n > 20:
        errors.append(f"[scope] {d['deck_id']} has {n} slots (must be 13-20)")
    if n != d.get("slide_count"):
        errors.append(f"[count] {d['deck_id']} slide_count={d.get('slide_count')} != actual {n}")
    for sl in d["slides"]:
        lid = sl["layout_id"]
        if lid not in lay:
            errors.append(f"[ref] {d['deck_id']} slide {sl['n']} -> unknown layout '{lid}'")
            continue
        slot_ids = {s["slot_id"] for s in lay[lid]["slots"]}
        for psid in sl.get("placeholders", {}):
            if psid not in slot_ids:
                errors.append(f"[ref] {d['deck_id']} slide {sl['n']} assigns placeholder to '{psid}' absent in {lid}")

# ── rendered-carcass checks (if present) ─────────────────────────────────────
for d in templates["decks"]:
    html_path = os.path.join(out_dir, f"{d['deck_id']}.html")
    if os.path.exists(html_path):
        html = open(html_path, encoding="utf-8").read()
        if "[Placeholder]" in html:
            errors.append(f"[literal] {d['deck_id']}.html contains literal '[Placeholder]'")
        for tok in ("#000000", "#FFFFFF"):
            if tok.lower() in html.lower():
                errors.append(f"[zero-black] {d['deck_id']}.html contains forbidden {tok}")
    else:
        print(f"  note: {d['deck_id']}.html not rendered yet (skipping render checks)")

if errors:
    print("validate_layouts FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"validate_layouts passed: {len(lay)} layouts, {len(templates['decks'])} deck templates, "
      f"slots/canvas/footer/overlap/routing/max_chars/parity/refs/render OK.")
sys.exit(0)
