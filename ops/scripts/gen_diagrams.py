import os
import json
import subprocess
import sys

# Load tokens
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
TOKENS_PATH = os.path.join(PROJECT_ROOT, "04_design_system", "diagram_tokens.json")

with open(TOKENS_PATH, "r", encoding="utf-8") as f:
    tokens = json.load(f)

colors = tokens["color"]
font = tokens["fontFamily"]
padding = tokens["padding"]
min_gap = tokens["minGap"]
font_sizes = tokens["fontSize"]

def ceramide_extra_drawing(pad, gap, colors, font, width, height):
    svg = []
    # Down arrow from step 3 box to lipid bilayer
    svg.append(f'  <path d="M 327 110 L 327 148" fill="none" stroke="{colors["dark"]}" stroke-width="2" marker-end="url(#arrow)"/>')
    
    # Lipid bilayer box
    svg.append(f'  <rect x="30" y="155" width="340" height="108" rx="6" fill="{colors["bg"]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    
    # Corneocyte labels
    svg.append(f'  <line x1="40" y1="168" x2="120" y2="168" stroke="{colors["herbal"]}" stroke-width="2" stroke-dasharray="3,2"/>')
    svg.append(f'  <text x="80" y="181" font-family="{font}" font-size="9" fill="{colors["text"]}" text-anchor="middle">Corneocyte</text>')
    svg.append(f'  <line x1="40" y1="190" x2="120" y2="190" stroke="{colors["herbal"]}" stroke-width="1" stroke-dasharray="3,2"/>')
    
    svg.append(f'  <line x1="40" y1="218" x2="120" y2="218" stroke="{colors["herbal"]}" stroke-width="2" stroke-dasharray="3,2"/>')
    svg.append(f'  <text x="80" y="231" font-family="{font}" font-size="9" fill="{colors["text"]}" text-anchor="middle">Corneocyte</text>')
    svg.append(f'  <line x1="40" y1="244" x2="120" y2="244" stroke="{colors["herbal"]}" stroke-width="1" stroke-dasharray="3,2"/>')
    
    # Lipids circles
    for cx in [143, 157, 171, 185]:
        svg.append(f'  <circle cx="{cx}" cy="197" r="4" fill="{colors["herbal"]}"/>')
        svg.append(f'  <line x1="{cx}" y1="201" x2="{cx}" y2="209" stroke="{colors["dark"]}" stroke-width="1"/>')
        svg.append(f'  <circle cx="{cx}" cy="217" r="4" fill="{colors["herbal"]}"/>')
        
    # Annotation text on the right
    svg.append(f'  <text x="200" y="175" font-family="{font}" font-size="10" font-weight="bold" fill="{colors["herbal"]}">Липидные пласты</text>')
    svg.append(f'  <text x="200" y="191" font-family="{font}" font-size="9" fill="{colors["text"]}">Церамиды &amp; липиды</text>')
    svg.append(f'  <text x="200" y="207" font-family="{font}" font-size="9" fill="{colors["warn"]}" font-weight="bold">Блокада TEWL</text>')
    svg.append(f'  <text x="200" y="223" font-family="{font}" font-size="8" fill="{colors["herbal"]}">снижение испарения</text>')
    svg.append(f'  <text x="200" y="235" font-family="{font}" font-size="8" fill="{colors["herbal"]}">воды кожей</text>')
    return "\n".join(svg)

def xml_escape(text):
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

def collagen_extra_drawing(pad, gap, colors, font, width, height):
    svg = []
    svg.append(f'  <text x="36" y="135" font-family="{font}" font-size="9" fill="{colors["herbal"]}" font-weight="bold">Транскрипция генов:</text>')
    svg.append(f'  <ellipse cx="200" cy="220" rx="168" ry="60" fill="none" stroke="{colors["herbal"]}" stroke-width="1.5" stroke-dasharray="5,4"/>')
    svg.append(f'  <text x="200" y="152" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["herbal"]}" letter-spacing="0.08em" text-anchor="middle">ЯДРО / NUCLEUS</text>')
    
    svg.append(f'  <path d="M 50 213 Q 70 198 90 213 T 130 213 T 170 213" fill="none" stroke="{colors["text"]}" stroke-width="2.5"/>')
    svg.append(f'  <path d="M 50 233 Q 70 248 90 233 T 130 233 T 170 233" fill="none" stroke="{colors["herbal"]}" stroke-width="2.5"/>')
    for px in [70, 110, 150]:
        svg.append(f'  <line x1="{px}" y1="214" x2="{px}" y2="232" stroke="{colors["text"]}" stroke-width="1" opacity="0.5"/>')
    svg.append(f'  <text x="110" y="252" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="middle">ДНК - гены COL1A1/3</text>')
    
    svg.append(f'  <path d="M 200 208 L 200 168" fill="none" stroke="{colors["warn"]}" stroke-width="1.5" stroke-dasharray="3,2" marker-end="url(#arrow)"/>')
    svg.append(f'  <text x="210" y="190" font-family="{font}" font-size="8" fill="{colors["warn"]}">мРНК</text>')
    
    svg.append(f'  <path d="M 230 213 Q 250 198 270 213 T 310 213 T 350 213" fill="none" stroke="{colors["text"]}" stroke-width="2.5" opacity="0.5"/>')
    svg.append(f'  <path d="M 230 233 Q 250 248 270 233 T 310 233 T 350 233" fill="none" stroke="{colors["herbal"]}" stroke-width="2.5" opacity="0.5"/>')
    svg.append(f'  <text x="290" y="252" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="middle">Хроматин</text>')
    return "\n".join(svg)

def clean_label(text):

    if not text:
        return ""
    words = text.split()
    if len(words) > tokens["density"]["maxLabelWords"]:
        return " ".join(words[:tokens["density"]["maxLabelWords"]]) + "..."
    return text

def run_qa_check(filepath):
    qa_script = os.path.join(PROJECT_ROOT, "ops", "scripts", "qa_svg_bounds.js")
    res = subprocess.run(
        ["node", qa_script, filepath, "5"],
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        print(f"QA Bounds Check Failed for {os.path.basename(filepath)}:")
        print(res.stdout)
        print(res.stderr)
        return False
    return True

# 1. PROCESS FLOW GENERATOR
def make_process_flow(title, subtitle, steps, source_note, extra_drawing_func=None, width=400, height=300):
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    # Background
    svg.append(f'  <rect width="{width}" height="{height}" rx="16" fill="{colors["bg"]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    
    # Arrow Marker Defs
    svg.append('  <defs>')
    svg.append(f'    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append(f'      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{colors["dark"]}"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')
    
    # Title & Subtitle
    svg.append(f'  <text x="{width/2}" y="24" font-family="{font}" font-size="{font_sizes["title"]}" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">{xml_escape(title)}</text>')
    if subtitle:
        svg.append(f'  <text x="{width/2}" y="38" font-family="{font}" font-size="{font_sizes["label"]}" fill="{colors["herbal"]}" text-anchor="middle">{xml_escape(subtitle)}</text>')
        
    # Steps
    n = len(steps)
    available_w = width - 2 * padding
    h_gap = max(min_gap * 2, 30)
    box_w = (available_w - (n - 1) * h_gap) / n
    box_h = 50
    box_y = 60
    
    for i, step in enumerate(steps):
        x = padding + i * (box_w + h_gap)
        lbl = xml_escape(clean_label(step["label"]))
        sub = xml_escape(clean_label(step.get("sublabel", "")))
        
        rect_color = colors["bgAlt"] if i == 0 else (colors["sage"] if i == 1 else colors["bg"])
        stroke_color = colors["herbal"] if i < 2 else colors["dark"]
        
        svg.append(f'  <g transform="translate({x:.1f}, {box_y})">')
        svg.append(f'    <rect x="0" y="0" width="{box_w:.1f}" height="{box_h}" rx="6" fill="{rect_color}" stroke="{stroke_color}" stroke-width="1.5"/>')
        if sub:
            svg.append(f'    <text x="{box_w/2:.1f}" y="22" font-family="{font}" font-size="10" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">{lbl}</text>')
            svg.append(f'    <text x="{box_w/2:.1f}" y="36" font-family="{font}" font-size="8" fill="{colors["herbal"]}" text-anchor="middle">{sub}</text>')
        else:
            svg.append(f'    <text x="{box_w/2:.1f}" y="29" font-family="{font}" font-size="10" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">{lbl}</text>')
        svg.append('  </g>')
        
        if i < n - 1:
            arrow_start_x = x + box_w
            arrow_end_x = x + box_w + h_gap
            arrow_y = box_y + box_h / 2
            svg.append(f'  <path d="M {arrow_start_x:.1f} {arrow_y:.1f} L {arrow_end_x - 6:.1f} {arrow_y:.1f}" fill="none" stroke="{colors["dark"]}" stroke-width="2" marker-end="url(#arrow)"/>')
            
    if extra_drawing_func:
        svg.append(extra_drawing_func(box_w, h_gap))
        
    if source_note:
        svg.append(f'  <text x="{width/2}" y="{height - 12}" font-family="{font}" font-size="{font_sizes["sublabel"]}" fill="{colors["herbal"]}" text-anchor="middle">{xml_escape(source_note)}</text>')
        
    svg.append('</svg>')
    return "\n".join(svg)

# 2. LAYERED ANATOMY GENERATOR
def make_layered_anatomy(title, subtitle, layers, stages, source_note, width=450, height=300):
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append(f'  <rect width="{width}" height="{height}" rx="16" fill="{colors["bg"]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    
    # Title
    svg.append(f'  <text x="{width/2}" y="24" font-family="{font}" font-size="{font_sizes["title"]}" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">{xml_escape(title)}</text>')
    if subtitle:
        svg.append(f'  <text x="{width/2}" y="38" font-family="{font}" font-size="{font_sizes["label"]}" fill="{colors["herbal"]}" text-anchor="middle">{xml_escape(subtitle)}</text>')
        
    svg.append('  <defs>')
    svg.append(f'    <marker id="arrow-dark" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append(f'      <path d="M 0 2 L 8 5 L 0 8 z" fill="{colors["moleculeStroke"]}"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')
    
    # Left Layers (stacked)
    for layer in layers:
        y = layer["y"]
        h = layer["height"]
        fill_val = layer["fill"]
        stroke_val = layer["stroke"]
        opacity_val = layer.get("opacity", 1.0)
        svg.append(f'  <g transform="translate(20, {y})">')
        svg.append(f'    <rect x="0" y="0" width="185" height="{h}" rx="4" fill="{fill_val}" stroke="{stroke_val}" stroke-width="1" opacity="{opacity_val}"/>')
        
        # custom glyph drawings inside layers if specified
        if layer["name"] == "Corneocyte Layer":
            svg.append(f'    <path d="M 16 11 L 38 11 M 54 11 L 76 11 M 92 11 L 114 11 M 130 11 L 152 11 M 168 11 L 185 11" stroke="{colors["warn"]}" stroke-width="1.5"/>')
        elif layer["name"] == "Granular Layer":
            for cx in [22, 50, 78, 106, 134, 162]:
                svg.append(f'    <circle cx="{cx}" cy="17" r="7" fill="none" stroke="{colors["herbal"]}" stroke-width="1"/>')
                svg.append(f'    <circle cx="{cx}" cy="17" r="2" fill="{colors["herbal"]}"/>')
        elif layer["name"] == "Spinous Layer":
            for cx in [20, 60, 100, 140]:
                svg.append(f'    <circle cx="{cx}" cy="18" r="6" fill="{colors["border"]}"/>')
                svg.append(f'    <path d="M {cx-5} 18 L {cx+5} 18 M {cx} 13 L {cx} 23" stroke="{colors["herbal"]}" stroke-width="1"/>')
            for cx in [40, 80, 120]:
                svg.append(f'    <circle cx="{cx}" cy="36" r="6" fill="{colors["border"]}" stroke="{colors["herbal"]}" stroke-width="1"/>')
        elif layer["name"] == "Basal Layer":
            for cx in [25, 65, 105, 145]:
                svg.append(f'    <ellipse cx="{cx}" cy="14" rx="10" ry="8" fill="{colors["border"]}" stroke="{colors["moleculeStroke"]}" stroke-width="1"/>')
                
        svg.append('  </g>')
        
        # Label below layer bar
        svg.append(f'  <text x="22" y="{y + h + 11}" font-family="{font}" font-size="8" font-weight="bold" fill="{stroke_val}">{xml_escape(clean_label(layer["label"]))}</text>')
        
    # Right differentiation timeline
    svg.append(f'  <path d="M 250 252 L 250 62" fill="none" stroke="{colors["moleculeStroke"]}" stroke-width="2.5" stroke-dasharray="2,2" marker-end="url(#arrow-dark)"/>')
    
    for stage in stages:
        ty = stage["y"]
        lbl1 = xml_escape(clean_label(stage["title"]))
        lbl2 = xml_escape(clean_label(stage.get("sub", "")))
        is_badge = stage.get("is_badge", False)
        
        if is_badge:
            # y = 118, h = 24
            svg.append(f'  <rect x="264" y="118" width="80" height="24" rx="4" fill="{colors["bgAlt"]}" stroke="{colors["warn"]}" stroke-width="1"/>')
            svg.append(f'  <text x="304" y="134" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["warn"]}" text-anchor="middle">{lbl1}</text>')
        else:
            svg.append(f'  <text x="264" y="{ty}" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["moleculeStroke"]}">{lbl1}</text>')
            if lbl2:
                svg.append(f'  <text x="264" y="{ty+13}" font-family="{font}" font-size="8" fill="{colors["text"]}">{lbl2}</text>')
                
    if source_note:
        svg.append(f'  <text x="{width/2}" y="{height - 12}" font-family="{font}" font-size="{font_sizes["sublabel"]}" fill="{colors["herbal"]}" text-anchor="middle">{xml_escape(source_note)}</text>')
        
    svg.append('</svg>')
    return "\n".join(svg)

# 3. XY CURVE GENERATOR
def make_xy_curve(title, left_panel, right_panel, source_note, width=450, height=300):
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append(f'  <rect width="{width}" height="{height}" rx="16" fill="{colors["bg"]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    
    # Title
    svg.append(f'  <text x="{width/2}" y="24" font-family="{font}" font-size="{font_sizes["title"]}" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">{xml_escape(title)}</text>')
    
    # --- LEFT Panel ---
    # Optimum range box
    svg.append(f'  <rect x="71" y="80" width="67" height="149" fill="{colors["border"]}" opacity="0.4"/>')
    svg.append(f'  <line x1="70" y1="229" x2="200" y2="229" stroke="{colors["dark"]}" stroke-width="1.5"/>')
    svg.append(f'  <line x1="70" y1="79"  x2="70"  y2="229" stroke="{colors["dark"]}" stroke-width="1.5"/>')
    
    svg.append(f'  <text x="135" y="62" font-family="{font}" font-size="11" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">{xml_escape(left_panel["title"])}</text>')
    svg.append(f'  <text x="104" y="108" font-family="{font}" font-size="9" fill="{colors["herbal"]}" font-weight="bold" text-anchor="middle">Оптимум</text>')
    svg.append(f'  <text x="104" y="120" font-family="{font}" font-size="9" fill="{colors["herbal"]}" font-weight="bold" text-anchor="middle">(pH &lt; 3.5)</text>')
    
    # Left Curve path
    svg.append(f'  <path d="M 70 94 Q 100 105 138 145 T 200 227" fill="none" stroke="{colors["warn"]}" stroke-width="2.5"/>')
    
    # Y-axis marks
    svg.append(f'  <line x1="66" y1="94" x2="70" y2="94" stroke="{colors["dark"]}"/>')
    svg.append(f'  <text x="63" y="98" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="end">Max</text>')
    svg.append(f'  <line x1="66" y1="229" x2="70" y2="229" stroke="{colors["dark"]}"/>')
    svg.append(f'  <text x="63" y="233" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="end">Min</text>')
    
    # X-axis ticks
    for tick_x, label_x in [(70, "2.0"), (138, "3.5"), (200, "5.0")]:
        svg.append(f'  <line x1="{tick_x}" y1="229" x2="{tick_x}" y2="233" stroke="{colors["dark"]}"/>')
        svg.append(f'  <text x="{tick_x}" y="243" font-family="{font}" font-size="9" fill="{colors["text"]}" text-anchor="middle">{label_x}</text>')
        
    svg.append(f'  <text x="135" y="258" font-family="{font}" font-size="10" fill="{colors["dark"]}" text-anchor="middle">pH формулы</text>')
    
    # Divider
    svg.append(f'  <line x1="225" y1="55" x2="225" y2="270" stroke="{colors["border"]}" stroke-width="1" stroke-dasharray="4,4"/>')
    
    # --- RIGHT Panel ---
    svg.append(f'  <line x1="258" y1="229" x2="413" y2="229" stroke="{colors["dark"]}" stroke-width="1.5"/>')
    svg.append(f'  <line x1="258" y1="79"  x2="258" y2="229" stroke="{colors["dark"]}" stroke-width="1.5"/>')
    
    svg.append(f'  <text x="335" y="62" font-family="{font}" font-size="11" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">{xml_escape(right_panel["title"])}</text>')
    
    # peak dashed line
    svg.append(f'  <line x1="335" y1="79" x2="335" y2="229" stroke="{colors["herbal"]}" stroke-width="1.5" stroke-dasharray="3,3"/>')
    
    # Right Curve path
    svg.append(f'  <path d="M 258 227 Q 300 120 335 92 Q 370 122 413 170" fill="none" stroke="{colors["herbal"]}" stroke-width="2.5"/>')
    
    # Callout Box
    svg.append(f'  <rect x="348" y="70" width="60" height="26" fill="{colors["bgAlt"]}" rx="4" stroke="{colors["warn"]}" stroke-width="1"/>')
    svg.append(f'  <text x="378" y="80" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["warn"]}" text-anchor="middle">Пик @20%</text>')
    svg.append(f'  <text x="378" y="90" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="middle">макс абсорб</text>')
    svg.append(f'  <line x1="348" y1="83" x2="335" y2="92" stroke="{colors["warn"]}" stroke-width="1"/>')
    
    svg.append(f'  <text x="388" y="112" font-family="{font}" font-size="8" fill="{colors["warn"]}" text-anchor="middle">спад</text>')
    svg.append(f'  <text x="388" y="122" font-family="{font}" font-size="8" fill="{colors["warn"]}" text-anchor="middle">выше 20%</text>')
    svg.append(f'  <line x1="388" y1="127" x2="388" y2="142" stroke="{colors["warn"]}" stroke-width="1"/>')
    
    # Y-axis marks
    svg.append(f'  <line x1="254" y1="92" x2="258" y2="92" stroke="{colors["dark"]}"/>')
    svg.append(f'  <text x="252" y="96" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="end">Max</text>')
    svg.append(f'  <line x1="254" y1="229" x2="258" y2="229" stroke="{colors["dark"]}"/>')
    svg.append(f'  <text x="252" y="233" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="end">Min</text>')
    
    # X-axis ticks
    for tick_x, label_x in [(258, "0%"), (335, "20%"), (413, "40%")]:
        svg.append(f'  <line x1="{tick_x}" y1="229" x2="{tick_x}" y2="233" stroke="{colors["dark"]}"/>')
        svg.append(f'  <text x="{tick_x}" y="243" font-family="{font}" font-size="9" fill="{colors["text"]}" text-anchor="middle">{label_x}</text>')
        
    svg.append(f'  <text x="335" y="258" font-family="{font}" font-size="10" fill="{colors["dark"]}" text-anchor="middle">Концентрация L-AA</text>')
    
    if source_note:
        svg.append(f'  <text x="{width/2}" y="{height - 12}" font-family="{font}" font-size="{font_sizes["sublabel"]}" fill="{colors["herbal"]}" text-anchor="middle">{clean_label(source_note)}</text>')
        
    svg.append('</svg>')
    return "\n".join(svg)

# 4. BESPOKE MELANOSOME
def make_melanosome_transfer(title, subtitle, source_note, width=400, height=300):
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append(f'  <rect width="{width}" height="{height}" rx="16" fill="{colors["bg"]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    
    svg.append(f'  <text x="{width/2}" y="25" font-family="{font}" font-size="{font_sizes["title"]}" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">{xml_escape(title)}</text>')
    if subtitle:
        svg.append(f'  <text x="{width/2}" y="40" font-family="{font}" font-size="{font_sizes["label"]}" fill="{colors["herbal"]}" text-anchor="middle">{xml_escape(subtitle)}</text>')
        
    # Keratinocyte 1
    svg.append('  <g transform="translate(30, 55)">')
    svg.append(f'    <rect x="0" y="0" width="140" height="50" rx="4" fill="{colors["border"]}" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append(f'    <text x="70" y="22" font-family="{font}" font-size="11" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">Keratinocyte</text>')
    svg.append(f'    <text x="70" y="38" font-family="{font}" font-size="9" fill="{colors["text"]}" text-anchor="middle">Кератиноцит</text>')
    svg.append('  </g>')
    
    # Keratinocyte 2
    svg.append('  <g transform="translate(228, 55)">')
    svg.append(f'    <rect x="0" y="0" width="142" height="50" rx="4" fill="{colors["border"]}" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append(f'    <text x="71" y="22" font-family="{font}" font-size="11" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">Keratinocyte</text>')
    svg.append(f'    <text x="71" y="38" font-family="{font}" font-size="9" fill="{colors["text"]}" text-anchor="middle">Кератиноцит</text>')
    svg.append('  </g>')
    
    # Blocking Bar
    svg.append(f'  <rect x="20" y="128" width="360" height="18" rx="4" fill="{colors["bgAlt"]}" stroke="{colors["warn"]}" stroke-width="1.5"/>')
    svg.append(f'  <text x="200" y="141" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["warn"]}" text-anchor="middle">БЛОКАДА ПЕРЕНОСА МЕЛАНОСОМ</text>')
    
    # Blocked marks
    svg.append(f'  <text x="100" y="124" font-family="{font}" font-size="12" font-weight="bold" fill="{colors["warn"]}" text-anchor="middle">✕</text>')
    svg.append(f'  <text x="300" y="124" font-family="{font}" font-size="12" font-weight="bold" fill="{colors["warn"]}" text-anchor="middle">✕</text>')
    
    # Dendrites
    svg.append(f'  <path d="M 155 228 C 138 211, 105 192, 100 172" fill="none" stroke="{colors["dark"]}" stroke-width="3.5" stroke-linecap="round"/>')
    svg.append(f'  <path d="M 225 228 C 242 211, 275 192, 280 172" fill="none" stroke="{colors["dark"]}" stroke-width="3.5" stroke-linecap="round"/>')
    
    # Melanosomes
    for cx, cy in [(138, 209), (113, 189), (242, 209), (267, 189)]:
        svg.append(f'  <circle cx="{cx}" cy="{cy}" r="3.5" fill="{colors["moleculeStroke"]}"/>')
    for cx, cy in [(100, 174), (280, 174)]:
        svg.append(f'  <circle cx="{cx}" cy="{cy}" r="3" fill="{colors["moleculeStroke"]}"/>')
    for cx, cy in [(162, 250), (218, 250)]:
        svg.append(f'  <circle cx="{cx}" cy="{cy}" r="4" fill="{colors["moleculeStroke"]}"/>')
        
    # Melanocyte Body
    svg.append(f'  <ellipse cx="190" cy="245" rx="88" ry="36" fill="{colors["bg"]}" stroke="{colors["dark"]}" stroke-width="2"/>')
    svg.append(f'  <text x="190" y="241" font-family="{font}" font-size="12" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">Melanocyte</text>')
    svg.append(f'  <text x="190" y="256" font-family="{font}" font-size="9" fill="{colors["herbal"]}" text-anchor="middle">Меланоцит</text>')
    
    if source_note:
        svg.append(f'  <text x="{width/2}" y="{height - 12}" font-family="{font}" font-size="{font_sizes["sublabel"]}" fill="{colors["herbal"]}" text-anchor="middle">{xml_escape(source_note)}</text>')
        
    svg.append('</svg>')
    return "\n".join(svg)

# 5. BESPOKE DESMOSOME DESMOLYSIS
def make_desmosome_desmolysis(title, subtitle, source_note, width=400, height=300):
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append(f'  <rect width="{width}" height="{height}" rx="16" fill="{colors["bg"]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    
    svg.append('  <defs>')
    svg.append(f'    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append(f'      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{colors["dark"]}"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')
    
    svg.append(f'  <text x="{width/2}" y="25" font-family="{font}" font-size="{font_sizes["title"]}" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">{xml_escape(title)}</text>')
    
    # Left Section
    svg.append(f'  <text x="95" y="58" font-family="{font}" font-size="11" font-weight="bold" fill="{colors["dark"]}" text-anchor="middle">Плотный роговой слой</text>')
    svg.append(f'  <rect x="30" y="90" width="50" height="148" rx="4" fill="{colors["border"]}" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append(f'  <rect x="110" y="90" width="50" height="148" rx="4" fill="{colors["border"]}" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append(f'  <text x="55" y="86" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="middle">C-1</text>')
    svg.append(f'  <text x="135" y="86" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="middle">C-2</text>')
    
    # Bridges
    for by in [115, 155, 195]:
        svg.append(f'  <rect x="80" y="{by}" width="30" height="6" fill="{colors["bgAlt"]}" stroke="{colors["dark"]}" stroke-width="0.75"/>')
        
    svg.append(f'  <text x="95" y="252" font-family="{font}" font-size="9" fill="{colors["text"]}" text-anchor="middle">Десмосомы интактны</text>')
    
    # Middle Arrow
    svg.append(f'  <path d="M 178 165 L 213 165" fill="none" stroke="{colors["dark"]}" stroke-width="2" marker-end="url(#arrow)"/>')
    svg.append(f'  <text x="196" y="152" font-family="{font}" font-size="10" font-weight="bold" fill="{colors["herbal"]}" text-anchor="middle">BHA</text>')
    svg.append(f'  <text x="196" y="184" font-family="{font}" font-size="9" fill="{colors["text"]}" text-anchor="middle">Эксфолиация</text>')
    
    # Right Section
    svg.append(f'  <text x="305" y="58" font-family="{font}" font-size="11" font-weight="bold" fill="{colors["warn"]}" text-anchor="middle">Десмолиз и десквамация</text>')
    
    # Tilted Corneocytes
    svg.append('  <g transform="translate(220, 90) rotate(-2, 25, 74)">')
    svg.append(f'    <rect x="0" y="0" width="50" height="148" rx="4" fill="{colors["border"]}" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append('  </g>')
    svg.append('  <g transform="translate(320, 90) rotate(2, 25, 74)">')
    svg.append(f'    <rect x="0" y="0" width="50" height="148" rx="4" fill="{colors["border"]}" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append('  </g>')
    
    svg.append(f'  <text x="245" y="86" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="middle">C-1</text>')
    svg.append(f'  <text x="345" y="86" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="middle">C-2</text>')
    
    # Broken bridges
    for by in [118, 158, 198]:
        svg.append(f'  <line x1="270" y1="{by}" x2="282" y2="{by}" stroke="{colors["warn"]}" stroke-width="1.5" stroke-dasharray="2,2"/>')
        svg.append(f'  <line x1="300" y1="{by}" x2="312" y2="{by}" stroke="{colors["warn"]}" stroke-width="1.5" stroke-dasharray="2,2"/>')
        # BHA Star
        svg.append(f'  <polygon points="291,{by-6} 294,{by-2} 299,{by-2} 295,{by+1} 297,{by+6} 291,{by+3} 285,{by+6} 287,{by+1} 283,{by-2} 288,{by-2}" fill="{colors["warn"]}" stroke="{colors["dark"]}" stroke-width="0.5"/>')
        
    svg.append(f'  <text x="305" y="252" font-family="{font}" font-size="9" fill="{colors["warn"]}" font-weight="bold" text-anchor="middle">Связи разрушены BHA</text>')
    
    if source_note:
        svg.append(f'  <text x="{width/2}" y="{height - 12}" font-family="{font}" font-size="{font_sizes["sublabel"]}" fill="{colors["herbal"]}" text-anchor="middle">{xml_escape(source_note)}</text>')
        
    svg.append('</svg>')
    return "\n".join(svg)

# 6. BESPOKE RAR RXR
def make_rar_rxr_mechanism(title, subtitle, source_note, width=400, height=300):
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append(f'  <rect width="{width}" height="{height}" rx="16" fill="{colors["bg"]}" stroke="{colors["border"]}" stroke-width="1.5"/>')
    
    svg.append('  <defs>')
    svg.append(f'    <marker id="arrow-g" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append(f'      <path d="M 0 2 L 8 5 L 0 8 z" fill="{colors["herbal"]}"/>')
    svg.append('    </marker>')
    svg.append(f'    <marker id="arrow-d" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append(f'      <path d="M 0 2 L 8 5 L 0 8 z" fill="{colors["moleculeStroke"]}"/>')
    svg.append('    </marker>')
    svg.append('  </defs>')
    
    svg.append(f'  <text x="{width/2}" y="22" font-family="{font}" font-size="{font_sizes["title"]}" font-weight="bold" fill="{colors["moleculeStroke"]}" text-anchor="middle">{xml_escape(title)}</text>')
    if subtitle:
        svg.append(f'  <text x="{width/2}" y="37" font-family="{font}" font-size="{font_sizes["label"]}" fill="{colors["herbal"]}" text-anchor="middle">{xml_escape(subtitle)}</text>')
        
    # Nucleus outline
    svg.append(f'  <path d="M 90 290 C 90 118, 390 118, 390 290" fill="none" stroke="{colors["herbal"]}" stroke-width="1.5" stroke-dasharray="4,4"/>')
    svg.append(f'  <text x="335" y="82" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["herbal"]}" letter-spacing="0.1em" text-anchor="middle">ЯДРО / NUCLEUS</text>')
    svg.append(f'  <text x="48" y="80" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["herbal"]}" letter-spacing="0.1em">ЦИТОПЛАЗМА</text>')
    
    # Tretinoin (RA)
    svg.append(f'  <circle cx="55" cy="110" r="14" fill="{colors["herbal"]}" opacity="0.12"/>')
    svg.append(f'  <polygon points="49,109 55,103 61,109 57,117 53,117" fill="none" stroke="{colors["moleculeStroke"]}" stroke-width="2"/>')
    svg.append(f'  <circle cx="55" cy="110" r="3" fill="{colors["warn"]}"/>')
    svg.append(f'  <text x="75" y="115" font-family="{font}" font-size="11" font-weight="bold" fill="{colors["moleculeStroke"]}">RA (Tretinoin)</text>')
    
    # Entry Arrow
    svg.append(f'  <path d="M 125 130 L 168 158" fill="none" stroke="{colors["herbal"]}" stroke-width="2" marker-end="url(#arrow-g)"/>')
    
    # DNA left
    svg.append('  <g transform="translate(130, 240)">')
    svg.append(f'    <line x1="0" y1="0" x2="62" y2="0" stroke="{colors["text"]}" stroke-width="3"/>')
    svg.append(f'    <path d="M 6 -14 Q 22 12 38 -14 T 58 -14" fill="none" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append(f'    <path d="M 6 14  Q 22 -12 38 14  T 58 14"  fill="none" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append(f'    <line x1="20" y1="-7" x2="20" y2="7" stroke="{colors["text"]}" stroke-width="1"/>')
    svg.append(f'    <line x1="42" y1="-7" x2="42" y2="7" stroke="{colors["text"]}" stroke-width="1"/>')
    svg.append(f'    <line x1="58" y1="-7" x2="58" y2="7" stroke="{colors["text"]}" stroke-width="1"/>')
    svg.append('  </g>')
    
    # RARE Box
    svg.append(f'  <rect x="196" y="232" width="78" height="16" rx="3" fill="{colors["bgAlt"]}" stroke="{colors["warn"]}" stroke-width="1.2"/>')
    svg.append(f'  <text x="235" y="243" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["warn"]}" text-anchor="middle">RARE Element</text>')
    
    # DNA right
    svg.append('  <g transform="translate(278, 240)">')
    svg.append(f'    <line x1="0" y1="0" x2="90" y2="0" stroke="{colors["text"]}" stroke-width="3"/>')
    svg.append(f'    <path d="M 6 -14 Q 22 12 38 -14 T 68 -14 T 88 -14" fill="none" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append(f'    <path d="M 6 14  Q 22 -12 38 14  T 68 14  T 88 14"  fill="none" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append(f'    <line x1="22" y1="-7" x2="22" y2="7" stroke="{colors["text"]}" stroke-width="1"/>')
    svg.append(f'    <line x1="50" y1="-7" x2="50" y2="7" stroke="{colors["text"]}" stroke-width="1"/>')
    svg.append(f'    <line x1="76" y1="-7" x2="76" y2="7" stroke="{colors["text"]}" stroke-width="1"/>')
    svg.append('  </g>')
    
    # RXR / RAR box
    svg.append('  <g transform="translate(192, 178)">')
    svg.append(f'    <rect x="0" y="0" width="38" height="28" rx="7" fill="{colors["border"]}" stroke="{colors["herbal"]}" stroke-width="1.5"/>')
    svg.append(f'    <text x="19" y="18" font-family="{font}" font-size="10" font-weight="bold" fill="{colors["moleculeStroke"]}" text-anchor="middle">RXR</text>')
    svg.append('  </g>')
    svg.append('  <g transform="translate(234, 178)">')
    svg.append(f'    <rect x="0" y="0" width="38" height="28" rx="7" fill="{colors["herbal"]}" stroke="{colors["moleculeStroke"]}" stroke-width="1.5"/>')
    svg.append(f'    <text x="19" y="18" font-family="{font}" font-size="10" font-weight="bold" fill="{colors["bg"]}" text-anchor="middle">RAR</text>')
    svg.append('  </g>')
    
    # Ligand L
    svg.append('  <g transform="translate(277, 169)">')
    svg.append(f'    <circle cx="0" cy="0" r="10" fill="{colors["warn"]}" stroke="{colors["moleculeStroke"]}" stroke-width="1"/>')
    svg.append(f'    <text x="0" y="4" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["bg"]}" text-anchor="middle">L</text>')
    svg.append('  </g>')
    
    # Transcription Activation
    svg.append(f'  <path d="M 248 176 Q 280 142 312 130" fill="none" stroke="{colors["moleculeStroke"]}" stroke-width="2" stroke-dasharray="3,2" marker-end="url(#arrow-d)"/>')
    
    # Result Box
    svg.append('  <g transform="translate(298, 95)">')
    svg.append(f'    <rect x="0" y="0" width="82" height="32" rx="6" fill="{colors["border"]}" stroke="{colors["herbal"]}" stroke-width="1"/>')
    svg.append(f'    <text x="41" y="14" font-family="{font}" font-size="9" font-weight="bold" fill="{colors["moleculeStroke"]}" text-anchor="middle">ТРАНСКРИПЦИЯ</text>')
    svg.append(f'    <text x="41" y="26" font-family="{font}" font-size="8" fill="{colors["text"]}" text-anchor="middle">активация генов</text>')
    svg.append('  </g>')
    
    if source_note:
        svg.append(f'  <text x="{width/2}" y="{height - 12}" font-family="{font}" font-size="{font_sizes["sublabel"]}" fill="{colors["herbal"]}" text-anchor="middle">{xml_escape(source_note)}</text>')
        
    svg.append('</svg>')
    return "\n".join(svg)

# Main Generation Task List
DIAGRAMS = [
    {
        "filename": "ceramide_synthesis.svg",
        "type": "process_flow",
        "data": {
            "title": "Ниацинамид: Синтез церамидов",
            "subtitle": "Стимуляция липидов рогового слоя",
            "steps": [
                {"label": "Niacinamide", "sublabel": "Витамин B3"},
                {"label": "Синтез церамидов", "sublabel": "стимуляция барьера"},
                {"label": "Сфинголипиды", "sublabel": "& Церамиды"}
            ],
            "source_note": "Источник: fact_0024 - Tanno 2000, PMID 10971556",
            "extra_drawing_func": lambda bw, hg: ceramide_extra_drawing(padding, min_gap, colors, font, 400, 300)
        }
    },
    {
        "filename": "collagen_synthesis.svg",
        "type": "process_flow",
        "data": {
            "title": "Стимуляция коллагена I/III",
            "subtitle": "Витамин C усиливает мРНК",
            "steps": [
                {"label": "L-Ascorbate", "sublabel": "Витамин C"},
                {"label": "Экспрессия генов", "sublabel": "mRNA COL1A1/3"},
                {"label": "Коллаген I / III", "sublabel": "Тройная спираль"}
            ],
            "source_note": "Источник: fact_0030/46 - Pinnell 2001, PMID 11207686",
            "extra_drawing_func": lambda bw, hg: collagen_extra_drawing(padding, min_gap, colors, font, 400, 300)
        }
    },
    {
        "filename": "skin_layers_turnover.svg",
        "type": "layered_anatomy",
        "data": {
            "title": "СТРОЕНИЕ ЭПИДЕРМИСА & ТУРНОВЕР",
            "subtitle": "Дифференцировка кератиноцитов и цикл обновления",
            "layers": [
                {"name": "Corneocyte Layer", "label": "Роговой слой / Corneum", "y": 50, "height": 22, "fill": colors["bgAlt"], "stroke": colors["warn"], "opacity": 0.9},
                {"name": "Granular Layer", "label": "Зернистый / Granulosum", "y": 90, "height": 34, "fill": colors["border"], "stroke": colors["herbal"]},
                {"name": "Spinous Layer", "label": "Шиповатый / Spinosum", "y": 140, "height": 48, "fill": colors["bg"], "stroke": colors["herbal"]},
                {"name": "Basal Layer", "label": "Базальный / Basale", "y": 202, "height": 28, "fill": colors["herbal"], "stroke": colors["moleculeStroke"]}
            ],
            "stages": [
                {"title": "Слущивание / Desquamation", "sub": "Обновление эпидермиса", "y": 85},
                {"title": "Цикл ~26-28 дн.", "sub": "", "y": 118, "is_badge": True},
                {"title": "Миграция & Кератинизация", "sub": "Накопление кератина", "y": 179},
                {"title": "Деление базальных клеток", "sub": "Постоянный митоз", "y": 237}
            ],
            "source_note": "Источник: fact_0048 - Kanitakis 2002 (структура эпидермиса)"
        }
    },
    {
        "filename": "ascorbic_acid_absorption.svg",
        "type": "xy_curve",
        "data": {
            "title": "Чрескожное всасывание L-AA",
            "left_panel": {"title": "Зависимость от pH"},
            "right_panel": {"title": "Зависимость от конц."},
            "source_note": "Источник: Pinnell et al., 2001 (PMID 11207686)"
        }
    },
    {
        "filename": "melanosome_transfer.svg",
        "type": "melanosome",
        "data": {
            "title": "Подавление переноса меланосом",
            "subtitle": "Ниацинамид блокирует перенос в кератиноциты",
            "source_note": "Источник: fact_0034 - Hakozaki 2002, PMID 12100180"
        }
    },
    {
        "filename": "desmosome_desmolysis.svg",
        "type": "desmolysis",
        "data": {
            "title": "Салициловая кислота: Механизм десмолиза",
            "subtitle": "",
            "source_note": "BHA-индуцированное разрушение десмосомных связей"
        }
    },
    {
        "filename": "rar_rxr_mechanism.svg",
        "type": "rar_rxr",
        "data": {
            "title": "МЕХАНИЗМ RAR / RXR RECEPTORS",
            "subtitle": "Связывание ретиноевой кислоты с рецепторами ядра",
            "source_note": "Источник: fact_0001/02 - PMID 15773538 (Kang 2005)"
        }
    }
]

def main():
    target_dir = os.path.join(PROJECT_ROOT, "04_design_system", "assets", "mechanisms")
    os.makedirs(target_dir, exist_ok=True)
    
    has_errors = False
    for diag in DIAGRAMS:
        fname = diag["filename"]
        dtype = diag["type"]
        data = diag["data"]
        out_path = os.path.join(target_dir, fname)
        print(f"Generating diagram {fname} ({dtype})...")
        
        if dtype == "process_flow":
            content = make_process_flow(data["title"], data.get("subtitle"), data["steps"], data.get("source_note"), data.get("extra_drawing_func"))
        elif dtype == "layered_anatomy":
            content = make_layered_anatomy(data["title"], data.get("subtitle"), data["layers"], data["stages"], data.get("source_note"))
        elif dtype == "xy_curve":
            content = make_xy_curve(data["title"], data["left_panel"], data["right_panel"], data.get("source_note"))
        elif dtype == "melanosome":
            content = make_melanosome_transfer(data["title"], data.get("subtitle"), data.get("source_note"))
        elif dtype == "desmolysis":
            content = make_desmosome_desmolysis(data["title"], data.get("subtitle"), data.get("source_note"))
        elif dtype == "rar_rxr":
            content = make_rar_rxr_mechanism(data["title"], data.get("subtitle"), data.get("source_note"))
        else:
            print(f"Error: Unknown diagram type {dtype}")
            sys.exit(1)
            
        with open(out_path, "w", encoding="utf-8") as f_out:
            f_out.write(content)
            
        if not run_qa_check(out_path):
            has_errors = True
            
    if has_errors:
        print("\nFail: One or more generated diagrams did not pass bounds QA check!")
        sys.exit(1)
    else:
        print("\nSuccess: All diagrams generated programmatically and passed bounds QA check!")
        sys.exit(0)

if __name__ == "__main__":
    main()
