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
 *   node tools/weektest.mjs shinjin 5
 *   node tools/weektest.mjs shinjin all
 *
 * 先に `python3 -m http.server 8777` を リポジトリの中で 立てておくこと。
 */
import { createRequire } from 'module';
import path from 'path';
import { fileURLToPath } from 'url';

/* **playwright と chromium の置き場所は、入れ直すと変わる。**
   番号つきの道（/opt/pw-browsers/chromium-1194/…）を 書き込んでいたので、
   入れ替わった日に **道具が丸ごと動かなくなった**（2026-10-30）。
   だから **決め打ちにせず、その場で探す**。見つからなければ
   playwright に まかせる（`executablePath` を 渡さない）。
   どうしても 指したいときは PW= と CHROME= で 渡せる。 */
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
  const roots = ['/opt/pw-browsers'];
  const out = [];
  for (const r of roots) {
    let names = [];
    try { names = fs.readdirSync(r); } catch (e) { continue; }
    for (const n of names) {
      if (!n.startsWith('chromium')) continue;
      for (const d of ['chrome-linux', 'chrome-linux64']) {
        const f = r + '/' + n + '/' + d + '/chrome';
        if (fs.existsSync(f)) out.push(f);
      }
    }
  }
  out.sort();                      // 番号が大きい＝新しいものを 使う
  return out.length ? out[out.length - 1] : null;   // 無ければ playwright にまかせる
}
const { chromium } = findPlaywright();

const R = path.dirname(path.dirname(fileURLToPath(import.meta.url))) + '/';
const BASE = process.env.BASE || 'http://localhost:8777';
const CHROME = findChrome();
const HASH = 'ebec3cabb51c7aed2a0e3b893a08691fbadc9ad0eed58fe3c51ebe75d532a48c';

const J = p => JSON.parse(fs.readFileSync(R + p, 'utf8'));

/* 1週あたりの問題の数。合計20問 */
const N = { kv: 4, gram: 8, read: 4, chou: 4 };

/* ── **復習の週** ───────────────────────────────────────
 * N2コースは **新しい教材が 第22週で 終わる**（第2期からは 読解・聴解と
 * 「要復習」の回しなおし）。ところが **紙の冊子は 第25週まで 続く**
 * （第13単元＝第23週、第14単元＝第24週、12月の月末確認＝第25週）。
 * そのため **紙の単元が ある週に 週テストが 無い**という すき間ができていた。
 * 持ち主の問い「N2の2から14単元で週テストをだせますか」（2026-11-03）。
 *
 * この週は **その週に習う分**が 無いので、**第1週からの 積み上げ**から出す。
 * **新しい問題は やはり1つも書かない。**選び方だけが ちがう。
 * 文型は **その週の紙の単元が ねらう文型を 先に**置く。
 */
const REVIEW = { shinjin: [], n2: [23, 24, 25] };

/* そのコース・その週は どのレベルか（読解・聴解をえらぶのに使う） */
function levelOf(course, w) {
  if (course === 'shinjin') return w <= 4 ? 'N5' : w <= 12 ? 'N4' : 'N3';
  return w <= 20 ? 'N3' : 'N2';          /* N2コースは前半でN3を仕上げる */
}

/* 「〜」の有無・前後の空白だけの ちがいは 同じものとして 見る */
const norm = s => String(s).replace(/[〜～\s]/g, '');

/* その週の **紙の冊子の単元**が ねらう文型。`n2/weeks.json` の `aim` に
   「つつある、にわたって、わけではない」のように 読点で ならべてある。
   見出しの言葉（「根拠を本文から探す」など）は 文型表に 無いので 落ちる。 */
function aimPatterns(course, w) {
  if (course !== 'n2') return [];
  let pw;
  try { pw = J('n2/weeks.json').paper.weeks[String(w)]; } catch (e) { return []; }
  if (!pw || !pw.aim) return [];
  return pw.aim.split(/[、。]/).map(x => x.trim()).filter(Boolean);
}

/* ── 文型 ───────────────────────────────────────────── */
function gramQs(course, w, want) {
  const idx = J('bunpo/grammar.json');
  const all = {};
  for (const f of idx.files)
    for (const g of J('bunpo/' + f.file).grammar) all[g.id] = g;
  const wk = J('bunpo/weeks.json').courses[course].weeks;
  let ids = (wk[String(w)] || []);
  /* **復習の週**は その週ぶんが 無い。第1週からの 積み上げを使い、
     **その週の紙の単元が ねらう文型を 先に**置く。
     順番は 週ごとに ずらす（毎週 同じ10項目では 復習にならない）。 */
  if (!ids.length && REVIEW[course].includes(w)) {
    const cum = [];
    for (let i = 1; i < w; i++) for (const id of (wk[String(i)] || [])) cum.push(id);
    const uniq = [...new Set(cum)];
    const head = [];
    for (const p of aimPatterns(course, w)) {
      /* 文型の名前は「〜にわたって／〜にわたる」のように **／で2つ**書いてある
         ことがある。まるごと くらべると 当たらない（第23週で にわたって が
         落ちた・2026-11-03）。／で 割って 片方ずつ くらべる。 */
      /* **同じ名前の文型が N3とN2に 両方ある。**「〜にわたって」は
         n3-026 と n2-ni-watatte の2つ。先に見つかったほうを 取ると、
         そのコースが 習っていない側に 当たって 落ちる（2026-11-03）。
         **習った側（積み上げの中にある側）を 選ぶ。** */
      const cands = Object.values(all).filter(
        x => String(x.pattern).split('／').some(y => norm(y) === norm(p)));
      const g = cands.find(x => uniq.includes(x.id));
      if (g) head.push(g.id);
    }
    const rest = uniq.filter(id => !head.includes(id));
    const s = (w * 13) % (rest.length || 1);      /* 週ごとに ずらす */
    ids = head.concat(rest.slice(s), rest.slice(0, s));
  }
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
async function kvQs(page, wk, wv, want, seed) {
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
      /* **HTMLを、模試の画面が分かる書き方に直す。**
         模試の engine は 問題文を **逃がす（エスケープする）**ので、
         `<span class="yomi">…</span>` を そのまま入れると
         **タグが画面にそのまま出る**（2026-10-25c・持ち主が見つけた）。
         engine が分かるのは `漢字《かんじ》` だけ。
         下線は 本番の模試と同じく 全角の ＿ ではさむ。 */
      var plain = function (h) {
        return String(h)
          .replace(/<ruby>([^<]*)<rt[^>]*>([^<]*)<\/rt><\/ruby>/g, '$1《$2》')
          .replace(/<u[^>]*>([^<]*)<\/u>/g, '＿$1＿')
          .replace(/<br\s*\/?>/g, '　／　')
          .replace(/<[^>]+>/g, '')
          .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
          .replace(/[ \t]+/g, ' ').replace(/\s*\n\s*/g, ' ').trim();
      };
      /* note は「語（よみ）＝ 意味（尼語）」の形。**＝ や ： の右は 尼語**なので
         日本語の欄に残さず、`explain_id` へ回す。 */
      var note = q.note || '', ja = note, id = '';
      var cut = note.search(/[＝：]/);
      if (cut >= 0) { ja = note.slice(0, cut).trim(); id = note.slice(cut + 1).trim(); }
      /* **問題文そのものを 付ける。**
         練習問題の画面では、聞いていること（「読み方は？」）は `kind` に入っていて、
         画面が 見出しとして 上に出す。`q` は 手がかり（語・文）だけ。
         それを そのまま 模試の形に 移したので、問が
           問3　perbedaan; ketidaksesuaian
         のように **尼語の手がかりだけ**になり、**何を聞かれているのか 書いていなかった**
         （2026-10-25d・持ち主が見つけた）。
         大問の見出しに 書いてあっても、実習生は 一問ずつ 読む。
         だから **一問ごとに 日本語で 聞くことを 書く**。 */
      var ASK = {
        'kanjiread': 'つぎの漢字の読み方は、どれですか。',
        'reading': '＿＿の言葉の読み方は、どれですか。',
        'orth': 'つぎの言葉を漢字で書くと、どれですか。',
        'context-blank': '（　　　）に入る言葉は、どれですか。',
        'context-mean': 'つぎの意味の言葉は、どれですか。',
        'para': 'だいたい同じ意味の言葉は、どれですか。',
        'usage': 'つぎの言葉の使い方が正しい文は、どれですか。',
        'gokei': '（　）に入るものは、どれですか。'
      };
      var ak = t;
      if (t === 'context') ak = q.kind.indexOf('（　）に入る') >= 0 ? 'context-blank' : 'context-mean';
      /* 尼語の言い方は `kind` の「／」の右に 入っている。そのまま 使う。 */
      var idPart = (q.kind.split('／')[1] || '').trim();
      var body = plain(q.q);
      /* 「意味に合う言葉」の問は 手がかりが **尼語の意味だけ**なので、
         問だけ見ると 尼語しか 書いていない。日本語の枠で くるむ。 */
      if (ak === 'context-mean') body = '「' + body + '」の意味の言葉は、どれですか。';
      out.push({ kind: q.kind, ask: ASK[ak] || 'つぎの問いに答えなさい。', askId: idPart,
                 q: body, choices: q.choices.map(plain),
                 answer: q.choices.indexOf(q.answer), explain: ja, explain_id: id });
    }
    return out.filter(x => x.answer >= 0);
  }, [wk, wv, want, seed]);
}

/* ── 1週ぶんを組み立てる ─────────────────────────────── */
function build(course, w, lv, kv, gr, rd, ch, review) {
  const S = {}, order = [];
  const add = (key, label, name, inst, body, instId) => {
    S[key] = { label, name, inst, ...(instId ? { inst_id: instId } : {}), ...body };
    order.push(key);
  };
  /* **何を聞かれているのかを、問の すぐ上に 日本語で 書く。**
     前は どの大問も「つぎの問いに答えなさい。」だけで、問の中身は
     手がかり（語・尼語の意味）だけだった。だから
       問3　perbedaan; ketidaksesuaian
     のように **聞かれていることが どこにも 書いていなかった**
     （2026-10-25d・持ち主が見つけた）。 */
  kv.forEach((q, i) => add('問題' + (i + 1), '問題' + (i + 1),
    q.kind.split('／')[0].replace(/^問題\d+\s*/, '').trim() || '漢字・語彙',
    q.ask,
    /* `explain_id`（尼語）を 落とさない。ここで項目を 組み直すので、
       `kvQs` が 付けた 欄を 一つでも 書き忘れると 画面から 消える（2026-10-25c）。 */
    { items: [{ q: q.q, choices: q.choices, answer: q.answer,
                explain: q.explain, explain_id: q.explain_id || '' }] }, q.askId));
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
  /* **復習の週は そう書く。**「その週に習った分だけ」と 書いてあるのに
     積み上げから 出ていたら、実習生は 見ていない語が 出たと 思う。 */
  /* **太字は `<b>` で 書く。**模試の画面は `lead` を そのまま HTMLとして 出すので、
     `**…**` と書くと **星印が そのまま 画面に出る**。50本ぜんぶで そうなっていた
     （2026-11-03に 画面で 見つけた）。 */
  const LEAD = review
    ? '<b>第1週からの 積み上げ</b>から出ています。この週は 新しい教材が 無いためです。'
      + '紙の冊子の ねらう文型を 先に 入れています。20分の目安です。'
    : '<b>その週に習った分だけ</b>から出ています。20分の目安です。';
  return {
    no: w, title: NAME + '　第' + w + '週のテスト' + (review ? '（復習）' : ''), level: lv,
    ...(review ? { review: true } : {}),
    minutes: { '言語知識・読解': 20, '聴解': 6 },
    counts: { 言語知識: kv.length + gr.length,
              読解: rd.reduce((a, r) => a + r.qi.length, 0),
              聴解: ch.length, 合計: total },
    parts: [
      { name: '言語知識・読解', minutes: 20,
        sections: order.filter(k => !k.startsWith('聴解')),
        next: '聴解へ進む（約6分）',
        lead: LEAD },
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
    ? [...new Set(Object.keys(gw).concat(Object.keys(kw.vocab)).map(Number)
        .filter(hasAny).concat(REVIEW[course]))].sort((a, b) => a - b)
    : [Number(arg)];

  const b = await chromium.launch(CHROME ? { executablePath: CHROME } : {});
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
    const review = !hasAny(w) && REVIEW[course].includes(w);
    const gr = gramQs(course, w, N.gram);
    /* 文型が無い週は、そのぶんを漢字・語彙で埋める */
    const wantKv = N.kv + (gr.length ? 0 : N.gram);
    /* **復習の週**は その週ぶんの漢字・語彙が 無いので、第1週からの 積み上げを渡す。 */
    let wk = kw.kanji[String(w)] || [], wv = kw.vocab[String(w)] || [];
    if (review) {
      const ak = [], av = [];
      for (let i = 1; i < w; i++) {
        ak.push(...(kw.kanji[String(i)] || []));
        av.push(...(kw.vocab[String(i)] || []));
      }
      wk = [...new Set(ak)]; wv = [...new Set(av)];
    }
    const kv = await kvQs(page, wk, wv, wantKv, w * 7919 + (course === 'n2' ? 101 : 1));
    const rd = readQs(lv, w, N.read);
    const ch = chouQs(lv, w, N.chou);
    const paper = build(course, w, lv, kv, gr, rd, ch, review);
    const n = paper.counts.合計;
    const f = 'moshi/w-' + course + '-' + w + '.json';
    /* **すでにある週は、黙って 書きかえない。**
       種は固定しているが、**もとの語彙・漢字のデータが 増えたり 直ったりすると
       選ばれる語が ずれる**。`all` を かけ直したら 第6〜21週の12本が
       中身ごと 変わった（2026-11-03）。実習生が すでに 受けた週の問題が
       変われば、前に取った点と くらべられない。
       作り直したいときだけ FORCE=1 を 付ける。 */
    if (fs.existsSync(R + f) && !process.env.FORCE) {
      console.log('第%s週 %s  そのまま（すでにあります。作り直すなら FORCE=1）',
        String(w).padStart(2), lv);
      continue;
    }
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
