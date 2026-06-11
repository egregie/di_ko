const { chromium } = require('playwright');
const path = require('path');

async function main() {
    const filename = process.argv[2] || 'deck_retinoids_v2.html';
    const projectRoot = path.resolve(__dirname, '..', '..');
    const htmlPath = path.resolve(projectRoot, '06_render', 'out', filename);
    const fileUrl = `file://${htmlPath.replace(/\\/g, '/')}`;

    console.log(`Auditing layout bounds for: ${fileUrl}`);
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(fileUrl, { waitUntil: 'load' });

    const results = await page.evaluate(() => {
        const slides = Array.from(document.querySelectorAll('.slide'));
        const errors = [];
        
        // Zero Black check on the entire document body text and styles
        const bodyHtml = document.body.innerHTML.toLowerCase();
        
        // Check for forbidden color matches
        const forbiddenPatterns = [
            /\bcolor\s*:\s*#000(000)?\b/g,
            /\bcolor\s*:\s*#fff(fff)?\b/g,
            /\bcolor\s*:\s*black\b/g,
            /\bcolor\s*:\s*white\b/g,
            /\bfill\s*=\s*"#000(000)?"/g,
            /\bfill\s*=\s*"#fff(fff)?"/g,
            /\bfill\s*=\s*"black"/g,
            /\bfill\s*=\s*"white"/g,
            /\bstroke\s*=\s*"#000(000)?"/g,
            /\bstroke\s*=\s*"#fff(fff)?"/g,
            /\bstroke\s*=\s*"black"/g,
            /\bstroke\s*=\s*"white"/g
        ];
        
        for (const pattern of forbiddenPatterns) {
            if (pattern.test(bodyHtml)) {
                errors.push({
                    check: 'zero_black_logo',
                    details: `Zero Black violation: HTML contains forbidden color pattern ${pattern.toString()}`
                });
                break;
            }
        }

        slides.forEach((slide, idx) => {
            const slideNum = idx + 1;
            const isCover = slide.classList.contains('cover-layout');
            const isSection = slide.classList.contains('section-divider-layout');
            const isClosing = (idx === slides.length - 1);
            
            // Check logo heights and widths
            const footerLogo = slide.querySelector('.footer-logo');
            if (footerLogo) {
                const r = footerLogo.getBoundingClientRect();
                if (r.height < 18) {
                    errors.push({
                        check: 'logo_min_size',
                        slide: slideNum,
                        details: `Footer logo height is ${r.height.toFixed(1)}px (min: 18px)`
                    });
                }
            }

            if (isCover) {
                // Cover checks
                const coverLogo = slide.querySelector('.cover-logo');
                if (!coverLogo || !coverLogo.querySelector('svg')) {
                    errors.push({
                        check: 'cover_descriptor_present',
                        slide: slideNum,
                        details: 'Cover slide is missing the descriptor lockup logo'
                    });
                }
            } else if (isSection) {
                // Section divider checks
                const sectionLogo = slide.querySelector('.section-logo');
                if (!sectionLogo || !sectionLogo.querySelector('svg')) {
                    errors.push({
                        check: 'section_logo_present',
                        slide: slideNum,
                        details: 'Section divider slide is missing the horizontal logo'
                    });
                }
            } else {
                // Content slide checks
                const footer = slide.querySelector('.slide-footer');
                if (!footer || footer.getAttribute('data-brand-footer') !== '1') {
                    errors.push({
                        check: 'brand_footer_present',
                        slide: slideNum,
                        details: 'Content slide is missing the brand footer'
                    });
                }
                
                // Footer zone reserved check
                const contentSelectors = [
                    'h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li', 'table',
                    '.media-box', '.card', '.timeline-step', '.compare-card',
                    '.stat-card', '.alert-box', '.summary-box', 'img', 'svg'
                ];
                
                contentSelectors.forEach(selector => {
                    const elements = Array.from(slide.querySelectorAll(selector));
                    elements.forEach(el => {
                        if (el.closest('.slide-footer') || el.closest('.disclaimers') || el.closest('.sources-ref')) {
                            return;
                        }
                        
                        const rect = el.getBoundingClientRect();
                        const slideRect = slide.getBoundingClientRect();
                        const bottomRel = rect.bottom - slideRect.top;
                        
                        if (bottomRel > 530.1 && rect.height > 0) {
                            errors.push({
                                check: 'footer_zone_reserved',
                                slide: slideNum,
                                details: `Content element <${el.tagName.toLowerCase()}> (class: ${el.className}) overlaps footer zone (bottom: ${bottomRel.toFixed(1)}px > 530px)`
                            });
                        }
                    });
                });
            }

            if (isClosing) {
                // Closing slide checks
                const closingBadge = slide.querySelector('.closing-badge');
                if (!closingBadge || !closingBadge.querySelector('svg')) {
                    errors.push({
                        check: 'closing_badge_present',
                        slide: slideNum,
                        details: 'Closing slide is missing the badge logo'
                    });
                }
            }
        });
        
        return errors;
    });

    await browser.close();

    console.log(`Audit complete. Errors found: ${results.length}`);
    if (results.length > 0) {
        console.error(JSON.stringify(results, null, 2));
        process.exit(1);
    } else {
        console.log("ALL HTML LAYOUT AND BRAND CHECKS PASSED!");
        process.exit(0);
    }
}

main().catch(err => {
    console.error('Error in layout bounds check:', err);
    process.exit(1);
});
