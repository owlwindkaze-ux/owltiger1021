const fs = require('fs');
const OUT = '/tmp/shindan/out';
fs.mkdirSync(OUT, { recursive: true });

/* ---------- 正解の位置をばらす（種を固定しているので毎回同じ結果） ---------- */
function rng(seed) { let a = seed >>> 0; return () => (a = (a * 1664525 + 1013904223) >>> 0) / 4294967296; }
function permute(n, r) {                     // 0..n-1 の並べ替えを返す
  const a = [...Array(n).keys()];
  for (let i = n - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}
function shuffleQ(q, r) {
  if (q.kind === 'sort') {
    const p = permute(q.parts.length, r);            // 新しい位置 → 元の位置
    const back = []; p.forEach((old, ni) => back[old] = ni);
    q.parts = p.map(old => q.parts[old]);
    q.order = q.order.map(o => back[o - 1] + 1);     // 正しい文の並び（新しい番号で）
    q.ans = q.order[q.star - 1];
    return;
  }
  if (!q.opts || q.opts.length < 2) return;
  const p = permute(q.opts.length, r);
  const old = q.opts, oldAns = q.ans;
  q.opts = p.map(i => old[i]);
  q.ans = p.indexOf(oldAns - 1) + 1;
}
function walk(set) {
  const r = rng(20261207 + set.no * 7919);
  [set.p1, set.p2].forEach(part => part.groups.forEach(g => g.items.forEach(q => shuffleQ(q, r))));
  set.p3.passages.forEach(p => p.items.forEach(q => shuffleQ(q, r)));
  /* 聴解は台本と選択肢の文言をそろえる必要があるので、並べ替えたあとに答えの文字列を作り直す */
  const flat = [];
  set.p4.groups.forEach(g => g.items.forEach(q => { shuffleQ(q, r); flat.push(q); }));
  let i = 0;
  set.listen.forEach(g => g.items.forEach(it => {
    const q = flat[i++];
    if (q.opts.length === 4) it.answer = q.ans + '　' + q.opts[q.ans - 1];
    else it.answer = String(q.ans);
  }));
}

/* ---------- 点検 ---------- */
function check(set) {
  const bad = [];
  const eachQ = fn => {
    [set.p1, set.p2, set.p4].forEach(part => part.groups.forEach(g => g.items.forEach(q => fn(q, part.title))));
    set.p3.passages.forEach(p => p.items.forEach(q => fn(q, set.p3.title)));
  };
  eachQ((q, t) => {
    const n = q.kind === 'sort' ? q.parts.length : q.opts.length;
    if (!(Number.isInteger(q.ans) && q.ans >= 1 && q.ans <= n)) bad.push(t + '/' + q.id + ' 正解が範囲外');
    const list = q.kind === 'sort' ? q.parts : q.opts;
    if (new Set(list.map(x => String(x).trim())).size !== list.length) bad.push(t + '/' + q.id + ' 選択肢が重複');
    if (!q.kind && !q.why && !/聴解/.test(t)) bad.push(t + '/' + q.id + ' 解説なし');
  });
  /* 並べ替えは、正しい順に並べた文が意味の通る1文になっているか（解説と一致するか）を見る */
  set.p2.groups[1].items.forEach(q => {
    const sent = q.order.map(o => q.parts[o - 1]).join('');
    if (!q.why.includes(sent)) bad.push('第2部/' + q.id + ' 並べ替えの文と解説が不一致：' + sent);
    if (q.ans !== q.order[q.star - 1]) bad.push('第2部/' + q.id + ' ★の答えがずれている');
  });
  /* 聴解：台本の答えと問題用紙の選択肢が一致するか */
  const flat = []; set.p4.groups.forEach(g => g.items.forEach(q => flat.push(q)));
  let i = 0;
  set.listen.forEach(g => g.items.forEach(it => {
    const q = flat[i]; const no = '問' + (i + 1); i++;
    if (it.no !== no) bad.push('聴解 ' + it.no + ' の番号がずれている');
    const m = String(it.answer).match(/^(\d)/);
    if (!m || Number(m[1]) !== q.ans) bad.push('聴解 ' + no + ' 台本と解答の番号が不一致');
    if (q.opts.length === 4) {
      const txt = String(it.answer).replace(/^\d[　 ]*/, '');
      if (q.opts[q.ans - 1].trim() !== txt.trim()) bad.push('聴解 ' + no + ' 選択肢の文言が不一致');
    }
  }));
  if (i !== flat.length) bad.push('聴解の数が合わない 台本' + i + ' 用紙' + flat.length);
  /* 日本語以外の文字 */
  const blob = JSON.stringify(set);
  const ng = blob.match(/[а-яА-ЯёЁ가-힣]/g);
  if (ng) bad.push('日本語以外の文字：' + [...new Set(ng)].join(''));
  return bad;
}

/* ---------- 正解の散らばりを見る ---------- */
function spread(set) {
  const c = {};
  const add = q => { c[q.ans] = (c[q.ans] || 0) + 1; };
  [set.p1, set.p2, set.p4].forEach(p => p.groups.forEach(g => g.items.forEach(add)));
  set.p3.passages.forEach(p => p.items.forEach(add));
  return [1, 2, 3, 4].map(n => n + ':' + (c[n] || 0)).join(' ');
}

const sets = [require('./set1.js'), require('./set2.js')];
sets.forEach(walk);
let ok = true;
sets.forEach(s => {
  const bad = check(s);
  console.log('第' + s.no + '回　不備', bad.length, bad.length ? bad : '');
  console.log('　正解の散らばり', spread(s));
  if (bad.length) ok = false;
});
fs.writeFileSync(OUT + '/sets.json', JSON.stringify(sets));
console.log(ok ? '点検OK' : '★不備あり');
