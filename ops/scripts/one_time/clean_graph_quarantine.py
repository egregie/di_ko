import os
import json

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    
    # 1. Delete relationship files
    rels_to_delete = ["rel_0043.json", "rel_0044.json", "rel_0045.json"]
    for rel_file in rels_to_delete:
        rel_path = os.path.join(project_root, "03_knowledge_graph", "relationships", rel_file)
        if os.path.exists(rel_path):
            os.remove(rel_path)
            print(f"Deleted relationship {rel_file}")
            
    # 2. Clean references in entity files
    entities_dir = os.path.join(project_root, "03_knowledge_graph", "entities")
    facts_to_remove = {"fact_0023", "fact_0026", "fact_0027"}
    
    for filename in os.listdir(entities_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(entities_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                fact_ids = data.get("fact_ids", [])
                new_fact_ids = [fid for fid in fact_ids if fid not in facts_to_remove]
                
                if len(fact_ids) != len(new_fact_ids):
                    data["fact_ids"] = new_fact_ids
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"Cleaned quarantined facts from entity {filename}")
            except Exception as e:
                print(f"Error cleaning entity {filename}: {e}")
                
    # 3. Clean up rejected/fact_0004.json
    rejected_0004 = os.path.join(project_root, "02_processing", "verify", "rejected", "fact_0004.json")
    if os.path.exists(rejected_0004):
        os.remove(rejected_0004)
        print("Removed duplicate rejected fact_0004.json")

if __name__ == "__main__":
    run()
