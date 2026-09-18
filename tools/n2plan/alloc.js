/* N2ロードマップの週ごとの学習範囲を決める。
   第1週の月曜＝2026-08-31。本試験＝2027-12-05（日）。全66週。
   考え方は新人コースの学習範囲表と同じ。
   語彙は「その週に習う漢字を使う語を同じ週に置く」（A案）。 */
const fs = require('fs');
const R = '/home/user/owltiger1021/';
const kd = JSON.parse(fs.readFileSync(R+'kanji-data.json','utf8')).kanji;
const vw = JSON.parse(fs.readFileSync(R+'vocab-data.json','utf8')).words;
const gramFiles = ['grammar-n5.json','grammar-n4.json','grammar-n3.json','grammar-n2.json','grammar-kiroku.json'];
let gAll = [];
gramFiles.forEach(f => { gAll = gAll.concat(JSON.parse(fs.readFileSync(R+'bunpo/'+f,'utf8')).grammar); });

const isN2 = x => x.level === 'N2' || (x.also||[]).includes('N2');
const f = x => x.freq || 9999;
const kN2 = kd.filter(k => isN2(k) && k.level === 'N2').sort((a,b) => f(a)-f(b) || a.character.localeCompare(b.character));
const kKaigoN2 = kd.filter(k => k.level !== 'N2' && isN2(k));   /* 介護・N3の札で入っている46+1字 */
const vN2 = vw.filter(w => w.level === 'N2');
const gN2 = gAll.filter(isN2);
/* 第0期のN3見直しは、N2の札を持たない61項目だけにする。
   N2の札を持つ89項目は第1期でN2として学ぶので、二度置かない。 */
const gN3 = gAll.filter(x => x.level === 'N3' && !(x.also||[]).includes('N2'));
const kN3 = kd.filter(k => k.level === 'N3').sort((a,b) => f(a)-f(b));

/* ---- 期（フェーズ）。週番号で区切る ---- */
const PH = [
 {no:0, name:'診断・移行期',     from:1,  to:5,  aim:'診断テストで現在地を知り、N3の土台を点検する'},
 {no:1, name:'基礎構築期',       from:6,  to:22, aim:'N2の漢字・語彙・文型をひととおり「覚えた」にする'},
 {no:2, name:'実戦力養成期',     from:23, to:39, aim:'読解を主軸に演習量を増やし、聴解を本格的に始める'},
 {no:3, name:'模試・仕上げ期①', from:40, to:48, aim:'模試で弱点を洗い出し、その場で補強する'},
 {no:4, name:'最終追い込み期',   from:49, to:65, aim:'区分別に基準点（各19点）を安全圏へ。時間配分を固める'},
 {no:5, name:'直前期',           from:66, to:66, aim:'新しい教材は開かない。既出の高速回転のみ'},
];
const phaseOf = w => PH.find(p => w >= p.from && w <= p.to);

function split(total, weeks){
  const base = Math.floor(total/weeks), rest = total % weeks;
  return Array.from({length:weeks}, (_,i) => base + (i < rest ? 1 : 0));
}
const isKanji = c => /[一-鿿]/.test(c);
const charsOf = w => [...(w.word||'')].filter(isKanji);

const plan = {};   /* 週 → {kanji, vocab, gram, task[]} */
for (let w = 1; w <= 66; w++) plan[w] = {kanji:[], vocab:[], gram:[], task:[]};

/* ---- 第0期（1〜5週）：診断とN3の点検 ---- */
{
  const w = [1,2,3,4,5];
  let i = 0;
  split(gN3.length, 5).forEach((n,k) => { plan[w[k]].gram = gN3.slice(i, i+n); i += n; });
  i = 0;
  split(kN3.length, 5).forEach((n,k) => { plan[w[k]].kanji = kN3.slice(i, i+n); i += n; });
  plan[1].task.push('N2診断テスト（29問）を受ける。結果を弱点マップに書く');
  plan[5].task.push('弱点マップを見直し、第1期でどこに時間をかけるか決める');
  w.forEach(x => plan[x].task.push('N3の見直し。すでに「覚えた」印のものは飛ばしてよい'));
}

/* ---- 第1期（6〜23週・18週）：N2の漢字・語彙・文型 ---- */
{
  const w = []; for (let x = 6; x <= 22; x++) w.push(x);
  let i = 0;
  split(kN2.length, w.length).forEach((n,k) => { plan[w[k]].kanji = kN2.slice(i, i+n); i += n; });
  i = 0;
  split(gN2.length, w.length).forEach((n,k) => { plan[w[k]].gram = gN2.slice(i, i+n); i += n; });
  /* 語彙はA案：その週の漢字を使う語を同じ週に。
     かな・カタカナだけの語は、どの週の漢字とも結びつかない。
     「足りない分を埋める」形にすると、足りなくなった週にまとめて落ち、
     その週がかなだらけになる。だから先に毎週の取り分を決めておく。 */
  const rest = vN2.slice(), used = new Set();
  const counts = split(vN2.length, w.length);
  const kanaAll = vN2.filter(it => charsOf(it).length === 0).length;
  const kanaPer = split(Math.round(kanaAll * counts.reduce((a,b)=>a+b,0) / vN2.length), w.length);
  w.forEach((x, wi) => {
    const want = counts[wi];
    const learned = new Set();
    for (let y = 1; y <= x; y++) (plan[y].kanji||[]).forEach(k => learned.add(k.character));
    kKaigoN2.forEach(k => learned.add(k.character));   /* 介護で既習の46字も読める */
    const thisWeek = new Set((plan[x].kanji||[]).map(k => k.character));
    const pick = [];
    const take = (test, limit) => {
      const cap = limit === undefined ? want : Math.min(want, pick.length + limit);
      for (let j = 0; j < rest.length && pick.length < cap; j++){
        const it = rest[j];
        if (used.has(it.word)) continue;
        if (!test(it)) continue;
        pick.push(it); used.add(it.word); rest.splice(j,1); j--;
      }
    };
    take(it => charsOf(it).length === 0, kanaPer[wi]);
    take(it => charsOf(it).some(c => thisWeek.has(c)));
    take(it => { const c = charsOf(it); return c.length && c.every(y => learned.has(y)); });
    take(() => true);
    plan[x].vocab = pick;
  });
  plan[6].task.push('第1期はじめ。1日の使い方を決める（公休90分・日勤30〜40分・早出40分）');
  plan[22].task.push('到達度確認テスト。区分ごとに何点取れるか見る');
}
/* ---- 第2期（23〜39週）：読解を主軸に ---- */
{
  /* 第2期で使うのは、はじめに書いた15本まで。
     あとから書き足した n2-16 以降は 第4期で使うので、ここでは取らない。 */
  const rd = JSON.parse(fs.readFileSync(R+'dokkai/reading-n2.json','utf8')).passages
               .filter(p => Number(p.id.split('-')[1]) <= 15);
  for (let x = 23; x <= 39; x++){
    const i = x - 23;
    if (i < rd.length) plan[x].task.push('読解 N2を1本（' + rd[i].type + '「' + rd[i].title + '」）。時間を計る（15〜25分）');
    else plan[x].task.push('読解 N2の見直し。まちがえた設問だけをもう一度');
    plan[x].task.push('読解 N3を1本、速さの練習として（10分。短文3分・中文4分30秒が目安）');
    plan[x].task.push('聴解 週6問。2日に分けて 1日15分（N2の統合理解から始め、終わったらN3を「ふつう」の速さで）');
    /* ここまでで 週75分ほど。第2期は新しく覚えるものが無く、週の予算
       （370〜410分）が大きく余る。余りを「要復習」に固定して、
       何をどれだけ回すかを はっきりさせる。 */
    plan[x].task.push('語彙の「要復習」を 1日60語');
    plan[x].task.push('文型の「要復習」を 1日10項目');
  }
  plan[23].task.unshift('第2期はじめ。公休90分の使い方を決める（読解25分＋読解N3 10分＋聴解15分＋要復習40分）');
  plan[32].task.push('読解と聴解を、本番の速さで通してみる（模試は第3期から）');
}
/* ---- 第3期（40〜48週）：模試と補強 ----
   以前は「弱点の区分を埋める」の2行が9週とも同じで、中身が無かった。
   2026年9月に155分の模試を3回分（moshi/）作り、
   「受ける → まちがいを埋める」を3回くり返す形にした。 */
{
  const rounds = [
    [40, 41, 42, '①'],
    [43, 44, 45, '②'],
    [46, 47, 48, '③'],
  ];
  rounds.forEach(function(r){
    const [w1, w2, w3, no] = r;
    plan[w1].task.push('模試' + no + 'を 受ける（本番と同じ155分。土曜に通しで）');
    plan[w1].task.push('区分ごとの点（言語知識・読解・聴解）を 記録する');
    plan[w2].task.push('模試' + no + 'の まちがい直し（言語知識）。文字・語彙と文型の「要復習」に印を付ける');
    plan[w3].task.push('模試' + no + 'の まちがい直し（読解・聴解）。読解は もう一度 時間を計って解く');
    [w1, w2, w3].forEach(function(w){ plan[w].task.push('聴解 毎日10分（本番の速さ）'); });
  });
  plan[48].task.push('3回の点の動きを 並べて 見る。19点に とどかない区分が 残っていないか');
}
/* ---- 第4期（49〜65週）：新しい読解20本・聴解30問で仕上げる ----
   以前は「要復習をすべて回す」だけで、17週分の中身がなかった。
   （読解15本・聴解9問が第2期で尽きていたため。）
   2026年9月に読解を20本・聴解を30問 書き足し、この期に配った。
   100日コースはN3の教材なので、ここには置かない。 */
{
  const rd = JSON.parse(fs.readFileSync(R+'dokkai/reading-n2.json','utf8')).passages
               .filter(p => Number(p.id.split('-')[1]) >= 16);          /* 新しい20本 */
  const html = fs.readFileSync(R+'choukai/index.html','utf8');
  const a = html.indexOf('const DATA = ['), b = html.indexOf('\n];', a);
  /* 第3期の模試で、N2の聴解は ひととおり 聞いている。
     第4期は その二周目なので、N2の7パート すべてを 配る。 */
  const DATA = JSON.parse(html.slice(a + 'const DATA = '.length, b + 2))
                 .filter(p => p.level === 'N2');
  /* 同じ音声の問題は ひとかたまりにする（問1と問2を別の週に分けないため） */
  const units = [];
  DATA.forEach(p => {
    const title = p.title.split('―')[0].trim();
    let cur = [];
    p.items.forEach((it, qi) => {
      if (it.sameAudioAs != null && cur.length) cur.push(qi + 1);
      else { if (cur.length) units.push([p.no, title, cur]); cur = [qi + 1]; }
    });
    if (cur.length) units.push([p.no, title, cur]);
  });
  const weeks = []; for (let x = 49; x <= 65; x++) weeks.push(x);
  const split = (t, n) => { const b = Math.floor(t/n), r = t % n;
    return Array.from({length:n}, (_, k) => b + (k < r ? 1 : 0)); };
  const rcut = split(rd.length, weeks.length), ccut = split(units.length, weeks.length);
  const cycle = ['漢字・語彙','漢字・語彙','漢字・語彙','漢字・語彙','文型','文型','文型','文型'];
  let ri = 0, ci = 0;
  weeks.forEach((x, n) => {
    for (let t = 0; t < rcut[n]; t++){
      const p = rd[ri++];
      /* n2-16〜n2-30 は 第3期の模試で 初見で解いている。第4期は その二周目。 */
      const num = Number(p.id.split('-')[1]);
      const tail = (num <= 30) ? '）。模試で解いた文章の二周目' : '）。時間を計る';
      plan[x].task.push('読解 N2を1本（' + p.type + '「' + p.title + '」' + tail);
    }
    const take = units.slice(ci, ci + ccut[n]); ci += ccut[n];
    const byp = new Map();
    take.forEach(([no, title, qs]) => {
      const key = no + '\u0000' + title;
      byp.set(key, (byp.get(key) || []).concat(qs));
    });
    byp.forEach((qs, key) => {
      const [no, title] = key.split('\u0000');
      const rng = qs.length > 2 ? (qs[0] + '〜' + qs[qs.length - 1]) : qs.join('・');
      plan[x].task.push('聴解 ' + no + '（' + title + '）の 問' + rng + '（模試で聞いた問題の二周目）');
    });
    plan[x].task.push(cycle[n % cycle.length] + 'の「要復習」を 回す');
    plan[x].task.push('まちがえた問題だけを、もう一度');
    plan[x].task.push('土曜は本番と同じ155分で通し演習');
  });
  if (ri !== rd.length || ci !== units.length) throw new Error('第4期の配り残し ' + ri + '/' + ci);
  plan[54].task.push('模試④（区分ごとに19点を超えているか見る）');
  plan[58].task.push('模試⑤');
  plan[62].task.push('模試⑥（最後の本番形式）');
}
/* ---- 第5期（66週）：直前 ---- */
plan[66].task.push('新しい教材は開かない。まちがえた問題と、覚えた印のない語だけを見る');
plan[66].task.push('前日は勉強しない。持ち物と会場・時間を確かめる');
plan[66].task.push('12月5日（日）本試験');

fs.writeFileSync('/tmp/n2plan/plan.json', JSON.stringify({plan, PH}));

/* ---- 点検 ---- */
let kt=0, vt=0, gt=0;
const seen={k:new Set(), v:new Set(), g:new Set()};
const bad=[];
for (let w=1; w<=66; w++){
  plan[w].kanji.forEach(k => { kt++; if(seen.k.has(k.character)) bad.push('漢字重複 '+k.character); seen.k.add(k.character); });
  plan[w].vocab.forEach(v => { vt++; if(seen.v.has(v.word)) bad.push('語彙重複 '+v.word); seen.v.add(v.word); });
  plan[w].gram.forEach(g => { gt++; if(seen.g.has(g.id)) bad.push('文型重複 '+g.id); seen.g.add(g.id); });
}
console.log('第0期 N3見直し：漢字'+kN3.length+'字・文型'+gN3.length+'項目');
console.log('第1期 N2：漢字'+kN2.length+'字・語彙'+vN2.length+'語・文型'+gN2.length+'項目');
console.log('割り当て合計：漢字'+kt+'／語彙'+vt+'／文型'+gt+'　重複:'+(bad.length?bad.slice(0,3):'なし'));
let hit=0, tot=0;
for (let w=6; w<=22; w++){
  const tw = new Set(plan[w].kanji.map(k=>k.character));
  plan[w].vocab.forEach(v => { tot++; if(charsOf(v).some(c=>tw.has(c))) hit++; });
}
console.log('第1期：その週の漢字を使う語 '+hit+'/'+tot+'語（'+Math.round(hit/tot*100)+'%）');
/* 読める語（その週の漢字＋それまでに習った漢字＋かな語）の割合 */
let ok=0, all=0;
const learnedAll = new Set();
kKaigoN2.forEach(k => learnedAll.add(k.character));
kd.filter(k => ['N5','N4','N3'].includes(k.level)).forEach(k => learnedAll.add(k.character));
for (let w=6; w<=22; w++){
  plan[w].kanji.forEach(k => learnedAll.add(k.character));
  plan[w].vocab.forEach(v => { all++; const c = charsOf(v); if (!c.length || c.every(x => learnedAll.has(x))) ok++; });
}
console.log('第1期：その週までに習った漢字だけで読める語 '+ok+'/'+all+'語（'+Math.round(ok/all*100)+'%）');
console.log('週ごとの数（第1期の例）：');
[6,10,15,20,22].forEach(w => console.log('  第'+w+'週  漢字'+plan[w].kanji.length+'　語彙'+plan[w].vocab.length+'　文型'+plan[w].gram.length));
