"""Phase 8.7b grade-fix audit (read-only by default).

Re-derives the defensible EBM grade for every active fact from its source
pub-type + abstract design (evidence.derive_grade, DEC-025) and prints a delta
table vs the currently stored evidence_level. With --apply it writes the
corrected (downgraded-only) grades back and stamps audit_flag. Never upgrades.
"""
import json, os, glob, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "..", "lib"))
import evidence  # noqa: E402

ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
RANK = {"A": 3, "B": 2, "C": 1, "D": 0}
APPLY = "--apply" in sys.argv

src = {s["source_id"]: s for s in json.load(open(os.path.join(ROOT, "03_knowledge_graph/sources.json"), encoding="utf-8"))["sources"]}

rows = []
for fp in sorted(glob.glob(os.path.join(ROOT, "03_knowledge_graph/facts/fact_*.json"))):
    f = json.load(open(fp, encoding="utf-8"))
    sid = (f.get("sources") or ["?"])[0]
    pmid = src.get(sid, {}).get("pmid", "")
    pt, ab = [], ""
    cf = os.path.join(ROOT, f"ops/cache/eutils/{pmid}.json")
    if pmid and os.path.exists(cf):
        c = json.load(open(cf, encoding="utf-8"))
        pt, ab = c.get("pubtype", []), c.get("abstract", "")
    cur = f.get("evidence_level", "?")
    new, signal = evidence.derive_grade(pt, ab)
    delta = ""
    if cur in RANK and RANK[new] < RANK[cur]:
        delta = f"DOWN {cur}->{new}"
    elif cur in RANK and RANK[new] > RANK[cur]:
        delta = f"(up {cur}->{new}, kept {cur})"  # never inflate
    rows.append({"fp": fp, "fid": f["fact_id"], "cur": cur, "new": new,
                 "delta": delta, "signal": signal, "pt": " / ".join(pt) or "(none)", "fact": f})

print(f"{'fact':11} {'cur':3} {'new':3} {'delta':14} {'signal':42} pubtype")
print("-" * 130)
downs = 0
for r in rows:
    if r["delta"].startswith("DOWN"):
        downs += 1
    mark = ">>" if r["delta"].startswith("DOWN") else "  "
    print(f"{mark}{r['fid']:9} {r['cur']:3} {r['new']:3} {r['delta']:14} {r['signal']:42} {r['pt'][:40]}")

from collections import Counter
cc, nc = Counter(r["cur"] for r in rows), Counter(r["new"] for r in rows)
print("-" * 130)
print(f"current grade dist: {dict(sorted(cc.items()))}")
print(f"derived grade dist: {dict(sorted(nc.items()))}")
print(f"DOWNGRADES (inflated facts): {downs} / {len(rows)}")

if APPLY:
    for r in rows:
        if r["delta"].startswith("DOWN"):
            f = r["fact"]
            f["evidence_level"] = r["new"]
            f["audit_flag"] = "grade_corrected"
            f["grade_audit"] = {"prev": r["cur"], "derived": r["new"], "signal": r["signal"], "by": "grade_audit.py (DEC-025)"}
            json.dump(f, open(r["fp"], "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nAPPLIED {downs} downgrades (audit_flag=grade_corrected).")
else:
    print("\n(read-only; re-run with --apply to write corrected grades)")
