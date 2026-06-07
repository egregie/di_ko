const { chromium } = require('playwright');
const path = require('path');

async function main() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    // Resolve absolute path to the local HTML file
    const htmlPath = path.resolve(__dirname, '..', '..', '06_render', 'out', 'deck_retinoids.html');
    const fileUrl = `file://${htmlPath.replace(/\\/g, '/')}`;
    
    console.log(`Loading file URL: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'load' });
    
    // Set viewport to the 16:9 target size
    await page.setViewportSize({ width: 1024, height: 576 });
    
    // Render PDF with custom width and height, zero margins
    const pdfPath = path.resolve(__dirname, '..', '..', '06_render', 'out', 'deck_retinoids.pdf');
    console.log(`Saving PDF to: ${pdfPath}`);
    await page.pdf({
        path: pdfPath,
        width: '1024px',
        height: '576px',
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
