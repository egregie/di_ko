// Contact sheet: render all SVGs in a dir into a labeled grid PNG for visual inspection.
// usage: node contact_sheet.js <dir-relative-to-root> <out-png-name> [cols] [bg]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const root = path.resolve(__dirname, '..', '..', '..');
  const dir = path.resolve(root, process.argv[2]);
  const outName = process.argv[3] || '_contact.png';
  const cols = parseInt(process.argv[4], 10) || 5;
  const bg = process.argv[5] || '#F8F6F4';
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
  const cells = files.map(f => {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    return `<div class="cell"><div class="box" style="color:#2C3440">${svg}</div><div class="lbl">${f}</div></div>`;
  }).join('');
  const html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
    body{margin:0;background:${bg};font-family:Arial,sans-serif;}
    .grid{display:grid;grid-template-columns:repeat(${cols},1fr);gap:14px;padding:18px;}
    .cell{border:1px solid #D7E0CE;border-radius:8px;background:#fff;padding:8px;display:flex;flex-direction:column;align-items:center;}
    .box{height:120px;width:100%;display:flex;align-items:center;justify-content:center;}
    .box svg{max-height:118px;max-width:100%;height:auto;width:auto;}
    .lbl{font-size:11px;color:#3D4A40;margin-top:6px;text-align:center;word-break:break-all;}
  </style></head><body><div class="grid">${cells}</div></body></html>`;
  const tmp = path.resolve(root, '06_render', 'out', '_sheet.html');
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage();
  await p.setViewportSize({ width: 1400, height: 900 });
  await p.goto('file://' + tmp.split(path.sep).join('/'), { waitUntil: 'load' });
  await p.screenshot({ path: `06_render/out/${outName}`, fullPage: true });
  await b.close();
  fs.unlinkSync(tmp);
  console.log(`contact sheet: 06_render/out/${outName} (${files.length} svgs)`);
})();
