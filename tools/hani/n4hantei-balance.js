/* 正解の番号の かたよりを 直す。
   選択肢の 並べかえだけを して、文も 正解の中身も 変えない。
   ただし 順番に 意味の ある選択肢（一つ・二つ…／一時・二時…／曜日）は 並べかえない。 */
'use strict';
const fs = require('fs');
const path = __dirname + '/n4hantei-data.js';
let src = fs.readFileSync(path, 'utf8');
const D = require(path);

/* 順番に 意味が あるか */
const ORDERED = [
  /^(一|二|三|四|五|六|七|八|九|十)つ$/,
  /^(午前|午後)?\s*[一二三四五六七八九十]+時/,
  /^[月火水木金土日]曜日$/,
];
const isOrdered = opts => ORDERED.some(re => opts.filter(o => re.test(o)).length >= 3);

let seed = 20270228;
const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;

/* いま どの番号が 何問あるか */
const items = [];
(function walk(o) {
  if (Array.isArray(o)) return o.forEach(walk);
  if (o && typeof o === 'object') {
    if (Array.isArray(o.opts) && typeof o.ans === 'number') items.push(o);
    Object.values(o).forEach(walk);
  }
})(D);

const want = items.length;                     /* 番号ごとの ちょうどよい数 */
const cnt = [0, 0, 0, 0];
const plan = [];
items.forEach(it => {
  if (isOrdered(it.opts)) { cnt[it.ans]++; plan.push(null); return; }
  plan.push(it);
});
/* 並べかえられる問題に、番号を できるだけ 平らに 配る */
const free = plan.filter(Boolean);
const targets = [];
for (let i = 0; i < free.length; i++) targets.push(i % 4);
/* 3択の問題に ④を 当てないよう、あとで 直す */
for (let i = targets.length - 1; i > 0; i--) {
  const j = Math.floor(rnd() * (i + 1));
  [targets[i], targets[j]] = [targets[j], targets[i]];
}
const changes = [];
free.forEach((it, i) => {
  let t = targets[i];
  if (t >= it.opts.length) t = it.opts.length - 1;
  if (t === it.ans) return;
  const opts = it.opts.slice();
  const right = opts[it.ans];
  opts.splice(it.ans, 1);
  opts.splice(t, 0, right);
  changes.push({ before: it.opts.slice(), after: opts, ansBefore: it.ans, ansAfter: t });
  it.opts = opts; it.ans = t;
});

/* ソースの 文字列を 置きかえる */
let n = 0;
changes.forEach(c => {
  const before = 'opts: [' + c.before.map(o => "'" + o.replace(/'/g, "\\'") + "'").join(', ') + ']';
  const after = 'opts: [' + c.after.map(o => "'" + o.replace(/'/g, "\\'") + "'").join(', ') + ']';
  const beforeAns = 'ans: ' + c.ansBefore, afterAns = 'ans: ' + c.ansAfter;
  const idx = src.indexOf(before);
  if (idx < 0) { console.log('見つからない:', before.slice(0, 60)); return; }
  const tailIdx = src.indexOf(beforeAns, idx);
  if (tailIdx < 0 || tailIdx - idx > 400) { console.log('ans が 見つからない:', before.slice(0, 40)); return; }
  src = src.slice(0, idx) + after + src.slice(idx + before.length, tailIdx)
      + afterAns + src.slice(tailIdx + beforeAns.length);
  n++;
});
fs.writeFileSync(path, src);
console.log('並べかえた問題', n, '／ 順番に意味があるので さわらなかった問題',
            items.length - free.length);
