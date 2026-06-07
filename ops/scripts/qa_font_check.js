const { chromium } = require('playwright');
const path = require('path');

async function main() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    // Resolve absolute path to the local HTML file
    const htmlPath = path.resolve(__dirname, '..', '..', '06_render', 'out', 'deck_retinoids.html');
    const fileUrl = `file://${htmlPath.replace(/\\/g, '/')}`;
    
    console.log(`Loading file URL in Playwright: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'load' });
    
    // Wait for fonts to be ready
    await page.evaluate(async () => {
        await document.fonts.ready;
    });
    
    // Check if Arimo is loaded
    const hasArimo = await page.evaluate(() => {
        return document.fonts.check("12px Arimo");
    });
    
    // Measure text width to confirm rendering engine size mapping
    const textWidth = await page.evaluate(() => {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        ctx.font = "100px Arimo";
        return ctx.measureText("Test Font Width").width;
    });
    
    console.log(`Font Arimo loaded successfully: ${hasArimo}`);
    console.log(`Rendered text width (100px Arimo): ${textWidth}px`);
    
    // Offline mode validation check
    await page.context().setOffline(true);
    let hasArimoOffline = false;
    try {
        await page.reload({ waitUntil: 'load' });
        await page.evaluate(async () => {
            await document.fonts.ready;
        });
        hasArimoOffline = await page.evaluate(() => {
            return document.fonts.check("12px Arimo");
        });
        console.log(`Font Arimo loaded offline: ${hasArimoOffline}`);
    } catch (e) {
        console.log(`Offline reload failed: ${e.message}`);
    }
    
    await browser.close();
    
    // Output standard result line for parent script parsing
    console.log(`RESULT_ARIMO_LOADED=${hasArimo}`);
    console.log(`RESULT_ARIMO_OFFLINE_LOADED=${hasArimoOffline}`);
    
    if (!hasArimo) {
        console.error("QA Font Audit: FAIL - Arimo font is not active.");
        process.exit(1);
    } else {
        console.log("QA Font Audit: PASS");
        process.exit(0);
    }
}

main().catch(err => {
    console.error('Error in QA font check:', err);
    process.exit(1);
});
