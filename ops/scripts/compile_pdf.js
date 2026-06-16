const { chromium } = require('playwright');
const path = require('path');

async function main() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    // Resolve absolute path to the local HTML file
    const baseName = process.argv[2] || 'deck_retinoids_v2';
    const htmlPath = path.resolve(__dirname, '..', '..', '06_render', 'out', `${baseName}.html`);
    const fileUrl = `file://${htmlPath.replace(/\\/g, '/')}`;
    
    console.log(`Loading file URL: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'load' });
    
    // Set viewport to the 16:9 target size (optional argv override, backward-compatible)
    const W = parseInt(process.argv[3], 10) || 1024;
    const Hh = parseInt(process.argv[4], 10) || 576;
    await page.setViewportSize({ width: W, height: Hh });

    // Render PDF with custom width and height, zero margins
    const pdfPath = path.resolve(__dirname, '..', '..', '06_render', 'out', `${baseName}.pdf`);
    console.log(`Saving PDF to: ${pdfPath} (${W}x${Hh})`);
    await page.pdf({
        path: pdfPath,
        width: `${W}px`,
        height: `${Hh}px`,
        printBackground: true,
        margin: { top: 0, bottom: 0, left: 0, right: 0 }
    });

    
    await browser.close();
    console.log('PDF compile complete.');
}

main().catch(err => {
    console.error('Error compiling PDF:', err);
    process.exit(1);
});
