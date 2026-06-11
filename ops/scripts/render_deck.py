import os
import json
import glob
import argparse

def main():
    parser = argparse.ArgumentParser(description="Render HTML deck from json specs")
    parser.add_argument("--deck", type=str, default="deck_retinoids_v2", help="Name of the deck directory and files prefix")
    args = parser.parse_args()
    
    deck_name = args.deck
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    tokens_path = os.path.join(project_root, "04_design_system", "design-tokens.json")
    specs_dir = os.path.join(project_root, "05_content", "specs", deck_name)
    out_dir = os.path.join(project_root, "06_render", "out")
    os.makedirs(out_dir, exist_ok=True)
    
    with open(tokens_path, "r", encoding="utf-8") as f:
        tokens = json.load(f)
        
    color = tokens["color"]
    font = tokens["font"]
    radius = tokens["radius"]
    type_scale = tokens["type"]
    
    # Read all slide specs in order
    # Load asset provenance registry
    registry_path = os.path.join(project_root, "04_design_system", "assets", "asset_provenance.json")
    registry = {}
    if os.path.exists(registry_path):
        try:
            with open(registry_path, "r", encoding="utf-8") as rf:
                registry = json.load(rf)
        except Exception as e:
            print(f"Warning: Failed to load asset registry: {e}")

    # ── Brand-layer: load logo SVG assets inline ───────────────────────────────
    logo_dir = os.path.join(project_root, "04_design_system", "assets", "logo")

    def load_svg(variant):
        """Return SVG file content as string, or empty string on failure."""
        svg_path = os.path.join(logo_dir, f"ym_proskin_{variant}.svg")
        try:
            with open(svg_path, "r", encoding="utf-8") as _f:
                return _f.read().strip()
        except Exception as _e:
            print(f"Warning: Could not load logo SVG '{variant}': {_e}")
            return ""

    svg_mark       = load_svg("mark")
    svg_horizontal = load_svg("horizontal")
    svg_descriptor = load_svg("descriptor")
    svg_badge      = load_svg("badge")

    def set_svg_color(svg_str, color):
        """Inject color attribute on the root <svg> element (used by currentColor)."""
        import re as _re
        return _re.sub(r'(<svg[^>]*?)\s*color="[^"]*"', rf'\1 color="{color}"', svg_str, count=1)

    # Slide canvas: 1024 x 576 px
    # Footer zone: bottom 46 px (0.08 * 576 ≈ 46)
    CANVAS_W, CANVAS_H = 1024, 576
    FOOTER_H = 46  # reserved brand-chrome strip
    # ──────────────────────────────────────────────────────────────────────────

    spec_files = sorted(glob.glob(os.path.join(specs_dir, f"{deck_name}-s*.json")))
    total_slides = len(spec_files)
    slides_html = []
    
    for slide_idx, sf in enumerate(spec_files):
        with open(sf, "r", encoding="utf-8") as f:
            slide = json.load(f)

        slide_num   = slide_idx + 1
        is_closing  = (slide_idx == total_slides - 1)
        is_cover    = (slide_idx == 0)

        layout = slide.get("layout", "summary")
        title = slide.get("title", "")
        subtitle = slide.get("subtitle", "")
        body = slide.get("body", [])
        media = slide.get("media", {})
        components = slide.get("components", {})
        disclaimers = list(slide.get("disclaimers", []))
        source_refs = slide.get("source_refs", [])
        
        # Resolve media asset and attribution
        asset_name = media.get("asset", "")
        attribution = ""
        is_real_image = False
        img_src = ""
        media_fit = media.get("fit", "contain")
        media_caption = media.get("caption", "")
        
        if asset_name:
            asset_data = registry.get(asset_name) or {}
            # Fallback check stripping extension
            if not asset_data:
                base_name = os.path.splitext(asset_name)[0]
                asset_data = registry.get(base_name) or {}
                
            attribution = asset_data.get("attribution", "")
            rel_path = asset_data.get("path", "")
            
            if rel_path:
                abs_path = os.path.join(project_root, rel_path)
                if os.path.exists(abs_path):
                    is_real_image = True
                    # Path relative to output folder 06_render/out/
                    img_src = "../../" + rel_path
                    
        # Append CC-BY attribution to disclaimers if present
        if attribution:
            disclaimers.append(attribution)
            
        # Build disclaimers section
        disc_html = ""
        if disclaimers:
            disc_html = f'<div class="disclaimers">{" | ".join(disclaimers)}</div>'

        # Build source refs section
        sources_html = ""
        if source_refs:
            sources_html = f'<div class="sources-ref">Источники: {", ".join(source_refs)}</div>'

        # ── Brand-layer footer chrome (all slides except cover and section_divider) ──
        if layout in ("cover", "section_divider"):
            brand_footer_html = ""
        else:
            _mark_color = "#6D8470" # herbal for Warm White background
            _mark_svg   = set_svg_color(svg_mark, _mark_color)
            import re as _re
            _mark_svg_clean = _re.sub(r'\s*(width|height)="[^"]*"', '', _mark_svg)
            brand_footer_html = f'''
            <div class="slide-footer" data-brand-footer="1">
                <div class="footer-logo" style="color:{_mark_color}">{_mark_svg_clean}</div>
                <span class="footer-wordmark">YM PROSKIN</span>
                <span class="footer-slide-num">{slide_num}</span>
            </div>
            '''

        # ── Cover: descriptor lockup (0.34 W = ~348px @ 1024) ──────────────────
        _desc_svg = set_svg_color(svg_descriptor, "#2C3440")  # bg-alt (#E6D2CA) → dark
        cover_logo_html = f'''
        <div class="cover-logo" style="color:#2C3440">{_desc_svg}</div>
        '''

        # ── Section divider: horizontal lockup (0.22 W = ~225px @ 1024) ────────
        _horiz_svg = set_svg_color(svg_horizontal, "#2C3440")  # Soft Beige bg → dark
        section_logo_html = f'''
        <div class="section-logo" style="color:#2C3440">{_horiz_svg}</div>
        '''

        # ── Closing slide: badge (0.18 W = ~184px @ 1024, centred) ─────────────
        _badge_svg = set_svg_color(svg_badge, "#2C3440")  # warm white bg → dark
        closing_logo_html = f'''
        <div class="closing-badge" style="color:#2C3440">{_badge_svg}</div>
        ''' if is_closing else ""
        # ───────────────────────────────────────────────────────────────────────
            
        # Build media block HTML
        media_html = ""
        if asset_name:
            if is_real_image:
                media_html = f"""
                <div class="media-box image-media" style="background: transparent; border: none; padding: 0; display: flex; align-items: center; justify-content: center; height: 100%; width: 100%;">
                    <img src="{img_src}" alt="{media_caption}" style="max-width: 100%; max-height: 100%; object-fit: {media_fit};" />
                </div>
                """
            else:
                display_caption = media_caption
                if "placeholder" in asset_name.lower() and not display_caption.startswith("[Placeholder]"):
                    display_caption = f"[Placeholder] {display_caption}"
                media_html = f"""
                <div class="media-box placeholder-media">
                    <span class="media-caption">{display_caption}</span>
                </div>
                """
                
        slide_content = ""
        
        if layout == "cover":
            slide_content = f"""
            <div class="slide cover-layout">
                <div class="header-group">
                    <span class="category-tag">{slide.get('section', '')}</span>
                    <h1 class="display-title">{title}</h1>
                    <p class="subtitle-text">{subtitle}</p>
                    {cover_logo_html}
                </div>
                <div class="cover-media">
                    {media_html}
                </div>
                {disc_html}
            </div>
            """

        elif layout == "section_divider":
            slide_content = f"""
            <div class="slide section-divider-layout">
                {section_logo_html}
                <span class="category-tag">{slide.get('section', '')}</span>
                <h1 class="divider-title">{title}</h1>
                <p class="divider-subtitle">{subtitle}</p>
                {disc_html}
            </div>
            """
            
        elif layout == "quote_callout":
            quote_text = ""
            for item in body:
                if item.get("type") == "quote":
                    quote_text = item.get("text", "")
            slide_content = f"""
            <div class="slide quote-layout">
                <div class="slide-header">
                    <h2 class="slide-title">{title}</h2>
                    <p class="slide-subtitle">{subtitle}</p>
                </div>
                <div class="quote-container">
                    <span class="quote-mark">“</span>
                    <p class="quote-text">{quote_text}</p>
                </div>
                {sources_html}
                {disc_html}
                {brand_footer_html}
            </div>
            """
            
        elif layout == "two_columns_image":
            bullets = ""
            for item in body:
                if item.get("type") == "bullet":
                    bullets += f'<li>{item.get("text", "")}</li>'
            slide_content = f"""
            <div class="slide two-columns-layout">
                <div class="slide-header">
                    <h2 class="slide-title">{title}</h2>
                    <p class="slide-subtitle">{subtitle}</p>
                </div>
                <div class="columns-grid">
                    <div class="column-left">
                        <ul class="bullets-list">
                            {bullets}
                        </ul>
                    </div>
                    <div class="column-right">
                        {media_html}
                    </div>
                </div>
                {sources_html}
                {disc_html}
                {brand_footer_html}
            </div>
            """
            
        elif layout == "three_cards":
            cards = ""
            for item in body:
                if item.get("type") == "card":
                    cards += f"""
                    <div class="card">
                        <h3 class="card-title">{item.get('title', '')}</h3>
                        <p class="card-text">{item.get('text', '')}</p>
                    </div>
                    """
            slide_content = f"""
            <div class="slide three-cards-layout">
                <div class="slide-header">
                    <h2 class="slide-title">{title}</h2>
                    <p class="slide-subtitle">{subtitle}</p>
                </div>
                <div class="cards-grid">
                    {cards}
                </div>
                {sources_html}
                {disc_html}
                {brand_footer_html}
            </div>
            """
            
        elif layout == "timeline_protocol":
            steps_html = ""
            step_idx = 0
            for item in body:
                if item.get("type") == "step":
                    step_idx += 1
                    steps_html += f"""
                    <div class="timeline-step">
                        <div class="step-num">{step_idx}</div>
                        <h3 class="step-label">{item.get('label', '')}</h3>
                        <p class="step-desc">{item.get('desc', '')}</p>
                    </div>
                    """
            slide_content = f"""
            <div class="slide timeline-layout">
                <div class="slide-header">
                    <h2 class="slide-title">{title}</h2>
                    <p class="slide-subtitle">{subtitle}</p>
                </div>
                <div class="timeline-container">
                    {steps_html}
                </div>
                {sources_html}
                {disc_html}
                {brand_footer_html}
            </div>
            """
            
        elif layout == "comparison":
            left_label, left_text = "", ""
            right_label, right_text = "", ""
            for item in body:
                if item.get("type") == "compare_left":
                    left_label = item.get("label", "")
                    left_text = item.get("text", "")
                elif item.get("type") == "compare_right":
                    right_label = item.get("label", "")
                    right_text = item.get("text", "")
            slide_content = f"""
            <div class="slide comparison-layout">
                <div class="slide-header">
                    <h2 class="slide-title">{title}</h2>
                    <p class="slide-subtitle">{subtitle}</p>
                </div>
                <div class="comparison-grid">
                    <div class="compare-card compare-left">
                        <span class="compare-label">{left_label}</span>
                        <p class="compare-text">{left_text}</p>
                    </div>
                    <div class="compare-card compare-right">
                        <span class="compare-label">{right_label}</span>
                        <p class="compare-text">{right_text}</p>
                    </div>
                </div>
                {sources_html}
                {disc_html}
                {brand_footer_html}
            </div>
            """
            
        elif layout == "statistics":
            stats_html = ""
            for item in body:
                if item.get("type") == "stat_item":
                    stats_html += f"""
                    <div class="stat-card">
                        <span class="stat-number">{item.get('number', '')}</span>
                        <h3 class="stat-label">{item.get('label', '')}</h3>
                        <p class="stat-desc">{item.get('desc', '')}</p>
                    </div>
                    """
            slide_content = f"""
            <div class="slide statistics-layout">
                <div class="slide-header">
                    <h2 class="slide-title">{title}</h2>
                    <p class="slide-subtitle">{subtitle}</p>
                </div>
                <div class="stats-grid">
                    {stats_html}
                </div>
                {sources_html}
                {disc_html}
                {brand_footer_html}
            </div>
            """
            
        elif layout == "contraindication_alert":
            alert = components.get("alert", {})
            alert_title = alert.get("title", "Противопоказание")
            alert_text = alert.get("text", "")
            slide_content = f"""
            <div class="slide alert-layout">
                <div class="slide-header">
                    <h2 class="slide-title">{title}</h2>
                    <p class="slide-subtitle">{subtitle}</p>
                </div>
                <div class="alert-box">
                    <div class="alert-icon">⚠️</div>
                    <div class="alert-content">
                        <h3 class="alert-box-title">{alert_title}</h3>
                        <p class="alert-box-text">{alert_text}</p>
                    </div>
                </div>
                {sources_html}
                {disc_html}
                {brand_footer_html}
            </div>
            """
            
        elif layout == "summary":
            bullets = ""
            for item in body:
                if item.get("type") == "bullet":
                    bullets += f'<li>{item.get("text", "")}</li>'
            slide_content = f"""
            <div class="slide summary-layout">
                <div class="slide-header">
                    <h2 class="slide-title">{title}</h2>
                    <p class="slide-subtitle">{subtitle}</p>
                </div>
                <div class="summary-box">
                    <ul class="bullets-list summary-list">
                        {bullets}
                    </ul>
                </div>
                {closing_logo_html}
                {sources_html}
                {disc_html}
                {brand_footer_html}
            </div>
            """
            
        slides_html.append(slide_content.strip())
        
    # Full HTML wrapper with styles derived from design-tokens.json
    html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>YM PROSKIN — {deck_name}</title>
    <style>
        @font-face {{
            font-family: '{font["family"]}';
            font-style: normal;
            font-weight: 100 900;
            src: url('../../04_design_system/fonts/Arimo[wght].ttf') format('truetype');
        }}
        @import url('https://fonts.googleapis.com/css2?family={font["family"].replace(" ", "+")}:wght@400;500;700&display=swap');
        
        :root {{
            --bg: {color["bg"]};
            --bg-alt: {color["bgAlt"]};
            --sage: {color["sage"]};
            --herbal: {color["herbal"]};
            --dark: {color["dark"]};
            --text: {color["text"]};
            --border: {color["border"]};
            --warn: {color["warn"]};
            
            --font-family: '{font["family"]}', sans-serif;
            --lh-min: {font["lineHeightMin"]};
            
            --radius-btn: {radius["btn"]}px;
            --radius-card: {radius["card"]}px;
            --radius-badge: {radius["badge"]}px;
            
            --fs-display: {type_scale["display"]}px;
            --fs-h1: {type_scale["h1"]}px;
            --fs-h2: {type_scale["h2"]}px;
            --fs-h3: {type_scale["h3"]}px;
            --fs-label: {type_scale["label"]}px;
            --fs-body: {type_scale["body"]}px;
            --fs-body-sm: {type_scale["bodySm"]}px;
            --fs-caption: {type_scale["caption"]}px;
        }}
        
        body {{
            margin: 0;
            padding: 0;
            background-color: var(--dark);
            font-family: var(--font-family);
            color: var(--text);
            line-height: var(--lh-min);
            box-sizing: border-box;
        }}
        
        .slide {{
            width: 1024px;
            height: 576px;
            background-color: var(--bg);
            position: relative;
            box-sizing: border-box;
            padding: 40px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            margin-bottom: 20px; /* spacing in HTML view */
        }}
        
        @media print {{
            body {{
                background-color: transparent;
            }}
            .slide {{
                margin-bottom: 0;
                page-break-after: always;
                page-break-inside: avoid;
            }}
        }}
        
        /* Typography Elements */
        .slide-header {{
            margin-bottom: 24px;
        }}
        
        .slide-title {{
            font-size: var(--fs-h2);
            font-weight: 700;
            color: var(--dark);
            margin: 0 0 8px 0;
            letter-spacing: -0.01em;
        }}
        
        .slide-subtitle {{
            font-size: var(--fs-body);
            color: var(--herbal);
            margin: 0;
            font-weight: 500;
        }}
        
        /* Bullets */
        .bullets-list {{
            margin: 0;
            padding-left: 20px;
            font-size: var(--fs-body);
        }}
        
        .bullets-list li {{
            margin-bottom: 12px;
            color: var(--text);
        }}
        
        /* ── Brand-layer footer chrome ─────────────────────────────────────── */
        .slide-footer {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 46px;          /* 0.08 × 576 reserved band */
            display: flex;
            align-items: center;
            padding: 0 24px;
            border-top: 1px solid var(--sage);
            background-color: transparent;
            box-sizing: border-box;
            z-index: 10;
        }}
        .footer-logo {{
            display: flex;
            align-items: center;
            height: 24px;          /* ≈ 0.034 × 576 × 1.2 — mark height */
            width: 24px;
            flex-shrink: 0;
        }}
        .footer-logo svg {{
            height: 100%;
            width: auto;
        }}
        .footer-wordmark {{
            font-family: var(--font-family);
            font-size: var(--fs-caption);
            font-weight: 700;
            color: {color["text"]};
            letter-spacing: {font["labelTrackEm"]}em;
            text-transform: uppercase;
            margin-left: 8px;
            flex: 1;
        }}
        .footer-slide-num {{
            font-family: var(--font-family);
            font-size: var(--fs-caption);
            color: {color["herbal"]};
            font-weight: 500;
        }}

        /* ── Cover logo (descriptor) ──────────────────────────────────────── */
        .cover-logo {{
            width: 348px;          /* 0.34 × 1024 */
            max-width: 100%;
            margin-top: 16px;
        }}
        .cover-logo svg {{
            width: 100%;
            height: auto;
        }}

        /* ── Section divider logo (horizontal) ───────────────────────────── */
        .section-logo {{
            width: 225px;          /* 0.22 × 1024 */
            margin-bottom: 12px;
        }}
        .section-logo svg {{
            width: 100%;
            height: auto;
        }}

        /* ── Closing slide badge ──────────────────────────────────────────── */
        .closing-badge {{
            width: 184px;          /* 0.18 × 1024 */
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -58%);
        }}
        .closing-badge svg {{
            width: 100%;
            height: auto;
        }}

        /* Footer Metadata — live inside footer or just above it */
        .disclaimers {{
            position: absolute;
            bottom: 50px;          /* above footer strip */
            left: 40px;
            font-size: var(--fs-caption);
            color: var(--herbal);
            text-transform: uppercase;
            letter-spacing: {font["labelTrackEm"]}em;
            font-weight: 700;
        }}

        .sources-ref {{
            position: absolute;
            bottom: 50px;          /* above footer strip */
            right: 40px;
            font-size: var(--fs-caption);
            color: var(--text);
            font-weight: 500;
        }}
        
        /* Media box */
        .media-box {{
            background-color: var(--sage);
            border-radius: var(--radius-card);
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            width: 100%;
            box-sizing: border-box;
            color: var(--herbal);
            font-size: var(--fs-body-sm);
            font-weight: 500;
            padding: 20px;
            text-align: center;
        }}
        
        /* Layout specific styles */
        
        /* 1. Cover */
        .cover-layout {{
            background-color: var(--bg-alt);
            display: grid;
            grid-template-columns: 1fr 1fr;
            align-items: center;
            gap: 40px;
        }}
        
        .cover-layout .header-group {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .category-tag {{
            font-size: var(--fs-label);
            font-weight: 700;
            color: var(--herbal);
            text-transform: uppercase;
            letter-spacing: {font["labelTrackEm"]}em;
            margin-bottom: 12px;
        }}
        
        .display-title {{
            font-size: var(--fs-h1);
            font-weight: 700;
            color: var(--dark);
            margin: 0 0 16px 0;
            line-height: 1.2;
        }}
        
        .cover-layout .subtitle-text {{
            font-size: var(--fs-body);
            color: var(--text);
            margin: 0;
        }}
        
        .cover-media {{
            height: 320px;
        }}
        
        /* 2. Section Divider */
        .section-divider-layout {{
            background-color: var(--bg-alt);
            padding: 80px 40px;
            justify-content: center;
        }}
        
        .divider-title {{
            font-size: var(--fs-display);
            font-weight: 700;
            color: var(--dark);
            margin: 24px 0 16px 0;
            line-height: 1.1;
        }}
        
        .divider-subtitle {{
            font-size: var(--fs-h3);
            color: var(--text);
            margin: 0;
            font-weight: 500;
        }}
        
        /* 3. Quote Callout */
        .quote-layout .quote-container {{
            margin-top: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 0 40px;
        }}
        
        .quote-mark {{
            font-size: 80px;
            color: var(--sage);
            line-height: 0.1;
            font-family: serif;
        }}
        
        .quote-text {{
            font-size: var(--fs-h3);
            font-style: italic;
            color: var(--dark);
            margin: 0;
            font-weight: 500;
        }}
        
        /* 4. Two columns */
        .two-columns-layout .columns-grid {{
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 40px;
            height: 300px;
        }}
        
        /* 5. Three cards */
        .three-cards-layout .cards-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            height: 300px;
        }}
        
        .three-cards-layout .card {{
            background-color: var(--bg-alt);
            border-radius: var(--radius-card);
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            border: 1px solid var(--border);
        }}
        
        .card-title {{
            font-size: var(--fs-h3);
            color: var(--dark);
            margin: 0 0 12px 0;
            font-weight: 700;
        }}
        
        .card-text {{
            font-size: var(--fs-body-sm);
            color: var(--text);
            margin: 0;
        }}
        
        /* 6. Timeline Protocol */
        .timeline-layout .timeline-container {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 20px;
            height: 300px;
        }}
        
        .timeline-step {{
            background-color: var(--bg-alt);
            border-radius: var(--radius-card);
            padding: 20px;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            box-sizing: border-box;
        }}
        
        .step-num {{
            font-size: var(--fs-caption);
            background-color: var(--herbal);
            color: var(--bg);
            border-radius: var(--radius-badge);
            padding: 4px 10px;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        
        .step-label {{
            font-size: var(--fs-body);
            font-weight: 700;
            color: var(--dark);
            margin: 0 0 8px 0;
        }}
        
        .step-desc {{
            font-size: var(--fs-caption);
            color: var(--text);
            margin: 0;
        }}
        
        /* 7. Comparison */
        .comparison-layout .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            height: 300px;
        }}
        
        .compare-card {{
            background-color: var(--bg-alt);
            border-radius: var(--radius-card);
            padding: 32px;
            border: 1px solid var(--border);
            box-sizing: border-box;
        }}
        
        .compare-label {{
            font-size: var(--fs-h3);
            font-weight: 700;
            color: var(--herbal);
            display: block;
            margin-bottom: 16px;
        }}
        
        .compare-text {{
            font-size: var(--fs-body);
            color: var(--text);
            margin: 0;
        }}
        
        /* 8. Statistics */
        .statistics-layout .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            height: 300px;
        }}
        
        .stat-card {{
            background-color: var(--bg-alt);
            border-radius: var(--radius-card);
            padding: 24px;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            box-sizing: border-box;
        }}
        
        .stat-number {{
            font-size: var(--fs-display);
            font-weight: 700;
            color: var(--herbal);
            line-height: 1;
            margin-bottom: 12px;
        }}
        
        .stat-label {{
            font-size: var(--fs-h3);
            font-weight: 700;
            color: var(--dark);
            margin: 0 0 8px 0;
        }}
        
        .stat-desc {{
            font-size: var(--fs-body-sm);
            color: var(--text);
            margin: 0;
        }}
        
        /* 9. Alert */
        .alert-layout .alert-box {{
            background-color: var(--bg-alt);
            border: 2px solid var(--warn);
            border-radius: var(--radius-card);
            padding: 32px;
            display: flex;
            align-items: center;
            gap: 24px;
            margin-top: 40px;
        }}
        
        .alert-icon {{
            font-size: 48px;
        }}
        
        .alert-content {{
            display: flex;
            flex-direction: column;
        }}
        
        .alert-box-title {{
            font-size: var(--fs-h3);
            color: var(--warn);
            margin: 0 0 8px 0;
            font-weight: 700;
        }}
        
        .alert-box-text {{
            font-size: var(--fs-body);
            color: var(--text);
            margin: 0;
            font-weight: 500;
        }}
        
        /* 10. Summary */
        .summary-layout .summary-box {{
            background-color: var(--bg-alt);
            border-radius: var(--radius-card);
            padding: 32px;
            height: 300px;
            box-sizing: border-box;
            border: 1px solid var(--border);
        }}
        
        .summary-list li {{
            margin-bottom: 16px;
        }}
        
    </style>
</head>
<body>
    {"".join(slides_html)}
</body>
</html>
"""
    
    out_html_path = os.path.join(out_dir, f"{deck_name}.html")
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"HTML presentation written successfully to {out_html_path}")

if __name__ == "__main__":
    main()
