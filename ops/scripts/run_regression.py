import os
import json
import subprocess
import shutil
import glob

def run_cmd(cmd, cwd):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = "c:/di_ko"
    
    sources_path = os.path.join(project_root, "03_knowledge_graph", "sources.json")
    sources_backup = os.path.join(project_root, "03_knowledge_graph", "sources.json.bak")
    
    # Backup sources.json
    shutil.copy2(sources_path, sources_backup)
    
    # Pre-populate eutils cache from source_check_phase1.json to avoid network calls
    source_check_path = os.path.join(project_root, "ops", "logs", "source_check_phase1.json")
    if os.path.exists(source_check_path):
        import re
        cache_dir = os.path.join(project_root, "ops", "cache", "eutils")
        os.makedirs(cache_dir, exist_ok=True)
        try:
            with open(source_check_path, "r", encoding="utf-8") as f:
                sources_check = json.load(f)
            for src in sources_check:
                if src.get("exists"):
                    pmid = src.get("pmid")
                    doi = src.get("doi")
                    cache_data = {
                        "exists": True,
                        "title": src.get("title", ""),
                        "pubtype": src.get("pubtype", []),
                        "abstract": src.get("abstract", "")
                    }
                    if pmid:
                        cf = os.path.join(cache_dir, f"{pmid}.json")
                        with open(cf, "w", encoding="utf-8") as fc:
                            json.dump(cache_data, fc, indent=2, ensure_ascii=False)
                    elif doi:
                        safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', doi)
                        cf = os.path.join(cache_dir, f"doi_{safe_name}.json")
                        with open(cf, "w", encoding="utf-8") as fc:
                            json.dump(cache_data, fc, indent=2, ensure_ascii=False)
            print("Successfully pre-populated eutils cache from source_check_phase1.json")
        except Exception as e:
            print("Warning: Failed to pre-populate cache:", e)

    log_lines = [
        "# Regression Test Log — Phase 2.5 (Collection Hardening)",
        "",
        "This log documents the automated verification results of the gatekeeper script `verify_gate.py`.",
        "",
    ]
    
    try:
        # Load sources to append test sources
        with open(sources_path, "r", encoding="utf-8") as f:
            sources_data = json.load(f)
            
        test_fake_source = {
            "source_id": "SRC-TEST-FAKE",
            "name": "Fake Source for Verification Testing",
            "type": "journal",
            "url": "https://pubmed.ncbi.nlm.nih.gov/99999999/",
            "tier": "A",
            "pmid": "99999999",
            "doi": "",
            "accessed": "2026-06-07"
        }
        test_irrelevant_source = {
            "source_id": "SRC-TEST-IRRELEVANT",
            "name": "Real Source but Irrelevant to Vitamin C",
            "type": "journal",
            "url": "https://pubmed.ncbi.nlm.nih.gov/15773538/",
            "tier": "A",
            "pmid": "15773538", # Kang 2005 (Mechanism of action of topical retinoids)
            "doi": "",
            "accessed": "2026-06-07"
        }
        
        sources_data["sources"].append(test_fake_source)
        sources_data["sources"].append(test_irrelevant_source)
        
        with open(sources_path, "w", encoding="utf-8") as f:
            json.dump(sources_data, f, indent=2, ensure_ascii=False)
            
        # CASE 1: 12 Clean Facts
        log_lines.append("## Case 1: Existing 12 Clean Facts")
        log_lines.append("All 12 clean facts in the active knowledge graph must pass the gate successfully.")
        log_lines.append("")
        log_lines.append("| Fact ID | Statement | Verdict | Evidence OK | Action | Status |")
        log_lines.append("|---|---|---|---|---|---|")
        
        facts_dir = os.path.join(project_root, "03_knowledge_graph", "facts")
        fact_files = sorted(glob_files(facts_dir, "fact_*.json"))
        
        all_clean_passed = True
        for ff in fact_files:
            code, stdout, stderr = run_cmd(["python", "ops/scripts/verify_gate.py", ff], project_root)
            fact_id = os.path.splitext(os.path.basename(ff))[0]
            
            try:
                out = json.loads(stdout)
                verdict = out.get("verdict")
                ev_ok = out.get("evidence_ok")
                action = out.get("action")
            except Exception:
                verdict = "parse_error"
                ev_ok = False
                action = "error"
                
            status_str = "PASS" if (code == 0 and action == "write") else "FAIL"
            if status_str == "FAIL":
                all_clean_passed = False
                
            # Load statement for logging
            with open(ff, "r", encoding="utf-8") as f:
                f_data = json.load(f)
            stmt = f_data.get("statement", "")
            stmt_short = stmt[:40] + "..." if len(stmt) > 40 else stmt
            
            log_lines.append(f"| {fact_id} | {stmt_short} | {verdict} | {ev_ok} | {action} | {status_str} |")
            
        log_lines.append("")
        log_lines.append(f"**Case 1 Result**: {'SUCCESS' if all_clean_passed else 'FAILURE'}")
        log_lines.append("")
        
        # CASE 2: Fake PMID
        log_lines.append("## Case 2: Fabricated PMID 99999999")
        log_lines.append("A candidate fact referencing a non-existent PMID must be automatically rejected with verdict `SOURCE_NOT_FOUND`.")
        log_lines.append("")
        
        fake_fact_path = os.path.join(script_dir, "fact_fake_pmid.json")
        fake_fact_data = {
            "fact_id": "fact_fake_pmid",
            "statement": "Retinoids regulate gene transcription by binding to RAR and RXR nuclear receptors.",
            "entity_id": "retinoids",
            "confidence": 0.95,
            "evidence_level": "A",
            "sources": ["SRC-TEST-FAKE"],
            "contradictions": [],
            "verified_by": "verifier",
            "date": "2026-06-07"
        }
        with open(fake_fact_path, "w", encoding="utf-8") as f:
            json.dump(fake_fact_data, f, indent=2)
            
        code, stdout, stderr = run_cmd(["python", "ops/scripts/verify_gate.py", fake_fact_path], project_root)
        try:
            out = json.loads(stdout)
            verdict = out.get("verdict")
            action = out.get("action")
        except Exception:
            verdict = "parse_error"
            action = "error"
            
        rejected_file_exists = os.path.exists(os.path.join(project_root, "02_processing", "verify", "rejected", "fact_fake_pmid.json"))
        status_str = "PASS" if (code != 0 and verdict == "SOURCE_NOT_FOUND" and action == "reject" and rejected_file_exists) else "FAIL"
        
        log_lines.append(f"- Candidate Fact ID: `fact_fake_pmid`")
        log_lines.append(f"- Exit Code: `{code}` (Expected: non-zero)")
        log_lines.append(f"- Output Verdict: `{verdict}` (Expected: `SOURCE_NOT_FOUND`)")
        log_lines.append(f"- Routing Action: `{action}` (Expected: `reject`)")
        log_lines.append(f"- In Rejected Folder: `{rejected_file_exists}` (Expected: `True`)")
        log_lines.append(f"- **Status**: {status_str}")
        log_lines.append("")
        
        # CASE 3: Irrelevant PMID
        log_lines.append("## Case 3: Real PMID but Irrelevant Claim")
        log_lines.append("A candidate fact with a real PMID but unrelated statement must be automatically rejected with verdict `UNSUPPORTED`.")
        log_lines.append("")
        
        irrelevant_fact_path = os.path.join(script_dir, "fact_irrelevant.json")
        irrelevant_fact_data = {
            "fact_id": "fact_irrelevant",
            "statement": "Vitamin C is a water-soluble antioxidant that brightens skin and stimulates collagen production.",
            "entity_id": "vitamin_c",
            "confidence": 0.95,
            "evidence_level": "A",
            "sources": ["SRC-TEST-IRRELEVANT"],
            "contradictions": [],
            "verified_by": "verifier",
            "date": "2026-06-07"
        }
        with open(irrelevant_fact_path, "w", encoding="utf-8") as f:
            json.dump(irrelevant_fact_data, f, indent=2)
            
        code, stdout, stderr = run_cmd(["python", "ops/scripts/verify_gate.py", irrelevant_fact_path], project_root)
        try:
            out = json.loads(stdout)
            verdict = out.get("verdict")
            action = out.get("action")
        except Exception:
            verdict = "parse_error"
            action = "error"
            
        rejected_file_exists = os.path.exists(os.path.join(project_root, "02_processing", "verify", "rejected", "fact_irrelevant.json"))
        status_str = "PASS" if (code != 0 and verdict == "UNSUPPORTED" and action == "reject" and rejected_file_exists) else "FAIL"
        
        log_lines.append(f"- Candidate Fact ID: `fact_irrelevant`")
        log_lines.append(f"- Exit Code: `{code}` (Expected: non-zero)")
        log_lines.append(f"- Output Verdict: `{verdict}` (Expected: `UNSUPPORTED`)")
        log_lines.append(f"- Routing Action: `{action}` (Expected: `reject`)")
        log_lines.append(f"- In Rejected Folder: `{rejected_file_exists}` (Expected: `True`)")
        log_lines.append(f"- **Status**: {status_str}")
        log_lines.append("")
        
        # CASE 4: Marginally Weak Claim (overlap < 15%)
        log_lines.append("## Case 4: Marginally Weak Claim")
        log_lines.append("A candidate fact with a real PMID but weak claim alignment (overlap < 15%) must be automatically rejected under the pre-filter gate.")
        log_lines.append("")
        
        weak_fact_path = os.path.join(script_dir, "fact_weak_mismatch.json")
        weak_fact_data = {
            "fact_id": "fact_weak_mismatch",
            "statement": "topical niacinamide regulates gene transcription and binds directly to receptors",
            "entity_id": "niacinamide",
            "confidence": 0.95,
            "evidence_level": "A",
            "sources": ["SRC-A026"],
            "contradictions": [],
            "verified_by": "verifier",
            "date": "2026-06-07"
        }
        with open(weak_fact_path, "w", encoding="utf-8") as f:
            json.dump(weak_fact_data, f, indent=2)
            
        code, stdout, stderr = run_cmd(["python", "ops/scripts/verify_gate.py", weak_fact_path], project_root)
        try:
            out = json.loads(stdout)
            verdict = out.get("verdict")
            action = out.get("action")
        except Exception:
            verdict = "parse_error"
            action = "error"
            
        rejected_file_exists = os.path.exists(os.path.join(project_root, "02_processing", "verify", "rejected", "fact_weak_mismatch.json"))
        status_str = "PASS" if (code != 0 and verdict == "UNSUPPORTED" and action == "reject" and rejected_file_exists) else "FAIL"
        
        log_lines.append(f"- Candidate Fact ID: `fact_weak_mismatch`")
        log_lines.append(f"- Exit Code: `{code}` (Expected: non-zero)")
        log_lines.append(f"- Output Verdict: `{verdict}` (Expected: `UNSUPPORTED`)")
        log_lines.append(f"- Routing Action: `{action}` (Expected: `reject`)")
        log_lines.append(f"- In Rejected Folder: `{rejected_file_exists}` (Expected: `True`)")
        log_lines.append(f"- **Status**: {status_str}")
        log_lines.append("")
        
    finally:
        # Restore sources.json
        if os.path.exists(sources_backup):
            shutil.copy2(sources_backup, sources_path)
            os.remove(sources_backup)
            
        # Clean up test files in scratch
        for f_name in ["fact_fake_pmid.json", "fact_irrelevant.json", "fact_weak_mismatch.json"]:
            p = os.path.join(script_dir, f_name)
            if os.path.exists(p):
                os.remove(p)
                
        # Clean up rejected files as requested by TZ (Case 2: "Затем удалить тестовый факт из rejected")
        rejected_fake = os.path.join(project_root, "02_processing", "verify", "rejected", "fact_fake_pmid.json")
        if os.path.exists(rejected_fake):
            os.remove(rejected_fake)
            
        rejected_irrelevant = os.path.join(project_root, "02_processing", "verify", "rejected", "fact_irrelevant.json")
        if os.path.exists(rejected_irrelevant):
            os.remove(rejected_irrelevant)
            
        rejected_weak = os.path.join(project_root, "02_processing", "verify", "rejected", "fact_weak_mismatch.json")
        if os.path.exists(rejected_weak):
            os.remove(rejected_weak)
            
    # Write output log
    out_log_path = os.path.join(project_root, "ops", "logs", "hardening_regression.md")
    os.makedirs(os.path.dirname(out_log_path), exist_ok=True)
    with open(out_log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print(f"Regression log written to {out_log_path}")

def glob_files(directory, pattern):
    return glob.glob(os.path.join(directory, pattern))

if __name__ == "__main__":
    main()
