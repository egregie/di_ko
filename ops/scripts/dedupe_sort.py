import os
import sys
import json

EVIDENCE_RANK = {"A": 1, "B": 2, "C": 3, "D": 4}

def deduplicate_facts(facts):
    """
    Deduplicates facts based on statement/entity_id,
    retaining the one with the highest evidence level.
    """
    deduped = {}
    for fact in facts:
        # Standardize statement to find matching facts
        key = (fact.get("entity_id", "").lower().strip(), fact.get("statement", "").lower().strip())
        
        level = fact.get("evidence_level", "D").upper()
        if level not in EVIDENCE_RANK:
            level = "D"
            
        if key not in deduped:
            deduped[key] = fact
        else:
            existing_fact = deduped[key]
            existing_level = existing_fact.get("evidence_level", "D").upper()
            
            # Keep the fact with the lower rank value (higher evidence quality)
            if EVIDENCE_RANK[level] < EVIDENCE_RANK[existing_level]:
                deduped[key] = fact
            else:
                # Merge sources and contradictions
                existing_sources = set(existing_fact.get("sources", []))
                existing_sources.update(fact.get("sources", []))
                existing_fact["sources"] = sorted(list(existing_sources))
                
                existing_contradictions = set(existing_fact.get("contradictions", []))
                existing_contradictions.update(fact.get("contradictions", []))
                existing_fact["contradictions"] = sorted(list(existing_contradictions))
                
    return list(deduped.values())

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    processing_dir = os.path.join(project_root, "02_processing")
    
    if not os.path.exists(processing_dir):
        print("Processing directory does not exist. Skipping deduplication.", file=sys.stderr)
        sys.exit(0)
        
    facts_to_process = []
    
    # Read all fact JSON files under 02_processing
    for filename in os.listdir(processing_dir):
        if filename.endswith(".json") and filename.startswith("fact_"):
            filepath = os.path.join(processing_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                facts_to_process.append((filepath, data))
            except Exception as e:
                print(f"Error reading {filename}: {e}", file=sys.stderr)
                
    if not facts_to_process:
        print("No facts found to deduplicate.")
        sys.exit(0)
        
    raw_facts = [item[1] for item in facts_to_process]
    deduped_facts = deduplicate_facts(raw_facts)
    
    # Clean output: sort by evidence quality (rank)
    deduped_facts.sort(key=lambda x: (EVIDENCE_RANK.get(x.get("evidence_level", "D").upper(), 4), -x.get("confidence", 0.0)))
    
    # Write back the consolidated/deduplicated files
    # First delete existing files to prevent old files remaining
    for filepath, _ in facts_to_process:
        os.remove(filepath)
        
    for fact in deduped_facts:
        fact_id = fact.get("fact_id", "fact_unknown")
        out_path = os.path.join(processing_dir, f"{fact_id}.json")
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(fact, f, indent=2, ensure_ascii=False)
            print(f"Deduplicated fact written: {fact_id}.json")
        except Exception as e:
            print(f"Error writing deduplicated fact {fact_id}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
