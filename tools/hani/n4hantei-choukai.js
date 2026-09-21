/* N4到達度判定テストの聴解12問を、診断テストの読み上げ画面（shindan/index.html）
 * に 第3のセットとして 入れる。
 *
 *   node tools/hani/n4hantei-choukai.js
 *
 * 問題は n4hantei-data.js の 1か所だけに ある。紙の冊子も この画面も そこから作るので、
 * 片方だけ 古くなる ことが ない。
 */
'use strict';
const fs = require('fs');
const D = require(__dirname + '/n4hantei-data.js');
const PAGE = __dirname + '/../../shindan/index.html';

const N = ['1', '2', '3', '4'];

/* 原稿の 1行を、画面の形に 変える。
   「先輩：〜」のように 役が 付いている行は line、
   役が 無い行（場面の 説明）は q として 読ませる。 */
function toSteps(kind, x, qno) {
  const steps = [];
  const lines = String(x.script).split('\n').map(s => s.trim()).filter(Boolean);
  lines.forEach((ln, i) => {
    const m = ln.match(/^([^：:]{1,6})[：:](.+)$/);
    if (m) steps.push({ k: 'line', sp: m[1], v: m[2].trim() });
    else steps.push({ k: 'q', v: ln });
    /* 場面の 説明の あとは、質問を 読む前に 少し 間を あける */
    if (i === 0 && !m) steps.push({ k: 'pause', s: 2 });
  });
  /* 課題理解・ポイント理解は、会話の あとに もう一度 質問を 読む（本番と 同じ） */
  if (x.q) steps.push({ k: 'q', v: x.q });
  /* 発話表現・即時応答は、選択肢も 読み上げる */
  if (!x.q) x.opts.forEach((o, i) => steps.push({ k: 'line', sp: N[i], v: o }));
  steps.push({ k: 'pause', s: 8, a: true });
  return steps;
}

const GROUPS = [
  ['課題理解', '問題1　課題理解'],
  ['ポイント理解', '問題2　ポイント理解'],
  ['発話表現', '問題3　発話表現'],
  ['即時応答', '問題4　即時応答']
];

/* 紙の冊子は 1番から 通しで 番号を ふる。聴解は その続きなので、
   前の 部の 問題数を 数えて、同じ番号に そろえる（職員が 見くらべるため）。 */
const BEFORE = D.P1.length + D.P2.length + D.P3.length + D.P4.length
  + D.P5.length + D.P6.length + D.P7.items.length
  + D.P8.reduce((s2, p2) => s2 + p2.items.length, 0);

let n = 0;
const groups = GROUPS.map(([key, title]) => ({
  group: title,
  items: D.P9[key].map(x => {
    n++;
    return {
      no: '問' + (BEFORE + n),
      answer: N[x.ans] + '　' + x.opts[x.ans],
      why: x.why || '',
      steps: toSteps(key, x, n)
    };
  })
}));

const SET = { when: 'N4到達度判定テスト（第12週・2月末）', groups: groups };

/* ---- ページに 入れる ---- */
let src = fs.readFileSync(PAGE, 'utf8');

/* ① データ。既に n4 が あれば 入れ替える */
const m = src.match(/var DATA = (\{[\s\S]*?\});\n/);
if (!m) { console.error('DATA が 見つかりません'); process.exit(1); }
const data = JSON.parse(m[1]);
data.n4 = SET;
src = src.replace(m[0], 'var DATA = ' + JSON.stringify(data) + ';\n');

/* ② ボタン。無ければ 足す */
const btn = '<button class="btn" data-set="n4" id="sn4">N4到達度判定（12月・問55〜66）</button>';
if (src.indexOf('data-set="n4"') < 0) {
  const anchor = '<button class="btn" data-set="2" id="s2">第2回（3月）</button>';
  if (src.indexOf(anchor) < 0) { console.error('ボタンの場所が 見つかりません'); process.exit(1); }
  src = src.replace(anchor, anchor + '\n      ' + btn);
}

fs.writeFileSync(PAGE, src);
console.log('読み上げ画面に N4到達度判定の聴解 ' + n + '問を 入れた（問'
  + (BEFORE + 1) + '〜問' + (BEFORE + n) + '。紙の冊子と 同じ番号）');
