const fs = require('fs');
const T = JSON.parse(fs.readFileSync('/tmp/hani/tests.json','utf8'));
const W1 = new Date(2026,11,7);
const md = w => { const d = new Date(W1.getTime()+(w-1)*7*86400000);
  return (d.getMonth()+1)+'/'+d.getDate(); };
const esc = s => String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const ruby = s => esc(s).replace(/([^\s]+?)《(.+?)》/g, '<ruby>$1<rt>$2</rt></ruby>');
const { withRuby } = require(__dirname + '/../hani/ruby.js');
/* 指示文・見出しだけにふりがなを付ける。
   問題の語や選択肢に付けると、それが答えになってしまうので付けない。 */
const R = s => withRuby(esc(s));
const CIRC = ['①','②','③','④'];

const css = `
body{margin:0;font-family:"IPAPGothic","IPAGothic","WenQuanYi Zen Hei",sans-serif;color:#1b2733;font-size:10.5pt;line-height:1.8}
.pg{page-break-before:always}.pg:first-child{page-break-before:auto}
h1{font-size:17pt;color:#9a3412;margin:0 0 2mm}
h2{font-size:12.5pt;color:#9a3412;margin:0 0 3mm;padding:2mm 0 2mm 3mm;border-left:5px solid #c2410c;background:#fff7ed;page-break-after:avoid}
h3{font-size:10.5pt;color:#0e7a52;margin:5mm 0 2mm;page-break-after:avoid}
p{margin:2mm 0}.lead{font-size:9.5pt;color:#55606c}
.q{margin:0 0 3.5mm;page-break-inside:avoid}
.qt{font-weight:bold}.qt .no{display:inline-block;min-width:7mm;color:#c2410c}
.qs{font-size:12pt;margin:0 0 1mm 7mm}
.opts{margin:0 0 0 7mm;display:flex;flex-wrap:wrap;gap:1mm 6mm}
.opts.col span{display:block;width:100%}
.psg{border:1px solid #d8c3b4;border-radius:4px;padding:4mm 5mm;margin:0 0 4mm;background:#fffdf9;page-break-inside:avoid;white-space:pre-wrap}
ruby rt{font-size:6pt;color:#6b7784}
table{border-collapse:collapse;width:100%;margin:2mm 0;font-size:9.5pt}
th,td{border:1px solid #d8c3b4;padding:1.4mm 2mm;text-align:left}
th{background:#fdf0e6}
.cover{text-align:center;padding-top:28mm}
.cover .t{font-size:21pt;font-weight:bold;color:#9a3412}
.cover .s{font-size:12pt;color:#55606c;margin-top:3mm}
.namebox{margin:16mm auto 0;width:118mm;border:2px solid #c2410c;border-radius:6px;padding:6mm;text-align:left}
.namebox .r{display:flex;align-items:flex-end;gap:4mm;margin:4mm 0}
.namebox .lb{width:26mm;font-weight:bold}
.namebox .ln{flex:1;border-bottom:1px solid #8b9aa9;height:8mm}
.rules{margin:12mm auto 0;width:150mm;text-align:left;font-size:10pt}
.box{border:2px solid #c2410c;background:#fff7ed;border-radius:5px;padding:3mm 4mm;margin:3mm 0}
.box b{color:#9a3412}
.tip{border-left:4px solid #0e7a52;background:#f2fbf7;padding:2.5mm 4mm;margin:3mm 0;font-size:9.5pt}
.sc .sp{display:inline-block;min-width:11mm;font-weight:bold;color:#c2410c}
.sc{font-size:9.5pt}
tr{page-break-inside:avoid}
`;

const optHtml = (q, rb) => {
  const long = q.opts.some(o => String(o).length > 16);
  const f = rb ? (x => R(ruby(x))) : ruby;   /* 読解だけ ふりがなを付ける */
  return `<div class="opts${long?' col':''}">` +
    q.opts.map((o,i) => `<span>${CIRC[i]} ${f(o)}</span>`).join('') + '</div>';
};

let pages = [];
T.forEach(t => {
  let n = 0;
  /* 表紙 */
  pages.push(`<div class="pg"><div class="cover">
    <div class="t">${R('月次確認テスト　第'+t.no+'回')}</div>
    <div class="s">${R('第'+t.week+'週')}（${md(t.week)}の週）に 行います　／　15分・20問</div>
    <div class="namebox">
      <div class="r"><span class="lb">${R('名前')} / Nama</span><span class="ln"></span></div>
      <div class="r"><span class="lb">日にち / Tanggal</span><span class="ln"></span></div>
      <div class="r"><span class="lb">${R('点数')}</span><span class="ln"></span></div>
    </div>
    <ul class="rules">
      <li><b>${R('範囲')}：${R(t.range)}</b>　※ここに 書いて ある ${R('範囲')}からだけ 出ます</li>
      <li>${R('時間')}は <b>15分</b>です。わからない ときは とばして ください。</li>
      <li>${R('答え')}は、${R('正しい')} ものの ${R('番号')}（①②③④）に ○を つけて ください。</li>
      <li>これは ${R('合格')}・${R('不合格')}を ${R('決める')} テストでは ありません。<br>
        <i>Tes ini bukan untuk lulus/tidak lulus. Untuk melihat apa yang perlu diulang.</i></li>
    </ul></div></div>`);
  /* 本体 */
  let body = `<div class="pg"><h2>${R('月次確認テスト 第'+t.no+'回')}（20問・15分）</h2>`;
  t.parts.forEach(p => {
    body += `<h3>${R(p.head)}</h3>`;
    if (p.reading) {
      const rbP = t.no <= 3;
      body += `<p class="lead">${rbP?R(ruby(p.reading.intro||'')):ruby(p.reading.intro||'')}</p>`
        + `<div class="psg">${rbP?R(ruby(p.reading.text||'')):ruby(p.reading.text||'')}</div>`;
    }
    if (p.listen) body += `<p class="lead">この 紙には ${R('会話')}が 書いて ありません。音を 聞いて ${R('答え')}ます。1回だけ 流れます。</p>`;
    (p.items||[]).forEach(q => {
      n++;
      /* 設問文がないときは、番号と語を1行にまとめる（空行を作らない） */
      /* 読解にふりがなを付けるのは第1〜3回だけ。
         第4回はN3の力を測るので、N3漢字にふりがなを付けると測れなくなる。 */
      const rb = !!p.reading && t.no <= 3;
      body += q.q
        ? `<div class="q"><div class="qt"><span class="no">${n}</span>${R(esc(q.q))}</div>`
          + (q.s ? `<div class="qs">${rb?R(ruby(q.s)):ruby(q.s)}</div>` : '') + optHtml(q, rb) + '</div>'
        : `<div class="q"><div class="qt"><span class="no">${n}</span>`
          + `<span style="font-size:12pt">${rb?R(ruby(q.s||'')):ruby(q.s||'')}</span></div>` + optHtml(q, rb) + '</div>';
    });
  });
  pages.push(body + '</div>');
});

/* 採点・記録 */
let key = `<div class="pg"><h1>月次確認テスト　採点と使い方</h1>
<p class="lead"><b>ここから先は職員用です。</b>ふりがなは付けていません。<br>
テストの直後に採点し、記録表に書いてから面談に入ります。</p>
<div class="box"><b>この4回のテストの位置づけ</b><br>
月末の面談で「量を増やすか、減らすか」を決めるための<b>数字</b>です。
本人の自己申告のチェックだけでは、判断ができません。<br>
<b>14点（70%）以上</b>＝その月の分は身についた → 次の月へ進む<br>
<b>10〜13点</b>＝穴がある → 翌月に<b>復習を1日5分足す</b>。量は増やさない<br>
<b>9点以下</b>＝ついていけていない → 翌月の量を<b>半分に減らす</b>。範囲表の同じ週をもう一度</div>
<div class="tip"><b>点が低かったとき、本人を責めないでください。</b>
量が多すぎたか、生活が大変だったかのどちらかです。どちらも職員が調整するものです。</div>
<h2>いつ行うか</h2>
<table><thead><tr><th>回</th><th>週</th><th>時期</th><th>範囲</th></tr></thead><tbody>`;
T.forEach(t => key += `<tr><td>第${t.no}回</td><td>第${t.week}週</td><td>${md(t.week)}の週</td><td>${esc(t.range)}</td></tr>`);
key += `</tbody></table>
<p class="lead">第4週・第8週・第12週・第20週の<b>木曜</b>に行い、その週の面談で結果を使います。
第16週は診断テスト第2回があるので、月次テストは行いません。</p>

<h2>記録表（2名分）</h2>
<table><thead><tr><th>回</th><th>日にち</th><th>Aさん</th><th>判定</th><th>Bさん</th><th>判定</th></tr></thead><tbody>
${T.map(t => `<tr><td>第${t.no}回</td><td>　　/　　</td><td>　　/20</td><td></td><td>　　/20</td><td></td></tr>`).join('')}
</tbody></table></div>`;
pages.push(key);

/* 正解 */
T.forEach(t => {
  let n = 0, rows = '';
  t.parts.forEach(p => (p.items||[]).forEach(q => {
    n++; rows += `<tr><td>${n}</td><td><b>${q.ans}</b></td><td>${esc(q.why||'')}</td></tr>`;
  }));
  let h = `<div class="pg"><h1>第${t.no}回　正解</h1>
    <p class="lead">${esc(t.range)}</p>
    <table><thead><tr><th style="width:8%">問</th><th style="width:8%">正解</th><th>ことば・ポイント</th></tr></thead>
    <tbody>${rows}</tbody></table>`;
  if (t.listen) {
    h += `<h2>聴解スクリプト</h2><p class="lead">職員が読み上げます。会話は<b>1回だけ</b>、ふつうの速さで。</p>`;
    t.listen.forEach(it => {
      h += `<div class="q"><div class="qt">${esc(it.no)}　正解：${esc(it.answer)}</div><div class="sc">`
        + it.steps.map(st => st.k==='line' ? `<div><span class="sp">${esc(st.sp)}</span>${esc(st.v)}</div>`
          : st.k==='q' ? `<div><span class="sp">（質問）</span>${esc(st.v)}</div>`
          : `<div><span class="sp">（間）</span>${st.s}秒${st.a?'　※答えを書かせる':''}</div>`).join('')
        + `</div><div class="lead">${esc(it.why)}</div></div>`;
    });
  }
  pages.push(h + '</div>');
});

fs.writeFileSync('/tmp/hani/tests.html',
  `<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>月次確認テスト</title>
  <style>${css}</style></head><body>${pages.join('')}</body></html>`);
console.log('HTML 出力');
