import sys
import os
import json
import datetime
import argparse

# Configure python path to find the lib module
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(SCRIPT_DIR, "lib")
sys.path.append(LIB_DIR)

import evidence

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def truncate_title(title, max_words=15):
    if not title:
        return ""
    # Remove newlines and multiple spaces
    title_clean = " ".join(title.split())
    words = title_clean.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return title_clean

def main():
    parser = argparse.ArgumentParser(description="Verify Fact Gate")
    parser.add_argument("candidate_path", type=str, help="Path to candidate fact JSON")
    parser.add_argument("--force-live", "--no-cache", action="store_true", help="Ignore cache and fetch live")
    args = parser.parse_args()
    
    candidate_path = args.candidate_path
    force_live = args.force_live
    
    if not os.path.exists(candidate_path):
        print(f"Error: Candidate file {candidate_path} not found.")
        sys.exit(2)
        
    project_root = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
    sources_path = os.path.join(project_root, "03_knowledge_graph", "sources.json")
    
    # Load candidate fact
    try:
        fact = load_json(candidate_path)
    except Exception as e:
        print(f"Error parsing candidate JSON: {e}")
        sys.exit(2)
        
    fact_id = fact.get("fact_id", "unknown_fact")
    statement = fact.get("statement", "")
    evidence_level = fact.get("evidence_level", "D")
    fact_sources = fact.get("sources", [])
    
    # Load sources registry
    if not os.path.exists(sources_path):
        print(f"Error: sources.json not found at {sources_path}")
        sys.exit(2)
        
    try:
        sources_db = load_json(sources_path)
    except Exception as e:
        print(f"Error parsing sources.json: {e}")
        sys.exit(2)
        
    # Map source_id to source details
    sources_map = {src["source_id"]: src for src in sources_db.get("sources", [])}
    
    # Check sources
    source_results = []
    
    for src_id in fact_sources:
        src_entry = sources_map.get(src_id)
        if not src_entry:
            # Source not found in sources.json
            continue
            
        pmid = src_entry.get("pmid", "")
        doi = src_entry.get("doi", "")
        
        # We need a valid identifier (pmid or doi)
        identifier = pmid or doi
        if not identifier:
            # Source exists in sources.json but has no PMID/DOI
            # Treat as needs manual validation
            source_results.append({
                "source_id": src_id,
                "exists": True,
                "title": src_entry.get("name", ""),
                "pubtype": [src_entry.get("type", "")],
                "abstract": "",
                "verdict": "NEEDS_MANUAL",
                "evidence_ok": False
            })
            continue
            
        # Call evidence library
        check_res = evidence.check_source(identifier, force_live=force_live)
        if not check_res.get("exists"):
            source_results.append({
                "source_id": src_id,
                "exists": False,
                "title": "",
                "pubtype": [],
                "abstract": "",
                "verdict": "SOURCE_NOT_FOUND",
                "evidence_ok": False
            })
            continue
            
        # Assess claim and evidence type
        abstract = check_res.get("abstract", "")
        title = check_res.get("title", "")
        pubtype = check_res.get("pubtype", [])
        
        verdict = evidence.assess_claim(statement, abstract)
        ev_ok = evidence.evidence_ok(evidence_level, pubtype)
        
        source_results.append({
            "source_id": src_id,
            "exists": True,
            "title": title,
            "pubtype": pubtype,
            "abstract": abstract,
            "verdict": verdict,
            "evidence_ok": ev_ok
        })
        
    # Aggregate results
    best_source = None
    if not source_results:
        # No sources could be resolved
        verdict = "SOURCE_NOT_FOUND"
        evidence_ok = False
    else:
        # Determine aggregate verdict: SUPPORTED > WEAK > NEEDS_MANUAL > UNSUPPORTED > SOURCE_NOT_FOUND
        verdict_precedence = ["SUPPORTED", "WEAK", "NEEDS_MANUAL", "UNSUPPORTED", "SOURCE_NOT_FOUND"]
        
        for v in verdict_precedence:
            matches = [s for s in source_results if s["verdict"] == v]
            if matches:
                # Find if any match has evidence_ok=True
                matches_ok = [m for m in matches if m["evidence_ok"]]
                if matches_ok:
                    best_source = matches_ok[0]
                else:
                    best_source = matches[0]
                break
                
        verdict = best_source["verdict"]
        evidence_ok = best_source["evidence_ok"]
        
    # Decisions & routing
    target_graph_path = os.path.join(project_root, "03_knowledge_graph", "facts", f"{fact_id}.json")
    target_reject_path = os.path.join(project_root, "02_processing", "verify", "rejected", f"{fact_id}.json")
    
    action = "reject"
    
    # Add verification provenance metadata
    fact["verified_via"] = "live" if force_live else "cache"
    fact["verified_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    fact["verified_by"] = "verifier"
    fact["date"] = datetime.datetime.utcnow().date().isoformat()
    if best_source and best_source.get("title"):
        fact["source_title"] = truncate_title(best_source["title"])
    else:
        fact["source_title"] = ""
    
    if verdict in ("SOURCE_NOT_FOUND", "UNSUPPORTED", "WEAK"):
        action = "reject"
        fact["audit_verdict"] = verdict
        fact["evidence_ok"] = evidence_ok
        write_json(target_reject_path, fact)
        # Clean up from active graph if it was there
        if os.path.exists(target_graph_path):
            os.remove(target_graph_path)
            
    elif verdict == "NEEDS_MANUAL":
        action = "write"
        # Set status to needs_manual
        fact["status"] = "needs_manual"
        fact["audit_verdict"] = verdict
        fact["evidence_ok"] = evidence_ok
        write_json(target_graph_path, fact)
        if os.path.exists(target_reject_path):
            os.remove(target_reject_path)
            
    elif verdict == "SUPPORTED":
        if evidence_ok:
            action = "write"
            fact["audit_verdict"] = verdict
            fact["evidence_ok"] = evidence_ok
            # Write clean fact
            write_json(target_graph_path, fact)
            if os.path.exists(target_reject_path):
                os.remove(target_reject_path)
        else:
            # SUPPORTED but evidence level is not ok (EVIDENCE_MISMATCH)
            # Treat as needs_manual so it doesn't get rejected outright, but requires review
            action = "write"
            fact["status"] = "needs_manual"
            fact["audit_verdict"] = "EVIDENCE_MISMATCH"
            fact["evidence_ok"] = False
            write_json(target_graph_path, fact)
            if os.path.exists(target_reject_path):
                os.remove(target_reject_path)
 
    # Print JSON output to stdout
    output = {
        "fact_id": fact_id,
        "verdict": verdict,
        "evidence_ok": evidence_ok,
        "action": action
    }
    print(json.dumps(output, ensure_ascii=False))
    
    if action == "reject":
        sys.exit(1)
    else:
        sys.exit(0)
 
if __name__ == "__main__":
    main()
