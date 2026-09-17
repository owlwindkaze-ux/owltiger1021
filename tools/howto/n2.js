/* N2コースの使い方（実習生向け）。N4を超える漢字にはふりがな。 */
const fs = require('fs');
const { withRuby } = require(__dirname + '/ruby.js');
const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const R = s => withRuby(esc(s));
const ID = s => `<span class="id">${esc(s)}</span>`;

const css = `
body{margin:0;font-family:"IPAPGothic","IPAGothic","WenQuanYi Zen Hei",sans-serif;color:#1b2733;font-size:10.5pt;line-height:1.95}
.pg{page-break-before:always}.pg:first-child{page-break-before:auto}
h1{font-size:19pt;color:#332e91;border-bottom:3px solid #332e91;padding-bottom:5px;margin:0 0 3mm}
h1 small{display:block;font-size:9.5pt;font-weight:400;color:#55606c;margin-top:1.5mm}
h2{font-size:13pt;color:#fff;background:#4338ca;margin:6mm 0 3mm;padding:1.8mm 3mm;border-radius:3px}
h3{font-size:11.5pt;color:#332e91;margin:4.5mm 0 1.5mm;border-left:4px solid #4338ca;padding-left:2.5mm}
p{margin:2mm 0}
.id{display:block;font-size:9pt;color:#6b7784;margin-top:.6mm}
.lead{font-size:10pt;color:#55606c}
table{border-collapse:collapse;width:100%;margin:2.5mm 0;font-size:10pt}
th,td{border:1px solid #c7c9e8;padding:1.8mm 2.4mm;text-align:left;vertical-align:top}
th{background:#eef2ff;color:#332e91}
tr{page-break-inside:avoid}
.box{border:2px solid #4338ca;background:#eef2ff;border-radius:5px;padding:3mm 4mm;margin:3mm 0}
.tip{border-left:4px solid #0e7a52;background:#f2fbf7;padding:2.5mm 4mm;margin:3mm 0}
.warn{border-left:4px solid #c2410c;background:#fff7ed;padding:2.5mm 4mm;margin:3mm 0}
ul{margin:1.5mm 0 1.5mm 5.5mm;padding:0}
li{margin:1.2mm 0}
.num{display:flex;gap:3mm;margin:3mm 0;break-inside:avoid}
.num .n{flex:none;width:8.5mm;height:8.5mm;border-radius:50%;background:#4338ca;color:#fff;
  font-weight:bold;text-align:center;line-height:8.5mm;font-size:10.5pt}
.num .t{flex:1}
.scr{background:#f6f8fb;border:1px solid #c7c9e8;border-radius:5px;padding:3mm 4mm;margin:2.5mm 0;font-size:10pt}
.scr b{color:#332e91}
.big{font-size:13pt;font-weight:bold;color:#332e91}
ruby{ruby-align:center}rt{font-size:6pt;color:#4338ca;font-weight:400}
h1 rt,h2 rt{font-size:6.8pt;color:inherit;opacity:.85}
h3 rt{font-size:6.2pt}th rt{font-size:5.8pt}
.foot{font-size:9pt;color:#6b7784;border-top:1px solid #c7c9e8;margin-top:5mm;padding-top:2mm}
`;

const P = [];

P.push(`<div class="pg">
<h1>${R('N2コースの 使い方')}<small>Cara memakai Kursus N2 ／ ${R('2026年9月から 2027年12月の 試験まで、66週')}</small></h1>

<p class="lead">${R('この紙は、N3に 合格した あなたが、つぎに N2を 目ざす ための ものです。')}
${ID('Kertas ini untuk Anda yang sudah lulus N3 dan ingin melanjutkan ke N2.')}</p>

<div class="box">
<p class="big">${R('N3のときと ちがう ところ')}</p>
<p>${R('N2は 1年4か月 かかります。長いので、<b>月ごと</b>ではなく <b>週ごと</b>に 進みます。')}<br>
${R('毎週、画面に「今週 やること」が 出ます。それだけ やれば よいです。')}</p>
${ID('N2 butuh 1 tahun 4 bulan. Karena panjang, rencananya per minggu, bukan per bulan. Setiap minggu layar menampilkan "tugas minggu ini".')}
</div>

<h2>${R('① ひらき方')}</h2>
<div class="num"><div class="n">1</div><div class="t">
${R('スマホで つぎの 住所を ひらきます。')}<br>
<span class="scr" style="display:inline-block;margin:1.5mm 0">https://owlwindkaze-ux.github.io/owltiger1021/</span>
${ID('Buka alamat di atas pada HP Anda.')}</div></div>
<div class="num"><div class="n">2</div><div class="t">
${R('合言葉 <b>owltiger2026</b> を 入れます。二回目からは 要りません。')}
${ID('Masukkan kata sandi owltiger2026. Setelah itu tidak diperlukan lagi.')}</div></div>
<div class="num"><div class="n">3</div><div class="t">
${R('メニューの「N2」を おします。')}
${ID('Tekan "N2" pada menu.')}</div></div>
<div class="num"><div class="n">4</div><div class="t">
${R('上に タブが 3つ あります。ふだん 見るのは <b>いちばん左</b>だけです。')}
${ID('Ada tiga tab di atas. Yang dilihat sehari-hari hanya yang paling kiri.')}</div></div>

<table>
<tr><th style="width:26%">${R('タブ')}</th><th>${R('いつ 見るか')}</th></tr>
<tr><td><b>${R('今週 やること')}</b></td><td>${R('<b>毎日</b>。ここだけ 見れば よいです。')}${ID('Setiap hari. Cukup lihat di sini.')}</td></tr>
<tr><td>${R('ロードマップ')}</td><td>${R('ときどき。1年4か月 ぜんたいの 流れを 見たいとき。')}${ID('Sesekali, kalau ingin melihat alur 1 tahun 4 bulan.')}</td></tr>
<tr><td>${R('診断テスト')}</td><td>${R('はじめに 一度だけ。いまの 力を 見ます。')}${ID('Satu kali di awal, untuk mengukur kemampuan sekarang.')}</td></tr>
</table>

<h2>${R('② 「今週 やること」の 見方')}</h2>
<table>
<tr><th style="width:32%">${R('出るもの')}</th><th>${R('意味')}</th></tr>
<tr><td>${R('第◯週　◯月◯日〜◯月◯日')}</td><td>${R('いまが 66週の うちの 何週目か。')}${ID('Minggu ke berapa dari 66 minggu.')}</td></tr>
<tr><td>${R('第◯期　◯◯◯期')}</td><td>${R('いまが どの 時期か。時期ごとに やることが 変わります。')}${ID('Tahap keberapa. Isi belajar berubah tiap tahap.')}</td></tr>
<tr><td><b>${R('今週 やること')}</b></td><td>${R('その週の 分。<b>月〜金の マス</b>が ある行は、平日 1日ずつ おします。')}${ID('Baris dengan kotak Sen–Jum dikerjakan tiap hari kerja.')}</td></tr>
<tr><td>${R('今週 ひらくもの')}</td><td>${R('おすと、<b>その週の 分だけ</b>が ひらきます。')}${ID('Saat ditekan, yang terbuka hanya bagian minggu itu.')}</td></tr>
<tr><td>${R('今週の 一覧')}</td><td>${R('たたんで あります。おすと、その週の 漢字・語彙・文型が ぜんぶ 見られます。')}${ID('Dilipat. Tekan untuk melihat seluruh kanji, kosakata, dan pola minggu itu.')}</td></tr>
</table>

<div class="tip">
<b>${R('「今週 ひらくもの」は、押すだけで よいです。')}</b>
${R('レベルを えらんだり、絞り込みを おしたり する 必要は ありません。')}
${ID('Cukup ditekan. Anda tidak perlu memilih level atau menyaring sendiri.')}
</div>
</div>`);

P.push(`<div class="pg">
<h2>${R('③ 一日の 使い方')}</h2>
<p>${R('勤務の 種類で 分けます。曜日では ありません。')}
${ID('Dibagi menurut jenis shift, bukan menurut hari.')}</p>
<table>
<tr><th style="width:22%">${R('勤務')}</th><th style="width:16%">${R('時間')}</th><th>${R('中身')}</th></tr>
<tr><td>${R('公休（休みの日）')}</td><td><b>${R('90分')}</b></td>
<td>${R('読解25分 ＋ 読解N3を1本 10分 ＋ 聴解15分 ＋ 要復習40分')}</td></tr>
<tr><td>${R('日勤')}</td><td><b>${R('30〜40分')}</b></td>
<td>${R('出勤の 前に。帰ってからは 10〜15分で よいです。')}</td></tr>
<tr><td>${R('早出')}</td><td><b>${R('前10分＋後30分')}</b></td>
<td>${R('出勤の 前は 語彙と 文型を 早く 回すだけ。')}</td></tr>
<tr><td>${R('夜勤の日')}</td><td><b>${R('60分')}</b></td>
<td>${R('昼の あいだに。夜勤中は 仕事を 第一に します。')}</td></tr>
<tr><td>${R('夜勤明け')}</td><td><b>${R('0〜10分')}</b></td>
<td>${R('<b>休むのが 仕事です。</b>やらなくて かまいません。')}</td></tr>
</table>
<p class="lead">${R('一週間で だいたい 6〜7時間です。')}${ID('Sekitar 6–7 jam per minggu.')}</p>

<h2>${R('④ 66週の 流れ')}</h2>
<table>
<tr><th style="width:15%">${R('時期')}</th><th style="width:20%">${R('いつ')}</th><th>${R('すること')}</th></tr>
<tr><td>${R('第0期')}</td><td>${R('2026年9月〜10月')}</td>
<td>${R('診断テストを 受ける。N3を 見直す。覚えた印の あるものは 飛ばして よいです。')}</td></tr>
<tr><td>${R('第1期')}</td><td>${R('2026年10月〜2027年1月')}</td>
<td>${R('N2の 漢字320字・語彙1,735語・文型170項目を ひととおり 覚える。<b>ここが いちばん 量が 多い</b>です。')}</td></tr>
<tr><td>${R('第2期')}</td><td>${R('2027年2月〜5月')}</td>
<td>${R('新しく 覚えるものは ありません。読解を 週1本、聴解を 週6問。あとは 要復習を 回します。')}</td></tr>
<tr><td>${R('第3期')}</td><td>${R('2027年6月〜7月')}</td>
<td>${R('155分の 模試を 3回。受けて、まちがいを 直して、また 受けます。')}</td></tr>
<tr><td>${R('第4期')}</td><td>${R('2027年8月〜11月')}</td>
<td>${R('模試で 解いた 読解と 聴解を、もう一度。土曜は 155分の 通し練習。')}</td></tr>
<tr><td>${R('第5期')}</td><td>${R('2027年11月末')}</td>
<td>${R('新しい ものは ひらきません。12月5日（日）が 本番です。')}</td></tr>
</table>

<h2>${R('⑤ 時期で 変わる こと')}</h2>
<div class="scr">
<b>${R('第0期・第1期')}</b>（${R('〜2027年1月')}）<br>
${R('「今週 ひらくもの」を おすと、<b>その週の 分だけ</b>が 出ます。')}<br>
${R('漢字は 平日1日 4字ほど、語彙は 20語ほど、文型は 2項目ほどです。')}
</div>
<div class="scr">
<b>${R('第2期から')}</b>（${R('2027年2月〜')}）<br>
${R('新しく 覚えるものが なくなるので、「今週 ひらくもの」を おすと <b>「要復習」だけ</b>が 出ます。')}<br>
${R('ボタンの 下に、どちらが 出るか 書いてあります。')}
</div>
<div class="warn">
<b>${R('第2期からが、いちばん 差が つきます。')}</b>
${R('新しい ものが 来ないので、<b>自分で 要復習を 回さない人</b>は 力が 止まります。')}
${R('語彙は 1日60語、文型は 1日10項目が 目安です。')}
${ID('Mulai tahap 2 tidak ada materi baru. Yang tidak mengulang sendiri akan berhenti berkembang. Patokan: 60 kosakata dan 10 pola per hari.')}
</div>
</div>`);

P.push(`<div class="pg">
<h2>${R('⑥ 模試の 受け方')}</h2>
<p>${R('第3期（2027年6月〜7月）に 3回 あります。第4期でも もう一度 使います。')}
${ID('Ada tiga kali pada tahap 3 (Juni–Juli 2027), dan dipakai lagi pada tahap 4.')}</p>
<div class="num"><div class="n">1</div><div class="t">
${R('<b>土曜日に、通しで やります。</b>途中で やめると、意味が 半分に なります。')}
${ID('Kerjakan sekaligus pada hari Sabtu. Kalau berhenti di tengah, manfaatnya berkurang setengah.')}</div></div>
<div class="num"><div class="n">2</div><div class="t">
${R('言語知識と 読解で <b>105分</b>、休んでから 聴解 <b>50分</b>。合わせて 155分です。')}
${ID('105 menit untuk pengetahuan bahasa dan membaca, lalu 50 menit menyimak. Totalnya 155 menit.')}</div></div>
<div class="num"><div class="n">3</div><div class="t">
${R('終わると、区分ごとの 点が 出ます。<b>合計90点 かつ どの区分も 19点以上</b>で 合格の 目安です。')}
${ID('Setelah selesai, nilai per bagian ditampilkan. Patokan lulus: total 90 poin dan setiap bagian minimal 19.')}</div></div>
<div class="num"><div class="n">4</div><div class="t">
${R('つぎの 2週で、まちがえた 問題を 直します。1週目は 言語知識、2週目は 読解と 聴解です。')}
${ID('Dua minggu berikutnya dipakai untuk memperbaiki kesalahan.')}</div></div>

<div class="warn">
<b>${R('19点に とどかない 区分が あると、合計が 高くても 不合格です。')}</b>
${R('赤で 出た 区分を、つぎの 2週で 集中して 直してください。')}
${ID('Kalau ada satu bagian di bawah 19, Anda tidak lulus meski totalnya tinggi. Perbaiki bagian yang ditandai merah.')}
</div>

<h2>${R('⑦ 困ったときは')}</h2>
<table>
<tr><th style="width:38%">${R('こんなとき')}</th><th>${R('こうしてください')}</th></tr>
<tr><td>${R('第1期の 量が 多すぎる')}</td>
<td>${R('語彙を 半分に 減らして よいです。漢字と 文型は 減らさないでください。')}${ID('Boleh mengurangi kosakata sampai separuh, tetapi kanji dan pola kalimat jangan dikurangi.')}</td></tr>
<tr><td>${R('一週 まるごと できなかった')}</td>
<td>${R('追いかけません。今週の 分から 始めます。抜けた分は 要復習で 戻ってきます。')}${ID('Jangan mengejar. Mulai dari minggu ini. Yang terlewat akan kembali lewat "perlu diulang".')}</td></tr>
<tr><td>${R('読解の 時間が 足りない')}</td>
<td>${R('短文3分・中文5分を 目安に、<b>時間を 計って</b> 練習します。')}${ID('Latih dengan stopwatch: teks pendek 3 menit, teks sedang 5 menit.')}</td></tr>
<tr><td>${R('聴解が 聞き取れない')}</td>
<td>${R('一度 答えてから、スクリプトを 見ます。見ながら もう一度 聞くと 伸びます。')}${ID('Jawab dulu, lalu lihat skripnya. Dengarkan sekali lagi sambil membaca skrip.')}</td></tr>
<tr><td>${R('7月の N3を 受ける人')}</td>
<td>${R('第44週（2027年7月）が その週です。模試③の かわりに 本番を 受けて かまいません。')}</td></tr>
<tr><td>${R('紙で 全部 見たい')}</td>
<td>${R('「N2 週ごとの学習範囲表」に 66週分 すべて 入っています。職員に 言ってください。')}${ID('Semua 66 minggu ada di lembar cetak. Silakan minta kepada staf.')}</td></tr>
</table>

<div class="box">
<p class="big">${R('N2で いちばん 大事な こと')}</p>
<p>${R('N3は「覚える」試験でした。N2は <b>「速く 正しく 読む・聞く」</b>試験です。')}<br>
${R('だから、覚えたあとの <b>第2期からが 本当の 勝負</b>です。')}<br>
${R('毎週の 読解1本と 聴解6問を、<b>時間を 計って</b> 続けてください。')}</p>
${ID('N3 adalah ujian menghafal. N2 adalah ujian membaca dan menyimak dengan cepat dan tepat. Karena itu, yang menentukan adalah tahap 2 dan seterusnya — teruslah berlatih dengan mengukur waktu.')}
</div>

<p class="foot">${R('N2コースの 使い方 ／ Cara memakai Kursus N2　　合言葉 owltiger2026　　本番 2027年12月5日（日）')}</p>
</div>`);

const html = `<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<title>N2コースの使い方</title><style>${css}</style></head><body>${P.join('\n')}</body></html>`;
fs.writeFileSync(process.env.OUT || '/tmp/howto/n2.html', html);
console.log('HTML 出力　ページ', P.length);
