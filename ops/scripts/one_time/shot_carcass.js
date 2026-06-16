// QA helper: screenshot specific carcass slides to PNG for visual verification.
// usage: node shot_carcass.js <deck_id> <comma-separated slide numbers>
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const deck = process.argv[2];
  const nums = process.argv[3].split(',').map(Number);
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage();
  await p.setViewportSize({ width: 1280, height: 720 });
  const subdir = process.argv[4] || 'out';
  const html = path.resolve(__dirname, '..', '..', '..', '06_render', subdir, deck + '.html').split(path.sep).join('/');
  await p.goto('file://' + html, { waitUntil: 'load' });
  const secs = await p.$$('section.slide');
  for (const n of nums) {
    await secs[n - 1].screenshot({ path: `06_render/out/_shot_${deck}_s${n}.png` });
    console.log('shot s' + n);
  }
  await b.close();
})();
