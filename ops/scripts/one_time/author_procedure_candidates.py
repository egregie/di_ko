"""Phase 8.7b C2: stage PROCEDURE scarring candidates (discovery output).
Idempotent. Statements aligned to single contiguous abstract sentences (8.7a
grounding lesson). These are STAGED ONLY — the grounded judge (verify_gate) is
the sole arbiter and must be run when Gemini quota resets. Not written to graph.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CAND = os.path.join(ROOT, "02_processing", "verify", "candidates")
SOURCES = os.path.join(ROOT, "03_knowledge_graph", "sources.json")
os.makedirs(CAND, exist_ok=True)

# (fact_id, statement, entity_id, source_id, evidence_level, pmid, doi, title)
ROWS = [
    ("fact_0075",
     "Subcision is a surgical technique for managing atrophic acne scars.",
     "subcision", "SRC-A066", "B", "36943759", "10.1097/DSS.0000000000003706",
     "Surgical Subcision for Acne Scars: A Review of Instrumentation"),
    ("fact_0076",
     "Subcision is a safe and effective method for treating atrophic acne scars.",
     "subcision", "SRC-A067", "B", "36315903", "10.1111/jocd.15480",
     "Subcision in acne scarring: A review of clinical trials"),
    ("fact_0077",
     "Subcision is the most commonly used treatment technique for rolling atrophic acne scars.",
     "subcision", "SRC-A068", "B", "40296542", "10.1111/jocd.70219",
     "Subdermal Laser-Assisted Scar Subcision (SLASS) Combined With Fractional CO2 Laser for Acne Scars"),
    ("fact_0078",
     "Ablative fractional carbon dioxide laser is an effective therapy for the treatment of atrophic acne scars.",
     "fractional_laser", "SRC-A069", "A", "29304516", "10.1055/s-0037-1606096",
     "Ablative Fractional CO2 Laser for Facial Atrophic Acne Scars"),
    ("fact_0079",
     "Fractional radiofrequency produces a significantly lower incidence of post-inflammatory hyperpigmentation than laser treatment for atrophic acne scars.",
     "radiofrequency_microneedling", "SRC-A070", "A", "36062400", "10.1111/jocd.15348",
     "Meta-analysis of fractional radiofrequency treatment for acne and/or acne scars"),
]


def main():
    for fid, stmt, ent, src, lvl, _pmid, _doi, _title in ROWS:
        fact = {
            "fact_id": fid, "statement": stmt, "entity_id": ent,
            "confidence": 0.9, "evidence_level": lvl, "sources": [src],
            "contradictions": [],
        }
        with open(os.path.join(CAND, f"{fid}.json"), "w", encoding="utf-8") as f:
            json.dump(fact, f, indent=2, ensure_ascii=False)

    db = json.load(open(SOURCES, encoding="utf-8"))
    by_id = {s["source_id"]: s for s in db["sources"]}
    for _fid, _stmt, _ent, src, _lvl, pmid, doi, title in ROWS:
        by_id[src] = {
            "source_id": src, "name": title, "type": "journal",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "tier": "A", "pmid": pmid, "doi": doi, "accessed": "2026-06-11",
        }
    db["sources"] = list(by_id.values())
    json.dump(db, open(SOURCES, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(json.dumps({"staged_candidates": len(ROWS), "sources_total": len(db["sources"])}))


if __name__ == "__main__":
    main()
