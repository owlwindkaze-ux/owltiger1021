const fs = require('fs');
const R = '/home/user/owltiger1021/';
const kd = JSON.parse(fs.readFileSync(R+'kanji-data.json','utf8')).kanji;
const vw = JSON.parse(fs.readFileSync(R+'vocab-data.json','utf8')).words;
const gN4 = JSON.parse(fs.readFileSync(R+'bunpo/grammar-n4.json','utf8')).grammar;
const gN3 = JSON.parse(fs.readFileSync(R+'bunpo/grammar-n3.json','utf8')).grammar;

const f = x => x.freq || 9999;
const byFreq = lv => kd.filter(k => k.level === lv).sort((a,b) => f(a)-f(b) || a.character.localeCompare(b.character));

/* ---- 漢字：週ごとに何字ずつか ---- */
function split(total, weeks){          /* できるだけ均等に分ける */
  const base = Math.floor(total/weeks), rest = total % weeks;
  return Array.from({length:weeks}, (_,i) => base + (i < rest ? 1 : 0));
}
const kanjiPlan = {};                  /* 週 → 漢字の配列 */
(function(){
  const n5 = byFreq('N5'), n4 = byFreq('N4'), n3 = byFreq('N3');
  let i = 0;
  split(n5.length, 4).forEach((n,w) => { kanjiPlan[w+1] = n5.slice(i, i+n); i += n; });
  i = 0;
  split(n4.length, 8).forEach((n,w) => { kanjiPlan[w+5] = n4.slice(i, i+n); i += n; });
  i = 0;
  split(n3.length, 18).forEach((n,w) => { kanjiPlan[w+13] = n3.slice(i, i+n); i += n; });
})();

/* ---- 語彙：A案（その週の漢字を使う語を同じ週に置く） ---- */
const isKanji = c => /[一-鿿]/.test(c);
const charsOf = w => [...(w.word||'')].filter(isKanji);
const vocabPlan = {};
(function(){
  /* 第1〜4週：N5語彙から週50語。第5〜12週：N4語彙662語を全部 */
  /* ---- N3語彙のえらび方 ----
     N3の語彙は2,078語あるが、全部を18週で配ると平日1日24語になり、
     漢字21字・文型8項目と合わせて続かない。そこで1,000語に絞る。
     絞り方は「読めるかどうか」を軸にした：
       ① この30週で習う漢字（N5+N4+N3の613字）だけでできている語に限る（1,171語）。
          習わない漢字を含む語は、読めないので覚えようがない。
       ② そのうち、介護・現場の印がついた語、分野名のついた語、基本語、カタカナ語は必ず残す。
       ③ 残りは、語をつくる漢字の頻度順位の平均が小さい順（＝よく使う字でできている順）に、
          1,000語になるまで取る。 */
  const N3W = (function(){
    const rank = {};                       /* 漢字 → 頻度順位。習う字だけ */
    kd.forEach(k => { if (['N5','N4','N3'].includes(k.level)) rank[k.character] = k.freq || 9999; });
    const readable = vw.filter(w => w.level === 'N3' && charsOf(w).every(c => c in rank));
    const keep = w => w.care || w.workplace ||
      (w.category && !['カタカナ語','基本語'].includes(w.category)) ||
      w.category === '基本語' || w.category === 'カタカナ語';
    const must = readable.filter(keep);
    const restN3 = readable.filter(w => !keep(w)).sort((a,b) => {
      const av = charsOf(a), bv = charsOf(b);
      const am = av.length ? av.reduce((s,c)=>s+rank[c],0)/av.length : 0;   /* かなだけの語は先に */
      const bm = bv.length ? bv.reduce((s,c)=>s+rank[c],0)/bv.length : 0;
      return am - bm || a.word.localeCompare(b.word);
    });
    const out = must.concat(restN3).slice(0, 1000);
    console.log('N3語彙：読める語', readable.length, '→ 必ず残す', must.length,
                '＋ よく使う字の語', out.length - must.length, '＝', out.length, '語');
    return out;
  })();

  const pools = [
    { weeks:[1,2,3,4],           per:50, list: vw.filter(w => w.level==='N5') },
    { weeks:[5,6,7,8,9,10,11,12], per:null, list: vw.filter(w => w.level==='N4') },
    { weeks:[13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30], per:null, list: N3W }
  ];
  pools.forEach(pool => {
    const used = new Set();
    const rest = pool.list.slice();
    const counts = pool.per ? pool.weeks.map(() => pool.per)
                            : split(pool.list.length, pool.weeks.length);
    /* かな・カタカナだけの語は、どの週の漢字とも結びつかない。
       「①②で足りない分を埋める」形にすると、足りなくなった週に
       まとめて落ちてしまい、その週がかなだらけになる。
       そこで、あらかじめ毎週の取り分を決めて、先に取っておく。 */
    /* 取り分は、その期に実際に取る語数に合わせて決める。
       プール全体の数で決めると、一部しか取らない期（N5の200語など）で
       かな語ばかりになってしまう。 */
    const kanaAll = pool.list.filter(it => charsOf(it).length === 0).length;
    const takeTotal = counts.reduce((a,b) => a+b, 0);
    const kanaQuota = Math.round(kanaAll * takeTotal / pool.list.length);
    const kanaPer = split(kanaQuota, pool.weeks.length);
    pool.weeks.forEach((w, wi) => {
      const want = counts[wi];
      const learned = new Set();       /* その週までに習う漢字 */
      for (let x = 1; x <= w; x++) (kanjiPlan[x]||[]).forEach(k => learned.add(k.character));
      const thisWeek = new Set((kanjiPlan[w]||[]).map(k => k.character));
      const pick = [];
      const take = (test, limit) => {
        const cap = limit === undefined ? want : Math.min(want, pick.length + limit);
        for (let j = 0; j < rest.length && pick.length < cap; j++) {
          const it = rest[j];
          if (used.has(it.word)) continue;
          if (!test(it)) continue;
          pick.push(it); used.add(it.word); rest.splice(j,1); j--;
        }
      };
      /* ⓪ かな語の取り分を先に　① その週の漢字を使う語
         ② そこまでに習った漢字だけで書ける語　③ 残り */
      take(it => charsOf(it).length === 0, kanaPer[wi]);
      take(it => charsOf(it).some(c => thisWeek.has(c)));
      take(it => { const c = charsOf(it); return c.length && c.every(x => learned.has(x)); });
      take(() => true);
      vocabPlan[w] = pick;
    });
  });
})();

/* ---- 文型 ---- */
const gramPlan = {};
(function(){
  let i = 0;
  split(gN4.length, 8).forEach((n,w) => { gramPlan[w+5] = gN4.slice(i, i+n); i += n; });
  i = 0;
  split(gN3.length, 18).forEach((n,w) => { gramPlan[w+13] = gN3.slice(i, i+n); i += n; });
})();

/* ---- 点検 ---- */
let kt=0, vt=0, gt=0, bad=[];
const seenK=new Set(), seenV=new Set(), seenG=new Set();
for (let w=1; w<=30; w++){
  (kanjiPlan[w]||[]).forEach(k => { kt++; if(seenK.has(k.character)) bad.push('漢字重複 '+k.character); seenK.add(k.character); });
  (vocabPlan[w]||[]).forEach(v => { vt++; if(seenV.has(v.word)) bad.push('語彙重複 '+v.word); seenV.add(v.word); });
  (gramPlan[w]||[]).forEach(g => { gt++; if(seenG.has(g.id)) bad.push('文型重複 '+g.id); seenG.add(g.id); });
}
console.log('漢字', kt, '字 ／ 語彙', vt, '語 ／ 文型', gt, '項目');
console.log('重複など:', bad.length ? bad.slice(0,5) : 'なし');
console.log('---- 週ごとの数 ----');
for (let w=1; w<=30; w++){
  const k=(kanjiPlan[w]||[]).length, v=(vocabPlan[w]||[]).length, g=(gramPlan[w]||[]).length;
  if(w<=13 || w===20 || w===30) console.log(' 第'+String(w).padStart(2)+'週  漢字'+String(k).padStart(3)+'  語彙'+String(v).padStart(3)+'  文型'+String(g).padStart(3));
}
/* 連動がどれくらい効いたか */
let hit=0, tot=0;
for (let w=5; w<=12; w++){
  const thisWeek = new Set((kanjiPlan[w]||[]).map(k=>k.character));
  (vocabPlan[w]||[]).forEach(v => { tot++; if(charsOf(v).some(c=>thisWeek.has(c))) hit++; });
}
console.log('第5〜12週：その週の漢字を使う語が', hit, '/', tot, '語（'+Math.round(hit/tot*100)+'%）');
let h2=0, t2=0;
for (let w=13; w<=30; w++){
  const thisWeek = new Set((kanjiPlan[w]||[]).map(k=>k.character));
  (vocabPlan[w]||[]).forEach(v => { t2++; if(charsOf(v).some(c=>thisWeek.has(c))) h2++; });
}
console.log('第13〜30週：その週の漢字を使う語が', h2, '/', t2, '語（'+Math.round(h2/t2*100)+'%）');
fs.writeFileSync('/tmp/hani/plan.json', JSON.stringify({kanjiPlan, vocabPlan, gramPlan}));
