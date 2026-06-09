import json
import os
import datetime

project_root = "c:/di_ko"
prov_path = os.path.join(project_root, "04_design_system", "assets", "asset_provenance.json")

with open(prov_path, "r", encoding="utf-8") as f:
    data = json.load(f)

mechanisms = [
    "rar_rxr_mechanism",
    "skin_layers_turnover",
    "collagen_synthesis",
    "ascorbic_acid_absorption",
    "ceramide_synthesis",
    "melanosome_transfer",
    "desmosome_desmolysis"
]

timestamp = datetime.datetime.utcnow().isoformat() + "Z"

for m in mechanisms:
    if m in data:
        data[m]["generated_by"] = "gen_diagrams.py"
        data[m]["fetched_at"] = timestamp
        # Update license to own/generated since they are now code-drawn vectors
        # (keeping attribution strings if we cite Servier style influence)
        if m in ("ascorbic_acid_absorption", "desmosome_desmolysis"):
            data[m]["license"] = "own/generated"
            data[m]["attribution"] = ""
        else:
            data[m]["license"] = "own/generated"

with open(prov_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("asset_provenance.json updated successfully!")
