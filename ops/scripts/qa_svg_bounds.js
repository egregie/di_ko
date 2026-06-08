const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function main() {
    const svgFile = process.argv[2];
    const margin = parseFloat(process.argv[3]) || 5.0; // Default safety margin in viewBox units

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
    
    // Resolve absolute path to the SVG file
    const absoluteSvgPath = path.resolve(svgFile);
    const fileUrl = `file://${absoluteSvgPath.replace(/\\/g, '/')}`;
    
    await page.goto(fileUrl);
    
    const auditResult = await page.evaluate((marginThreshold) => {
        const svg = document.querySelector('svg');
        if (!svg) {
            return { success: false, error: 'No SVG element found' };
        }
        
        let W = 400;
        let H = 300;
        
        if (svg.viewBox && svg.viewBox.baseVal) {
            W = svg.viewBox.baseVal.width;
            H = svg.viewBox.baseVal.height;
        } else {
            W = parseFloat(svg.getAttribute('width')) || W;
            H = parseFloat(svg.getAttribute('height')) || H;
        }
        
        const svgRect = svg.getBoundingClientRect();
        const errors = [];
        
        // Query all drawable elements
        const elements = svg.querySelectorAll('text, path, rect, circle, ellipse, polygon, polyline, line, image');
        
        for (const el of elements) {
            // Ignore background rect
            if (el.tagName.toLowerCase() === 'rect') {
                const rx = parseFloat(el.getAttribute('x')) || 0;
                const ry = parseFloat(el.getAttribute('y')) || 0;
                const rw = parseFloat(el.getAttribute('width')) || 0;
                const rh = parseFloat(el.getAttribute('height')) || 0;
                
                // If the rect matches the viewport, ignore it (it's the background canvas)
                if (Math.abs(rx) < 1 && Math.abs(ry) < 1 && Math.abs(rw - W) < 2 && Math.abs(rh - H) < 2) {
                    continue;
                }
            }
            
            // Ignore elements inside <defs> or <marker>
            if (el.closest('defs') || el.closest('marker')) {
                continue;
            }
            
            const rect = el.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) {
                continue; // Element not rendered or has no size
            }
            
            // Map client rect to SVG viewBox space
            const left = (rect.left - svgRect.left) / svgRect.width * W;
            const right = (rect.right - svgRect.left) / svgRect.width * W;
            const top = (rect.top - svgRect.top) / svgRect.height * H;
            const bottom = (rect.bottom - svgRect.top) / svgRect.height * H;
            
            const textContent = el.tagName.toLowerCase() === 'text' ? el.textContent : '';
            const desc = el.tagName.toLowerCase() + (textContent ? ` ("${textContent}")` : '');
            
            // Check boundaries with margin
            if (left < marginThreshold) {
                errors.push({
                    element: desc,
                    boundary: 'left',
                    value: left,
                    expected: `>= ${marginThreshold}`,
                    details: `Element left edge (${left.toFixed(2)}) is closer than ${marginThreshold} units to the left border.`
                });
            }
            if (right > W - marginThreshold) {
                errors.push({
                    element: desc,
                    boundary: 'right',
                    value: right,
                    expected: `<= ${W - marginThreshold}`,
                    details: `Element right edge (${right.toFixed(2)}) exceeds right boundary of ${W - marginThreshold} units (W=${W}).`
                });
            }
            if (top < marginThreshold) {
                errors.push({
                    element: desc,
                    boundary: 'top',
                    value: top,
                    expected: `>= ${marginThreshold}`,
                    details: `Element top edge (${top.toFixed(2)}) is closer than ${marginThreshold} units to the top border.`
                });
            }
            if (bottom > H - marginThreshold) {
                errors.push({
                    element: desc,
                    boundary: 'bottom',
                    value: bottom,
                    expected: `<= ${H - marginThreshold}`,
                    details: `Element bottom edge (${bottom.toFixed(2)}) exceeds bottom boundary of ${H - marginThreshold} units (H=${H}).`
                });
            }
        }
        
        return {
            success: errors.length === 0,
            viewBox: { width: W, height: H },
            errors: errors
        };
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
