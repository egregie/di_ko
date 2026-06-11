import os
import sys
import json

def validate_types(data, template, path=""):
    # Skip type validation for the confidence key to allow string/reserved value
    if path == "confidence" or path.endswith(".confidence"):
        return
        
    # Allow float where int is expected and vice-versa
    if isinstance(data, (int, float)) and isinstance(template, (int, float)):
        return
    
    if type(data) != type(template):
        raise ValueError(f"Type mismatch at '{path}': expected {type(template).__name__}, got {type(data).__name__}")
    
    if isinstance(template, dict):
        for k, v in template.items():
            if k not in data:
                raise ValueError(f"Missing key at '{path}': '{k}'")
            validate_types(data[k], v, f"{path}.{k}" if path else k)
            
    elif isinstance(template, list):
        if len(template) > 0:
            item_template = template[0]
            for idx, item in enumerate(data):
                validate_types(item, item_template, f"{path}[{idx}]")

def main():
    # Paths relative to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    schemas_dir = os.path.join(project_root, "00_governance", "schemas")
    kg_dir = os.path.join(project_root, "03_knowledge_graph")
    
    # Load templates
    try:
        with open(os.path.join(schemas_dir, "entity.json"), "r", encoding="utf-8") as f:
            entity_template = json.load(f)
        with open(os.path.join(schemas_dir, "fact.json"), "r", encoding="utf-8") as f:
            fact_template = json.load(f)
        with open(os.path.join(schemas_dir, "relationship.json"), "r", encoding="utf-8") as f:
            relationship_template = json.load(f)
        with open(os.path.join(schemas_dir, "source.json"), "r", encoding="utf-8") as f:
            source_template = json.load(f)
    except Exception as e:
        print(f"Error loading schema templates: {e}", file=sys.stderr)
        sys.exit(1)
        
    errors = []
    
    # 1. Validate entities
    entities_path = os.path.join(kg_dir, "entities")
    if os.path.exists(entities_path):
        for filename in os.listdir(entities_path):
            if filename.endswith(".json"):
                filepath = os.path.join(entities_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    validate_types(data, entity_template)
                except Exception as e:
                    errors.append(f"Entity file '{filename}' validation failed: {e}")
                    
    import re
    # Load sources to verify cache integrity for facts
    sources_filepath = os.path.join(kg_dir, "sources.json")
    sources_map = {}
    if os.path.exists(sources_filepath):
        try:
            with open(sources_filepath, "r", encoding="utf-8") as sf:
                s_data = json.load(sf)
                sources_map = {src["source_id"]: src for src in s_data.get("sources", [])}
        except Exception:
            pass

    # 2. Validate facts
    facts_path = os.path.join(kg_dir, "facts")
    cache_dir = os.path.join(project_root, "ops", "cache", "eutils")
    if os.path.exists(facts_path):
        for filename in os.listdir(facts_path):
            if filename.endswith(".json"):
                filepath = os.path.join(facts_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    validate_types(data, fact_template)
                    
                    # Cache integrity check
                    if data.get("verified_via") == "cache":
                        fact_sources = data.get("sources", [])
                        if fact_sources:
                            src_id = fact_sources[0]
                            src_entry = sources_map.get(src_id)
                            if src_entry:
                                pmid = src_entry.get("pmid", "")
                                doi = src_entry.get("doi", "")
                                if pmid:
                                    cache_file = os.path.join(cache_dir, f"{pmid}.json")
                                elif doi:
                                    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', doi)
                                    cache_file = os.path.join(cache_dir, f"doi_{safe_name}.json")
                                else:
                                    cache_file = None
                                    
                                if not cache_file:
                                    errors.append(f"Fact file '{filename}' has verified_via='cache' but no valid identifier (PMID/DOI) in source '{src_id}'.")
                                elif not os.path.exists(cache_file):
                                    errors.append(f"Fact file '{filename}' has verified_via='cache' but cache file '{os.path.basename(cache_file)}' is missing.")
                                else:
                                    # Verify provenance inside cache file
                                    try:
                                        with open(cache_file, "r", encoding="utf-8") as cf:
                                            cache_data = json.load(cf)
                                        if not cache_data.get("fetched"):
                                            errors.append(f"Fact file '{filename}' has verified_via='cache' but cache file '{os.path.basename(cache_file)}' has fetched != true.")
                                        else:
                                            required_provenance = ["source_url", "http_status", "fetched_at", "raw_hash"]
                                            missing_provenance = [field for field in required_provenance if field not in cache_data]
                                            if missing_provenance:
                                                errors.append(f"Fact file '{filename}' has verified_via='cache' but cache file '{os.path.basename(cache_file)}' is missing provenance fields: {missing_provenance}.")
                                    except Exception as ce:
                                        errors.append(f"Fact file '{filename}' failed to parse cache file '{os.path.basename(cache_file)}': {ce}")
                except Exception as e:
                    errors.append(f"Fact file '{filename}' validation failed: {e}")

                    
    # 3. Validate relationships
    relationships_path = os.path.join(kg_dir, "relationships")
    if os.path.exists(relationships_path):
        for filename in os.listdir(relationships_path):
            if filename.endswith(".json"):
                filepath = os.path.join(relationships_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    validate_types(data, relationship_template)
                except Exception as e:
                    errors.append(f"Relationship file '{filename}' validation failed: {e}")
                    
    # 4. Validate sources
    sources_filepath = os.path.join(kg_dir, "sources.json")
    if os.path.exists(sources_filepath):
        try:
            with open(sources_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # The structure of sources.json is {"sources": [source_objects]}
            if not isinstance(data, dict) or "sources" not in data:
                raise ValueError("sources.json must be an object with a 'sources' key")
            
            sources_list = data["sources"]
            if not isinstance(sources_list, list):
                raise ValueError("'sources' key in sources.json must be an array")
                
            for idx, src in enumerate(sources_list):
                try:
                    validate_types(src, source_template)
                except Exception as e:
                    errors.append(f"sources.json item at index {idx} validation failed: {e}")
        except Exception as e:
            errors.append(f"sources.json validation failed: {e}")

    # 5. Cross-reference integrity (Phase 8.7b)
    rejected_dir = os.path.join(project_root, "02_processing", "verify", "rejected")
    rejected_ids = set()
    if os.path.exists(rejected_dir):
        for fn in os.listdir(rejected_dir):
            if fn.endswith(".json"):
                rejected_ids.add(fn[:-5])
    entity_ids = set()
    if os.path.exists(entities_path):
        for fn in os.listdir(entities_path):
            if fn.endswith(".json"):
                entity_ids.add(fn[:-5])

    # 5a. Broken fact-link: entity fact_ids must not point to a quarantined (rejected) fact
    if os.path.exists(entities_path):
        for filename in os.listdir(entities_path):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(entities_path, filename), "r", encoding="utf-8") as f:
                        edata = json.load(f)
                    for fid in edata.get("fact_ids", []):
                        if fid in rejected_ids:
                            errors.append(f"Entity '{filename}' references quarantined fact '{fid}' (present in 02_processing/verify/rejected/). Restore via gate or unlink.")
                except Exception:
                    pass

    # 5b. Dangling relationship: from/to must reference an existing entity file
    if os.path.exists(relationships_path):
        for filename in os.listdir(relationships_path):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(relationships_path, filename), "r", encoding="utf-8") as f:
                        rdata = json.load(f)
                    for key in ("from", "to"):
                        ref = rdata.get(key)
                        if ref and ref not in entity_ids:
                            errors.append(f"Relationship '{filename}' {key}='{ref}' references a missing entity (no file in entities/). Create the entity or remove the relationship.")
                except Exception:
                    pass

    if errors:
        print("Graph validation FAILED with the following errors:", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Graph validation passed successfully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
