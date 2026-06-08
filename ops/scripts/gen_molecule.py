import os
import sys
import json
import socket
import urllib.request
import urllib.parse
import urllib.error
import time
import datetime
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D

# Happy Eyeballs / Dual-stack IPv6 socket workaround: force IPv4 for NCBI and PubChem
orig_getaddrinfo = socket.getaddrinfo

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host in ("eutils.ncbi.nlm.nih.gov", "pubchem.ncbi.nlm.nih.gov") and family == 0:
        return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    return orig_getaddrinfo(host, port, family, type, proto, flags)

socket.getaddrinfo = custom_getaddrinfo

# Standard Compound Mappings
COMPOUNDS = {
    "retinol": "retinol",
    "tretinoin": "tretinoin",
    "adapalene": "adapalene",
    "ascorbic_acid": "ascorbic acid",
    "sodium_ascorbyl_phosphate": "sodium ascorbyl phosphate",
    "magnesium_ascorbyl_phosphate": "magnesium ascorbyl phosphate",
    "ascorbyl_glucoside": "ascorbyl glucoside",
    "niacinamide": "niacinamide",
    "glycolic_acid": "glycolic acid",
    "lactic_acid": "lactic acid",
    "mandelic_acid": "mandelic acid",
    "salicylic_acid": "salicylic acid"
}

def load_brand_color(tokens_path):
    try:
        with open(tokens_path, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        hex_color = tokens.get("color", {}).get("dark", "#1D291C")
        # Convert hex to RGB float tuple normalized to [0, 1]
        hex_color = hex_color.lstrip("#")
        return (
            int(hex_color[0:2], 16) / 255.0,
            int(hex_color[2:4], 16) / 255.0,
            int(hex_color[4:6], 16) / 255.0
        ), tokens.get("color", {}).get("dark", "#1D291C")
    except Exception:
        return (29/255.0, 41/255.0, 28/255.0), "#1D291C"

def query_pubchem(name):
    # Throttle
    time.sleep(0.5)
    
    # 1. Resolve Name -> CID
    url_cid = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(name)}/cids/json"
    req_cid = urllib.request.Request(
        url_cid, 
        headers={'User-Agent': 'ym-proskin-collector/1.0 (mailto:admin@ym-proskin.local)'}
    )
    
    try:
        with urllib.request.urlopen(req_cid, timeout=20) as r:
            res_cid = json.loads(r.read().decode('utf-8'))
        cid = res_cid["IdentifierList"]["CID"][0]
    except urllib.error.HTTPError as e:
        print(f"PubChem HTTP error for compound '{name}': {e.code}")
        return None, None
    except Exception as e:
        print(f"Error resolving CID for '{name}': {e}")
        return None, None
        
    # 2. Resolve CID -> SMILES (Fetch CanonicalSMILES and ConnectivitySMILES)
    url_smiles = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/CanonicalSMILES,ConnectivitySMILES/json"
    req_smiles = urllib.request.Request(
        url_smiles, 
        headers={'User-Agent': 'ym-proskin-collector/1.0 (mailto:admin@ym-proskin.local)'}
    )
    
    try:
        with urllib.request.urlopen(req_smiles, timeout=20) as r:
            res_smiles = json.loads(r.read().decode('utf-8'))
        props = res_smiles["PropertyTable"]["Properties"][0]
        # Prefer CanonicalSMILES, fallback to ConnectivitySMILES
        smiles = props.get("CanonicalSMILES") or props.get("ConnectivitySMILES")
        if not smiles:
            print(f"SMILES not found in properties for '{name}' (CID: {cid})")
            return cid, None
        return cid, smiles
    except Exception as e:
        print(f"Error fetching SMILES for CID {cid}: {e}")
        return cid, None

def render_molecule_svg(smiles, rgb_color, output_path):
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        raise ValueError("Invalid SMILES string")
        
    # Compute 2D coordinates for drawing
    Chem.rdDepictor.Compute2DCoords(mol)
    
    # Render to SVG (300x300 canvas size)
    d2d = rdMolDraw2D.MolDraw2DSVG(300, 300)
    opts = d2d.drawOptions()
    
    # Background: transparent (no default white box)
    opts.clearBackground = False
    opts.backgroundColour = (1, 1, 1, 0)
    
    # Custom colors
    opts.symbolColour = rgb_color
    
    # Set Palette for all element symbols to the same color
    for i in range(1, 118):
        opts.updateAtomPalette({i: rgb_color})
        
    # Draw
    d2d.DrawMolecule(mol)
    d2d.FinishDrawing()
    svg = d2d.GetDrawingText()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

def update_registry(registry_path, compound_id, relative_path, cid, smiles):
    registry = {}
    if os.path.exists(registry_path):
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception:
            registry = {}
            
    registry[compound_id] = {
        "id": compound_id,
        "type": "molecule",
        "path": relative_path,
        "source_of_truth": f"PubChem CID {cid} (SMILES: {smiles})",
        "license": "generated/own",
        "attribution": "",
        "generated_by": "gen_molecule.py",
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate SVG structures for cosmetic molecules")
    parser.add_argument("--compound", type=str, help="Specific compound ID to generate")
    parser.add_argument("--all", action="store_true", help="Generate all 12 target compounds")
    args = parser.parse_args()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    tokens_path = os.path.join(project_root, "04_design_system", "design-tokens.json")
    registry_path = os.path.join(project_root, "04_design_system", "assets", "asset_provenance.json")
    molecules_dir = os.path.join(project_root, "04_design_system", "assets", "molecules")
    
    rgb_color, hex_color = load_brand_color(tokens_path)
    print(f"Using brand color: {hex_color} -> RGB: {rgb_color}")
    
    targets = {}
    if args.all:
        targets = COMPOUNDS
    elif args.compound:
        if args.compound in COMPOUNDS:
            targets = {args.compound: COMPOUNDS[args.compound]}
        else:
            print(f"Unknown compound ID: '{args.compound}'. Available IDs: {list(COMPOUNDS.keys())}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)
        
    success_count = 0
    
    for comp_id, comp_name in targets.items():
        print(f"\nProcessing '{comp_id}' ({comp_name})...")
        cid, smiles = query_pubchem(comp_name)
        
        if not cid or not smiles:
            print(f"Error: PubChem resolution failed for '{comp_name}'. status: blocked.")
            # Under P012 / P013, if PubChem fails, block task execution
            sys.exit(1)
            
        print(f"  Resolved: CID {cid}")
        print(f"  SMILES: {smiles}")
        
        output_file = f"{comp_id}.svg"
        output_path = os.path.join(molecules_dir, output_file)
        relative_path = f"04_design_system/assets/molecules/{output_file}"
        
        try:
            render_molecule_svg(smiles, rgb_color, output_path)
            print(f"  Rendered structure SVG to {output_path}")
            update_registry(registry_path, comp_id, relative_path, cid, smiles)
            print(f"  Registered in provenance registry.")
            success_count += 1
        except Exception as e:
            print(f"  Failed to render molecular SVG: {e}")
            sys.exit(1)
            
    print(f"\nDone. Successfully generated and registered {success_count} molecules.")

if __name__ == "__main__":
    main()
