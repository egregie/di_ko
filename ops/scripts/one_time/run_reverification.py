import os
import json
import subprocess
import sys
import glob

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    
    verify_gate_path = os.path.join(project_root, "ops", "scripts", "verify_gate.py")
    facts_dir = os.path.join(project_root, "03_knowledge_graph", "facts")
    cache_dir = os.path.join(project_root, "ops", "cache", "eutils")
    
    # Load sources to get PMID maps
    sources_path = os.path.join(project_root, "03_knowledge_graph", "sources.json")
    with open(sources_path, "r", encoding="utf-8") as sf:
        sources_db = json.load(sf)
    sources_map = {s["source_id"]: s for s in sources_db.get("sources", [])}
    
    # Get all fact files currently in facts directory
    fact_paths = glob.glob(os.path.join(facts_dir, "fact_*.json"))
    fact_paths.sort()
    
    reverify_results = []
    
    print(f"Starting live re-verification of {len(fact_paths)} active facts...")
    for idx, fpath in enumerate(fact_paths):
        fid = os.path.splitext(os.path.basename(fpath))[0]
        
        with open(fpath, "r", encoding="utf-8") as f:
            fact_data = json.load(f)
            
        topic = fact_data.get("entity_id", "")
        source_id = fact_data.get("sources", [""])[0]
        src_entry = sources_map.get(source_id, {})
        pmid = src_entry.get("pmid", "")
        doi = src_entry.get("doi", "")
        identifier = pmid or doi
        
        print(f"[{idx+1}/{len(fact_paths)}] Live auditing {fid} (Topic: {topic}, ID: {identifier})...")
        
        # Run verify_gate.py with --force-live
        proc = subprocess.run(
            [sys.executable, verify_gate_path, fpath, "--force-live"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout_str = proc.stdout.strip()
        stderr_str = proc.stderr.strip()
        
        verdict = "ERROR"
        evidence_ok = False
        action = "reject"
        
        try:
            res_obj = json.loads(stdout_str)
            verdict = res_obj.get("verdict")
            evidence_ok = res_obj.get("evidence_ok")
            action = res_obj.get("action")
        except Exception as e:
            print(f"Error parsing verify_gate output for {fid}: {e}")
            print(f"stdout: {stdout_str}")
            print(f"stderr: {stderr_str}")
            
        # Check cache file for fetched title & exists
        live_exists = False
        fetched_title = ""
        if identifier:
            if pmid:
                cfile = os.path.join(cache_dir, f"{pmid}.json")
            else:
                import re
                safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', doi)
                cfile = os.path.join(cache_dir, f"doi_{safe_name}.json")
                
            if os.path.exists(cfile):
                try:
                    with open(cfile, "r", encoding="utf-8") as cf:
                        cdata = json.load(cf)
                        live_exists = cdata.get("exists", False)
                        fetched_title = cdata.get("title", "")
                except Exception:
                    pass
                    
        # Truncate title to <= 12 words
        title_words = fetched_title.split()
        if len(title_words) > 12:
            fetched_title_short = " ".join(title_words[:12]) + "..."
        else:
            fetched_title_short = fetched_title
            
        reverify_results.append({
            "fact_id": fid,
            "topic": topic,
            "source_id": source_id,
            "identifier": identifier,
            "live_exists": live_exists,
            "fetched_title": fetched_title_short,
            "verdict": verdict,
            "evidence_ok": evidence_ok,
            "action": action
        })
        print(f"Done {fid}: Verdict={verdict}, Action={action}")

    # Separate backfill facts (fact_0028..fact_0043)
    backfill_results = [r for r in reverify_results if int(r["fact_id"].split("_")[1]) >= 28]
    
    # 1. Write ops/logs/backfill_reverify.md
    log_lines = [
        "# Backfill Re-Verification Log — Phase 4.1",
        "",
        "This log documents the live verify-at-write gate audit for the 16 backfill facts (fact_0028 to fact_0043).",
        "All checks were performed live with Google DNS-over-HTTPS resolution enabled.",
        "",
        "## Re-Verification Results (16 facts)",
        "",
        "| Fact ID | Topic | Source ID | PMID/DOI | Live Exists | Fetched Title (≤12 words) | Verdict | Evidence OK | Action |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    
    backfill_rejected = 0
    for res in backfill_results:
        log_lines.append(
            f"| {res['fact_id']} | {res['topic']} | {res['source_id']} | {res['identifier']} | {res['live_exists']} | "
            f"{res['fetched_title']} | {res['verdict']} | {res['evidence_ok']} | {res['action']} |"
        )
        if res['action'] == "reject":
            backfill_rejected += 1
            
    log_lines.extend([
        "",
        "## Summary Metrics",
        "",
        f"- **Total Audited Facts**: {len(backfill_results)}",
        f"- **Verified & Written Facts**: {len(backfill_results) - backfill_rejected}",
        f"- **Rejected Facts**: {backfill_rejected}",
        f"- **Rejection Rate**: {(backfill_rejected / len(backfill_results)) * 100:.1f}%",
        "",
        "## Quarantine Details",
    ])
    
    if backfill_rejected == 0:
        log_lines.append("No facts failed verification in this run.")
    else:
        for res in backfill_results:
            if res['action'] == "reject":
                log_lines.append(f"- **{res['fact_id']}**: Rejected as `{res['verdict']}`. PMID/DOI {res['identifier']} does not support the claim.")
                
    backfill_log_path = os.path.join(project_root, "ops", "logs", "backfill_reverify.md")
    with open(backfill_log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print(f"Re-verification log written to {backfill_log_path}")

    # 2. Write ops/logs/scale_quality.md (overall and per-topic rejection statistics)
    # Group by topic
    topics = ["vitamin_c", "niacinamide", "exfoliants"]
    topic_stats = {t: {"processed": 0, "rejected": 0} for t in topics}
    
    # We only count backfill facts in scale_quality.md (since they are Phase 4 additions)
    for res in backfill_results:
        t = res["topic"]
        if t in topic_stats:
            topic_stats[t]["processed"] += 1
            if res["action"] == "reject":
                topic_stats[t]["rejected"] += 1
                
    scale_lines = [
        "# Scale Quality Report — Phase 4.1: Active Ingestion Audit",
        "",
        "## Per-Topic Rejection Rates (Backfill Candidates)",
        "| Topic | Total Processed | Rejected | Rejection Rate | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    
    for t in topics:
        stats = topic_stats[t]
        proc = stats["processed"]
        rej = stats["rejected"]
        rate = (rej / proc) * 100 if proc > 0 else 0.0
        status = "PASS" if rate <= 30.0 else "FAIL"
        scale_lines.append(f"| {t} | {proc} | {rej} | {rate:.1f}% | {status} |")
        
    scale_lines.extend([
        "",
        "## Ingested Backfill Facts Details",
        "| Fact ID | Topic | Statement | Verdict | Action |",
        "| --- | --- | --- | --- | --- |",
    ])
    
    # Reload active facts to get statements
    active_facts_db = {}
    for fpath in glob.glob(os.path.join(facts_dir, "fact_*.json")):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                fdata = json.load(f)
                active_facts_db[fdata["fact_id"]] = fdata
        except Exception:
            pass
            
    for res in backfill_results:
        fid = res["fact_id"]
        # If successfully written, statement is in active facts, else we can lookup from candidates
        if res["action"] == "write" and fid in active_facts_db:
            stmt = active_facts_db[fid]["statement"]
        else:
            cpath = os.path.join(project_root, "02_processing", "candidates", f"{fid}.json")
            if os.path.exists(cpath):
                with open(cpath, "r", encoding="utf-8") as cf:
                    stmt = json.load(cf).get("statement", "")
            else:
                stmt = ""
        scale_lines.append(f"| {fid} | {res['topic']} | {stmt} | {res['verdict']} | {res['action'].upper()} |")
        
    scale_log_path = os.path.join(project_root, "ops", "logs", "scale_quality.md")
    with open(scale_log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(scale_lines) + "\n")
    print(f"Scale quality report written to {scale_log_path}")

if __name__ == "__main__":
    run()
