const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function main() {
    const svgFile = process.argv[2];
    const margin = parseFloat(process.argv[3]) || 5.0;

    if (!svgFile) {
        console.error('Usage: node qa_svg_bounds.js <input_svg> [margin]');
        process.exit(1);
    }
    if (!fs.existsSync(svgFile)) {
        console.error(`Error: File not found: ${svgFile}`);
        process.exit(1);
    }

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    const absoluteSvgPath = path.resolve(svgFile);
    const fileUrl = `file://${absoluteSvgPath.replace(/\\/g, '/')}`;
    await page.goto(fileUrl);

    const auditResult = await page.evaluate((marginThreshold) => {
        const svg = document.querySelector('svg');
        if (!svg) return { success: false, error: 'No SVG element found' };

        let W = 400, H = 300;
        if (svg.viewBox && svg.viewBox.baseVal) {
            W = svg.viewBox.baseVal.width;
            H = svg.viewBox.baseVal.height;
        } else {
            W = parseFloat(svg.getAttribute('width')) || W;
            H = parseFloat(svg.getAttribute('height')) || H;
        }

        const svgRect = svg.getBoundingClientRect();
        const errors = [];

        function toViewBox(clientRect) {
            return {
                left:   (clientRect.left   - svgRect.left) / svgRect.width  * W,
                right:  (clientRect.right  - svgRect.left) / svgRect.width  * W,
                top:    (clientRect.top    - svgRect.top)  / svgRect.height * H,
                bottom: (clientRect.bottom - svgRect.top)  / svgRect.height * H,
                width:  clientRect.width  / svgRect.width  * W,
                height: clientRect.height / svgRect.height * H,
            };
        }

        function intersects(a, b) {
            return a.left < b.right && a.right > b.left &&
                   a.top  < b.bottom && a.bottom > b.top;
        }

        function overlapArea(a, b) {
            const w = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left));
            const h = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
            return w * h;
        }

        function isBackground(el) {
            if (el.tagName.toLowerCase() !== 'rect') return false;
            const rx = parseFloat(el.getAttribute('x')) || 0;
            const ry = parseFloat(el.getAttribute('y')) || 0;
            const rw = parseFloat(el.getAttribute('width')) || 0;
            const rh = parseFloat(el.getAttribute('height')) || 0;
            return Math.abs(rx) < 1 && Math.abs(ry) < 1 &&
                   Math.abs(rw - W) < 2 && Math.abs(rh - H) < 2;
        }

        function inDefsOrMarker(el) {
            return el.closest('defs') || el.closest('marker');
        }

        function hasVisibleFill(el) {
            const fill = el.getAttribute('fill');
            const opacity = parseFloat(el.getAttribute('opacity') || '1');
            const fillOpacity = parseFloat(el.getAttribute('fill-opacity') || '1');
            if (opacity < 0.05 || fillOpacity < 0.05) return false;
            if (!fill || fill === 'none') return false;
            return true;
        }

        function getRects(selector) {
            return Array.from(svg.querySelectorAll(selector)).filter(el => {
                if (inDefsOrMarker(el)) return false;
                if (isBackground(el)) return false;
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            });
        }

        // ── 1. Edge clipping check (original) ─────────────────────────────
        const allDrawable = svg.querySelectorAll('text, path, rect, circle, ellipse, polygon, polyline, line, image');
        for (const el of allDrawable) {
            if (inDefsOrMarker(el)) continue;
            if (isBackground(el)) continue;
            const r = el.getBoundingClientRect();
            if (r.width === 0 && r.height === 0) continue;
            const vb = toViewBox(r);
            const tag = el.tagName.toLowerCase();
            const label = tag + (tag === 'text' ? ` ("${el.textContent.trim().slice(0, 40)}")` : '');

            if (vb.left   < marginThreshold)       errors.push({ check: 'edge', element: label, boundary: 'left',   details: `left edge ${vb.left.toFixed(1)} < margin ${marginThreshold}` });
            if (vb.right  > W - marginThreshold)   errors.push({ check: 'edge', element: label, boundary: 'right',  details: `right edge ${vb.right.toFixed(1)} > ${(W-marginThreshold).toFixed(1)}` });
            if (vb.top    < marginThreshold)        errors.push({ check: 'edge', element: label, boundary: 'top',    details: `top edge ${vb.top.toFixed(1)} < margin ${marginThreshold}` });
            if (vb.bottom > H - marginThreshold)   errors.push({ check: 'edge', element: label, boundary: 'bottom', details: `bottom edge ${vb.bottom.toFixed(1)} > ${(H-marginThreshold).toFixed(1)}` });
        }

        // ── 2. Text ↔ Graphic overlap ──────────────────────────────────────
        const textNodes = Array.from(svg.querySelectorAll('text')).filter(el => {
            if (inDefsOrMarker(el)) return false;
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        });

        const graphicNodes = Array.from(svg.querySelectorAll('rect, circle, ellipse, polygon, path')).filter(el => {
            if (inDefsOrMarker(el)) return false;
            if (isBackground(el)) return false;
            if (!hasVisibleFill(el)) return false;
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        });

        for (const txt of textNodes) {
            const tvb = toViewBox(txt.getBoundingClientRect());
            for (const gfx of graphicNodes) {
                // Skip if the graphic is in the same immediate parent group as the text
                // (text labels placed on top of their own shape are valid design)
                if (gfx.parentElement === txt.parentElement) continue;
                // Skip if the graphic is the direct ancestor container of the text's group
                if (gfx.parentElement && gfx.parentElement === txt.closest('g')) continue;

                const gvb = toViewBox(gfx.getBoundingClientRect());
                if (!intersects(tvb, gvb)) continue;

                const oa = overlapArea(tvb, gvb);
                const txtArea = tvb.width * tvb.height;
                // Only flag if graphic meaningfully covers text (>20% of text area)
                if (txtArea > 0 && oa / txtArea > 0.20) {
                    errors.push({
                        check: 'text_graphic_overlap',
                        element: `text ("${txt.textContent.trim().slice(0, 40)}")`,
                        details: `overlaps <${gfx.tagName}> by ${(oa/txtArea*100).toFixed(0)}% of text area`
                    });
                    break;
                }
            }
        }

        // ── 3. Box ↔ Box overlap ───────────────────────────────────────────
        const filledRects = Array.from(svg.querySelectorAll('rect')).filter(el => {
            if (inDefsOrMarker(el)) return false;
            if (isBackground(el)) return false;
            if (!hasVisibleFill(el)) return false;
            const r = el.getBoundingClientRect();
            return r.width > 10 && r.height > 10; // skip tiny decorative rects
        });

        for (let i = 0; i < filledRects.length; i++) {
            for (let j = i + 1; j < filledRects.length; j++) {
                const a = toViewBox(filledRects[i].getBoundingClientRect());
                const b = toViewBox(filledRects[j].getBoundingClientRect());
                if (!intersects(a, b)) continue;
                const oa = overlapArea(a, b);
                const aArea = a.width * a.height;
                const bArea = b.width * b.height;
                // Significant overlap: >30% of the smaller box
                const smaller = Math.min(aArea, bArea);
                if (smaller > 0 && oa / smaller > 0.30) {
                    errors.push({
                        check: 'box_box_overlap',
                        element: `rect[${i}] & rect[${j}]`,
                        details: `boxes overlap by ${(oa/smaller*100).toFixed(0)}% of smaller box`
                    });
                }
            }
        }

        // ── 4. Text outside its container rect ────────────────────────────
        const PAD = 5; // allow 5px tolerance
        for (const txt of textNodes) {
            const parentG = txt.parentElement;
            if (!parentG || parentG.tagName.toLowerCase() !== 'g') continue;
            // Only check when the direct parent g has a rect as direct child (not ellipse/circle)
            const containerRect = parentG.querySelector(':scope > rect');
            if (!containerRect) continue;
            // Skip very small rects (decorative: desmosome bridges, tick marks)
            const crClient = containerRect.getBoundingClientRect();
            if (crClient.width < 30 || crClient.height < 10) continue;

            const tvb = toViewBox(txt.getBoundingClientRect());
            const cvb = toViewBox(crClient);
            if (tvb.left   < cvb.left   - PAD ||
                tvb.right  > cvb.right  + PAD ||
                tvb.top    < cvb.top    - PAD ||
                tvb.bottom > cvb.bottom + PAD) {
                errors.push({
                    check: 'text_outside_container',
                    element: `text ("${txt.textContent.trim().slice(0, 40)}")`,
                    details: `text bbox [l:${tvb.left.toFixed(1)},r:${tvb.right.toFixed(1)},t:${tvb.top.toFixed(1)},b:${tvb.bottom.toFixed(1)}] outside container [l:${cvb.left.toFixed(1)},r:${cvb.right.toFixed(1)},t:${cvb.top.toFixed(1)},b:${cvb.bottom.toFixed(1)}]`
                });
            }
        }

        return { success: errors.length === 0, viewBox: { width: W, height: H }, errors };
    }, margin);

    await browser.close();

    if (!auditResult.success) {
        console.error(`SVG BOUNDS AUDIT FAILED for ${svgFile}`);
        console.error(JSON.stringify(auditResult, null, 2));
        process.exit(1);
    } else {
        console.log(`SVG BOUNDS AUDIT PASSED for ${svgFile} (ViewBox: ${auditResult.viewBox.width}x${auditResult.viewBox.height})`);
        process.exit(0);
    }
}

main().catch(err => {
    console.error('Error in SVG boundary audit script:', err);
    process.exit(1);
});
