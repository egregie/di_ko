import os
import json
import subprocess
import sys
import time

facts_to_audit = [f"fact_00{i}" for i in range(17, 28)]

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    
    verify_gate_path = os.path.join(project_root, "ops", "scripts", "verify_gate.py")
    facts_dir = os.path.join(project_root, "03_knowledge_graph", "facts")
    
    audit_results = []
    
    # We load sources.json to lookup pmid
    sources_path = os.path.join(project_root, "03_knowledge_graph", "sources.json")
    with open(sources_path, "r", encoding="utf-8") as sf:
        sources_db = json.load(sf)
    sources_map = {s["source_id"]: s for s in sources_db["sources"]}
    
    print("Starting live audit of 11 facts...")
    for fid in facts_to_audit:
        fact_path = os.path.join(facts_dir, f"{fid}.json")
        if not os.path.exists(fact_path):
            # If not in active, maybe it was already rejected/moved
            # Try to load from candidates or verify/rejected
            candidate_path = os.path.join(project_root, "02_processing", "candidates", f"{fid}.json")
            if os.path.exists(candidate_path):
                fact_path = candidate_path
            else:
                print(f"Fact file for {fid} not found.")
                continue
                
        # Load fact data to find source
        with open(fact_path, "r", encoding="utf-8") as f:
            fact_data = json.load(f)
            
        source_id = fact_data["sources"][0]
        src_entry = sources_map.get(source_id, {})
        pmid = src_entry.get("pmid", "")
        
        print(f"Auditing {fid} (PMID {pmid}) live...")
        # Run verify_gate.py with --force-live
        # Note: verify_gate.py will exit with code 1 if rejected, which is expected for failed facts.
        proc = subprocess.run(
            [sys.executable, verify_gate_path, fact_path, "--force-live"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Parse stdout JSON
        stdout_str = proc.stdout.strip()
        stderr_str = proc.stderr.strip()
        
        try:
            # The stdout of verify_gate.py contains a JSON string with result
            res_obj = json.loads(stdout_str)
            verdict = res_obj.get("verdict")
            ev_ok = res_obj.get("evidence_ok")
            action = res_obj.get("action")
        except Exception as e:
            print(f"Error parsing verify_gate output for {fid}: {e}")
            print(f"stdout: {stdout_str}")
            print(f"stderr: {stderr_str}")
            continue
            
        # Get live exists & title from cache (which was just overwritten/updated by --force-live)
        cache_file = os.path.join(project_root, "ops", "cache", "eutils", f"{pmid}.json")
        live_exists = False
        fetched_title = ""
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as cf:
                cache_data = json.load(cf)
                live_exists = cache_data.get("exists", False)
                fetched_title = cache_data.get("title", "")
                
        # Truncate title to <= 12 words
        title_words = fetched_title.split()
        if len(title_words) > 12:
            fetched_title_short = " ".join(title_words[:12]) + "..."
        else:
            fetched_title_short = fetched_title
            
        audit_results.append({
            "fact_id": fid,
            "source_id": source_id,
            "pmid": pmid,
            "live_exists": live_exists,
            "fetched_title": fetched_title_short,
            "verdict": verdict,
            "evidence_ok": ev_ok,
            "action": action
        })
        print(f"Done {fid}: Verdict={verdict}, Action={action}")
        
    # Write audit log ops/logs/gate_authenticity_batch1.md
    log_lines = [
        "# Gate Authenticity Audit Log — Batch 1",
        "",
        "This log documents the live verify-at-write gate audit for the 11 Phase 3 candidate facts.",
        "The checks were run with `--force-live` to bypass the local cache and query PubMed directly.",
        "",
        "## Live Verification Results",
        "",
        "| Fact ID | Source ID | PMID | Live Exists | Fetched Title (≤12 words) | Verdict | Evidence OK | Action |",
        "|---|---|---|---|---|---|---|---|",
    ]
    
    rejected_count = 0
    total_count = len(audit_results)
    
    for res in audit_results:
        log_lines.append(
            f"| {res['fact_id']} | {res['source_id']} | {res['pmid']} | {res['live_exists']} | "
            f"{res['fetched_title']} | {res['verdict']} | {res['evidence_ok']} | {res['action']} |"
        )
        if res['action'] == "reject":
            rejected_count += 1
            
    real_rejection_rate = (rejected_count / total_count) * 100 if total_count > 0 else 0.0
    
    log_lines.extend([
        "",
        "## Summary Metrics",
        "",
        f"- **Total Audited Candidate Facts**: {total_count}",
        f"- **Verified (Ingested) Facts**: {total_count - rejected_count}",
        f"- **Rejected Facts**: {rejected_count}",
        f"- **Real Rejection Rate**: {real_rejection_rate:.1f}%",
        "",
        "## Reconciliation Notes",
        "The following facts failed dynamic verification and have been quarantined:",
    ])
    
    for res in audit_results:
        if res['action'] == "reject":
            log_lines.append(f"- **{res['fact_id']}**: Rejected as `{res['verdict']}`. Cited PMID {res['pmid']} does not support the statement.")
            
    log_path = os.path.join(project_root, "ops", "logs", "gate_authenticity_batch1.md")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
        
    print(f"Live audit complete. Report written to {log_path}")
    print(f"Real Rejection Rate: {real_rejection_rate:.1f}%")

if __name__ == "__main__":
    run()
