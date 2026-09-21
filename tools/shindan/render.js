const fs = require('fs');
const sets = JSON.parse(fs.readFileSync('/tmp/shindan/out/sets.json', 'utf8'));
const OUT = '/tmp/shindan/out';

const CSS = `
body { margin:0; font-family:"IPAPGothic","IPAGothic","WenQuanYi Zen Hei",sans-serif;
  color:#1b2733; font-size:10.5pt; line-height:1.7; }
.pg { page-break-before:always; }
.pg:first-child { page-break-before:auto; }
h1 { font-size:17pt; color:#12459c; margin:0 0 2mm; }
h2 { font-size:13pt; color:#12459c; margin:0 0 4mm; padding:2mm 0 2mm 3mm; border-left:5px solid #12459c;
     background:#f2f6fb; page-break-after:avoid; }
h3 { font-size:10.5pt; margin:5mm 0 2mm; color:#0e7a52; page-break-after:avoid; }
p { margin:2mm 0; }
.lead { font-size:9.5pt; color:#55606c; margin-bottom:4mm; }
.q { margin:0 0 3.5mm; page-break-inside:avoid; }
.qt { font-weight:bold; }
.qt .no { display:inline-block; min-width:7mm; color:#12459c; }
.opts { margin:1mm 0 0 7mm; display:flex; flex-wrap:wrap; gap:1mm 6mm; }
.opts span { white-space:nowrap; }
.opts.col span { display:block; width:100%; }
.psg { border:1px solid #b9c6d4; border-radius:4px; padding:4mm 5mm; margin:0 0 4mm; background:#fbfcfd;
  page-break-inside:avoid; }
.psg p { margin:1.5mm 0; }
table { border-collapse:collapse; width:100%; margin:2mm 0; font-size:9.5pt; }
th,td { border:1px solid #b9c6d4; padding:1.5mm 2mm; text-align:left; }
th { background:#eaf1f8; }
.box { border:1px solid #8b9aa9; height:11mm; margin:1mm 0 3mm; }
.kbox { display:flex; flex-wrap:wrap; gap:3mm; }
.kbox div { width:47mm; }
.kbox .k { font-size:9.5pt; color:#55606c; }
.kbox .sq { border:1px solid #8b9aa9; height:13mm; }
.wl { border-bottom:1px solid #8b9aa9; height:9mm; }
.cover { text-align:center; padding-top:30mm; }
.cover .t { font-size:22pt; font-weight:bold; color:#12459c; }
.cover .s { font-size:12pt; color:#55606c; margin-top:3mm; }
.namebox { margin:18mm auto 0; width:120mm; border:2px solid #12459c; border-radius:6px; padding:6mm; text-align:left; }
.namebox .r { display:flex; align-items:flex-end; gap:4mm; margin:4mm 0; }
.namebox .lb { width:24mm; font-weight:bold; }
.namebox .ln { flex:1; border-bottom:1px solid #8b9aa9; height:8mm; }
.rules { margin:14mm auto 0; width:150mm; text-align:left; font-size:10pt; }
.rules li { margin:1.5mm 0; }
.ft { position:relative; margin-top:6mm; border-top:1px solid #c9d4e0; padding-top:2mm;
  font-size:8.5pt; color:#6b7784; display:flex; justify-content:space-between; }
.key { font-size:9.5pt; }
.key td, .key th { padding:1.2mm 2mm; }
.warn { border:2px solid #c0392b; background:#fdf4f3; border-radius:5px; padding:3mm 4mm; margin:3mm 0; }
.warn b { color:#c0392b; }
.tip { border-left:4px solid #0e7a52; background:#f2fbf7; padding:2.5mm 4mm; margin:3mm 0; font-size:9.5pt; }
.sc { font-size:9.5pt; }
.sc .sp { display:inline-block; min-width:11mm; font-weight:bold; color:#12459c; }
.sc .qq { color:#0e7a52; font-weight:bold; }
ruby { ruby-align:center; }
rt { font-size:5.8pt; color:#8a5a12; font-weight:normal; letter-spacing:0; }
`;

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const keep = s => String(s);      // 本文はタグを残す
const { withRuby } = require(__dirname + '/../hani/ruby.js');
/* N4を超える漢字にふりがなを付ける。
   読めないせいで解けないと、読む力が測れないため。
   ただし「読みを答える問題」の語には付けない（答えになってしまう）。 */
const R = s => withRuby(String(s == null ? '' : s));
const CIRC = ['①', '②', '③', '④'];

/* ---------- 問題冊子 ---------- */
function optLine(q, col, rb) {
  const list = q.kind === 'sort' ? q.parts : q.opts;
  const long = list.some(x => String(x).length > 14);
  const f = rb ? R : (x => x);
  return `<div class="opts${(col || long) ? ' col' : ''}">` +
    list.map((o, i) => `<span>${CIRC[i]} ${f(keep(o))}</span>`).join('') + '</div>';
}
function qBlock(q, rb) {
  const f = rb ? R : (x => x);          /* 読解だけ ふりがなを付ける */
  if (q.kind === 'sort') {
    return `<div class="q"><div class="qt"><span class="no">${q.id}</span>` +
      `＿＿　＿★＿　＿＿　＿＿</div>${optLine(q, false, rb)}</div>`;
  }
  return `<div class="q"><div class="qt"><span class="no">${q.id}</span>${f(keep(q.text))}</div>${optLine(q, false, rb)}</div>`;
}

function booklet(s) {
  const P = [];
  /* 表紙 */
  P.push(`<div class="pg"><div class="cover">
    <div class="t">日本語　診断テスト</div>
    <div class="s">${R('第'+s.no+'回')}（${R(s.when)}）　N4レベルの${R('確認')}</div>
    <div class="namebox">
      <div class="r"><span class="lb">名前 / Nama</span><span class="ln"></span></div>
      <div class="r"><span class="lb">日にち / Tanggal</span><span class="ln"></span></div>
    </div>
    <ul class="rules">
      <li>このテストは、<b>${R('合格・不合格を決める')}ものでは ありません</b>。
        どこを 先に ${R('勉強')}すると いいかを 知るための ものです。</li>
      <li>Tes ini <b>bukan untuk lulus atau tidak lulus</b>. Untuk mengetahui bagian mana yang perlu dipelajari lebih dulu.</li>
      <li>わからない ときは、とばして ${R('次に')} ${R('進んで')} ください。</li>
      <li>${R('答え')}は、${R('正しい')} ものの ${R('番号')}（①②③④）に ○を つけて ください。</li>
      <li>${R('第4部')}は 音を 聞いて ${R('答え')}ます。${R('会話')}は <b>${R('1回')}だけ</b> ${R('流れます')}。</li>
      <li>${R('第5部')}は 字を 書きます。ていねいに 書いて ください。</li>
    </ul></div></div>`);

  /* 第1部・第2部 */
  [s.p1, s.p2].forEach(part => {
    const body = part.groups.map(g => `<h3>${R(esc(g.head))}</h3>` + g.items.map(qBlock).join('')).join('');
    P.push(`<div class="pg"><h2>${R(esc(part.title))}</h2>${body}</div>`);
  });

  /* 第3部（読解は2ページに分ける） */
  const rp = s.p3.passages;
  const rHtml = p => `<h3>${R(esc(p.head))}</h3><div class="psg">${R(keep(p.body))}</div>`
    + p.items.map(q => qBlock(q, true)).join('');
  P.push(`<div class="pg"><h2>${R(esc(s.p3.title))}</h2>${rHtml(rp[0])}${rHtml(rp[1])}</div>`);
  P.push(`<div class="pg">${rHtml(rp[2])}</div>`);

  /* 第4部 */
  const lHtml = s.p4.groups.map(g => `<h3>${R(esc(g.head))}</h3>` + g.items.map(qBlock).join('')).join('');
  P.push(`<div class="pg"><h2>${R(esc(s.p4.title))}</h2>
    <p class="lead">${R(esc(s.p4.note))}</p>${lHtml}
    <h3>メモらん</h3><div style="border:1px solid #c9d4e0;border-radius:4px;height:32mm"></div></div>`);

  /* 第5部 */
  const k = s.p5.kanji, w = s.p5.write;
  P.push(`<div class="pg"><h2>${R(esc(s.p5.title))}</h2>
    <h3>${R(esc(k.head))}</h3>
    <div class="kbox">${k.items.map(x =>
      `<div><div class="k">${x.id}　${esc(x.kana)}</div><div class="sq"></div></div>`).join('')}</div>
    <h3>${R(esc(w.head))}</h3>
    ${w.items.map(x => `<div class="q"><div class="qt"><span class="no">${x.id}</span>${R(keep(x.prompt))}</div>
      <div class="wl"></div><div class="wl"></div></div>`).join('')}</div>`);

  return `<!doctype html><html lang="ja"><head><meta charset="utf-8">
    <title>診断テスト 第${s.no}回</title><style>${CSS}</style></head><body>${P.join('')}</body></html>`;
}

/* ---------- 実施と採点 ---------- */
function keyTable(s) {
  const rows = [];
  const push = (part, q) => rows.push(`<tr><td>${part}</td><td>${q.id}</td><td><b>${q.ans}</b></td>
    <td>${esc(q.why || '')}</td></tr>`);
  s.p1.groups.forEach(g => g.items.forEach(q => push('第1部', q)));
  s.p2.groups.forEach(g => g.items.forEach(q => push('第2部', q)));
  s.p3.passages.forEach(p => p.items.forEach(q => push('第3部', q)));
  s.p4.groups.forEach(g => g.items.forEach(q => push('第4部', q)));
  return `<table class="key"><thead><tr><th>部</th><th>問</th><th>正解</th><th>解説</th></tr></thead>
    <tbody>${rows.join('')}</tbody></table>`;
}
function scriptHtml(s) {
  return s.listen.map(g => `<h3>${esc(g.group)}</h3>` + g.items.map(it => {
    const lines = it.steps.map(st => {
      if (st.k === 'line') return `<div><span class="sp">${esc(st.sp)}</span>${esc(st.v)}</div>`;
      if (st.k === 'q') return `<div><span class="sp">（質問）</span><span class="qq">${esc(st.v)}</span></div>`;
      return `<div><span class="sp">（間）</span>${st.s}秒${st.a ? '　※ここで答えを書かせる' : ''}</div>`;
    }).join('');
    return `<div class="q"><div class="qt">${esc(it.no)}　正解：${esc(it.answer)}</div>
      <div class="sc">${lines}</div><div class="lead">${esc(it.why)}</div></div>`;
  }).join('')).join('');
}
function kanjiKey(s) {
  return `<table class="key"><thead><tr><th>問</th><th>ひらがな</th><th>正解</th></tr></thead><tbody>` +
    s.p5.kanji.items.map(x => `<tr><td>${x.id}</td><td>${esc(x.kana)}</td><td><b>${esc(x.ans)}</b></td></tr>`).join('') +
    `</tbody></table>`;
}
function writeKey(s) {
  return s.p5.write.items.map(x => `<div class="q"><div class="qt"><span class="no">${x.id}</span>${keep(x.prompt)}</div>
    <div class="tip"><b>解答例</b>　${esc(x.model)}</div>
    <table class="key"><thead><tr><th>見るところ</th></tr></thead><tbody>` +
    x.rubric.map(r => `<tr><td>${esc(r)}</td></tr>`).join('') + `</tbody></table></div>`).join('');
}

function manual() {
  const P = [];
  P.push(`<div class="pg">
  <h1>日本語 診断テスト　実施と採点の手引き</h1>
  <p class="lead">N4取得を前提に入職する職員の、実際の力を確かめるためのものです。
    第1回（<b>第2週</b>）と第2回（3か月後）を同じ構成で作ってあります。<br>
    <b>第1週には「N4到達度判定テスト」（60分）を行います。</b>同じ週に両方やると重すぎるので、
    こちらは1週ずらしてあります。</p>

  <h2>1　このテストの考え方</h2>
  <div class="warn"><b>合否を決めるテストではありません。</b>
    「N4に受かっているか」ではなく、<b>読む・聞く・書くのどこに穴があるか</b>を見つけて、
    研修の順番を決めるためのものです。本人にも最初にそう伝えてください。
    点数だけを伝えると、萎縮して力が出なくなります。</div>

  <h2>2　全体の流れ（合計70分＋口頭5分）</h2>
  <table><thead><tr><th>時間</th><th>すること</th><th>用意するもの</th></tr></thead><tbody>
    <tr><td>0:00〜0:05</td><td>説明（目的・やり方・合否ではないこと）</td><td>問題冊子・鉛筆・消しゴム</td></tr>
    <tr><td>0:05〜0:15</td><td>第1部　文字・語彙（10分）</td><td>時計</td></tr>
    <tr><td>0:15〜0:25</td><td>第2部　文法（10分）</td><td></td></tr>
    <tr><td>0:25〜0:40</td><td>第3部　読解（15分）</td><td></td></tr>
    <tr><td>0:40〜0:55</td><td>第4部　聴解（15分）</td><td><b>音を出す端末</b>（次ページ）</td></tr>
    <tr><td>0:55〜1:10</td><td>第5部　書く（15分）</td><td></td></tr>
    <tr><td>そのあと</td><td>口頭チェック（1人5分ずつ・別室）</td><td>口頭シート（4ページ目）</td></tr>
  </tbody></table>
  <div class="tip">部と部の間に、1分ずつ休みを入れてかまいません。
    2人同時に行い、<b>席は離して</b>ください。第5部だけは、書いている様子（筆順・持ち方）も見ておくと参考になります。</div>

  <h2>3　いつ実施するか</h2>
  <ul>
    <li><b>第1回</b>　<b>第2週（入職から8〜14日目）</b>。第1週は「N4到達度判定テスト」に使うためです。<br>
      <b>2週間を過ぎないうちに行ってください。</b>過ぎると職場で覚えた分が混ざり、入職時点の力が測れません。</li>
    <li><b>第2回</b>　第1回から<b>3か月後</b>（3月）。同じ時間帯・同じ部屋で行うと、比べやすくなります。</li>
  </ul>

  <h2>4　やってはいけないこと</h2>
  <ul>
    <li>途中で答えを教える、ヒントを出す（どこが分からないかが見えなくなります）</li>
    <li>2人の点数を並べて見せる、他の職員に点数を言う</li>
    <li>「N4なのにこれくらいできないのか」と言う</li>
  </ul></div>`);

  P.push(`<div class="pg">
  <h2>5　第4部（聴解）の流し方</h2>
  <p>聴解は、システムの読み上げページを使います。ブラウザで次を開いてください。</p>
  <div class="warn"><b>https://owlwindkaze-ux.github.io/owltiger1021/shindan/</b><br>
    合言葉は ほかの画面と同じ <b>owltiger2026</b> です。<br>
    <b>LINEやメールの中で開かないでください。音が出ません。</b>「ブラウザで開く」を押してください。</div>
  <ol>
    <li>第1回／第2回を えらぶ</li>
    <li>「🔊 音のテスト」を押して、音が出ることを確かめる（<b>始める前に必ず</b>）</li>
    <li>スピーカーの音量を、2人が同じように聞こえる大きさにする</li>
    <li>「はじめから通して再生」を押す。<b>止めずに最後まで</b>流します</li>
  </ol>
  <div class="tip">音が出ないときは、このページの<b>スクリプト（次ページ以降）を職員が読み上げて</b>ください。
    会話は1回だけ、ふつうの速さで読みます。（間）のところで止めて、答えを書く時間を取ります。</div>

  <h2>6　採点のしかた</h2>
  <table><thead><tr><th>部</th><th>問数</th><th>配点</th><th>採点</th></tr></thead><tbody>
    <tr><td>第1部　文字・語彙</td><td>20</td><td>各1点＝20点</td><td>○×</td></tr>
    <tr><td>第2部　文法</td><td>15</td><td>各1点＝15点</td><td>○×</td></tr>
    <tr><td>第3部　読解</td><td>8</td><td>各1点＝8点</td><td>○×</td></tr>
    <tr><td>第4部　聴解</td><td>10</td><td>各1点＝10点</td><td>○×</td></tr>
    <tr><td>第5部A　漢字を書く</td><td>10</td><td>各1点＝10点</td><td>字が読めればよい。とめ・はねは見ない</td></tr>
    <tr><td>第5部B　文を書く</td><td>2</td><td>各5点＝10点</td><td>次ページの見るところで</td></tr>
  </tbody></table>
  <p><b>合計73点。ただし、合計点よりも「部ごとの正答率」を見てください。</b></p>

  <h2>7　判定の目安（部ごと）</h2>
  <table><thead><tr><th>正答率</th><th>見方</th><th>すること</th></tr></thead><tbody>
    <tr><td><b>80%以上</b></td><td>その分野のN4は確か</td><td>N3の学習に進んでよい</td></tr>
    <tr><td><b>60〜79%</b></td><td>N4だが穴がある</td><td>N3と並行して、その分野を補う</td></tr>
    <tr><td><b>60%未満</b></td><td>N4相当に届いていない</td><td>N3の前に、その分野をN4から立て直す</td></tr>
  </tbody></table>

  <h2>8　結果から研修計画へ</h2>
  <table><thead><tr><th>出方</th><th>読み取り</th><th>次の3か月</th></tr></thead><tbody>
    <tr><td>全部80%以上</td><td>N4は本物</td><td>100日コース第1週から開始。N3を7月に狙える</td></tr>
    <tr><td>聴解だけ低い</td><td>教室の日本語しか聞いていない</td><td>聴解を毎日10分（システムの聴解を「ゆっくり」から）</td></tr>
    <tr><td>読解だけ低い</td><td>語彙はあるが文を追えない</td><td>読解のN4を1日1本。時間を計る</td></tr>
    <tr><td>第5部だけ低い</td><td>読めるが書けない</td><td>漢字の書き取りを毎日5字。記録の文型から入る</td></tr>
    <tr><td>第1部・第2部が低い</td><td>土台が弱い</td><td>N3に進まず、N4の語彙・文型を3か月やり直す</td></tr>
  </tbody></table></div>`);

  P.push(`<div class="pg">
  <h2>9　記入表（2人ぶん・コピーして使ってください）</h2>
  <table><thead><tr><th>部</th><th>満点</th><th>Aさん 得点</th><th>正答率</th><th>Bさん 得点</th><th>正答率</th></tr></thead><tbody>
    <tr><td>第1部　文字・語彙</td><td>20</td><td></td><td>　　　%</td><td></td><td>　　　%</td></tr>
    <tr><td>第2部　文法</td><td>15</td><td></td><td>　　　%</td><td></td><td>　　　%</td></tr>
    <tr><td>第3部　読解</td><td>8</td><td></td><td>　　　%</td><td></td><td>　　　%</td></tr>
    <tr><td>第4部　聴解</td><td>10</td><td></td><td>　　　%</td><td></td><td>　　　%</td></tr>
    <tr><td>第5部A　漢字</td><td>10</td><td></td><td>　　　%</td><td></td><td>　　　%</td></tr>
    <tr><td>第5部B　文</td><td>10</td><td></td><td>　　　%</td><td></td><td>　　　%</td></tr>
    <tr><td><b>合計</b></td><td><b>73</b></td><td></td><td>　　　%</td><td></td><td>　　　%</td></tr>
  </tbody></table>
  <p class="lead">第2回のあとは、同じ表にもう一度書き入れて、第1回と並べてください。
    <b>点の高さではなく、上がった幅</b>を見ます。</p>

  <h2>10　口頭チェック（1人5分・別室で）</h2>
  <p>紙のテストでは分からない「話す・聞き返す」を見ます。うまく答えられなくても、態度は評価しません。</p>
  <table><thead><tr><th>質問</th><th>見るところ</th></tr></thead><tbody>
    <tr><td>1　お名前と、いつ 日本へ 来ましたか。</td><td>質問を聞き取れるか</td></tr>
    <tr><td>2　今日は どうやって ここまで 来ましたか。</td><td>順を追って言えるか（〜て、〜て）</td></tr>
    <tr><td>3　インドネシアでは、どんな 勉強を しましたか。</td><td>過去の形で言えるか</td></tr>
    <tr><td>4　（写真を見せて）この人は 今、何を して いますか。</td><td>「〜ています」が使えるか</td></tr>
    <tr><td>5　仕事で わからない 言葉が あったら、どう しますか。</td><td>聞き返す言い方を持っているか</td></tr>
  </tbody></table>
  <table><thead><tr><th>見るところ</th><th>Aさん</th><th>Bさん</th></tr></thead><tbody>
    <tr><td>質問が聞き取れる（1回で／2回で／聞き取れない）</td><td></td><td></td></tr>
    <tr><td>答えが返せる（文で／単語で／返せない）</td><td></td><td></td></tr>
    <tr><td>文が作れる（2文以上／1文／作れない）</td><td></td><td></td></tr>
    <tr><td>分からないとき聞き返せる（できる／だまる）</td><td></td><td></td></tr>
  </tbody></table>
  <div class="tip"><b>いちばん大事なのは5番です。</b>「もう一度お願いします」が言える人は、
    現場で伸びます。言えない人は、まずそこから教えてください。事故を防ぐ力に直結します。</div></div>`);

  /* 正解・スクリプト */
  sets.forEach(s => {
    P.push(`<div class="pg"><h1>第${s.no}回（${esc(s.when)}）　正解一覧</h1>
      ${keyTable(s)}
      <h2>第5部A　漢字を書く</h2>${kanjiKey(s)}</div>`);
    P.push(`<div class="pg"><h1>第${s.no}回　第5部B　文を書く（採点の目安）</h1>
      <p class="lead">意味が通じることを いちばん重く見ます。助詞の細かい誤りだけで 0点にはしないでください。</p>
      ${writeKey(s)}</div>`);
    P.push(`<div class="pg"><h1>第${s.no}回　第4部　聴解スクリプト</h1>
      <p class="lead">システムで再生できないときは、これを読み上げてください。会話は<b>1回だけ</b>、ふつうの速さで。
        「（間）」で止めて、答えを書く時間を取ります。</p>
      ${scriptHtml(s)}</div>`);
  });

  return `<!doctype html><html lang="ja"><head><meta charset="utf-8">
    <title>診断テスト 実施と採点</title><style>${CSS}</style></head><body>${P.join('')}</body></html>`;
}

sets.forEach(s => fs.writeFileSync(`${OUT}/mondai${s.no}.html`, booklet(s)));
fs.writeFileSync(`${OUT}/tebiki.html`, manual());
console.log('HTML 出力: mondai1 / mondai2 / tebiki');
