import os
import json
import glob
import subprocess
import urllib.request
import sys
from pptx import Presentation
from pptx.dml.color import RGBColor

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    tokens_path = os.path.join(project_root, "04_design_system", "design-tokens.json")
    specs_dir = os.path.join(project_root, "05_content", "specs", "deck_retinoids_v2")
    logs_dir = os.path.join(project_root, "ops", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # 1. Download Arimo font if not present
    fonts_dir = os.path.join(project_root, "04_design_system", "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
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
        
    pdf_errors = []
    pptx_errors = []
    warnings = []
    
    # Check Zero Black Policy
    color_tokens = tokens.get("color", {})
    for col_name, col_val in color_tokens.items():
        val_clean = str(col_val).strip().lower()
        if val_clean in ("#000000", "#000", "black", "rgb(0,0,0)", "rgba(0,0,0,1)"):
            pdf_errors.append(f"Zero Black violation: token 'color.{col_name}' is set to black ({col_val})")
            
    # Check Font Family
    font_family = tokens.get("font", {}).get("family", "")
    if font_family != "Arimo":
        pdf_errors.append(f"Font Family check failed: expected 'Arimo', got '{font_family}'")
        
    # 3. Check Slide Specs (Source Refs and Pregnancy warning)
    spec_files = sorted(glob.glob(os.path.join(specs_dir, "deck_retinoids_v2-s*.json")))
    total_slides = len(spec_files)
    
    quarantined_facts = {"fact_0023", "fact_0026", "fact_0027", "fact_0003", "fact_0008", "fact_0013", "fact_0016"}
    
    has_pregnancy_slide = False
    for sf in spec_files:
        with open(sf, "r", encoding="utf-8") as f:
            slide = json.load(f)
        
        layout = slide.get("layout", "")
        refs = slide.get("source_refs", [])
        
        # Check source refs on clinical slides (non-cover and non-section_divider)
        if layout not in ("cover", "section_divider"):
            if not refs:
                warnings.append(f"Slide '{os.path.basename(sf)}' is clinical but has no source references.")
            else:
                # [GATE] Check if any cited fact is quarantined
                for r in refs:
                    if r in quarantined_facts:
                        pdf_errors.append(f"GATE BLOCK: Slide '{os.path.basename(sf)}' cites quarantined fact '{r}'.")
                        pptx_errors.append(f"GATE BLOCK: Slide '{os.path.basename(sf)}' cites quarantined fact '{r}'.")
                        
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
        pdf_errors.append("Pregnancy precaution check failed: No pregnancy/lactation contraindication slide found.")
        pptx_errors.append("Pregnancy precaution check failed: No pregnancy/lactation contraindication slide found.")
        
    # 4. Run Playwright Font Load Check for PDF/HTML output
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
            pdf_errors.append("Playwright font rendering audit returned non-zero exit code.")
    except Exception as e:
        pdf_errors.append(f"Failed to run Playwright font check: {e}")
        
    if not font_check_passed:
        pdf_errors.append("Playwright check: Arimo webfont is not loaded.")
    if not font_check_offline_passed:
        warnings.append("Offline check: Arimo font could not be loaded in offline mode. Ensure local @font-face is active.")
        
    # 5. PPTX Specific Audits (Zero Black, Arimo, Structure)
    pptx_path = os.path.join(project_root, "06_render", "out", "deck_retinoids_v2.pptx")
    if not os.path.exists(pptx_path):
        pptx_errors.append("PPTX file not found in render output.")
    else:
        try:
            prs = Presentation(pptx_path)
            if len(prs.slides) != total_slides:
                pptx_errors.append(f"PPTX slide count mismatch: specs={total_slides}, pptx={len(prs.slides)}")
                
            for idx, slide in enumerate(prs.slides):
                for shape in slide.shapes:
                    # Check shapes solid fills
                    if shape.fill.type == 1:  # solid fill
                        rgb = shape.fill.fore_color.rgb
                        if rgb == RGBColor(0, 0, 0) or rgb == RGBColor(255, 255, 255):
                            pptx_errors.append(f"Slide {idx + 1}: PPTX Zero Black violation (shape solid color is {rgb})")
                            
                    # Check text box properties
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                if run.font.name != "Arimo":
                                    pptx_errors.append(f"Slide {idx + 1}: PPTX font fallback detected. Font family is '{run.font.name}', expected 'Arimo'.")
                                if run.font.color.type == 1:  # RGBColor
                                    rgb = run.font.color.rgb
                                    if rgb == RGBColor(0, 0, 0) or rgb == RGBColor(255, 255, 255):
                                        pptx_errors.append(f"Slide {idx + 1}: PPTX Zero Black violation (text run color is {rgb})")
        except Exception as e:
            pptx_errors.append(f"Failed to audit PPTX: {e}")
            
    # 6. Write QA Audit Report ops/logs/qa_deck_v2.md
    pdf_status = "FAIL" if pdf_errors else "PASS"
    pptx_status = "FAIL" if pptx_errors else "PASS"
    overall_status = "FAIL" if (pdf_errors or pptx_errors) else "PASS"
    
    report_lines = [
        "# QA Audit Report — Phase 3.5: Design System & Dual Render",
        "",
        f"**Overall Audit Status**: {overall_status}",
        "",
        "## PDF / HTML Render Audit",
        f"- **Status**: {pdf_status}",
        "",
        "### Errors",
    ]
    if pdf_errors:
        for err in pdf_errors:
            report_lines.append(f"- {err}")
    else:
        report_lines.append("- No PDF rendering or citation errors found.")
        
    report_lines.extend([
        "",
        "## PPTX (PowerPoint) Render Audit",
        f"- **Status**: {pptx_status}",
        "",
        "### Errors",
    ])
    if pptx_errors:
        for err in pptx_errors:
            report_lines.append(f"- {err}")
    else:
        report_lines.append("- No PPTX font, color, or structural errors found.")
        
    report_lines.extend([
        "",
        "## Warnings",
    ])
    if warnings:
        for warn in warnings:
            report_lines.append(f"- {warn}")
    else:
        report_lines.append("- No warnings.")
        
    report_lines.extend([
        "",
        "## Checked Invariants",
        f"- Zero Black Policy: {'PASS' if not any('Zero Black' in e for e in pdf_errors + pptx_errors) else 'FAIL'}",
        f"- Arimo font defined in tokens: {'PASS' if font_family == 'Arimo' else 'FAIL'}",
        f"- Pregnancy slide present: {'PASS' if has_pregnancy_slide else 'FAIL'}",
        f"- Playwright Font Load (Online): {'PASS' if font_check_passed else 'FAIL'}",
        f"- Playwright Font Load (Offline): {'PASS' if font_check_offline_passed else 'FAIL'}",
        f"- PPTX Element Font Check (Arimo): {'PASS' if not any('font' in e for e in pptx_errors) else 'FAIL'}",
        f"- Total slides checked: {total_slides}",
    ])
    
    report_content = "\n".join(report_lines) + "\n"
    report_path = os.path.join(logs_dir, "qa_deck_v2.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"\nQA audit complete. Report written to {report_path}")
    print(f"Overall Status: {overall_status}")
    
    if overall_status == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
