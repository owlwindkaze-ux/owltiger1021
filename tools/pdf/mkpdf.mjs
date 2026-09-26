// HTML を A4 の PDF にする。
//
// **なぜリポジトリに置いてあるか**
// この道具は もともと作業用の場所（/tmp）にしか無く、**場所が消えたときに
// PDFを作り直せなくなりました**（2026-09-26）。作った道具は必ず
// リポジトリに入れること。
//
//   NODE_PATH=/tmp/node_modules node tools/pdf/mkpdf.mjs <abs.html> <abs.pdf> "<右下に出す文字>"
//
// 必要なもの： playwright（/tmp/node_modules でよい）と /opt/pw-browsers の Chromium
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

/* ESM の import は NODE_PATH を見ない。playwright が repo の外（/tmp/node_modules）に
   入っていても動くように、置いてありそうな所を順に当たる。 */
const require_ = createRequire(import.meta.url);
function loadPlaywright() {
  const tries = ['playwright'];
  for (const d of [process.env.NODE_PATH, '/tmp/node_modules'].filter(Boolean))
    for (const one of d.split(':')) tries.push(path.join(one, 'playwright'));
  for (const t of tries) { try { return require_(t); } catch (e) {} }
  console.error('× playwright が見つかりません。'
    + 'npm install --no-save --prefix /tmp playwright を先に走らせてください');
  process.exit(1);
}
const { chromium } = loadPlaywright();

const [src, dst, footer = ''] = process.argv.slice(2);
if (!src || !dst) {
  console.error('つかいかた: node tools/pdf/mkpdf.mjs <abs.html> <abs.pdf> "<右下の文字>"');
  process.exit(1);
}
if (!path.isAbsolute(src) || !path.isAbsolute(dst)) {
  console.error('× パスは絶対パスで渡してください（file:// で開くため）');
  process.exit(1);
}

const EXE = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
             '/opt/pw-browsers/chromium/chrome-linux/chrome']
  .find(p => fs.existsSync(p));

const b = await chromium.launch(EXE ? { executablePath: EXE } : {});
const p = await b.newPage();
await p.goto('file://' + src, { waitUntil: 'load' });
/* 埋め込みフォントの用意を待つ。待たないと 1ページ目だけ字が崩れることがある */
await p.evaluate(() => document.fonts && document.fonts.ready);
await p.emulateMedia({ media: 'print' });

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const style = 'font-family:sans-serif;font-size:7.5pt;color:#6b7784;width:100%;'
            + 'padding:0 14mm;display:flex;justify-content:space-between';

await p.pdf({
  path: dst,
  format: 'A4',
  printBackground: true,
  displayHeaderFooter: true,
  headerTemplate: '<div></div>',
  footerTemplate: '<div style="' + style + '"><span>' + esc(footer)
    + '</span><span class="pageNumber"></span></div>',
  margin: { top: '16mm', right: '14mm', bottom: '18mm', left: '14mm' },
});
await b.close();
const kb = Math.round(fs.statSync(dst).size / 1024);
console.log('wrote ' + dst + '（' + kb + ' KB）');
