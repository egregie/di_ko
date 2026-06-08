# YM PROSKIN — Diagram Layout Checklist

These rules must be applied to all vector diagram assets (SVGs) used within the YM PROSKIN presentation decks:

1. **ViewBox Safety Margins**:
   - The SVG `viewBox` must cover all graphic elements and text with a uniform padding of at least **24px** on all sides from the actual content.
   - For internal rendering elements (text, pathways, shapes), a strict programmatic margin of **5px** from the viewBox edges is enforced. No active drawing content (except full-size background rects) should exceed or sit closer than 5px to the borders.

2. **Zero Overlaps**:
   - Adjacent boxes, dimer shapes (e.g. RXR–RAR heterodimers), and text labels must have a visible gap (at least **10px**) to prevent overlaps.
   - Text elements must never overlap other text or adjacent badges/icons.

3. **Text Size and Containment**:
   - Ensure all text elements are fully within the canvas boundaries.
   - Wrap long labels or decrease the font size/spacing so they fit their background shapes or lanes without clipping.
   - Use standard brand typography tokens (e.g., `Arimo` font).

4. **Centered Alignments**:
   - Central pathways and nuclear complexes must be symmetric and centered horizontally and vertically inside their enclosing boundaries (such as the nuclear arch or membranes).
   - Icons and glyphs inside circles/boxes must be aligned to the geometric center of their containers.

5. **Color System and Brand Styling**:
   - Respect the Zero Black policy: do not use absolute black (`#000000`) for drawing molecules or icons; use the dedicated brand tokens (`moleculeStroke` or `dark`).
   - Style colors must correspond to the designated design token palette (Herbal, Sage, BgAlt, etc.).

6. **Automatic Verification**:
   - Every mechanism diagram SVG is checked automatically during the QA deck run by `ops/scripts/qa_svg_bounds.js` using headless Playwright. Any boundary violations will fail the build.
