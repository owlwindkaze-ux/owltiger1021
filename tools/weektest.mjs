/* **週テスト**を組み立てる（SPEC 2.6-z57）。
 *
 * 持ち主から「新人コースやN2コースにも、100日コースのような**問題が作れないのか**」
 * →「**(A) 組み立てる。漢字・語彙も入れる**」。
 *
 * **新しい問題は1つも書かない。**その週に習う分から 集めるだけ。
 *
 *   文型      … データの中に 問題が入っている（N4だけで367問）
 *   読解・聴解 … 同じく 選択肢・正解つき
 *   漢字・語彙 … **データには無い。画面がその場で作っている。**
 *
 * 漢字・語彙だけ やり方が違う。Pythonに写すと **質が変わる**ので写さない。
 * **`kanji.html` をそのまま開いて、その中の `makeQuestion()` を呼ぶ。**
 * 画面と同じ問題が出る。
 *
 * **乱数は固定する。**作り直すたびに問題が変わると、前に取った点と
 * くらべられなくなるため。週ごとに決まった種を使う。
 *
 *   NODE_PATH=/tmp/node_modules node tools/weektest.mjs shinjin 5
 *   NODE_PATH=/tmp/node_modules node tools/weektest.mjs shinjin all
 *
 * 先に `python3 -m http.server 8777` を リポジトリの中で 立てておくこと。
 */
import { createRequire } from 'module';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire('/tmp/node_modules/');
const { chromium } = require('playwright');
const fs = require('fs');

const R = path.dirname(path.dirname(fileURLToPath(import.meta.url))) + '/';
const BASE = process.env.BASE || 'http://localhost:8777';
const CHROME = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const HASH = 'ebec3cabb51c7aed2a0e3b893a08691fbadc9ad0eed58fe3c51ebe75d532a48c';

const J = p => JSON.parse(fs.readFileSync(R + p, 'utf8'));

/* 1週あたりの問題の数。合計20問 */
const N = { kv: 4, gram: 8, read: 4, chou: 4 };

/* そのコース・その週は どのレベルか（読解・聴解をえらぶのに使う） */
function levelOf(course, w) {
  if (course === 'shinjin') return w <= 4 ? 'N5' : w <= 12 ? 'N4' : 'N3';
  return w <= 20 ? 'N3' : 'N2';          /* N2コースは前半でN3を仕上げる */
}

/* ── 文型 ───────────────────────────────────────────── */
function gramQs(course, w, want) {
  const idx = J('bunpo/grammar.json');
  const all = {};
  for (const f of idx.files)
    for (const g of J('bunpo/' + f.file).grammar) all[g.id] = g;
  const ids = (J('bunpo/weeks.json').courses[course].weeks[String(w)] || []);
  const out = [];
  for (const id of ids) {
    const g = all[id];
    if (!g) continue;
    for (const q of (g.quiz || [])) {
      if (q.type !== 'choice') continue;        /* 並べ替えは画面の作りが違うので使わない */
      if (!q.choices || typeof q.answer !== 'number') continue;
      /* **日本語の欄に インドネシア語を入れない。**
         文型の問題には `explain_ja` が無く、`explain_id`（尼語）だけ。
         前はそれを `explain` に入れていて、検査が鳴った（2026-10-25b）。
         画面は `explain`＝日本語、`explain_id`＝尼語 で 出し分ける。 */
      out.push({
        q: q.q, choices: q.choices, answer: q.answer,
        explain: '【' + g.pattern + '】' + (q.explain_ja ? '　' + q.explain_ja : ''),
        explain_id: q.explain_id || '',
      });
      break;                                    /* 1項目につき1問まで（かたよらせない） */
    }
    if (out.length >= want) break;
  }
  return out;
}

/* ── 読解 ───────────────────────────────────────────── */
function readQs(lv, w, want) {
  let ps = [];
  try { ps = J('dokkai/reading-' + lv.toLowerCase() + '.json').passages || []; } catch (e) { return []; }
  if (!ps.length) return [];
  const out = [];
  let got = 0;                                  /* **本の数ではなく 問の数で数える。**
                                                   前は本を1本取ると その設問を全部入れていて
                                                   4問のつもりが7問になった（2026-10-25） */
  const i = (w * 3) % ps.length;                /* 週ごとにずらす */
  for (let n = 0; n < ps.length && got < want; n++) {
    const p = ps[(i + n) % ps.length];
    const qi = [];
    for (let k = 0; k < p.questions.length && got + qi.length < want; k++) qi.push(k);
    if (qi.length) { out.push({ passage: p, qi }); got += qi.length; }
  }
  return out;
}

/* ── 聴解 ───────────────────────────────────────────── */
function chouQs(lv, w, want) {
  const s = fs.readFileSync(R + 'choukai/index.html', 'utf8');
  const a = s.indexOf('const DATA = [');
  const parts = JSON.parse(s.slice(a + 'const DATA = '.length, s.indexOf('\n];', a) + 2));
  const use = parts.filter(p => p.level === lv);
  const pool = [];
  for (const p of (use.length ? use : parts))
    for (const it of p.items) pool.push({ part: p.title, ...it });
  if (!pool.length) return [];
  const out = [];
  const start = (w * 5) % pool.length;
  for (let n = 0; n < pool.length && out.length < want; n++) {
    const it = pool[(start + n) % pool.length];
    if (!it.script || !it.opts || typeof it.ans !== 'number') continue;
    out.push(it);
  }
  return out;
}

/* ── 漢字・語彙（画面の中の作り方を そのまま呼ぶ）──────────── */
async function kvQs(page, kw, w, want, seed) {
  const wk = kw.kanji[String(w)] || [], wv = kw.vocab[String(w)] || [];
  if (!wv.length) return [];
  return await page.evaluate(async ([wk, wv, want, seed]) => {
    /* **乱数を固定する。**作り直しても同じ問題が出るように */
    let s = seed >>> 0;
    Math.random = function () {
      s = (s * 1664525 + 1013904223) >>> 0;
      return s / 4294967296;
    };
    await ensureAllKanji(); await ensureAllVocab();
    const kset = new Set(wk), vset = new Set(wv);
    const kpool = DATA.filter(k => kset.has(k.character));
    const pool = VOCAB.filter(x => vset.has(x.word) && x.study !== '参考' &&
                 x.word && x.reading && (x.meaning_id || x.meaning));
    const types = ['kanjiread', 'reading', 'orth', 'context', 'para', 'usage'];
    const out = [], seen = new Set();
    let guard = 0;
    while (out.length < want && guard++ < want * 60) {
      const t = types[guard % types.length];
      const q = makeQuestion(t, pool, kpool);
      if (!q) continue;
      const key = q.kind + '/' + q.key;
      if (seen.has(key)) continue;
      seen.add(key);
      /* note は「語（よみ）＝ 意味（尼語）」の形。**＝ や ： の右は 尼語**なので
         日本語の欄に残さず、`explain_id` へ回す。 */
      var note = q.note || '', ja = note, id = '';
      var cut = note.search(/[＝：]/);
      if (cut >= 0) { ja = note.slice(0, cut + 1).trim(); id = note.slice(cut + 1).trim(); }
      out.push({ kind: q.kind, q: q.q, choices: q.choices,
                 answer: q.choices.indexOf(q.answer), explain: ja, explain_id: id });
    }
    return out.filter(x => x.answer >= 0);
  }, [wk, wv, want, seed]);
}

/* ── 1週ぶんを組み立てる ─────────────────────────────── */
function build(course, w, lv, kv, gr, rd, ch) {
  const S = {}, order = [];
  const add = (key, label, name, inst, body) => {
    S[key] = { label, name, inst, ...body }; order.push(key);
  };
  kv.forEach((q, i) => add('問題' + (i + 1), '問題' + (i + 1),
    q.kind.split('／')[0].replace(/^問題\d+\s*/, '').trim() || '漢字・語彙',
    'つぎの問いに答えなさい。',
    { items: [{ q: q.q, choices: q.choices, answer: q.answer, explain: q.explain }] }));
  gr.forEach((q, i) => add('問題' + (kv.length + i + 1), '問題' + (kv.length + i + 1),
    '文法形式の判断', 'つぎの文の（　）に入れるのに最もよいものを、一つえらびなさい。',
    { group: '言語知識', items: [q] }));
  let n = kv.length + gr.length;
  rd.forEach((r, i) => add('問題' + (++n), '問題' + n,
    '内容理解', 'つぎの文章を読んで、質問に答えなさい。',
    { group: '読解', read: [r] }));
  ch.forEach((it, i) => add('聴解' + (i + 1), '聴解 問題' + (i + 1),
    it.part || '聞いて答える', '話を聞いて、質問に答えなさい。',
    { group: '聴解', items: [it] }));
  const total = kv.length + gr.length + rd.reduce((a, r) => a + r.qi.length, 0) + ch.length;
  const NAME = course === 'shinjin' ? '新人コース' : 'N2コース';
  return {
    no: w, title: NAME + '　第' + w + '週のテスト', level: lv,
    minutes: { '言語知識・読解': 20, '聴解': 6 },
    counts: { 言語知識: kv.length + gr.length,
              読解: rd.reduce((a, r) => a + r.qi.length, 0),
              聴解: ch.length, 合計: total },
    parts: [
      { name: '言語知識・読解', minutes: 20,
        sections: order.filter(k => !k.startsWith('聴解')),
        next: '聴解へ進む（約6分）',
        lead: '**その週に習った分だけ**から出ています。20分の目安です。' },
      { name: '聴解', minutes: 6, sections: order.filter(k => k.startsWith('聴解')),
        lead: 'まず1回で答えてみてください。' },
    ],
    order, sections: S,
  };
}

async function main() {
  const [course, arg] = process.argv.slice(2);
  if (!course || !arg) {
    console.log('使い方: node tools/weektest.mjs <shinjin|n2> <週番号|all>');
    process.exit(1);
  }
  const kw = J('kanji-weeks.json').courses[course];
  const gw = J('bunpo/weeks.json').courses[course].weeks;
  /* **文型がまだ無い週（新人コース第1〜4週）も作る。**
     その週は漢字・語彙だけなので、文型のぶんを漢字・語彙で埋める。 */
  const hasAny = w => (gw[String(w)] || []).length ||
                      (kw.vocab[String(w)] || []).length;
  const weeks = arg === 'all'
    ? [...new Set(Object.keys(gw).concat(Object.keys(kw.vocab)).map(Number))]
        .filter(hasAny).sort((a, b) => a - b)
    : [Number(arg)];

  const b = await chromium.launch({ executablePath: CHROME });
  const ctx = await b.newContext({ viewport: { width: 400, height: 900 } });
  await ctx.addInitScript(h => { try { localStorage.setItem('jlpt-kanji-gate-v1', h); } catch (e) {} }, HASH);
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  await page.goto(BASE + '/kanji.html');
  await page.waitForTimeout(3000);

  let bad = 0;
  for (const w of weeks) {
    const lv = levelOf(course, w);
    const gr = gramQs(course, w, N.gram);
    /* 文型が無い週は、そのぶんを漢字・語彙で埋める */
    const wantKv = N.kv + (gr.length ? 0 : N.gram);
    const kv = await kvQs(page, kw, w, wantKv, w * 7919 + (course === 'n2' ? 101 : 1));
    const rd = readQs(lv, w, N.read);
    const ch = chouQs(lv, w, N.chou);
    const paper = build(course, w, lv, kv, gr, rd, ch);
    const n = paper.counts.合計;
    const f = 'moshi/w-' + course + '-' + w + '.json';
    fs.writeFileSync(R + f, JSON.stringify(paper, null, 1) + '\n');
    const ok = n >= 12;   /* 作れる問題の数は週によって違う */
    if (!ok) bad++;
    console.log('第%s週 %s  漢字語彙%d 文型%d 読解%d 聴解%d ＝ %d問  %s',
      String(w).padStart(2), lv, kv.length, gr.length,
      rd.reduce((a, r) => a + r.qi.length, 0), ch.length, n, ok ? '' : '← 少ない');
  }
  await b.close();
  if (errs.length) { console.log('!! 画面のJSエラー:', errs[0]); process.exit(1); }
  if (bad) { console.log('× 15問に届かない週が %d あります。', bad); process.exit(1); }
  console.log('できました（%d週ぶん）', weeks.length);
}
main();
