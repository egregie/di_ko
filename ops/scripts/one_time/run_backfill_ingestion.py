import os
import json
import subprocess
import sys

backfill_facts = [
    # Vitamin C (6 facts)
    {
        "fact_id": "fact_0028",
        "statement": "topical L-ascorbic acid formulation requires a pH of less than 3.5 to achieve percutaneous absorption",
        "entity_id": "vitamin_c",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A028"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0029",
        "statement": "maximal percutaneous absorption of topical L-ascorbic acid occurs at a concentration of 20%",
        "entity_id": "vitamin_c",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A028"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0030",
        "statement": "topical L-ascorbic acid increases mRNA levels of collagen types I and iii in human skin in vivo",
        "entity_id": "vitamin_c",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A029"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0031",
        "statement": "topical magnesium ascorbyl phosphate stimulates collagen synthesis in dermal fibroblasts",
        "entity_id": "magnesium_ascorbyl_phosphate",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A030"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0032",
        "statement": "topical ascorbyl glucoside exhibits collagen-stimulating properties in human dermal fibroblasts",
        "entity_id": "ascorbyl_glucoside",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A030"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0033",
        "statement": "topical vitamin C increases collagen synthesis in human skin across various age groups",
        "entity_id": "vitamin_c",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A031"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    # Niacinamide (6 facts)
    {
        "fact_id": "fact_0034",
        "statement": "topical niacinamide reduces hyperpigmentation by suppressing melanosome transfer from melanocytes to keratinocytes",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A032"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0035",
        "statement": "topical niacinamide 4% is effective in treating melasma with comparable efficacy to 4% hydroquinone but with fewer side effects",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A033"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0036",
        "statement": "topical niacinamide 2% and 5% concentrations significantly decrease cutaneous hyperpigmentation and increase skin lightness",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A032"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0037",
        "statement": "the inhibitory effect of niacinamide on melanosome transfer is reversible",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A034"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0038",
        "statement": "topical niacinamide improves stratum corneum barrier function and provides clinical benefits in subjects with rosacea",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A035"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0039",
        "statement": "topical niacinamide reduces transepidermal water loss and increases epidermal stratum corneum hydration",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A036"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    # Exfoliants (4 facts)
    {
        "fact_id": "fact_0040",
        "statement": "topical mandelic acid twice daily for four weeks increases lower eyelid skin elasticity and firmness",
        "entity_id": "mandelic_acid",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A037"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0041",
        "statement": "45% mandelic acid peels are equally effective as 30% salicylic acid peels for mild-to-moderate acne vulgaris with better safety profile",
        "entity_id": "mandelic_acid",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A038"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0042",
        "statement": "topical 12% L-lactic acid increases both epidermal and dermal thickness and skin firmness after three months",
        "entity_id": "lactic_acid",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A039"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0043",
        "statement": "topical 5% L-lactic acid improves skin smoothness and decreases fine lines but does not produce dermal changes",
        "entity_id": "lactic_acid",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A039"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    }
]

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    
    candidates_dir = os.path.join(project_root, "02_processing", "candidates")
    os.makedirs(candidates_dir, exist_ok=True)
    
    verify_gate_path = os.path.join(project_root, "ops", "scripts", "verify_gate.py")
    
    results = []
    
    for f in backfill_facts:
        fact_id = f["fact_id"]
        candidate_path = os.path.join(candidates_dir, f"{fact_id}.json")
        with open(candidate_path, "w", encoding="utf-8") as out:
            json.dump(f, out, indent=2, ensure_ascii=False)
            
        print(f"Running verify_gate.py for {fact_id}...")
        proc = subprocess.run(
            [sys.executable, verify_gate_path, candidate_path],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Parse output
        stdout_str = proc.stdout.strip()
        try:
            res_obj = json.loads(stdout_str)
            results.append(res_obj)
            print(f"Result for {fact_id}: {res_obj}")
        except Exception as e:
            print(f"Error parsing verify_gate stdout for {fact_id}: {e}")
            print(f"stdout: {stdout_str}")
            print(f"stderr: {proc.stderr.strip()}")
            sys.exit(1)
            
        if proc.returncode != 0:
            print(f"Warning: {fact_id} was rejected or errored. Action: {res_obj.get('action')}")
            
    # Compute rejection rates by topic
    topic_map = {
        "fact_0028": "vitamin_c",
        "fact_0029": "vitamin_c",
        "fact_0030": "vitamin_c",
        "fact_0031": "vitamin_c", # MAP belongs to Vitamin C
        "fact_0032": "vitamin_c", # Ascorbyl glucoside belongs to Vitamin C
        "fact_0033": "vitamin_c",
        "fact_0034": "niacinamide",
        "fact_0035": "niacinamide",
        "fact_0036": "niacinamide",
        "fact_0037": "niacinamide",
        "fact_0038": "niacinamide",
        "fact_0039": "niacinamide",
        "fact_0040": "exfoliants",
        "fact_0041": "exfoliants",
        "fact_0042": "exfoliants",
        "fact_0043": "exfoliants"
    }
    
    stats = {
        "vitamin_c": {"total": 0, "rejected": 0},
        "niacinamide": {"total": 0, "rejected": 0},
        "exfoliants": {"total": 0, "rejected": 0}
    }
    
    for r in results:
        fact_id = r["fact_id"]
        topic = topic_map.get(fact_id)
        if topic:
            stats[topic]["total"] += 1
            if r["action"] == "reject":
                stats[topic]["rejected"] += 1
                
    print("\nScale Backfill Ingestion Summary:")
    report_lines = [
        "# Scale Quality Report — Phase 4: Active Ingestion Audit",
        "",
        "## Per-Topic Rejection Rates",
        "| Topic | Total Processed | Rejected | Rejection Rate | Status |",
        "| --- | --- | --- | --- | --- |"
    ]
    
    for topic, s in stats.items():
        total = s["total"]
        rejected = s["rejected"]
        rate = (rejected / total) * 100.0 if total > 0 else 0.0
        status = "PASS" if rate <= 30.0 else "FAIL (HIGH REJECTION)"
        print(f"Topic: {topic} - Processed: {total} - Rejected: {rejected} - Rate: {rate:.1f}%")
        report_lines.append(f"| {topic} | {total} | {rejected} | {rate:.1f}% | {status} |")
        
    report_lines.extend([
        "",
        "## Ingested Backfill Facts Details",
        "| Fact ID | Statement | Verdict | Action |",
        "| --- | --- | --- | --- |"
    ])
    for r in results:
        # Find statement
        statement = next(f["statement"] for f in backfill_facts if f["fact_id"] == r["fact_id"])
        report_lines.append(f"| {r['fact_id']} | {statement} | {r['verdict']} | {r['action'].upper()} |")
        
    report_path = os.path.join(project_root, "ops", "logs", "scale_quality.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"\nScale quality report written to {report_path}")

if __name__ == "__main__":
    run()
