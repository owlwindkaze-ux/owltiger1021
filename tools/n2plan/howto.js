const fs = require('fs');
const { withRuby } = require(__dirname + '/../hani/ruby.js');
const esc = s => String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const R = s => withRuby(esc(s));

const css = `
body{margin:0;font-family:"IPAPGothic","IPAGothic","WenQuanYi Zen Hei",sans-serif;color:#1b2733;font-size:10pt;line-height:1.85}
.pg{page-break-before:always}.pg:first-child{page-break-before:auto}
h1{font-size:19pt;color:#332e91;border-bottom:3px solid #332e91;padding-bottom:5px;margin:0 0 3mm}
h1 small{display:block;font-size:9.5pt;font-weight:400;color:#6b7784;margin-top:1.5mm}
h2{font-size:13pt;color:#fff;background:#4338ca;margin:6mm 0 3mm;padding:1.8mm 3mm;border-radius:3px}
h3{font-size:11pt;color:#332e91;margin:4mm 0 1.5mm;border-left:4px solid #4338ca;padding-left:2.5mm}
p{margin:2mm 0}
.lead{font-size:9.5pt;color:#55606c}
table{border-collapse:collapse;width:100%;margin:2.5mm 0;font-size:9.5pt}
th,td{border:1px solid #c7c9e8;padding:1.6mm 2.2mm;text-align:left;vertical-align:top}
th{background:#eef2ff;color:#332e91}
tr{page-break-inside:avoid}
.box{border:2px solid #4338ca;background:#eef2ff;border-radius:5px;padding:3mm 4mm;margin:3mm 0}
.box b{color:#332e91}
.tip{border-left:4px solid #0e7a52;background:#f2fbf7;padding:2.5mm 4mm;margin:3mm 0;font-size:9.5pt}
.warn{border-left:4px solid #c2410c;background:#fff7ed;padding:2.5mm 4mm;margin:3mm 0;font-size:9.5pt}
ul{margin:1.5mm 0 1.5mm 5.5mm;padding:0}
li{margin:1mm 0}
.num{display:flex;gap:3mm;margin:2.5mm 0;break-inside:avoid}
.num .n{flex:none;width:8mm;height:8mm;border-radius:50%;background:#4338ca;color:#fff;
  font-weight:bold;text-align:center;line-height:8mm;font-size:10pt}
.num .t{flex:1}
.time{font-family:"IPAGothic",monospace;background:#f4f5fb;border:1px solid #c7c9e8;border-radius:4px;
  padding:2.5mm 3.5mm;margin:2.5mm 0;font-size:10pt;line-height:1.9;white-space:pre}
ruby{ruby-align:center}rt{font-size:5.8pt;color:#4338ca;font-weight:400}
h1 rt,h2 rt{font-size:6.5pt;color:inherit;opacity:.8}
h3 rt{font-size:6pt}
th rt{font-size:5.6pt}
.foot{font-size:8.5pt;color:#6b7784;border-top:1px solid #c7c9e8;margin-top:5mm;padding-top:2mm}
`;

const P = [];

P.push(`<div class="pg">
<h1>${R('N2の 勉強の しかた')}<small>Cara belajar untuk JLPT N2 ／ 2026年9月〜2027年12月</small></h1>
<p class="lead">${R('この紙は、N2に合格するまでの66週を、毎日どう進めるかをまとめたものです。手もとに置いて、毎週見てください。')}</p>

<h2>${R('考え方は 三つだけ')}</h2>
<div class="num"><div class="n">1</div><div class="t"><b>${R('範囲は 自分で 決めません。')}</b><br>
${R('66週分すべて決めてあります。毎週「今週はここ」と書いてある分だけをやります。先を見て不安になる必要はありません。')}</div></div>
<div class="num"><div class="n">2</div><div class="t"><b>${R('覚える順番には 理由が あります。')}</b><br>
${R('その週に習う漢字を使う語が、同じ週の語彙に入っています。「団」を習う週に「団体・集団・劇団」が来ます。手がかりが一つで済むようにしてあります。')}</div></div>
<div class="num"><div class="n">3</div><div class="t"><b>${R('夜勤明けは 休みます。')}</b><br>
${R('これは計画に入れてあります。休んでも遅れません。')}</div></div>

<h2>${R('一週間の 流れ（勤務ごとに 変える）')}</h2>
<p>${R('曜日ではなく、勤務で決めます。')}</p>
<table>
<tr><th style="width:22%">${R('勤務')}</th><th style="width:24%">${R('いつ')}</th><th style="width:14%">${R('時間')}</th><th>${R('やること')}</th></tr>
<tr><td><b>${R('公休')}</b>（${R('月10日')}）</td><td>${R('昼の どこか')}</td><td><b>${R('90分')}</b></td><td>${R('読解45分 ＋ 文型・語彙30分 ＋ 聴解15分')}</td></tr>
<tr><td><b>${R('日勤')}</b>（${R('月10〜15日')}）</td><td>${R('出勤前 7:30〜9:00')}</td><td><b>${R('30〜40分')}</b></td><td>${R('文型と語彙。帰宅後は やりたければ10分')}</td></tr>
<tr><td><b>${R('早出')}</b>（${R('月6日')}）</td><td>${R('出勤前と 帰宅後')}</td><td><b>${R('10分＋30分')}</b></td><td>${R('朝は 前の日の 見直しだけ。夜に 新しい分')}</td></tr>
<tr><td><b>${R('夜勤の日')}</b>（${R('月4日')}）</td><td>${R('日中 10:00〜16:00')}</td><td><b>${R('60分')}</b></td><td>${R('ここが 重点日。まとめて 進めます')}</td></tr>
<tr><td><b>${R('夜勤明け')}</b></td><td>—</td><td><b>${R('0分')}</b></td><td>${R('休みます。余力が あれば 聴解を 聞き流すだけ')}</td></tr>
</table>
<div class="box"><b>${R('週の合計は 6時間半ほどです。')}</b>${R('これで66週後に間に合う計算になっています。')}</div>
</div>`);

P.push(`<div class="pg">
<h2>${R('一日の 中身')}<span style="font-size:9pt;font-weight:400">　${R('第1期（2026年10月〜2027年1月）')}</span></h2>
<p>${R('いちばん長い第1期は、毎日この三つだけです。')}</p>
<div class="time">${R('漢字　 4字　 約10分\n語彙　21語　 約20分\n文型　 2項目 約20分\n────────────────\n　　　　　　　約50分')}</div>
<div class="tip">${R('公休の日だけ、この前に読解45分を足します。')}</div>

<h3>${R('画面で 押す 順番')}</h3>
<div class="num"><div class="n">1</div><div class="t"><b>${R('漢字（10分）')}</b><br>
${R('「漢字・語彙」→ N2 の札 → 今週の4字を開く。書き順を1回見て、読みを声に出します。')}</div></div>
<div class="num"><div class="n">2</div><div class="t"><b>${R('語彙（20分）')}</b><br>
${R('「漢字・語彙」→ 熟語 のタブ → N2 の札。今週の21語。')}<br>
<b>${R('意味が 出てきたら「覚えた」、出てこなければ「要復習」を 押します。')}</b>${R('この印が あとで 効きます。')}</div></div>
<div class="num"><div class="n">3</div><div class="t"><b>${R('文型（20分）')}</b><br>
${R('「文型・文法」→ N2 の札 → 今週の2項目。例文3つを声に出して読み、そのあと練習問題3問。1項目10分の配分です。')}</div></div>

<h2>${R('期ごとに 変わるところ')}</h2>
<h3>${R('第1期（6〜22週）　ためる時期')}</h3>
<p>${R('上の三つを黙々と進めます。読解は公休だけでよく、聴解は週15分で十分です。')}
<b>${R('ここで焦って読解を増やすと、覚える時間が削られます。')}</b></p>

<h3>${R('第2期（23〜39週）　読解に 切りかえる')}</h3>
<p>${R('ここから主役が変わります。')}</p>
<div class="time">${R('読解 N2を 週1本　　時間を計る（画面が計ります）\n読解 N3を 週1本　　速さの練習。内容は分かるので\n　　　　　　　　　　「時間内に読めるか」だけ見る\n聴解 週6問\n文型・語彙は「要復習」の印が付いたものだけ')}</div>
<div class="warn"><b>${R('N2で落ちる人の多くは、読めないのではなく、時間内に読み切れません。')}</b><br>
${R('だから、内容の分かるN3を速く読む練習を入れてあります。')}</div>

<h3>${R('第3期（40〜48週）　模試と 補強')}</h3>
<p>${R('模試を受けて、点が低かった区分だけを埋めます。')}<b>${R('全部やり直さないのがこつです。')}</b></p>

<h3>${R('第4期（49〜65週）　100日コース')}</h3>
<p>${R('月〜日の日課が決まっている14週分を、そのまま進めます。')}
<b>${R('土曜は必ず50分で通しテスト。')}</b>${R('本番と同じ時間に体を慣らします。')}</p>

<h3>${R('第5期（66週）　直前')}</h3>
<p><b>${R('新しい教材は開きません。')}</b>${R('まちがえた問題と、覚えた印のない語だけを見ます。前の日は勉強しません。')}</p>
</div>`);

P.push(`<div class="pg">
<h2>${R('つまずいた ときの 手当て')}</h2>
<table>
<tr><th style="width:38%">${R('起きたこと')}</th><th>${R('どうするか')}</th></tr>
<tr><td>${R('一週間 できなかった')}</td><td><b>${R('取り戻しません。')}</b>${R('その週は飛ばして、今週の分から再開します。')}</td></tr>
<tr><td>${R('語彙が 覚えられない')}</td><td>${R('21語を 7語ずつ3回に分けます。朝・昼・夜に 見るだけでよいです。')}</td></tr>
<tr><td>${R('読解が 時間内に 終わらない')}</td><td>${R('解けた数ではなく、')}<b>${R('どこで止まったか')}</b>${R('を見ます。語彙が足りないのか、戻り読みをしているのか。')}</td></tr>
<tr><td>${R('模試の 点が 伸びない')}</td><td>${R('合計ではなく')}<b>${R('区分ごと')}</b>${R('に見ます。各19点が先です。合計90点はあとからついてきます。')}</td></tr>
<tr><td>${R('夜勤が 続いて つらい')}</td><td>${R('夜勤明けは0分でよいことを思い出してください。計画に入っています。')}</td></tr>
</table>

<h2>${R('いちばん 大事な こと')}</h2>
<div class="box" style="font-size:11pt">
<b>${R('「覚えた／要復習」の印を 押してください。')}</b><br>
${R('この印を押さないと、第3期からの「要復習だけ回す」ができません。')}
<b>${R('66週のうち、後半40週の効率が、この一手にかかっています。')}</b>
</div>

<h2>${R('66週の 全体')}</h2>
<table>
<tr><th style="width:12%">${R('期（き）')}</th><th style="width:16%">${R('週')}</th><th>${R('中身')}</th></tr>
<tr><td>${R('第0期')}</td><td>1〜5</td><td>${R('診断テスト ＋ N3の 見直し')}</td></tr>
<tr><td>${R('第1期')}</td><td>6〜22</td><td>${R('漢字18〜19字・語彙102語・文型10項目（週）')}</td></tr>
<tr><td>${R('第2期')}</td><td>23〜39</td><td>${R('読解が主役。第32週に 模試①')}</td></tr>
<tr><td>${R('第3期')}</td><td>40〜48</td><td>${R('模試②と補強。第44週が7月の本試験')}</td></tr>
<tr><td>${R('第4期')}</td><td>49〜65</td><td>${R('100日コース14週。模試④⑤⑥')}</td></tr>
<tr><td>${R('第5期')}</td><td>66</td><td><b>${R('12月5日（日）本試験')}</b></td></tr>
</table>
<div class="foot">${R('くわしい範囲は「N2 週ごとの学習範囲表」を見てください。この紙は その使い方の 案内です。')}<br>
Rincian cakupan mingguan ada pada lembar jadwal mingguan N2. Lembar ini adalah panduan cara memakainya.</div>
</div>`);

fs.writeFileSync('/tmp/n2plan/howto.html',
  `<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>N2の勉強のしかた</title><style>${css}</style></head><body>${P.join('')}</body></html>`);
console.log('HTML 出力', P.length, 'ページ分');
