const { chromium } = require('playwright');
const path = require('path');

async function main() {
    const svgFile = process.argv[2];
    const pngFile = process.argv[3];
    const width = parseInt(process.argv[4]) || 300;
    const height = parseInt(process.argv[5]) || 300;

    if (!svgFile || !pngFile) {
        console.error('Usage: node convert_svg_to_png.js <input_svg> <output_png> [width] [height]');
        process.exit(1);
    }

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    // Resolve absolute path to the SVG file
    const absoluteSvgPath = path.resolve(svgFile);
    const fileUrl = `file://${absoluteSvgPath.replace(/\\/g, '/')}`;
    
    await page.goto(fileUrl);
    await page.setViewportSize({ width: width, height: height });
    
    // Take a screenshot of the page
    const absolutePngPath = path.resolve(pngFile);
    await page.screenshot({ path: absolutePngPath, omitBackground: true, type: 'png' });
    
    await browser.close();
    console.log(`Successfully converted ${svgFile} to ${pngFile}`);
}

main().catch(err => {
    console.error('Error converting SVG to PNG:', err);
    process.exit(1);
});
