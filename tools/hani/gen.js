const fs = require('fs');
const P = JSON.parse(fs.readFileSync('/tmp/hani/plan.json','utf8'));
const W1 = new Date(2026,11,7);
const mon = w => new Date(W1.getTime() + (w-1)*7*86400000);
const sun = w => new Date(mon(w).getTime() + 6*86400000);
const md = d => (d.getMonth()+1)+'/'+d.getDate();
const esc = s => String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const { withRuby } = require(__dirname + '/../hani/ruby.js');
/* 学習者が読むところは、N4を超える漢字にふりがなを付ける */
const R = s => withRuby(esc(s));
const PHASE = w => w<=4 ? 'ならし（N5）' : w<=12 ? 'N4を仕上げる' : w<=16 ? 'N3へ切りかえる' : '100日コース 第'+(w-16)+'週';

const css = `
body{margin:0;font-family:"IPAPGothic","IPAGothic","WenQuanYi Zen Hei",sans-serif;color:#1b2733;font-size:9.5pt;line-height:1.6}
.pg{page-break-before:always}.pg:first-child{page-break-before:auto}
h1{font-size:18pt;color:#9a3412;border-bottom:3px solid #9a3412;padding-bottom:5px;margin:0 0 4mm}
h2{font-size:13pt;color:#9a3412;margin:0 0 3mm;padding:2mm 0 2mm 3mm;border-left:5px solid #c2410c;background:#fff7ed}
h2 span{font-size:9.5pt;font-weight:400;color:#6b7784;margin-left:3mm}
h3{font-size:10pt;color:#0e7a52;margin:4mm 0 1.5mm;border-bottom:1px solid #cfe6dc;padding-bottom:1mm}
h3 b{color:#1b2733}
p{margin:2mm 0}
.lead{font-size:9pt;color:#55606c}
.kanji{display:flex;flex-wrap:wrap;gap:1.5mm}
.kanji div{border:1px solid #d8c3b4;border-radius:3px;width:16mm;text-align:center;padding:1mm 0}
.kanji .c{font-size:15pt;font-weight:bold;line-height:1.2}
.kanji .r{font-size:6.5pt;color:#6b7784;line-height:1.25;word-break:break-all}
.cols{column-count:3;column-gap:5mm;font-size:8.5pt}
.cols div{break-inside:avoid;padding:.3mm 0}
.cols .r{color:#6b7784}
ruby{ruby-align:center}
rt{font-size:5.6pt;color:#8a5a12;font-weight:400;letter-spacing:0}
h2 rt{font-size:6.5pt}
h3 rt{font-size:5.6pt}
.g div{break-inside:avoid;font-size:9pt;padding:.4mm 0}
.g{column-count:2;column-gap:5mm}
table{border-collapse:collapse;width:100%;margin:2mm 0;font-size:9pt}
th,td{border:1px solid #d8c3b4;padding:1.4mm 2mm;text-align:left}
th{background:#fdf0e6}
.box{border:2px solid #c2410c;background:#fff7ed;border-radius:5px;padding:3mm 4mm;margin:3mm 0}
.box b{color:#9a3412}
.tip{border-left:4px solid #0e7a52;background:#f2fbf7;padding:2.5mm 4mm;margin:3mm 0;font-size:9pt}
tr{page-break-inside:avoid}
`;

const kanjiHtml = list => '<div class="kanji">' + list.map(k =>
  `<div><div class="c">${esc(k.character)}</div><div class="r">${esc((k.on||[]).slice(0,1).join(''))}<br>${esc((k.kun||[]).slice(0,1).join(''))}</div></div>`).join('') + '</div>';
/* 読みが語と同じ（カタカナ語など）ときは、読みを出さない */
const vocabHtml = list => '<div class="cols">' + list.map(v => {
  const same = String(v.reading || '') === String(v.word || '');
  return `<div>${esc(v.word)}${same ? '' : '<span class="r">　' + esc(v.reading) + '</span>'}</div>`;
}).join('') + '</div>';
const gramHtml = list => '<div class="g">' + list.map(g =>
  `<div>${esc(g.pattern)}<span class="r" style="color:#6b7784">　${R(g.category)}</span></div>`).join('') + '</div>';

let pages = [];

/* 表紙 */
let overview = '<table><thead><tr><th>週</th><th>日にち</th><th>期</th><th>漢字</th><th>語彙</th><th>文型</th></tr></thead><tbody>';
let tk=0, tv=0, tg=0;
for (let w=1; w<=30; w++){
  const k=(P.kanjiPlan[w]||[]).length, v=(P.vocabPlan[w]||[]).length, g=(P.gramPlan[w]||[]).length;
  tk+=k; tv+=v; tg+=g;
  overview += `<tr><td>${w}</td><td>${md(mon(w))}〜${md(sun(w))}</td><td>${PHASE(w)}</td>`
    + `<td>${k||'―'}</td><td>${v||'―'}</td><td>${g||'―'}</td></tr>`;
}
overview += `<tr><th>合計</th><th></th><th></th><th>${tk}字</th><th>${tv}語</th><th>${tg}項目</th></tr></tbody></table>`;

pages.push(`<div class="pg">
<h1>週ごとの学習範囲表</h1>
<p class="lead"><b>この1ページ目は職員用です。</b>2ページ目からが実習生の見るところで、
N4を超える漢字にはふりがなを付けてあります。<br>
新人職員 日本語研修プログラム（2026年12月7日〜2027年7月4日・全30週）の付表。
この表が「今週どこまでやるか」の決まりです。月次確認テストは、ここに書いてある範囲からだけ出します。</p>

<div class="box"><b>順番の決め方</b><br>
<b>漢字</b>＝使う回数の多い字から。アプリの一覧も同じ順に並びます（レベル順→頻度順）。<br>
<b>語彙</b>＝<b>その週に習う漢字を使う語を、同じ週に置きました。</b>
「事・場・動・通」を習う週に「用事・場所・運動・通る」が来ます。覚える手がかりが1つで済みます。<br>
<b>文型</b>＝意味のまとまり順（条件→推量→伝聞→授受…）。アプリの並びと同じです。</div>

<div class="tip"><b>語彙について、正直なところ</b><br>
N4語彙662語のうち、<b>その週の漢字と結びつけられたのは147語</b>です。
既に習った漢字だけで読める語39語、かな・カタカナだけの語125語を足して、<b>311語（47%）</b>は既習漢字だけで読めます。<br>
残り<b>351語はN3以上の漢字を含む</b>ので、<b>ふりがなを見ながら覚える</b>ことになります。
これはN4語彙の性質上どうにもなりません（「郵便局」の「郵」はN3漢字）。
アプリはふりがなを出すので、読めなくても進められます。</div>

<div class="tip"><b>N3語彙を1,000語に絞った理由</b><br>
手もとのN3語彙は<b>2,078語</b>あります。第13〜30週の18週で全部を配ると平日1日24語になり、
漢字4字・文型2項目と合わせると1日1時間半をこえます。続きません。そこで<b>1,000語に絞りました</b>。<br>
① <b>この30週で習う漢字（613字）だけでできている語</b>に限りました（1,171語）。
習わない漢字を含む語は読めないので、覚えようがありません。<br>
② そのうち<b>介護・現場の語、分野名のついた語、基本語、カタカナ語は必ず残しました</b>（256語）。<br>
③ 残りは<b>使う回数の多い漢字でできている語から</b>順に、1,000語になるまで取りました。<br>
結果、第13〜30週では<b>その週の漢字を使う語が467語（47%）</b>になり、N4期の22%より結びつきが強くなっています。</div>

<h2>全体の数<span>この表に載っている分</span></h2>
${overview}
</div>`);

/* 第1〜4週：N5 */
for (let w=1; w<=4; w++){
  pages.push(`<div class="pg">
  <h2>${R('第'+w+'週　'+PHASE(w))}<span>${md(mon(w))}（月）〜${md(sun(w))}（日）　1日15分</span></h2>
  <h3>漢字　<b>${(P.kanjiPlan[w]||[]).length}字</b>${R('（平日1日5字）')}</h3>
  ${kanjiHtml(P.kanjiPlan[w]||[])}
  <h3>${R('語彙')}　<b>${(P.vocabPlan[w]||[]).length}語</b>${R('（平日1日10語）')}</h3>
  ${vocabHtml(P.vocabPlan[w]||[])}
  </div>`);
}
/* 第5〜12週：N4 */
for (let w=5; w<=12; w++){
  pages.push(`<div class="pg">
  <h2>${R('第'+w+'週　'+PHASE(w))}<span>${md(mon(w))}（月）〜${md(sun(w))}（日）　1日30分</span></h2>
  <h3>漢字　<b>${(P.kanjiPlan[w]||[]).length}字</b>${R('（平日1日4字）')}</h3>
  ${kanjiHtml(P.kanjiPlan[w]||[])}
  <h3>${R('文型')}　<b>${(P.gramPlan[w]||[]).length}${R('項目')}</b>${R('（平日1日3項目）')}</h3>
  ${gramHtml(P.gramPlan[w]||[])}
  <h3>${R('語彙')}　<b>${(P.vocabPlan[w]||[]).length}語</b>${R('（平日1日17語）')}</h3>
  ${vocabHtml(P.vocabPlan[w]||[])}
  </div>`);
}
/* 第24・28週は模試、第29・30週は新しいことをしない週。画面（新人コース）と そろえる */
const WNOTE = {
  24:'<div class="box"><b>この週に N3模試 第1回（本番と同じ140分）</b><br>'
   + '文字・語彙30分 → 文法・読解70分 → 聴解40分。区分をまたいで戻れないので、'
   + '<b>公休など続けて140分とれる日</b>に受けます。区分ごとの点を出し、'
   + '<b>19点未満の区分を記録して</b>第25〜27週で埋めます。</div>',
  28:'<div class="box"><b>この週に N3模試 第2回（140分）</b><br>'
   + '第1回と同じ形です。第1回と並べて、区分ごとの伸びを見ます。</div>',
  29:'<div class="tip"><b>⚠ 画面では、この週は「新しいことをしない週」です</b><br>'
   + '第29週は<b>模試で19点に届かなかった区分だけ</b>をやる週にしてあります。'
   + 'このページに載っている漢字・語彙・文型は、<b>第28週までに前倒しで終わらせてください。</b></div>',
  30:'<div class="tip"><b>⚠ 画面では、この週は「直前の確認だけ」です</b><br>'
   + '月〜木は一度見た問題を30分だけ。<b>前の日（7月3日）は勉強させません。</b>'
   + 'このページに載っている分も、<b>第28週までに前倒しで終わらせてください。</b></div>'
};
/* 第13〜30週：N3（1週で1ページ。語彙が入ったので2週まとめると入らない） */
for (let w=13; w<=30; w++){
  pages.push(`<div class="pg">
  <h2>${R('第'+w+'週　'+PHASE(w))}<span>${md(mon(w))}（月）〜${md(sun(w))}（日）　${R(w<=16 ? '1日50分' : '1日60分')}</span></h2>
  ${WNOTE[w] || ''}
  <h3>漢字　<b>${(P.kanjiPlan[w]||[]).length}字</b>${R('（平日1日4字）')}</h3>
  ${kanjiHtml(P.kanjiPlan[w]||[])}
  <h3>${R('語彙')}　<b>${(P.vocabPlan[w]||[]).length}語</b>${R('（平日1日11語）')}</h3>
  ${vocabHtml(P.vocabPlan[w]||[])}
  <h3>${R('文型')}　<b>${(P.gramPlan[w]||[]).length}${R('項目')}</b>${R('（平日1日2項目）')}</h3>
  ${gramHtml(P.gramPlan[w]||[])}
  </div>`);
}

fs.writeFileSync('/tmp/hani/hani.html',
  `<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>週ごとの学習範囲表</title>
  <style>${css}</style></head><body>${pages.join('')}</body></html>`);
console.log('HTML 出力　ページ数の目安', pages.length);
