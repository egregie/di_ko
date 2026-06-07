import os
import json

rels = [
    {
        "rel_id": "rel_0031",
        "from": "glycolic_acid",
        "type": "is_a",
        "to": "exfoliants",
        "evidence_level": "A",
        "sources": ["SRC-A019"]
    },
    {
        "rel_id": "rel_0032",
        "from": "lactic_acid",
        "type": "is_a",
        "to": "exfoliants",
        "evidence_level": "A",
        "sources": ["SRC-A020"]
    },
    {
        "rel_id": "rel_0033",
        "from": "mandelic_acid",
        "type": "is_a",
        "to": "exfoliants",
        "evidence_level": "A",
        "sources": ["SRC-A020"]
    },
    {
        "rel_id": "rel_0034",
        "from": "salicylic_acid",
        "type": "is_a",
        "to": "exfoliants",
        "evidence_level": "A",
        "sources": ["SRC-A021"]
    },
    {
        "rel_id": "rel_0035",
        "from": "exfoliants",
        "type": "used_for",
        "to": "acne",
        "evidence_level": "A",
        "sources": ["SRC-A019", "SRC-A020"]
    },
    {
        "rel_id": "rel_0036",
        "from": "exfoliants",
        "type": "used_for",
        "to": "photoaging",
        "evidence_level": "A",
        "sources": ["SRC-A021", "SRC-A022"]
    },
    {
        "rel_id": "rel_0037",
        "from": "sodium_ascorbyl_phosphate",
        "type": "belongs_to",
        "to": "vitamin_c",
        "evidence_level": "A",
        "sources": ["SRC-A023"]
    },
    {
        "rel_id": "rel_0038",
        "from": "magnesium_ascorbyl_phosphate",
        "type": "belongs_to",
        "to": "vitamin_c",
        "evidence_level": "A",
        "sources": ["SRC-A023"]
    },
    {
        "rel_id": "rel_0039",
        "from": "ascorbyl_glucoside",
        "type": "belongs_to",
        "to": "vitamin_c",
        "evidence_level": "A",
        "sources": ["SRC-A023"]
    },
    {
        "rel_id": "rel_0040",
        "from": "vitamin_c",
        "type": "used_for",
        "to": "photoaging",
        "evidence_level": "A",
        "sources": ["SRC-A023"]
    },
    {
        "rel_id": "rel_0041",
        "from": "niacinamide",
        "type": "used_for",
        "to": "acne",
        "evidence_level": "A",
        "sources": ["SRC-A026", "SRC-A027"]
    },
    {
        "rel_id": "rel_0042",
        "from": "niacinamide",
        "type": "used_for",
        "to": "barrier",
        "evidence_level": "A",
        "sources": ["SRC-A026"]
    },
    {
        "rel_id": "rel_0043",
        "from": "glycolic_acid",
        "type": "interacts_with",
        "to": "retinol",
        "evidence_level": "A",
        "sources": ["SRC-A019"]
    },
    {
        "rel_id": "rel_0044",
        "from": "niacinamide",
        "type": "interacts_with",
        "to": "retinol",
        "evidence_level": "A",
        "sources": ["SRC-A026"]
    },
    {
        "rel_id": "rel_0045",
        "from": "sodium_ascorbyl_phosphate",
        "type": "interacts_with",
        "to": "retinol",
        "evidence_level": "A",
        "sources": ["SRC-A025"]
    }
]

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    rels_dir = os.path.join(project_root, "03_knowledge_graph", "relationships")
    
    for r in rels:
        rel_id = r["rel_id"]
        rel_path = os.path.join(rels_dir, f"{rel_id}.json")
        with open(rel_path, "w", encoding="utf-8") as out:
            json.dump(r, out, indent=2, ensure_ascii=False)
        print(f"Created relationship {rel_id}")

if __name__ == "__main__":
    run()
