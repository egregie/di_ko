import os
import json
import glob

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    tokens_path = os.path.join(project_root, "04_design_system", "design-tokens.json")
    specs_dir = os.path.join(project_root, "05_content", "specs", "deck_retinoids")
    out_dir = os.path.join(project_root, "06_render", "out")
    os.makedirs(out_dir, exist_ok=True)
    
    with open(tokens_path, "r", encoding="utf-8") as f:
        tokens = json.load(f)
        
    color = tokens["color"]
    font = tokens["font"]
    radius = tokens["radius"]
    type_scale = tokens["type"]
    
    # Read all slide specs in order
    spec_files = sorted(glob.glob(os.path.join(specs_dir, "deck_retinoids-s*.json")))
    slides_html = []
    
    for sf in spec_files:
        with open(sf, "r", encoding="utf-8") as f:
            slide = json.load(f)
            
        layout = slide.get("layout", "summary")
        title = slide.get("title", "")
        subtitle = slide.get("subtitle", "")
        body = slide.get("body", [])
        media = slide.get("media", {})
        components = slide.get("components", {})
        disclaimers = slide.get("disclaimers", [])
        source_refs = slide.get("source_refs", [])
        
        # Build disclaimers section
        disc_html = ""
        if disclaimers:
            disc_html = f'<div class="disclaimers">{" | ".join(disclaimers)}</div>'
            
        # Build source refs section
        sources_html = ""
        if source_refs:
            sources_html = f'<div class="sources-ref">Источники: {", ".join(source_refs)}</div>'
            
        slide_content = ""
        
        if layout == "cover":
            slide_content = f"""
            <div class="slide cover-layout">
                <div class="header-group">
                    <span class="category-tag">{slide.get('section', '')}</span>
                    <h1 class="display-title">{title}</h1>
                    <p class="subtitle-text">{subtitle}</p>
                </div>
                <div class="cover-media">
                    <div class="media-box placeholder-media">
                        <span class="media-caption">{media.get('caption', '')}</span>
                    </div>
                </div>
                {disc_html}
            </div>
            """
            
        elif layout == "quote":
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
                        <div class="media-box placeholder-media">
                            <span class="media-caption">{media.get('caption', '')}</span>
                        </div>
                    </div>
                </div>
                {sources_html}
                {disc_html}
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
                {sources_html}
                {disc_html}
            </div>
            """
            
        slides_html.append(slide_content.strip())
        
    # Full HTML wrapper with styles derived from design-tokens.json
    html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>YM PROSKIN — Ретиноиды</title>
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
        
        /* Footer Metadata */
        .disclaimers {{
            position: absolute;
            bottom: 20px;
            left: 40px;
            font-size: var(--fs-caption);
            color: var(--herbal);
            text-transform: uppercase;
            letter-spacing: {font["labelTrackEm"]}em;
            font-weight: 700;
        }}
        
        .sources-ref {{
            position: absolute;
            bottom: 20px;
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
        
        /* 2. Quote */
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
        
        /* 3. Two columns */
        .two-columns-layout .columns-grid {{
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 40px;
            height: 300px;
        }}
        
        /* 4. Three cards */
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
        
        /* 5. Alert */
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
        
        /* 6. Summary */
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
    
    out_html_path = os.path.join(out_dir, "deck_retinoids.html")
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"HTML presentation written successfully to {out_html_path}")

if __name__ == "__main__":
    main()
