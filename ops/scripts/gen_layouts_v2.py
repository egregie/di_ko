"""
Phase 8.2 — generate 04_design_system/layouts_v2.json (Expert-Authority Layout System).

Geometry authored once as absolute bounds @1280x720; relative_bounds auto-computed
so bounds/relative parity is guaranteed (validate_layouts checks this).
Inherits the placeholder_contract.json routing model (Phase 8.0). No content here —
only composition + slot geometry for empty-carcass rendering.
"""
import os, json

W, H = 1280, 720
FOOTER_Y, FOOTER_H = 662, 58          # reserved brand-chrome band (~0.08H)
FOOTER_SAFE = FOOTER_Y - 8            # content slots on footer layouts must end by here (654)
LM = 64                               # left/right margin
CW = W - 2 * LM                       # content width = 1152

# max_chars per text block_type (brandbook §4.6 discipline: h1<=50, callout<=100)
MAXC = {
    "display_h1": 50, "h1": 50, "h2": 64, "h3": 40,
    "body": 240, "body_sm": 160, "caption": 90,
}
# placeholder routing (inherits placeholder_contract.json routing_rules)
ROUTE = {
    "id_logo": "logo_registry",
    "id_illustration": "diagram_engine",
    "id_graph": "diagram_engine",
    "id_img": "stage2_claude_design",
}

def slot(sid, block_type, x, y, w, h, min_size=None):
    is_ph = block_type.startswith("id_")
    s = {
        "slot_id": sid,
        "kind": "placeholder" if is_ph else "content",
        "block_type": block_type,
        "bounds": {"x": x, "y": y, "w": w, "h": h},
        "relative_bounds": {
            "x": round(x / W, 4), "y": round(y / H, 4),
            "w": round(w / W, 4), "h": round(h / H, 4),
        },
    }
    if is_ph:
        s["route"] = ROUTE[block_type]
        s["constraints"] = {"min_size": min_size if min_size is not None else 24}
    else:
        s["constraints"] = {"max_chars": MAXC[block_type]}
    return s

def rubric(): return slot("rubric_label", "caption", LM, 40, 480, 22)
def title(bt="h2"): return slot("title", bt, LM, 72, CW, 58)

# row of N equal cards in a band [y, y+h], gap g
def card_row(prefix, n, y, h, g=24, bt="body"):
    w = (CW - (n - 1) * g) // n
    out = []
    for i in range(n):
        out.append(slot(f"{prefix}_{i+1}", bt, LM + i * (w + g), y, w, h))
    return out

# N stacked horizontal bars in [y0, y1]
def stack(prefix, n, y0, y1, g=16, bt="body"):
    h = (y1 - y0 - (n - 1) * g) // n
    return [slot(f"{prefix}_{i+1}", bt, LM, y0 + i * (h + g), CW, h) for i in range(n)]

layouts = []

def L(layout_id, name, klass, footer_reserved, slots, lead=False):
    layouts.append({
        "layout_id": layout_id, "name": name, "class": klass,
        "canvas": {"w": W, "h": H},
        "footer_reserved": footer_reserved,
        # Authority/Knowledge/Evidence cells that assert a fact MUST trace to fact_id
        # OR be flagged an authorial frame (anti-fabrication, extends grade-honesty 8.7b).
        "cell_provenance_required": klass in ("authority", "evidence"),
        "slots": slots,
    })

# ── Class A — EXPERT AUTHORITY ──────────────────────────────────────────────
L("A1_classification", "Classification", "authority", True,
  [rubric(), title(), *card_row("category", 4, 168, FOOTER_SAFE - 168)])

# A2 Framework — REWORK (8.3): 2x2 parameter cards (icon+label+text), not a stack of identical bars.
def _quad():
    y0, y1, g = 168, FOOTER_SAFE, 22
    ch = (y1 - y0 - g) // 2
    cw = (CW - 24) // 2
    xs = [LM, LM + cw + 24]; ys = [y0, y0 + ch + g]
    out = []
    for r in range(2):
        for c in range(2):
            out.append(slot(f"param_{r*2+c+1}", "body", xs[c], ys[r], cw, ch))
    return out
L("A2_framework", "Framework (parameter grid)", "authority", True,
  [rubric(), title(), *_quad()])

# Decision Map: root node + 3 branch columns (no id_ placeholder per §3 deck tables)
L("A3_decision_map", "Decision Map", "authority", True,
  [rubric(), title(),
   slot("root", "body", LM + CW//2 - 220, 168, 440, 90),
   *card_row("branch", 3, 296, FOOTER_SAFE - 296)])

# Matrix: column-header row + 3 data rows (assets x properties)
L("A4_matrix", "Matrix (assets x properties)", "authority", True,
  [rubric(), title(),
   slot("col_header", "body_sm", LM, 168, CW, 56),
   *stack("row", 3, 236, FOOTER_SAFE)])

# ── Class B — KNOWLEDGE DELIVERY ────────────────────────────────────────────
L("B1_split", "Split (visual + text)", "knowledge", True,
  [rubric(), title(),
   slot("visual", "id_illustration", LM, 168, 552, FOOTER_SAFE - 168),
   slot("text", "body", LM + 552 + 32, 168, CW - 552 - 32, FOOTER_SAFE - 168)])

# Timeline/Process: track (id_graph) + 4 step text blocks
L("B2_process", "Timeline / Process", "knowledge", True,
  [rubric(), title(),
   slot("track", "id_graph", LM, 168, CW, 120),
   *card_row("step", 4, 312, FOOTER_SAFE - 312, bt="body_sm")])

# Anatomy: skin-layer illustration (left) + 3 stacked caption labels (right)
L("B3_anatomy", "Anatomy (layered)", "knowledge", True,
  [rubric(), title(),
   slot("anatomy", "id_illustration", LM, 168, 660, FOOTER_SAFE - 168),
   *[slot(f"label_{i+1}", "body_sm", LM + 660 + 32, 168 + i*150, CW - 660 - 32, 134) for i in range(3)]])

# ── Class C — EVIDENCE ──────────────────────────────────────────────────────
# Comparison: A-vs-B table (id_graph) + 2 column-header captions
# C1 Comparison — REWORK (8.3): smaller table plate + interpretation text + grade/source caption (not a full-width empty plate).
L("C1_comparison", "Comparison (A vs B)", "evidence", True,
  [rubric(), title(),
   slot("table", "id_graph", LM, 168, 700, FOOTER_SAFE - 168),
   slot("interp", "body", LM + 700 + 28, 168, CW - 700 - 28, 420),
   slot("grade_caption", "caption", LM + 700 + 28, 600, CW - 700 - 28, 40)])

# Evidence Summary: facts+grade chart (id_graph) + grade-legend caption
L("C2_evidence_summary", "Evidence Summary (+grade)", "evidence", True,
  [rubric(), title(),
   slot("facts", "id_graph", LM, 168, CW, FOOTER_SAFE - 168 - 32),
   slot("grade_legend", "caption", LM, FOOTER_SAFE - 26, CW, 24)])

# Research Chart: chart (id_graph) + source caption (max 1-2 per deck — GUARD doc-noted)
# C3 Research Chart — REWORK (8.3): chart plate + interpretation text + source caption (not a full-width empty plate).
L("C3_research_chart", "Research Chart", "evidence", True,
  [rubric(), title(),
   slot("chart", "id_graph", LM, 168, 680, FOOTER_SAFE - 168),
   slot("interp", "body", LM + 680 + 28, 168, CW - 680 - 28, 380),
   slot("source_caption", "caption", LM + 680 + 28, 560, CW - 680 - 28, 80)])

# ── Class D — TRUST / FRAME ─────────────────────────────────────────────────
# Title: horizontal lockup + display title + subtitle + cover illustration (no footer)
L("D1_title", "Title", "trust", False,
  [slot("logo", "id_logo", LM, 80, 384, 146, min_size=40),
   slot("deck_title", "display_h1", LM, 300, 672, 110),
   slot("subtitle", "body", LM, 420, 640, 44),
   slot("cover_art", "id_illustration", 760, 96, 456, 528)])

# Section divider: horizontal lockup + section number caption + display title (no footer)
L("D2_section", "Section divider", "trust", False,
  [slot("logo", "id_logo", LM, 120, 320, 122, min_size=40),
   slot("part_label", "caption", LM, 300, 480, 22),
   slot("section_title", "display_h1", LM, 336, CW, 110),
   slot("section_subtitle", "h3", LM, 460, 760, 40)])

# Closing: title + summary region + centered badge (footer present)
# D3 Closing — REWORK (8.3): real decision-map summary (3 stacked points) + badge kept (client: badge=Yes, empty body=No).
L("D3_closing", "Closing (decision summary + badge)", "trust", True,
  [rubric(), title(),
   slot("summary_1", "body", LM, 168, 720, 151),
   slot("summary_2", "body", LM, 335, 720, 151),
   slot("summary_3", "body", LM, 502, 720, 151),
   slot("badge", "id_logo", 832, 250, 360, 300, min_size=80)])

doc = {
    "library_version": "2.0",
    "phase": "8.2-authority-layouts",
    "canvas": {"w": W, "h": H, "aspect": "16:9"},
    "footer_band": {"y": FOOTER_Y, "h": FOOTER_H, "note": "reserved brand-chrome; no content slot may enter it on footer_reserved layouts"},
    "inherits": "00_governance/schemas/placeholder_contract.json (routing model, composite IDs, bounds+relative_bounds)",
    "routing_rules": {
        "id_logo": "logo_registry — fixed brand SVG (never generated)",
        "id_illustration": "diagram_engine — source-grounded from active graph (P019/P020)",
        "id_graph": "diagram_engine — data exclusively from verified facts (P018)",
        "id_img": "stage2_claude_design — generation/stock; asset_provenance entry required (P019)",
    },
    "anti_fabrication": {
        "rule": "Every Authority/Evidence cell making a factual assertion (number, effect, mechanism) MUST trace to a fact_id (P018) OR be explicitly flagged an authorial organizing frame (structure of thinking, not a proven fact).",
        "visible_distinction": "Factual cells carry a grade marker (A/B/C) or source caption; framing cells are neutral, no claim of proof.",
        "grade_honesty": "A framework may NOT turn a C-grade / self-reported item into an axiom-looking statement. Grade-honesty from Phase 8.7b extends to frameworks.",
        "enforced_by": "cell_provenance_required flag per layout (authority+evidence=true); content-fill phase (8.4-8.6) must satisfy it; not gated here (carcasses carry no content).",
    },
    "classes": {
        "authority": "lead slides — demonstrate the author's thinking (classification, framework, decision map, matrix)",
        "knowledge": "explain mechanics (split, process, anatomy)",
        "evidence": "support, do not lead (comparison, evidence summary, research chart)",
        "trust": "frame (title, section, closing); D4 before/after excluded by default (ethical risk)",
    },
    "layouts": layouts,
}

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                   "04_design_system", "layouts_v2.json")
out = os.path.abspath(out)
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)

# sanity report
print(f"wrote {out}")
print(f"layouts: {len(layouts)}")
for L_ in layouts:
    bad = []
    for s in L_["slots"]:
        b = s["bounds"]
        if b["x"] < 0 or b["y"] < 0 or b["x"]+b["w"] > W or b["y"]+b["h"] > H:
            bad.append((s["slot_id"], "out-of-canvas"))
        if L_["footer_reserved"] and b["y"]+b["h"] > FOOTER_Y:
            bad.append((s["slot_id"], "enters-footer"))
    flag = "OK" if not bad else f"!! {bad}"
    print(f"  {L_['layout_id']:22} {L_['class']:9} slots={len(L_['slots']):2} {flag}")
