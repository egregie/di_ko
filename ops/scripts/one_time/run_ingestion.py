import os
import json
import subprocess
import sys

# Define facts metadata
facts = [
    {
        "fact_id": "fact_0017",
        "statement": "glycolic acid and salicylic acid combination improves mild to moderate acne",
        "entity_id": "glycolic_acid",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A019"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0018",
        "statement": "salicylic-mandelic acid peels are effective for active acne lesions and post-acne hyperpigmentation",
        "entity_id": "salicylic_acid",
        "confidence": 0.90,
        "evidence_level": "A",
        "sources": ["SRC-A020"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0019",
        "statement": "topical 30% salicylic acid peels reduce fine lines, hyperpigmentation, and skin roughness in photoaged skin",
        "entity_id": "salicylic_acid",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A021"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0020",
        "statement": "glycolic acid peels clinical application improves mild facial photoaging",
        "entity_id": "glycolic_acid",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A022"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0021",
        "statement": "topical l-ascorbic acid promotes collagen synthesis and protects against ultraviolet-induced photodamage",
        "entity_id": "vitamin_c",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A023"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0022",
        "statement": "topical 5% sodium ascorbyl phosphate lotion is effective for acne vulgaris management",
        "entity_id": "sodium_ascorbyl_phosphate",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A024"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0023",
        "statement": "topical combination of sodium ascorbyl phosphate and retinol shows synergistic efficacy in acne treatment",
        "entity_id": "sodium_ascorbyl_phosphate",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A025"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0024",
        "statement": "topical niacinamide enhances ceramide synthesis and improves skin barrier function",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A026"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0025",
        "statement": "topical niacinamide reduces inflammatory lesions and regulates sebum excretion in acne vulgaris",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A027"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0026",
        "statement": "niacinamide pre-treatment improves skin tolerability and reduces irritation from topical retinoids",
        "entity_id": "niacinamide",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A026"],
        "contradictions": [],
        "verified_by": "verifier",
        "date": "2026-06-07"
    },
    {
        "fact_id": "fact_0027",
        "statement": "concurrent application of retinoids and alpha-hydroxy acids (ahas) increases risk of localized skin irritation",
        "entity_id": "glycolic_acid",
        "confidence": 0.95,
        "evidence_level": "A",
        "sources": ["SRC-A019"],
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
    
    for f in facts:
        fact_id = f["fact_id"]
        candidate_path = os.path.join(candidates_dir, f"{fact_id}.json")
        with open(candidate_path, "w", encoding="utf-8") as out:
            json.dump(f, out, indent=2, ensure_ascii=False)
            
        print(f"Running verify_gate.py for {fact_id}...")
        # Run verify_gate.py
        proc = subprocess.run(
            [sys.executable, verify_gate_path, candidate_path],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Parse output
        stdout_str = proc.stdout.strip()
        stderr_str = proc.stderr.strip()
        
        try:
            res_obj = json.loads(stdout_str)
            results.append(res_obj)
            print(f"Result for {fact_id}: {res_obj}")
        except Exception as e:
            print(f"Error parsing verify_gate stdout for {fact_id}: {e}")
            print(f"stdout: {stdout_str}")
            print(f"stderr: {stderr_str}")
            sys.exit(1)
            
        if proc.returncode != 0 and res_obj.get("action") == "reject":
            print(f"Warning: {fact_id} was rejected! Returncode: {proc.returncode}")
            
    print("\nIngestion completed. Summary of actions:")
    for res in results:
        print(f"Fact ID: {res.get('fact_id')} - Verdict: {res.get('verdict')} - Action: {res.get('action')}")

if __name__ == "__main__":
    run()
