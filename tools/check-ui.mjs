/* 全画面の絞り込み・札・タブを、実ブラウザで一つずつ動かして点検する。
 *
 *   python3 -m http.server 8899 &        （リポジトリの中で）
 *   node tools/check-ui.mjs
 *
 * 見つけたいのは、フラッシュカードで出たのと同じ形のまちがい。
 *   ・選び直したのに 表示が 変わらない（絞りが 効いていない）
 *   ・札に出ている数と、実際に出ている数が 合わない
 *   ・押すと 画面が こわれる（JSのエラー）
 */
/* playwright の置き場所。この環境では /tmp/node_modules に入れてある。
   別の場所なら PW=/path/to/playwright/index.js で渡す。 */
/* **playwright と chromium の置き場所は、入れ直すと変わる。**
   番号つきの道（/opt/pw-browsers/chromium-1194/…）を 書き込んでいたので、
   入れ替わった日に **道具が丸ごと動かなくなった**（2026-10-30）。
   だから **決め打ちにせず、その場で探す**。見つからなければ
   playwright に まかせる（`executablePath` を 渡さない）。
   どうしても 指したいときは PW= と CHROME= で 渡せる。 */
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');
function findPlaywright() {
  const tries = [process.env.PW, 'playwright',
                 '/opt/node-tools/node_modules/playwright',
                 '/tmp/node_modules/playwright'].filter(Boolean);
  for (const t of tries) { try { return require(t); } catch (e) { /* つぎ */ } }
  throw new Error('playwright が 見つかりません。PW=… で 渡してください');
}
function findChrome() {
  if (process.env.CHROME) return process.env.CHROME;
  const out = [];
  let names = [];
  try { names = fs.readdirSync('/opt/pw-browsers'); } catch (e) { names = []; }
  for (const n of names) {
    if (!n.startsWith('chromium')) continue;
    for (const d of ['chrome-linux', 'chrome-linux64']) {
      const f = '/opt/pw-browsers/' + n + '/' + d + '/chrome';
      if (fs.existsSync(f)) out.push(f);
    }
  }
  out.sort();
  return out.length ? out[out.length - 1] : null;
}
const { chromium, devices } = findPlaywright();

const BASE = process.env.BASE || 'http://localhost:8899';
const HASH = 'ebec3cabb51c7aed2a0e3b893a08691fbadc9ad0eed58fe3c51ebe75d532a48c';
const CHROME = findChrome();

const ng = [];
const say = (...a) => console.log(...a);
const bad = (m) => { ng.push(m); say('   ✗', m); };

/* 画面の「今の見え方」を短い文字列にする。これが変わらなければ 絞りが効いていない。 */
async function sig(p, countSel, listSel, n = 6) {
  return await p.evaluate(([c, l, n]) => {
    const cnt = c ? (document.querySelector(c)?.textContent || '').trim() : '';
    const box = l ? document.querySelector(l) : null;
    const items = box ? [...box.children].slice(0, n)
      .map(e => e.textContent.replace(/\s+/g, ' ').trim().slice(0, 18)) : [];
    return cnt + ' | ' + items.join('/');
  }, [countSel, listSel, n]);
}

async function newPage(b, url, opts = {}) {
  const c = await b.newContext({ ...devices['iPhone 13'], ...(opts.ctx || {}) });
  if (opts.time) await c.clock.install({ time: new Date(opts.time) });
  const errs = [];
  c.on('pageerror', e => errs.push(e.message));
  const p = await c.newPage();
  await p.addInitScript(h => localStorage.setItem('jlpt-kanji-gate-v1', h), HASH);
  if (opts.seed) await p.addInitScript(opts.seed);
  await p.goto(BASE + url);
  await p.waitForTimeout(opts.wait || 3000);
  return { c, p, errs };
}

/* select を 一つずつ 選び直して、見え方が 変わるかを 見る。
   reset は「いっしょに出ている ほかの絞り」。先に いちばん上（＝すべて）へ
   戻しておかないと、前の点検の絞りが残って どれを選んでも 0件になり、
   「効いていない」と まちがえて 見える。 */
async function checkSelect(p, id, countSel, listSel, label, reset = []) {
  for (const r of reset) {
    await p.evaluate(i => {
      const el = document.getElementById(i);
      if (el) { el.value = el.options[0].value; el.dispatchEvent(new Event('change')); }
    }, r);
  }
  await p.waitForTimeout(500);
  const opts = await p.$$eval('#' + id + ' option', es => es.map(e => ({ v: e.value, t: e.textContent.trim() })));
  if (!opts.length) { bad(label + ' #' + id + ' に 選択肢が ない'); return; }
  const seen = new Map();
  for (const o of opts) {
    await p.selectOption('#' + id, o.v).catch(() => {});
    await p.waitForTimeout(700);
    const s = await sig(p, countSel, listSel);
    if (seen.has(s)) seen.get(s).push(o.t); else seen.set(s, [o.t]);
  }
  const same = [...seen.values()].filter(v => v.length > 1);
  const total = opts.length;
  const distinct = seen.size;
  say('   #' + id + '：' + total + '個の選択肢 → ' + distinct + '通りの表示');
  if (distinct === 1 && total > 1) bad(label + ' #' + id + '：どれを選んでも 表示が 同じ');
  else same.forEach(v => say('      （同じ表示になる組：' + v.join(' / ') + '）'));
  return { total, distinct, same };
}

/* 札（chip）を 一つずつ 押して、見え方が 変わるかを 見る */
async function checkChips(p, chipSel, countSel, listSel, label) {
  const n = await p.$$eval(chipSel, e => e.length);
  if (!n) { say('   札なし'); return; }
  const seen = new Map();
  for (let i = 0; i < n; i++) {
    const t = await p.$$eval(chipSel, (e, i) => { e[i].click(); return e[i].textContent.trim(); }, i);
    await p.waitForTimeout(900);
    const s = await sig(p, countSel, listSel);
    if (seen.has(s)) seen.get(s).push(t); else seen.set(s, [t]);
  }
  say('   札：' + n + '個 → ' + seen.size + '通りの表示');
  if (seen.size === 1 && n > 1) bad(label + ' 札：どれを押しても 表示が 同じ');
  else [...seen.values()].filter(v => v.length > 1)
    .forEach(v => say('      （同じ表示になる組：' + v.join(' / ') + '）'));
}

const b = await chromium.launch(CHROME ? { executablePath: CHROME } : {});

/* ───────── 入口 ───────── */
{
  say('\n【入口メニュー index.html】');
  const { c, p, errs } = await newPage(b, '/index.html');
  const links = await p.$$eval('a[href]', e => e.filter(x => !/^https?:|^#|^mailto/.test(x.getAttribute('href')))
    .map(x => x.getAttribute('href')));
  const uniq = [...new Set(links)];
  say('   中へのリンク ' + uniq.length + '本');
  for (const h of uniq) {
    const r = await p.evaluate(async u => (await fetch(u, { method: 'GET' })).status, h).catch(() => 0);
    if (r !== 200) bad('入口：リンク先が開けない ' + h + '（' + r + '）');
  }
  if (errs.length) bad('入口：JSのエラー ' + errs[0]);
  await c.close();
}

/* ───────── 漢字・語彙 ───────── */
{
  say('\n【漢字・語彙 kanji.html】');
  const { c, p, errs } = await newPage(b, '/kanji.html', { wait: 7000 });

  say('  ① 漢字一覧');
  await checkChips(p, '#lvBar .chip, #lvChips .chip, .lv .chip', '#cnt', '#grid', '漢字一覧');
  await checkSelect(p, 'sort', '#cnt', '#grid', '漢字一覧', ['mark']);
  await checkSelect(p, 'mark', '#cnt', '#grid', '漢字一覧', ['sort']);

  say('  ② 語彙');
  await p.evaluate(() => openTab('vocab'));
  await p.waitForSelector('#vgrid .kcard', { timeout: 15000 }).catch(() => {});
  await p.waitForTimeout(1200);
  await checkSelect(p, 'vMark', '#vCnt', '#vgrid', '語彙', ['vCat', 'vSub', 'vForm']);
  await checkSelect(p, 'vCat', '#vCnt', '#vgrid', '語彙', ['vMark', 'vSub', 'vForm']);
  await checkSelect(p, 'vForm', '#vCnt', '#vgrid', '語彙', ['vMark', 'vCat', 'vSub']);
  /* 「形でしぼる」は7つに分けるので、7つの合計が 全部の数と 合うはず。
     合わなければ、どこにも入らない語か、二重に数えている語がある。 */
  {
    await p.evaluate(() => window.ensureAllVocab && window.ensureAllVocab());
    await p.waitForTimeout(2500);
    const num = async () => {
      await p.waitForTimeout(250);
      const t = await p.textContent('#vCnt');
      return parseInt(String(t).replace(/[^0-9]/g, ''), 10) || 0;
    };
    for (const id of ['vMark', 'vCat', 'vSub']) await p.selectOption('#' + id, 'all');
    await p.selectOption('#vForm', 'all');
    const all = await num();
    let sum = 0;
    for (const f of ['juku', 'mix', 'ichiji', 'kana', 'kata', 'gokei', 'phrase']) {
      await p.selectOption('#vForm', f); sum += await num();
    }
    await p.selectOption('#vForm', 'all');
    if (sum !== all) bad(`語彙：形でしぼるの合計 ${sum} が 全部の数 ${all} と 合わない`);
    else say(`     形でしぼる：7区分の合計 ${sum} ＝ 全部 ${all}　一致`);
  }

  say('  ③ カード');
  await p.evaluate(() => openTab('card')); await p.waitForTimeout(800);
  await p.selectOption('#fcType', 'vocab'); await p.waitForTimeout(600);
  await p.click('#fcStart'); await p.waitForTimeout(900);
  await checkSelect(p, 'fcLv', '#fcCount', null, 'カード');
  await checkSelect(p, 'fcPick', '#fcCount', null, 'カード');
  await p.selectOption('#fcPick', 'all'); await p.waitForTimeout(700);
  await checkSelect(p, 'fcType', '#fcCount', null, 'カード');

  say('  ④ 書き順');
  await p.evaluate(() => openTab('stroke')); await p.waitForTimeout(2500);
  await checkSelect(p, 'sSort', null, '#sgrid', '書き順');

  say('  ⑤ 練習問題（開始してから見る）');
  await p.evaluate(() => openTab('quiz')); await p.waitForTimeout(2500);
  for (const lv of ['N5', 'N3', 'N2']) {
    await p.selectOption('#qzLv', lv).catch(() => {});
    await p.selectOption('#qzNum', '10').catch(() => {});
    await p.click('#qzStart'); await p.waitForTimeout(1800);
    const q = (await p.textContent('#qzQ').catch(() => '')).replace(/\s+/g, ' ').trim().slice(0, 30);
    const nch = await p.$$eval('#qzChoices > *', e => e.length).catch(() => 0);
    say('   ' + lv + ' → 「' + q + '」 選択肢' + nch + '個');
    if (!q) bad('練習問題：' + lv + ' で問題が出ない');
    if (nch !== 4) bad('練習問題：' + lv + ' の選択肢が ' + nch + '個');
  }

  say('  ⑥ 学習状況');
  await p.evaluate(() => openTab('stats')); await p.waitForTimeout(2500);
  const st = await p.evaluate(() => (document.querySelector('#progWrap')?.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80));
  say('   ' + (st || '（中身なし）'));
  if (!st) bad('学習状況：中身が出ない');
  if (errs.length) bad('漢字・語彙：JSのエラー ' + errs[0]);
  await c.close();
}

/* ───────── 文型・文法 ───────── */
{
  say('\n【文型・文法 bunpo/】');
  const { c, p, errs } = await newPage(b, '/bunpo/#list', { wait: 4000 });
  /* 文型の件数は #listCnt（#hdStat は「覚えた数」で 絞っても変わらない） */
  await checkChips(p, '#lvChips .chip', '#listCnt', '#grid', '文型');
  await checkSelect(p, 'catSel', '#listCnt', '#grid', '文型', ['stSel']);
  await checkSelect(p, 'stSel', '#listCnt', '#grid', '文型', ['catSel']);
  if (errs.length) bad('文型：JSのエラー ' + errs[0]);
  await c.close();
}

/* ───────── 読解 ───────── */
{
  say('\n【読解 dokkai/】');
  const { c, p, errs } = await newPage(b, '/dokkai/#list', { wait: 4000 });
  /* 読解の件数は #cnt（#hdStat は全体の合計で、絞っても変わらない）。
     一覧は #plist。ここを まちがえると「どれを選んでも同じ」に見える。 */
  await checkChips(p, '#lvChips .chip', '#cnt', '#plist', '読解');
  for (const id of ['genreSel', 'typeSel', 'doneSel']) {
    await checkSelect(p, id, '#cnt', '#plist', '読解',
      ['genreSel', 'typeSel', 'doneSel'].filter(x => x !== id));
  }
  say('  おすすめの3つのボタン');
  const seen = new Set();
  for (const id of ['recField', 'recExam', 'recAll']) {
    await p.click('#' + id).catch(() => {});
    await p.waitForTimeout(900);
    const s = await sig(p, '#cnt', '#plist');
    say('   #' + id + ' → ' + s.slice(0, 70));
    seen.add(s);
  }
  if (seen.size < 3) bad('読解：おすすめ3つのうち、同じ表示になるものがある');
  if (errs.length) bad('読解：JSのエラー ' + errs[0]);
  await c.close();
}

/* ───────── 聴解 ───────── */
{
  say('\n【聴解 choukai/】');
  const { c, p, errs } = await newPage(b, '/choukai/', { wait: 3500 });
  await checkChips(p, '#lvChips .lvchip', '#hdStat', null, '聴解');
  const parts = await p.$$eval('.part:not(.hide)', e => e.length);
  say('   出ているパート ' + parts);
  if (errs.length) bad('聴解：JSのエラー ' + errs[0]);
  await c.close();
}

/* ───────── そのほかの画面 ───────── */
for (const [url, name, wait] of [
  ['/n3.html', '100日コース', 3000],
  ['/tegaki.html', '手書き', 3000],
  ['/shinjin/index.html', '新人コース', 3000],
  ['/n2/index.html', 'N2ロードマップ', 3000],
  ['/moshi/', '模試', 2500],
  ['/shindan/index.html', '診断テスト', 2500],
]) {
  say('\n【' + name + ' ' + url + '】');
  const { c, p, errs } = await newPage(b, url, { wait });
  const txt = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ').trim());
  say('   画面の文字数 ' + txt.length + '　' + txt.slice(0, 70));
  if (txt.length < 80) bad(name + '：画面がほぼ空');
  if (/合言葉を 入れて|Kata sandi/.test(txt.slice(0, 40))) bad(name + '：合言葉の画面から進めていない');
  if (errs.length) bad(name + '：JSのエラー ' + errs[0]);
  await c.close();
}

/* ───────── 週テストに直行したときの 見出しと戻り先 ─────────
   `?set=` で その回に直行する分岐を、見出しを入れる行より**前**に置くと、
   HTMLの初期値「N2模試・N2ロードマップ」が そのまま残る。
   新人コースの週テストに N2の名前が出ていた（2026-10-25c）。 */
say('\n【週テストに直行したときの見出し】');
for (const [lv, set, head, back] of [
  ['sjw', 5, '新人コース', '新人コース'],
  ['n2w', 3, 'N2コース', 'N2ロードマップ'],
]) {
  const { c, p, errs } = await newPage(b, '/moshi/?lv=' + lv + '&set=' + set, { wait: 2500 });
  const h = await p.evaluate(() => document.getElementById('hdTitle')?.textContent || '');
  const bk = await p.evaluate(() => document.getElementById('backLink')?.textContent || '');
  say('   ' + lv + '　見出し「' + h + '」　戻り「' + bk + '」');
  if (!h.includes(head)) bad('?set= 直行：' + lv + ' の見出しが「' + h + '」（' + head + 'のはず）');
  if (!bk.includes(back)) bad('?set= 直行：' + lv + ' の戻り先が「' + bk + '」（' + back + 'のはず）');
  /* 問題文に 生のタグが 見えていないか（持ち主が見つけたもの） */
  const t = await p.evaluate(() => document.body.innerText);
  if (/<[a-zA-Z/]/.test(t)) bad('?set= 直行：' + lv + ' の画面に生のタグが見えている');
  if (errs.length) bad('?set= 直行：' + lv + '　JSのエラー ' + errs[0]);
  await c.close();
}

/* ───────── コースの週めくりと、その週の受けわたし ─────────
   「◀ 前の週」で下見した週が、**漢字の画面にちゃんと渡るか**を見る。
   渡らないと、第4週を下見して「今週ひらくもの」を押しても
   今週の分が出てしまう。実際そうなっていた（2026-10-16）。
   しかも押したときの処理は try/catch の中にあり、
   **まちがえても画面には何も出ない**。だから機械で見張る。 */
for (const [url, name, nav, prev, now, link, total, time] of [
  ['/shinjin/index.html', '新人コース', '#weekNav', '#weekPrev', '#weekNow',
   '#today a[href*="kanji.html"], #rest a[href*="kanji.html"]', 30, '2027-01-06T09:00:00+09:00'],
  ['/n2/index.html', 'N2コース', '#wkNav', '#wkPrev', '#wkNow',
   '#wkApps a[data-open="week"]', 66, null],
]) {
  say('\n【' + name + '：週めくり】');
  const { c, p, errs } = await newPage(b, url, { wait: 3000, time });
  const navTxt = async () => (await p.$eval(nav, e => e.innerText.replace(/\s+/g, ' ').trim()));
  const weekOf = s => { const m = /第(\d+)週/.exec(s); return m ? +m[1] : null; };
  if (!(await p.$(nav))) { bad(name + '：前の週・次の週のボタンが無い'); await c.close(); continue; }
  const w0 = weekOf(await navTxt());
  if (!w0) { bad(name + '：いま第何週かが出ていない'); await c.close(); continue; }
  say('   いま 第' + w0 + '週 ／ 全' + total + '週');
  if (!new RegExp('全' + total + '週').test(await navTxt()))
    bad(name + '：全' + total + '週と出ていない');
  /* 2つ戻る → 下見の帯が出る */
  await p.click(prev); await p.waitForTimeout(500);
  await p.click(prev); await p.waitForTimeout(700);
  const w2 = weekOf(await navTxt());
  if (w2 !== w0 - 2) bad(name + '：2回もどったのに 第' + w2 + '週（第' + (w0 - 2) + '週のはず）');
  const pre = await p.evaluate(() => {
    const e = document.querySelector('#weekPre, #wkPre');
    return e && e.style.display !== 'none' ? e.innerText.replace(/\s+/g, ' ') : '';
  });
  if (!/下見/.test(pre)) bad(name + '：下見だと画面に書いていない（きょうの分とまちがえる）');
  /* その週が漢字の画面に渡るか */
  if (await p.$(link)) {
    await p.click(link);
    await p.waitForLoadState('load'); await p.waitForTimeout(3500);
    const msg = await p.evaluate(() => {
      const m = document.getElementById('wkMsg'); return m && !m.hidden ? m.innerText : '';
    });
    say('   漢字の帯 ' + (msg.slice(0, 56) || '(出ていない)'));
    if (!msg) bad(name + '：下見した週を開いても「今週の分だけ」が効いていない');
    else if (weekOf(msg) !== w2)
      bad(name + '：下見は第' + w2 + '週なのに、漢字の画面は第' + weekOf(msg) + '週を出している');
    const cnt = +((await p.evaluate(() => document.getElementById('cnt')?.textContent || '')).replace(/\D/g, '') || 0);
    if (cnt > 300) bad(name + '：下見した週なのに ' + cnt + '字 出ている（絞れていない）');
  } else bad(name + '：漢字をひらくボタンが見つからない');
  /* 戻る → 今週に戻り、帯が消える */
  await p.goBack(); await p.waitForTimeout(2500);
  if (await p.$(now)) {
    await p.click(now); await p.waitForTimeout(600);
    if (weekOf(await navTxt()) !== w0) bad(name + '：「今週にもどる」で今週に戻らない');
    const still = await p.evaluate(() => {
      const e = document.querySelector('#weekPre, #wkPre');
      return !!(e && e.style.display !== 'none');
    });
    if (still) bad(name + '：今週に戻ったのに 下見の帯が残っている');
  }
  if (errs.length) bad(name + '：JSのエラー ' + errs[0]);
  await c.close();
}

await b.close();
say('\n' + '='.repeat(60));
say('おかしいところ ' + ng.length + '件');
ng.forEach(x => say('  - ' + x));
say('='.repeat(60));
process.exit(ng.length ? 1 : 0);
