/* N4到達度判定テストの PDF もと（HTML）を 作る。
 *
 *   node tools/hani/n4hantei.js
 *     → /tmp/n4hantei/mondai.html   学習者に 配る 問題冊子
 *     → /tmp/n4hantei/staff.html    職員用（実施要領・正解・解説・聴解原稿・判定）
 *
 * 問題は n4hantei-data.js に 1か所だけ 置いてある。
 * 問題冊子・正解一覧・聴解原稿は すべて そこから 作るので、必ず 一致する。
 */
'use strict';
const fs = require('fs');
const D = require(__dirname + '/n4hantei-data.js');
const OUT = '/tmp/n4hantei';
fs.mkdirSync(OUT, { recursive: true });

const esc = s => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
/* __ことば__ は 下線にする（読み方・言いかえを 問う ところ） */
const nl = s => esc(s).replace(/\n/g, '<br>')
  .replace(/__(.+?)__/g, '<u>$1</u>');
const N = ['①', '②', '③', '④'];

/* 通し番号。問題冊子と 正解一覧で 同じ番号に なるよう、ここで 一度だけ ふる */
let no = 0;
const nextNo = () => ++no;

const css = `
body{margin:0;font-family:"IPAPGothic","IPAGothic","WenQuanYi Zen Hei",sans-serif;
  color:#12212e;font-size:10.5pt;line-height:1.85}
.pg{page-break-before:always}.pg:first-child{page-break-before:auto}
h1{font-size:18pt;color:#1d4ed8;border-bottom:3px solid #1d4ed8;padding-bottom:5px;margin:0 0 3mm}
h1 small{display:block;font-size:9.5pt;font-weight:400;color:#55606c;margin-top:1.5mm}
h2{font-size:13pt;color:#fff;background:#1d4ed8;margin:6mm 0 3mm;padding:1.8mm 3mm;border-radius:3px}
h3{font-size:11.5pt;color:#1d4ed8;margin:5mm 0 2mm;border-left:4px solid #1d4ed8;padding-left:2.5mm}
p{margin:2mm 0}
.inst{background:#eff6ff;border:1px solid #bfdbfe;border-radius:4px;padding:2mm 3mm;margin:2mm 0;font-size:10pt}
.q{margin:3.5mm 0;break-inside:avoid}
.q .n{display:inline-block;min-width:8mm;font-weight:bold;color:#1d4ed8}
.q .body{display:inline}
.opts{margin:1mm 0 0 8mm;padding:0;list-style:none}
.opts li{display:inline-block;margin-right:6mm;white-space:nowrap}
.psg{border:1px solid #cbd5e1;border-radius:4px;padding:3mm 4mm;margin:2.5mm 0;background:#f8fafc;
  white-space:pre-wrap;break-inside:avoid}
.psg .ttl{font-weight:bold;margin-bottom:1.5mm}
table{border-collapse:collapse;margin:2.5mm 0;font-size:10pt}
th,td{border:1px solid #94a3b8;padding:1.4mm 3mm;text-align:left}
th{background:#eff6ff}
.note{font-size:9.5pt;color:#475569;margin-top:1.5mm;white-space:pre-wrap}
.ansbox{border:2px solid #1d4ed8;border-radius:5px;padding:3mm 4mm;margin:3mm 0}
.sheet{width:100%;border-collapse:collapse;font-size:10pt}
.sheet td,.sheet th{border:1px solid #64748b;padding:1.6mm 2mm;text-align:center}
.sheet th{background:#eff6ff;font-size:9.5pt}
.key{font-size:10pt}
.key td,.key th{border:1px solid #94a3b8;padding:1.2mm 2.5mm}
.key .a{font-weight:bold;color:#1d4ed8;text-align:center}
.why{font-size:9.5pt;color:#475569}
.box{border:2px solid #1d4ed8;background:#eff6ff;border-radius:5px;padding:3mm 4mm;margin:3mm 0}
.warn{border-left:4px solid #c2410c;background:#fff7ed;padding:2.5mm 4mm;margin:3mm 0}
.scr{background:#f8fafc;border:1px solid #cbd5e1;border-radius:4px;padding:2.5mm 3.5mm;
  margin:2mm 0;white-space:pre-wrap;font-size:10pt;break-inside:avoid}
.foot{font-size:9pt;color:#6b7784;border-top:1px solid #cbd5e1;margin-top:5mm;padding-top:2mm}
`;

/* ============ 学習者に 配る 問題冊子 ============ */
const M = [];          /* 問題冊子 */
const KEY = [];        /* 正解一覧 [通し番号, 区分, 正解, 解説] */

function mcq(part, item, showOpts) {
  const n = nextNo();
  KEY.push([n, part, N[item.ans], item.why || '']);
  const opts = (showOpts || item.opts).map((o, i) =>
    `<li>${N[i]} ${esc(o)}</li>`).join('');
  return `<div class="q"><span class="n">${n}</span><span class="body">${nl(item.q)}</span>
    <ul class="opts">${opts}</ul></div>`;
}

M.push(`<div class="pg">
<h1>N4 到達度判定テスト<small>Tes pencapaian N4 ／ 新人コース 第1週（12月・入職のすぐあと）</small></h1>
<div class="box">
<p><b>これは、いま N4が どれくらい できるかを 見る テストです。</b>
点数で 人を 比べる ものでは ありません。また、<b>できなくても 心配 しないで ください。</b>
<b>できなかった ところを 見つけて、これから 何を 多く 勉強するかを 決める</b> ために 行います。</p>
<p style="font-size:9.5pt;color:#475569">Tes ini untuk melihat sejauh mana N4 sudah dikuasai.
Bukan untuk membandingkan orang, tapi untuk menemukan bagian yang belum bisa.</p>
</div>
<table>
<tr><th>部</th><th>中身</th><th>問</th><th>時間</th></tr>
<tr><td>第1部</td><td>文字・語彙</td><td>25問</td><td rowspan="3">45分<br>（3つ つづけて）</td></tr>
<tr><td>第2部</td><td>文法</td><td>20問</td></tr>
<tr><td>第3部</td><td>読解</td><td>9問</td></tr>
<tr><td>第4部</td><td>聴解</td><td>12問</td><td>15分</td></tr>
<tr><th colspan="2">合計</th><th>66問</th><th>60分</th></tr>
</table>
<div class="inst">
<b>気を つける こと</b><br>
・答えは <b>解答用紙</b>に 書いて ください。問題の 紙に 書いても 点に なりません。<br>
・わからない 問題は、<b>とばして 先へ</b> 進んで ください。あとで もどれます。<br>
・辞書・スマホは 使えません。<br>
・第4部（聴解）は、<b>1回だけ</b> 聞いて 答えます。
</div>
<p class="foot">名前（Nama）：＿＿＿＿＿＿＿＿＿＿＿＿　　日づけ：＿＿＿年＿＿月＿＿日</p>
</div>`);

/* ---- 第1部 ---- */
M.push(`<div class="pg"><h2>第1部　文字・語彙（25問）</h2>
<h3>問題1　<u>下線</u>の ことばの 読み方を、①②③④から 一つ えらんで ください。</h3>
${D.P1.map(x => mcq('文字・語彙', x)).join('')}
<h3>問題2　ひらがなの ことばを 漢字で 書くと どれですか。一つ えらんで ください。</h3>
${D.P2.map(x => mcq('文字・語彙', x)).join('')}
<h3>問題3　（　　）に 入る ことばを 一つ えらんで ください。</h3>
${D.P3.map(x => mcq('文字・語彙', x)).join('')}
<h3>問題4　<u>下線</u>の ことばと 意味が いちばん 近いものを 一つ えらんで ください。</h3>
${D.P4.map(x => mcq('文字・語彙', x)).join('')}
</div>`);

/* ---- 第2部 ---- */
const p6html = D.P6.map(x => {
  const n = nextNo();
  const shown = x.show.map(i => x.parts[i]);
  const ansIdx = x.show.indexOf(x.star);
  KEY.push([n, '文法', N[ansIdx], x.why || '']);
  const blanks = x.parts.map((_, i) => i === x.star ? '　★　' : '＿＿＿').join('');
  return `<div class="q"><span class="n">${n}</span><span class="body">${esc(x.head)}${blanks}${esc(x.tail)}<br>
    <span style="font-size:9.5pt;color:#475569">★に 入るものを 一つ えらんで ください。</span></span>
    <ul class="opts">${shown.map((o, i) => `<li>${N[i]} ${esc(o)}</li>`).join('')}</ul></div>`;
}).join('');

M.push(`<div class="pg"><h2>第2部　文法（20問）</h2>
<h3>問題5　（　　）に 入るものを 一つ えらんで ください。</h3>
${D.P5.map(x => mcq('文法', x)).join('')}
<h3>問題6　★に 入るものを 一つ えらんで ください。</h3>
${p6html}
<h3>問題7　文章を 読んで、（ ア ）（ イ ）に 入るものを 一つ えらんで ください。</h3>
<div class="psg">${nl(D.P7.text)}</div>
${D.P7.items.map(x => mcq('文法', x)).join('')}
</div>`);

/* ---- 第3部 ---- */
const p8html = D.P8.map(p => {
  let body = `<h3>${esc(p.title)}</h3><p>${nl(p.intro)}</p>`;
  if (p.text) body += `<div class="psg">${nl(p.text)}</div>`;
  if (p.table) {
    body += '<table>' + p.table.map((row, ri) =>
      '<tr>' + row.map(c => ri === 0 ? `<th>${esc(c)}</th>` : `<td>${esc(c)}</td>`).join('') + '</tr>'
    ).join('') + '</table>';
  }
  if (p.note) body += `<div class="note">${nl(p.note)}</div>`;
  body += p.items.map(x => mcq('読解', x)).join('');
  return body;
}).join('');

M.push(`<div class="pg"><h2>第3部　読解（9問）</h2>
<p class="inst">文章を 読んで、質問に 答えて ください。答えは 一つだけです。</p>
${p8html}
</div>`);

/* ---- 第4部（聴解）：学習者の 紙には 選択肢だけ 出す ---- */
const CH = [
  ['課題理解', 'この あと どう するかを 答えます。'],
  ['ポイント理解', '先に 質問を 読んでから 聞きます。'],
  ['発話表現', 'こんな とき 何と 言いますか。'],
  ['即時応答', '短い ことばに すぐ 答えます。']
];
let chHtml = '';
CH.forEach(([k, note]) => {
  chHtml += `<h3>${esc(k)}　<span style="font-size:9.5pt;font-weight:400;color:#475569">${esc(note)}</span></h3>`;
  D.P9[k].forEach(x => {
    const n = nextNo();
    KEY.push([n, '聴解', N[x.ans], x.why || '']);
    const q = (k === '課題理解' || k === 'ポイント理解')
      ? `<span class="body">${esc(x.q)}</span>` : '<span class="body">（音を 聞いて 答えます）</span>';
    chHtml += `<div class="q"><span class="n">${n}</span>${q}
      <ul class="opts">${x.opts.map((o, i) => `<li>${N[i]} ${esc(o)}</li>`).join('')}</ul></div>`;
  });
});

M.push(`<div class="pg"><h2>第4部　聴解（12問）</h2>
<p class="inst">音を 聞いて、答えを 一つ えらんで ください。<b>音は 1回だけ</b> 流れます。
「課題理解」「ポイント理解」は、質問が 紙にも 書いて あります。</p>
${chHtml}
</div>`);

/* ---- 解答用紙 ---- */
const rows = [];
for (let i = 1; i <= no; i += 5) {
  const cells = [];
  for (let j = i; j < i + 5 && j <= no; j++) {
    cells.push(`<th>${j}</th><td style="width:26mm">①　②　③　④</td>`);
  }
  rows.push('<tr>' + cells.join('') + '</tr>');
}
M.push(`<div class="pg"><h1>解答用紙<small>Lembar jawaban</small></h1>
<p>名前（Nama）：＿＿＿＿＿＿＿＿＿＿＿＿＿＿　　日づけ：＿＿＿年＿＿月＿＿日</p>
<p class="inst">正しいと 思う 番号を ○で かこんで ください。</p>
<table class="sheet">${rows.join('')}</table>
</div>`);

fs.writeFileSync(OUT + '/mondai.html',
  `<!doctype html><html lang="ja"><head><meta charset="utf-8">
   <title>N4到達度判定テスト</title><style>${css}</style></head><body>${M.join('\n')}</body></html>`);

/* ============ 職員用 ============ */
const S = [];
S.push(`<div class="pg">
<h1>N4 到達度判定テスト　職員用<small>実施要領・正解・解説・聴解の原稿・判定</small></h1>
<div class="box">
<p><b>このテストは、入職した時点で N4が どれだけ 身についているかを 判定し、
12月からの研修で どこを厚くするかを 決める ために 行います。</b></p>
<p>N4に合格していても、実際に使える力には 差があります。「N4を持っている」を前提にせず、<b>入口で実物を測ってから量を決める</b>ための道具です。
実施は<b>第1週（12月・入職のすぐあと）</b>。結果は その週のうちに面談で返します。</p>
</div>
<h2>1　実施のしかた</h2>
<table>
<tr><th>いつ</th><td><b>第1週（入職のすぐあと）</b>。勉強会の時間では足りないので、<b>60分まとめて</b>取ってください。来日直後で疲れているので、<b>午前中</b>が望ましい</td></tr>
<tr><th>もちもの</th><td>問題冊子・解答用紙・えんぴつ。辞書とスマホは しまわせる</td></tr>
<tr><th>第1〜3部</th><td><b>45分</b>。続けて解かせる。途中で区切らない</td></tr>
<tr><th>第4部（聴解）</th><td><b>15分</b>。<b>読み上げ画面で流します</b>（診断テストと同じ画面）。<br>
  入口メニュー →「新人コース」→「<b>テストの聴解（職員用）</b>」→ <b>「N4到達度判定（12月・問55〜66）」</b>を押す。<br>
  問55〜問66が出ます（紙の冊子と同じ番号）。<b>1回だけ</b>。むずかしければ2回まで（回数を記録すること）</td></tr>
<tr><th>音が出ないとき</th><td>この冊子の<b>5番の原稿を職員が読み上げて</b>ください。
  速さは ふつうより<b>少しゆっくり</b>。会話は役を変えて読みます</td></tr>
<tr><th>はじめる前に</th><td>読み上げ画面の<b>「音のテスト」を必ず押す</b>。
  音が出るか・音量・iPhoneの再生制限の解除を、ここで確かめます</td></tr>
<tr><th>採点</th><td>1問1点・<b>66点満点</b>。判定は<b>部ごとの正答率</b>で行う</td></tr>
</table>
<div class="warn"><b>点数を人に見せないこと。</b>本人にだけ返し、できなかった区分を一緒に確かめてください。
点は「これから何をするか」を決めるための材料です。</div>

<h2>2　判定の目安</h2>
<p>合計だけで決めず、<b>部ごとの正答率</b>を見てください。研修の量を決めるための材料です。</p>
<table>
<tr><th>判定</th><th>目安</th><th>12月からの研修を どうするか</th></tr>
<tr><td><b>A　N4は 身についている</b></td><td>合計 <b>80%以上</b>（53点以上）<br>かつ どの部も 60%以上</td>
  <td>予定どおり。第2期（第5〜12週）でN4を仕上げ、<b>早く終われば N3を前倒し</b>してよい</td></tr>
<tr><td><b>B　穴がある</b></td><td>合計 65〜79%（43〜52点）</td>
  <td>予定どおり進めるが、<b>60%未満だった部を 第2期で厚くする</b>。
  その区分の量を1.5倍にし、代わりにできている区分を減らす</td></tr>
<tr><td><b>C　N4が まだ入っていない</b></td><td>合計 65%未満（42点以下）<br>または どれかの部が 50%未満</td>
  <td><b>第1期（ならし）を第6週まで延ばし</b>、N5から積み直す。
  7月のN3は無理をさせず、<b>12月のN3受験に切りかえることも面談で相談する</b></td></tr>
</table>
<div class="warn"><b>Cが出ても、本人を責めないでください。</b>
N4に合格していても、使える力が落ちていることは ふつうにあります。
<b>入口で分かったほうが、あとで間に合わなくなるより ずっとよい</b>という話をしてください。</div>
<h3>部ごとの読み方</h3>
<table>
<tr><th>弱かった部</th><th>12月からの手当て</th></tr>
<tr><td>第1部 文字・語彙</td><td>いちばん優先。漢字と語彙の1日の量を増やす（他を減らしてでも）。
  カードを毎日使わせる</td></tr>
<tr><td>第2部 文法</td><td>文型の1日の項目数を増やす。例文を声に出して読ませる</td></tr>
<tr><td>第3部 読解</td><td>第2期の「読解 週2本」を週3本にする。時間はまだ計らない</td></tr>
<tr><td>第4部 聴解</td><td>「ゆっくり」の速さで毎日3問。仕事で聞こえた言葉のメモを続けさせる</td></tr>
</table>

<h2>3　記録表</h2>
<table class="sheet">
<tr><th>名前</th><th>第1部<br>文字・語彙<br>/25</th><th>第2部<br>文法<br>/20</th>
  <th>第3部<br>読解<br>/9</th><th>第4部<br>聴解<br>/12</th><th>合計<br>/66</th><th>％</th><th>判定</th></tr>
${'<tr><td style="height:9mm"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>'.repeat(8)}
</table>
</div>`);

/* 正解一覧 */
const keyRows = KEY.map(([n, part, a, why]) =>
  `<tr><td class="a">${n}</td><td>${esc(part)}</td><td class="a">${a}</td><td class="why">${esc(why)}</td></tr>`).join('');
S.push(`<div class="pg"><h2>4　正解と 解説</h2>
<table class="key"><tr><th>問</th><th>区分</th><th>正解</th><th>なぜ そうなるか</th></tr>
${keyRows}</table>
</div>`);

/* 聴解の原稿 */
let scr = '';
CH.forEach(([k]) => {
  scr += `<h3>${esc(k)}</h3>`;
  D.P9[k].forEach((x, i) => {
    scr += `<div class="scr"><b>${esc(k)} ${i + 1}</b>\n${esc(x.script)}`
        + (x.q ? `\n\n質問：${esc(x.q)}` : '')
        + `\n\n選択肢：${x.opts.map((o, j) => N[j] + ' ' + o).join('　')}`
        + `\n正解：${N[x.ans]}</div>`;
  });
});
S.push(`<div class="pg"><h2>5　聴解の 原稿</h2>
<div class="inst"><b>ふだんは 読み上げ画面（「N4到達度判定（12月・問55〜66）」）を 使ってください。</b>
この原稿は、<b>音が 出ないときに 職員が 読む</b> ためのものです。画面と 中身は 同じです。<br>
読むときは 問題番号を 言ってから（例：「問55」）。
会話は <b>役を 変えて</b> 読んでください。一人で 読むときは、少し 間を あけると 聞き取りやすく なります。
「発話表現」「即時応答」は <b>選択肢も 読み上げます</b>（紙にも 書いて あります）。</div>
${scr}
<p class="foot">問題・正解・この原稿は、すべて <code>tools/hani/n4hantei-data.js</code> の
1か所から 作っています。直すときは そこを 直して 作り直してください。</p>
</div>`);

fs.writeFileSync(OUT + '/staff.html',
  `<!doctype html><html lang="ja"><head><meta charset="utf-8">
   <title>N4到達度判定テスト 職員用</title><style>${css}</style></head><body>${S.join('\n')}</body></html>`);

console.log('HTML 出力　全' + no + '問（問題冊子・職員用）');
