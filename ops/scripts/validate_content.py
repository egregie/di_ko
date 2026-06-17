"""
Phase 8.3 — validate_content.py: anti-fabrication + content-integrity gate for filled decks.

FAIL if (per TZ Block F):
  - a factual block has no fact_id or no grade
  - fact_id is quarantined or absent from the graph
  - the grade recorded for a block != the fact's actual grade in the graph (grade fabrication)
  - a C-grade fact block carries no grade_level frame (grade-honesty)
  - text exceeds the slot's max_chars (overflow)
  - rendered content HTML contains literal "[Placeholder]"
  - rendered content HTML contains forbidden #000000 / #FFFFFF (Zero Black)
Note: bg-logo-over-text contrast is verified visually (screenshots) — see walkthrough.
"""
import os, json, glob, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DS = os.path.join(ROOT, "04_design_system")
CONTENT_DIR = os.path.join(ROOT, "06_render", "content")

FACTS = {}
for fp in glob.glob(os.path.join(ROOT, "03_knowledge_graph", "facts", "*.json")):
    d = json.load(open(fp, encoding="utf-8")); FACTS[d["fact_id"]] = d.get("evidence_level")
REJECTED = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ROOT, "02_processing", "verify", "rejected", "*.json"))}
layouts = {l["layout_id"]: l for l in json.load(open(os.path.join(DS, "layouts_v2.json"), encoding="utf-8"))["layouts"]}
templates = {d["deck_id"]: d for d in json.load(open(os.path.join(DS, "deck_templates.json"), encoding="utf-8"))["decks"]}

LIST_ITEM_MAX = 220
CARD_LABEL_MAX = 48
CARD_BODY_MAX = 210

errors = []

def texts_of(node):
    """yield (text, max_override) pieces for overflow checking."""
    k = node.get("kind")
    if k in ("frame", "fact", "caption"):
        yield node.get("text", ""), None
    elif k == "list":
        for it in node["items"]:
            for t, _ in texts_of(it): yield t, LIST_ITEM_MAX
    elif k == "card":
        yield node.get("label", ""), CARD_LABEL_MAX
        for t, _ in texts_of(node["body"]): yield t, CARD_BODY_MAX

for deck_id in ("deck_postacne_filled", "deck_retinoids_filled"):
    content = json.load(open(os.path.join(DS, f"{deck_id}_content.json"), encoding="utf-8"))
    prov = json.load(open(os.path.join(DS, f"{deck_id}_provenance.json"), encoding="utf-8"))
    tmpl = templates[content["template"]]
    layout_by_n = {s["n"]: s["layout_id"] for s in tmpl["slides"]}

    # 1-4. provenance factual-block checks
    for b in prov["blocks"]:
        if b["block"] != "fact":
            continue
        loc = f"{deck_id} s{b['slide']}/{b['slot']}"
        fid = b.get("fact_id")
        if not fid:                              errors.append(f"[no-fact_id] {loc}"); continue
        if not b.get("grade"):                   errors.append(f"[no-grade] {loc} {fid}")
        if b.get("quarantined"):                 errors.append(f"[quarantined] {loc} {fid}")
        if fid not in FACTS:                     errors.append(f"[missing-fact] {loc} {fid}"); continue
        if b.get("grade") != FACTS[fid]:         errors.append(f"[grade-mismatch] {loc} {fid}: block={b.get('grade')} graph={FACTS[fid]}")

    # content node checks: C-grade frame + overflow
    for s in content["slides"]:
        lid = layout_by_n[s["n"]]
        maxc = {sl["slot_id"]: sl.get("constraints", {}).get("max_chars") for sl in layouts[lid]["slots"]}
        for sid, node in s["slots"].items():
            # C-grade frame: any fact node must carry grade_level
            def check_frame(nd):
                if nd.get("kind") == "fact" and not nd.get("grade_level"):
                    errors.append(f"[no-grade-frame] {deck_id} s{s['n']}/{sid} {nd.get('fact_id')}")
                if nd.get("kind") == "list":
                    for it in nd["items"]: check_frame(it)
                if nd.get("kind") == "card":
                    check_frame(nd["body"])
            check_frame(node)
            # overflow
            slot_max = maxc.get(sid)
            for txt, override in texts_of(node):
                lim = override or slot_max
                if lim and len(txt) > lim:
                    errors.append(f"[overflow] {deck_id} s{s['n']}/{sid}: {len(txt)}>{lim} :: {txt[:40]}…")

    # 5-6. rendered HTML
    html_path = os.path.join(CONTENT_DIR, f"{deck_id}.html")
    if os.path.exists(html_path):
        html = open(html_path, encoding="utf-8").read()
        if "[Placeholder]" in html: errors.append(f"[literal] {deck_id}.html contains '[Placeholder]'")
        for tok in ("#000000", "#FFFFFF"):
            if tok.lower() in html.lower(): errors.append(f"[zero-black] {deck_id}.html has {tok}")
    else:
        errors.append(f"[no-render] {deck_id}.html not found in 06_render/content/")

if errors:
    print("validate_content FAILED:")
    for e in errors: print("  -", e)
    sys.exit(1)
print("validate_content passed: 2 decks; factual blocks traced to fact_id+grade (==graph), "
      "no quarantined refs, C-grade framed, no overflow, no literal [Placeholder], Zero-Black OK.")
sys.exit(0)
