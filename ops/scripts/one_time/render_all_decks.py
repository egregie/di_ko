import subprocess
import sys

DECKS = [
    "deck_retinoids_v2",
    "deck_vitamin_c",
    "deck_niacinamide",
    "deck_exfoliants",
    "deck_peptides"
]

project_root = "c:/di_ko"

def run_step(args, description):
    print(f"Running: {description}...")
    res = subprocess.run(args, cwd=project_root, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {description}")
        print("Stdout:\n", res.stdout)
        print("Stderr:\n", res.stderr)
        return False
    print(f"SUCCESS: {description}")
    return True

def main():
    success = True
    for deck in DECKS:
        print(f"\n======================================")
        print(f"Rendring and auditing deck: {deck}")
        print(f"======================================")
        
        # 1. HTML Render
        if not run_step(["python", "ops/scripts/render_deck.py", "--deck", deck], f"HTML Render for {deck}"):
            success = False
            continue
            
        # 2. PDF Compile
        if not run_step(["node", "ops/scripts/compile_pdf.js", deck], f"PDF Compile for {deck}"):
            success = False
            continue
            
        # 3. PPTX Render
        if not run_step(["python", "ops/scripts/render_pptx.py", "--deck", deck], f"PPTX Render for {deck}"):
            success = False
            continue
            
        # 4. QA Audit
        if not run_step(["python", "ops/scripts/qa_deck.py", "--deck", deck], f"QA Audit for {deck}"):
            success = False
            continue
            
    if not success:
        print("\nFail: One or more decks failed the rendering/QA process!")
        sys.exit(1)
    else:
        print("\nSuccess: All decks rendered, compiled, and passed QA successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
