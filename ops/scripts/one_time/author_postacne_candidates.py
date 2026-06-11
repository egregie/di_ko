"""Phase 8.7a: author postacne fact candidates + register their sources.

Idempotent. Statements are paraphrased from the live abstracts gathered by
collect_postacne_search.py (.tmp/postacne_search.md). The verify gate is the
sole arbiter of what enters the graph - this script only stages candidates.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CAND_DIR = os.path.join(ROOT, "02_processing", "verify", "candidates")
SOURCES = os.path.join(ROOT, "03_knowledge_graph", "sources.json")
os.makedirs(CAND_DIR, exist_ok=True)

# (fact_id, statement, entity_id, source_id, evidence_level, pmid, doi, title)
ROWS = [
    ("fact_0063",
     "15% azelaic acid gel effectively improved acne-induced post-inflammatory erythema and post-inflammatory hyperpigmentation with minimal adverse reactions",
     "azelaic_acid", "SRC-A054", "A", "38734843", "10.1007/s13555-024-01176-2",
     "Effects of 15% Azelaic Acid Gel in the Management of Post-Inflammatory Erythema and Post-Inflammatory Hyperpigmentation in Acne Vulgaris"),
    ("fact_0064",
     "Azelaic acid is more effective than vehicle for rosacea, acne and melasma",
     "azelaic_acid", "SRC-A055", "A", "37550898", "10.1111/jocd.15923",
     "A systematic review to evaluate the efficacy of azelaic acid in the management of acne, rosacea, melasma and skin aging"),
    ("fact_0065",
     "In a systematic review of topical treatments for post-inflammatory hyperpigmentation, retinoids and hydroxy acids were supported by the greatest number of high-quality studies, with broad-spectrum sunscreen recommended",
     "post_inflammatory_hyperpigmentation", "SRC-A056", "A", "34525885", "10.1080/09546634.2021.1981814",
     "Topical treatment for postinflammatory hyperpigmentation: a systematic review"),
    ("fact_0066",
     "Niacinamide is an effective skin lightening compound that works by inhibiting melanosome transfer from melanocytes to keratinocytes",
     "niacinamide", "SRC-A057", "A", "12100180", "10.1046/j.1365-2133.2002.04834.x",
     "The effect of niacinamide on reducing cutaneous pigmentation and suppression of melanosome transfer"),
    ("fact_0067",
     "A systematic review of randomized controlled trials found microneedling is an effective and well-tolerated treatment for atrophic acne scars with no serious adverse effects reported",
     "atrophic_acne_scars", "SRC-A058", "A", "33538106", "10.1111/iwj.13559",
     "Microneedling in the treatment of atrophic scars: A systematic review of randomised controlled trials"),
    ("fact_0068",
     "Combined microneedling and chemical peeling is superior to either treatment alone for atrophic acne scars, with favourable safety and patient-reported outcomes",
     "atrophic_acne_scars", "SRC-A059", "A", "41640476", "10.5114/ada.2025.154436",
     "Chemical peeling in combination with microneedling versus chemical peeling or microneedling monotherapy in the treatment of acne scars: a systematic review and meta-analysis"),
    ("fact_0069",
     "A systematic review found ablative fractional carbon dioxide laser is an effective therapy for atrophic acne scars, with treatment parameters customized per patient",
     "atrophic_acne_scars", "SRC-A060", "A", "29304516", "10.1055/s-0037-1606096",
     "Ablative Fractional CO2 Laser for Facial Atrophic Acne Scars"),
    ("fact_0070",
     "Meta-analysis found fractional picosecond laser achieves clinical improvement of atrophic acne scars similar to other fractional lasers but with lower risk of post-inflammatory hyperpigmentation and lower pain",
     "atrophic_acne_scars", "SRC-A061", "A", "37310182", "10.1111/jocd.15862",
     "Fractional picosecond laser for atrophic acne scars: A meta-analysis"),
    ("fact_0071",
     "Long-term treatment with adapalene 0.3 percent and benzoyl peroxide 2.5 percent gel reduces atrophic acne scar count, supporting early effective acne treatment to prevent and reduce scarring",
     "adapalene", "SRC-A062", "A", "31209851", "10.1007/s40257-019-00454-6",
     "Long-Term Effectiveness and Safety of Up to 48 Weeks Treatment with Topical Adapalene 0.3% Benzoyl Peroxide 2.5% Gel in the Prevention and Reduction of Atrophic Acne Scars"),
    ("fact_0072",
     "A 70% glycolic acid peel is an effective alternative to trichloroacetic acid peel for treating facial atrophic acne scars, especially for patients not tolerating TCA or requiring lesser downtime",
     "glycolic_acid", "SRC-A063", "B", "39483653", "10.25259/jcas_117_23",
     "A comparative study of 70% glycolic acid and 30% trichloroacetic acid peel in the treatment of facial atrophic acne scars: A split-face study"),
    ("fact_0073",
     "The chemical reconstruction of skin scars (CROSS) technique using trichloroacetic acid is well-tolerated and effective for treating ice pick atrophic acne scars",
     "atrophic_acne_scars", "SRC-A064", "B", "38722745", "10.1097/DSS.0000000000004228",
     "Comparing the Use of 80% Trichloroacetic Acid and 50% Trichloroacetic Acid for the Treatment of Ice Pick Acne Scars"),
    ("fact_0074",
     "Azelaic acid's inhibitory effect on melanocytes makes it widely used in the treatment of hyperpigmentation disorders such as melasma and post-inflammatory hyperpigmentation",
     "azelaic_acid", "SRC-A065", "B", "38282869", "10.5114/ada.2023.133955",
     "The multiple uses of azelaic acid in dermatology: mechanism of action, preparations, and potential therapeutic applications"),
]


def main():
    # 1) Write candidate facts
    for fid, stmt, ent, src, lvl, _pmid, _doi, _title in ROWS:
        fact = {
            "fact_id": fid,
            "statement": stmt,
            "entity_id": ent,
            "confidence": 0.9,
            "evidence_level": lvl,
            "sources": [src],
            "contradictions": [],
        }
        with open(os.path.join(CAND_DIR, f"{fid}.json"), "w", encoding="utf-8") as f:
            json.dump(fact, f, indent=2, ensure_ascii=False)

    # 2) Register sources (idempotent upsert by source_id)
    with open(SOURCES, "r", encoding="utf-8") as f:
        db = json.load(f)
    by_id = {s["source_id"]: s for s in db["sources"]}
    for _fid, _stmt, _ent, src, _lvl, pmid, doi, title in ROWS:
        by_id[src] = {
            "source_id": src,
            "name": title,
            "type": "journal",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "tier": "A",
            "pmid": pmid,
            "doi": doi,
            "accessed": "2026-06-11",
        }
    db["sources"] = list(by_id.values())
    with open(SOURCES, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print(json.dumps({"candidates": len(ROWS), "sources_total": len(db["sources"])}))


if __name__ == "__main__":
    main()
