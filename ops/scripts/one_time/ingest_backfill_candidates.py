import os
import json
import subprocess
import sys

candidates = [
    {
        "fact_id": "fact_0044",
        "statement": "topical L-ascorbic acid formulation requires a pH of less than 3.5 to achieve percutaneous absorption",
        "entity_id": "vitamin_c",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A028"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-08"
    },
    {
        "fact_id": "fact_0045",
        "statement": "maximal percutaneous absorption of topical L-ascorbic acid occurs at a concentration of 20%",
        "entity_id": "vitamin_c",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A028"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-08"
    },
    {
        "fact_id": "fact_0046",
        "statement": "topical L-ascorbic acid increases mRNA levels of collagen types I and iii in human skin in vivo",
        "entity_id": "vitamin_c",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A029"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-08"
    },
    {
        "fact_id": "fact_0047",
        "statement": "topical 5% niacinamide reduces fine lines, wrinkles, hyperpigmented spots, texture, red blotchiness, and yellowing in aging facial skin",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A040"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-08"
    },
    {
        "fact_id": "fact_0048",
        "statement": "topical alpha-hydroxy acids application to photoaged skin results in increased skin thickness, improved elastic fibers, and increased collagen density",
        "entity_id": "exfoliants",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A041"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-08"
    },
    {
        "fact_id": "fact_0049",
        "statement": "salicylic acid acts as a desmolytic agent by disrupting cellular junctions to exfoliate the stratum corneum and possesses comedolytic properties useful for acne",
        "entity_id": "exfoliants",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A042"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-08"
    },
    {
        "fact_id": "fact_0050",
        "statement": "topical 20% salicylic-10% mandelic acid combination peel is effective for the treatment of active acne and postacne hyperpigmentation in Asian skin",
        "entity_id": "exfoliants",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A043"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-08"
    }
]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    
    candidates_dir = os.path.join(project_root, "02_processing", "candidates")
    os.makedirs(candidates_dir, exist_ok=True)
    
    verify_gate_path = os.path.join(project_root, "ops", "scripts", "verify_gate.py")
    
    print("Ingesting and verifying backfill candidate facts live...")
    results = []
    
    for c in candidates:
        fact_id = c["fact_id"]
        temp_path = os.path.join(candidates_dir, f"temp_{fact_id}.json")
        with open(temp_path, "w", encoding="utf-8") as out:
            json.dump(c, out, indent=2, ensure_ascii=False)
            
        print(f"Running verify_gate on {fact_id} ({c['entity_id']})...")
        proc = subprocess.run(
            [sys.executable, verify_gate_path, temp_path, "--force-live"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Cleanup temp candidate
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        stdout_str = proc.stdout.strip()
        try:
            res = json.loads(stdout_str)
            print(f"  -> {res['action'].upper()} ({res['verdict']})")
            results.append(res)
        except Exception:
            print(f"  -> ERROR/FAIL (exit code {proc.returncode})")
            print(proc.stderr)
            results.append({
                "fact_id": fact_id,
                "verdict": "ERROR",
                "evidence_ok": False,
                "action": "reject"
            })
            
    # Print summary of results
    print("\nVerification Ingestion Summary:")
    passed_count = sum(1 for r in results if r["action"] == "write")
    rejected_count = sum(1 for r in results if r["action"] == "reject")
    print(f"Total processed: {len(candidates)}")
    print(f"Passed & written: {passed_count}")
    print(f"Rejected: {rejected_count}")

if __name__ == "__main__":
    main()
