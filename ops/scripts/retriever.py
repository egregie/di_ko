import os
import sys
import json
import argparse

EVIDENCE_RANK = {"A": 1, "B": 2, "C": 3, "D": 4}

def match_node(query, node, section):
    query = query.lower().strip()
    score = 0.0
    
    if section == "entities":
        entity_id = str(node.get("entity_id", "")).lower()
        title = str(node.get("title", "")).lower()
        entity_type = str(node.get("entity_type", "")).lower()
        aliases = [str(a).lower() for a in node.get("aliases", [])]
        tags = [str(t).lower() for t in node.get("tags", [])]
        
        if query == entity_id:
            score = 2.0
        elif query in entity_id or query in title:
            score = 1.5
        elif query in entity_type or any(query in a for a in aliases) or any(query in t for t in tags):
            score = 1.0
            
    elif section == "facts":
        fact_id = str(node.get("fact_id", "")).lower()
        statement = str(node.get("statement", "")).lower()
        entity_id = str(node.get("entity_id", "")).lower()
        
        if query == fact_id or query == entity_id:
            score = 2.0
        elif query in statement or query in entity_id:
            score = 1.5
            
    elif section == "relationships":
        rel_id = str(node.get("rel_id", "")).lower()
        from_id = str(node.get("from", "")).lower()
        type_str = str(node.get("type", "")).lower()
        to_id = str(node.get("to", "")).lower()
        
        if query == rel_id or query == from_id or query == to_id:
            score = 2.0
        elif query in from_id or query in to_id or query in type_str:
            score = 1.5
            
    return score

def main():
    parser = argparse.ArgumentParser(description="YM PROSKIN Graph Knowledge Retriever")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=30, help="Max nodes to return")
    args = parser.parse_args()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    index_path = os.path.join(project_root, "03_knowledge_graph", "graph_index.json")
    
    if not os.path.exists(index_path):
        # Empty graph index, return empty list
        print(json.dumps([]))
        sys.exit(0)
        
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    except Exception as e:
        print(f"Error loading index: {e}", file=sys.stderr)
        sys.exit(1)
        
    matched_nodes = []
    
    # Process index sections
    for section in ["entities", "facts", "relationships"]:
        items = index_data.get(section, {})
        # The items can be a list or dict. Let's handle both.
        if isinstance(items, dict):
            for key, val in items.items():
                score = match_node(args.query, val, section)
                if score > 0:
                    val["section"] = section
                    val["match_score"] = score
                    matched_nodes.append(val)
        elif isinstance(items, list):
            for val in items:
                score = match_node(args.query, val, section)
                if score > 0:
                    val["section"] = section
                    val["match_score"] = score
                    matched_nodes.append(val)
                    
    # Sort matched nodes:
    # 1. Match score (descending)
    # 2. Evidence level rank (A=1, B=2, C=3, D=4, ascending)
    def get_sort_key(node):
        score = node.get("match_score", 0.0)
        lvl = node.get("evidence_level", "D").upper()
        rank = EVIDENCE_RANK.get(lvl, 4)
        return (-score, rank)
        
    matched_nodes.sort(key=get_sort_key)
    
    # Limit results
    results = matched_nodes[:args.limit]
    
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
