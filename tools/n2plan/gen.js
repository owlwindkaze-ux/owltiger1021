const fs = require('fs');
const D = JSON.parse(fs.readFileSync('/tmp/n2plan/plan.json','utf8'));
const P = D.plan, PH = D.PH;
const W1 = new Date(2026,7,31);            /* 第1週の月曜 = 2026-08-31 */
const mon = w => new Date(W1.getTime() + (w-1)*7*86400000);
const sun = w => new Date(mon(w).getTime() + 6*86400000);
const md = d => (d.getMonth()+1)+'/'+d.getDate();
const esc = s => String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const { withRuby } = require(__dirname + '/../hani/ruby.js');
const R = s => withRuby(esc(s));
const phaseOf = w => PH.find(p => w >= p.from && w <= p.to);
const phName = w => { const p = phaseOf(w); return '第'+p.no+'期　'+p.name; };

const css = `
body{margin:0;font-family:"IPAPGothic","IPAGothic","WenQuanYi Zen Hei",sans-serif;color:#1b2733;font-size:9.5pt;line-height:1.6}
.pg{page-break-before:always}.pg:first-child{page-break-before:auto}
h1{font-size:18pt;color:#332e91;border-bottom:3px solid #332e91;padding-bottom:5px;margin:0 0 4mm}
h2{font-size:13pt;color:#332e91;margin:0 0 3mm;padding:2mm 0 2mm 3mm;border-left:5px solid #4338ca;background:#eef2ff}
h2 span{font-size:9.5pt;font-weight:400;color:#6b7784;margin-left:3mm}
h3{font-size:10pt;color:#0e7a52;margin:4mm 0 1.5mm;border-bottom:1px solid #cfe6dc;padding-bottom:1mm}
h3 b{color:#1b2733}
p{margin:2mm 0}.lead{font-size:9pt;color:#55606c}
.kanji{display:flex;flex-wrap:wrap;gap:1.5mm}
.kanji div{border:1px solid #c7c9e8;border-radius:3px;width:16mm;text-align:center;padding:1mm 0}
.kanji .c{font-size:15pt;font-weight:bold;line-height:1.2}
.kanji .r{font-size:6.5pt;color:#6b7784;line-height:1.25;word-break:break-all}
.cols{column-count:3;column-gap:5mm;font-size:8.5pt}
.cols div{break-inside:avoid;padding:.3mm 0}.cols .r{color:#6b7784}
ruby{ruby-align:center}rt{font-size:5.6pt;color:#4338ca;font-weight:400}
h2 rt{font-size:6.5pt}h3 rt{font-size:5.6pt}
.g{column-count:2;column-gap:5mm}.g div{break-inside:avoid;font-size:9pt;padding:.4mm 0}
table{border-collapse:collapse;width:100%;margin:2mm 0;font-size:9pt}
th,td{border:1px solid #c7c9e8;padding:1.4mm 2mm;text-align:left}
th{background:#eef2ff}
.box{border:2px solid #4338ca;background:#eef2ff;border-radius:5px;padding:3mm 4mm;margin:3mm 0}
.box b{color:#332e91}
.tip{border-left:4px solid #0e7a52;background:#f2fbf7;padding:2.5mm 4mm;margin:3mm 0;font-size:9pt}
ul.task{margin:1.5mm 0 0 5mm;padding:0;font-size:9pt}
ul.task li{margin:.6mm 0}
tr{page-break-inside:avoid}
`;
const kanjiHtml = list => !list.length ? '' : '<div class="kanji">' + list.map(k =>
  `<div><div class="c">${esc(k.character)}</div><div class="r">${esc((k.on||[]).slice(0,1).join(''))}<br>${esc((k.kun||[]).slice(0,1).join(''))}</div></div>`).join('') + '</div>';
const vocabHtml = list => !list.length ? '' : '<div class="cols">' + list.map(v => {
  const same = String(v.reading||'') === String(v.word||'');
  return `<div>${esc(v.word)}${same?'':'<span class="r">　'+esc(v.reading)+'</span>'}</div>`;
}).join('') + '</div>';
const gramHtml = list => !list.length ? '' : '<div class="g">' + list.map(g =>
  `<div>${esc(g.pattern)}<span class="r" style="color:#6b7784">　${R(g.category)}</span></div>`).join('') + '</div>';
/* 読解の題には 漢字《かんじ》 の形のふりがなが入っていることがある。
   そのまま出すと《》が見えてしまうので、先に ruby に変えておく。 */
const kakko = s => String(s).replace(/([一-鿿]+)《(.+?)》/g, '<ruby>$1<rt>$2</rt></ruby>');
/* 先に《》をルビに変え、そのあとで辞書のふりがなを当てる。
   順番を逆にすると、先に囲みの中が書きかえられて《》が残ってしまう。 */
const taskHtml = list => !list.length ? '' : '<ul class="task">' + list.map(t =>
  `<li>${R(kakko(t))}</li>`).join('') + '</ul>';

let pages = [];
/* ---- 1ページ目：職員用の全体表 ---- */
let ov = '<table><thead><tr><th>週</th><th>日にち</th><th>期</th><th>漢字</th><th>語彙</th><th>文型</th><th>そのほか</th></tr></thead><tbody>';
let tk=0,tv=0,tg=0;
for (let w=1; w<=66; w++){
  const p = P[w];
  tk+=p.kanji.length; tv+=p.vocab.length; tg+=p.gram.length;
  ov += `<tr><td>${w}</td><td>${md(mon(w))}〜${md(sun(w))}</td><td>${esc(phName(w))}</td>`
     + `<td>${p.kanji.length||''}</td><td>${p.vocab.length||''}</td><td>${p.gram.length||''}</td>`
     + `<td>${p.task.length?esc(p.task[0].replace(/《.+?》/g,'').slice(0,22)):''}</td></tr>`;
}
ov += `<tr><th>合計</th><th></th><th></th><th>${tk}字</th><th>${tv}語</th><th>${tg}項目</th><th></th></tr></tbody></table>`;
pages.push(`<div class="pg">
<h1>N2 週ごとの学習範囲表</h1>
<p class="lead"><b>この1ページ目は職員用です。</b>2ページ目からが本人の見るところで、N4を超える漢字にはふりがなを付けてあります。<br>
N2合格ロードマップ（2026年9月〜2027年12月・全66週）の付表。<b>この表が「今週どこまでやるか」の決まりです。</b></p>
<div class="box"><b>期の区切り</b><br>
${PH.map(p => `第${p.no}期　${p.name}（第${p.from}〜${p.to}週）　… ${p.aim}`).join('<br>')}</div>
<div class="tip"><b>順番の決め方</b><br>
<b>漢字</b>＝使う回数の多い字から。アプリの一覧も同じ順に並びます。<br>
<b>語彙</b>＝<b>その週に習う漢字を使う語を、同じ週に置きました。</b>覚える手がかりが一つで済みます。<br>
<b>文型</b>＝意味のまとまり順。アプリの並びと同じです。</div>
<div class="tip"><b>語彙について、正直なところ</b><br>
N2語彙1,738語のうち、<b>その週の漢字と直接結びつけられたのは241語（14%）</b>です。
N2は漢字320字に対して語彙が1,738語と多く、どうしても全部は結びつきません。<br>
ただし<b>その週までに習った漢字だけで読める語は1,210語（70%）</b>あります。残りはふりがなを見ながら覚えることになります。</div>
<h2>全体の数<span>この表に載っている分</span></h2>
${ov}
</div>`);

/* ---- 週ごと ---- */
for (let w=1; w<=66; w++){
  const p = P[w];
  const ph = phaseOf(w);
  let h = `<div class="pg"><h2>${R('第'+w+'週　'+phName(w))}<span>${md(mon(w))}（月）〜${md(sun(w))}（日）</span></h2>`;
  h += `<p class="lead">${R('この期のねらい：'+ph.aim)}</p>`;
  if (p.kanji.length){
    const per = (p.kanji.length/5).toFixed(0);
    h += `<h3>漢字　<b>${p.kanji.length}字</b>${R('（平日1日'+per+'字）')}</h3>${kanjiHtml(p.kanji)}`;
  }
  if (p.vocab.length){
    const per = (p.vocab.length/5).toFixed(0);
    h += `<h3>${R('語彙')}　<b>${p.vocab.length}${R('語')}</b>${R('（平日1日'+per+'語）')}</h3>${vocabHtml(p.vocab)}`;
  }
  if (p.gram.length){
    const per = (p.gram.length/5).toFixed(0);
    h += `<h3>${R('文型')}　<b>${p.gram.length}${R('項目')}</b>${R('（平日1日'+per+'項目）')}</h3>${gramHtml(p.gram)}`;
  }
  if (p.task.length) h += `<h3>${R('そのほか、この週にすること')}</h3>${taskHtml(p.task)}`;
  pages.push(h + '</div>');
}
fs.writeFileSync('/tmp/n2plan/n2hani.html',
  `<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>N2 週ごとの学習範囲表</title><style>${css}</style></head><body>${pages.join('')}</body></html>`);
console.log('HTML 出力　ページ数の目安', pages.length);
