import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
const [src, dst, foot] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage();
await p.setViewportSize({ width: 794, height: 1123 });
await p.goto('file://' + src, { waitUntil: 'load' });
await p.pdf({ path: dst, format: 'A4', printBackground: true,
  margin: { top: '14mm', bottom: '18mm', left: '16mm', right: '16mm' },
  displayHeaderFooter: true, headerTemplate: '<div></div>',
  footerTemplate: '<div style="width:100%;text-align:center;font-size:8pt;color:#6b7784;font-family:sans-serif">'
    + foot + '　—　<span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
await b.close();
console.log('wrote', dst);
