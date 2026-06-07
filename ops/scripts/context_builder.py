import os
import sys
import json

def load_full_node(project_root, node):
    section = node.get("section")
    path = node.get("path")
    if not path:
        return None
        
    full_path = os.path.join(project_root, "03_knowledge_graph", path)
    if not os.path.exists(full_path):
        return None
        
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def main():
    # Read stdin
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            retrieved = []
        else:
            retrieved = json.loads(input_data)
    except Exception as e:
        print(f"Error reading retriever input: {e}", file=sys.stderr)
        sys.exit(1)
        
    if not isinstance(retrieved, list):
        print("Input must be a JSON list of matched nodes.", file=sys.stderr)
        sys.exit(1)
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    compact_blocks = []
    
    for item in retrieved:
        full_node = load_full_node(project_root, item)
        if not full_node:
            continue
            
        section = item.get("section")
        
        if section == "entities":
            title = full_node.get("title", "Unknown")
            etype = full_node.get("entity_type", "Ingredient")
            lvl = full_node.get("evidence_level", "D")
            compact_blocks.append(f"Entity: {title} ({etype}) [Level {lvl}]")
            
        elif section == "facts":
            stmt = full_node.get("statement", "")
            lvl = full_node.get("evidence_level", "D")
            sources = ", ".join(full_node.get("sources", []))
            compact_blocks.append(f"Fact: {stmt} [Level {lvl}, Sources: {sources}]")
            
        elif section == "relationships":
            frm = full_node.get("from", "")
            rtype = full_node.get("type", "")
            to = full_node.get("to", "")
            lvl = full_node.get("evidence_level", "D")
            compact_blocks.append(f"Relation: {frm} -{rtype}-> {to} [Level {lvl}]")
            
    # Print clean compact context
    if not compact_blocks:
        print("No matching knowledge context found.")
    else:
        print("\n".join(compact_blocks))

if __name__ == "__main__":
    main()
