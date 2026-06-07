import os
import json
import glob
import subprocess
import urllib.request
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    tokens_path = os.path.join(project_root, "04_design_system", "design-tokens.json")
    specs_dir = os.path.join(project_root, "05_content", "specs", "deck_retinoids")
    logs_dir = os.path.join(project_root, "ops", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # 1. Ensure local font directory exists
    fonts_dir = os.path.join(project_root, "04_design_system", "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Download Arimo font if not present
    font_path = os.path.join(fonts_dir, "Arimo[wght].ttf")
    if not os.path.exists(font_path):
        print("Local Arimo font file not found. Downloading...")
        url = "https://github.com/google/fonts/raw/main/ofl/arimo/Arimo%5Bwght%5D.ttf"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            with open(font_path, "wb") as f:
                f.write(data)
            print(f"Font downloaded successfully to {font_path} ({len(data)} bytes)")
        except Exception as e:
            print(f"Warning: Failed to download local font: {e}")
            
    # 2. Load and verify design tokens
    with open(tokens_path, "r", encoding="utf-8") as f:
        tokens = json.load(f)
        
    errors = []
    warnings = []
    
    # Check Zero Black Policy
    color_tokens = tokens.get("color", {})
    for col_name, col_val in color_tokens.items():
        val_clean = str(col_val).strip().lower()
        if val_clean in ("#000000", "#000", "black", "rgb(0,0,0)", "rgba(0,0,0,1)"):
            errors.append(f"Zero Black violation: token 'color.{col_name}' is set to black ({col_val})")
            
    # Check Font Family
    font_family = tokens.get("font", {}).get("family", "")
    if font_family != "Arimo":
        errors.append(f"Font Family check failed: expected 'Arimo', got '{font_family}'")
        
    # 3. Check Slide Specs
    spec_files = sorted(glob.glob(os.path.join(specs_dir, "deck_retinoids-s*.json")))
    total_slides = len(spec_files)
    
    has_pregnancy_slide = False
    for sf in spec_files:
        with open(sf, "r", encoding="utf-8") as f:
            slide = json.load(f)
        
        # Check source refs on clinical slides (non-cover)
        layout = slide.get("layout", "")
        if layout != "cover":
            refs = slide.get("source_refs", [])
            if not refs:
                warnings.append(f"Slide '{os.path.basename(sf)}' has no source references.")
                
        # Check for pregnancy reference (pregnancy contraindication check)
        title = str(slide.get("title", "")).lower()
        subtitle = str(slide.get("subtitle", "")).lower()
        body_text = ""
        for item in slide.get("body", []):
            body_text += str(item.get("text", "")).lower()
        notes = str(slide.get("notes", "")).lower()
        
        combined_text = title + " " + subtitle + " " + body_text + " " + notes
        if "беременнос" in combined_text or "pregnancy" in combined_text or "лактаци" in combined_text:
            has_pregnancy_slide = True
            
    if not has_pregnancy_slide:
        errors.append("Pregnancy precaution check failed: No pregnancy/lactation contraindication slide found.")
        
    # 4. Run Playwright Font Load Check
    playwright_script = os.path.join(script_dir, "qa_font_check.js")
    font_check_passed = False
    font_check_offline_passed = False
    
    try:
        res = subprocess.run(
            ["node", playwright_script],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        print("Playwright stdout:\n", res.stdout)
        if res.stderr:
            print("Playwright stderr:\n", res.stderr)
            
        if "RESULT_ARIMO_LOADED=true" in res.stdout:
            font_check_passed = True
        if "RESULT_ARIMO_OFFLINE_LOADED=true" in res.stdout:
            font_check_offline_passed = True
            
        if res.returncode != 0:
            errors.append("Playwright font rendering audit returned non-zero exit code.")
    except Exception as e:
        errors.append(f"Failed to run Playwright font check: {e}")
        
    if not font_check_passed:
        errors.append("Playwright check: Arimo webfont is not loaded.")
    if not font_check_offline_passed:
        warnings.append("Offline check: Arimo font could not be loaded in offline mode. Ensure local @font-face is active.")
        
    # 5. Write QA Audit Report
    status = "FAIL" if errors else "PASS"
    
    report_lines = [
        "# QA Audit Report — Phase 2.5 (Collection Hardening)",
        "",
        f"**Audit Status**: {status}",
        "",
        "### Errors",
    ]
    if errors:
        for err in errors:
            report_lines.append(f"- {err}")
    else:
        report_lines.append("- No blocking errors found.")
        
    report_lines.extend([
        "",
        "### Warnings",
    ])
    if warnings:
        for warn in warnings:
            report_lines.append(f"- {warn}")
    else:
        report_lines.append("- No warnings.")
        
    report_lines.extend([
        "",
        "### Checked Invariants",
        f"- Zero Black Policy: {'PASS' if not any('Zero Black' in e for e in errors) else 'FAIL'}",
        f"- Arimo font defined in tokens: {'PASS' if font_family == 'Arimo' else 'FAIL'}",
        f"- Pregnancy slide present: {'PASS' if has_pregnancy_slide else 'FAIL'}",
        f"- Playwright Font Load (Online): {'PASS' if font_check_passed else 'FAIL'}",
        f"- Playwright Font Load (Offline): {'PASS' if font_check_offline_passed else 'FAIL'}",
        f"- Total slides checked: {total_slides}",
    ])
    
    report_content = "\n".join(report_lines) + "\n"
    report_path = os.path.join(logs_dir, "qa_pilot_deck.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"\nQA audit complete. Report written to {report_path}")
    print(f"Status: {status}")
    
    if status == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
