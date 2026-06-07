import os
import json

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    kg_dir = os.path.join(project_root, "03_knowledge_graph")
    
    index = {
        "entities": {},
        "facts": {},
        "relationships": {}
    }
    
    # 1. Parse entities
    entities_path = os.path.join(kg_dir, "entities")
    if os.path.exists(entities_path):
        for filename in sorted(os.listdir(entities_path)):
            if filename.endswith(".json"):
                filepath = os.path.join(entities_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    eid = data.get("entity_id")
                    if eid:
                        index["entities"][eid] = {
                            "entity_id": eid,
                            "entity_type": data.get("entity_type", ""),
                            "title": data.get("title", ""),
                            "aliases": data.get("aliases", []),
                            "tags": data.get("tags", []),
                            "evidence_level": data.get("evidence_level", "D"),
                            "path": f"entities/{filename}"
                        }
                except Exception as e:
                    print(f"Error parsing entity {filename}: {e}")

    # 2. Parse facts
    facts_path = os.path.join(kg_dir, "facts")
    if os.path.exists(facts_path):
        for filename in sorted(os.listdir(facts_path)):
            if filename.endswith(".json"):
                filepath = os.path.join(facts_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    fid = data.get("fact_id")
                    if fid:
                        index["facts"][fid] = {
                            "fact_id": fid,
                            "statement": data.get("statement", ""),
                            "entity_id": data.get("entity_id", ""),
                            "evidence_level": data.get("evidence_level", "D"),
                            "path": f"facts/{filename}"
                        }
                except Exception as e:
                    print(f"Error parsing fact {filename}: {e}")

    # 3. Parse relationships
    relationships_path = os.path.join(kg_dir, "relationships")
    if os.path.exists(relationships_path):
        for filename in sorted(os.listdir(relationships_path)):
            if filename.endswith(".json"):
                filepath = os.path.join(relationships_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    rid = data.get("rel_id")
                    if rid:
                        index["relationships"][rid] = {
                            "rel_id": rid,
                            "from": data.get("from", ""),
                            "type": data.get("type", ""),
                            "to": data.get("to", ""),
                            "evidence_level": data.get("evidence_level", "D"),
                            "path": f"relationships/{filename}"
                        }
                except Exception as e:
                    print(f"Error parsing relationship {filename}: {e}")

    # Write output to graph_index.json
    out_path = os.path.join(kg_dir, "graph_index.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Graph index generated successfully with {len(index['entities'])} entities, {len(index['facts'])} facts, and {len(index['relationships'])} relationships.")

if __name__ == "__main__":
    main()
