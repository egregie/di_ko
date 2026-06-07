import os
import json
import glob

def clean_ontology():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    
    entities_dir = os.path.join(project_root, "03_knowledge_graph", "entities")
    facts_dir = os.path.join(project_root, "03_knowledge_graph", "facts")
    rels_dir = os.path.join(project_root, "03_knowledge_graph", "relationships")
    
    # 0. Clean up any temporary pilot facts from the active graph
    pilot_files = glob.glob(os.path.join(facts_dir, "pilot_*.json"))
    for pf in pilot_files:
        try:
            os.remove(pf)
            print(f"Removed temporary pilot fact: {os.path.basename(pf)}")
        except Exception as e:
            print(f"Error removing {pf}: {e}")
            
    # 1. Load all active facts
    fact_files = glob.glob(os.path.join(facts_dir, "*.json"))
    active_facts = {}
    for ff in fact_files:
        try:
            with open(ff, "r", encoding="utf-8") as f:
                fact_data = json.load(f)
                active_facts[fact_data["fact_id"]] = fact_data
        except Exception as e:
            print(f"Error loading fact {ff}: {e}")
            
    # 2. Load all relationships
    rel_files = glob.glob(os.path.join(rels_dir, "*.json"))
    relationships = []
    for rf in rel_files:
        try:
            with open(rf, "r", encoding="utf-8") as f:
                rel_data = json.load(f)
                relationships.append(rel_data)
        except Exception as e:
            print(f"Error loading relationship {rf}: {e}")
            
    # Map child ingredients to parent categories based on is_a and belongs_to relationships
    child_to_parent = {}
    for r in relationships:
        if r["type"] in ("is_a", "belongs_to"):
            child = r["from"]
            parent = r["to"]
            child_to_parent[child] = parent
            
    # 3. Load all entities
    entity_files = glob.glob(os.path.join(entities_dir, "*.json"))
    entities = {}
    for ef in entity_files:
        try:
            with open(ef, "r", encoding="utf-8") as f:
                ent_data = json.load(f)
                # Initialize fact_ids list
                ent_data["fact_id_set"] = set()
                entities[ent_data["entity_id"]] = ent_data
        except Exception as e:
            print(f"Error loading entity {ef}: {e}")
            
    # 4. Map active facts to their direct entities
    for fid, fact in active_facts.items():
        ent_id = fact["entity_id"]
        if ent_id in entities:
            entities[ent_id]["fact_id_set"].add(fid)
            
    # 5. Propagate child fact IDs to parent categories (e.g. SAP -> Vitamin C, Lactic Acid -> Exfoliants)
    for child_id, parent_id in child_to_parent.items():
        if child_id in entities and parent_id in entities:
            # Add all facts of the child to the parent
            child_facts = entities[child_id]["fact_id_set"]
            entities[parent_id]["fact_id_set"].update(child_facts)
            
    # 6. Save updated entity JSON files with clean sorted fact_ids
    for ent_id, ent in entities.items():
        # Convert set back to sorted list
        ent["fact_ids"] = sorted(list(ent["fact_id_set"]))
        # Cleanup temporary set key
        del ent["fact_id_set"]
        
        ent_file_path = os.path.join(entities_dir, f"{ent_id}.json")
        try:
            with open(ent_file_path, "w", encoding="utf-8") as f:
                json.dump(ent, f, indent=2, ensure_ascii=False)
            print(f"Updated entity {ent_id} fact_ids: {ent['fact_ids']}")
        except Exception as e:
            print(f"Error saving entity {ent_id}: {e}")
            
    print("\nOntology synchronization completed successfully.")

if __name__ == "__main__":
    clean_ontology()
