/* 新人コースの使い方（実習生向け）。N4を超える漢字にはふりがな。 */
const fs = require('fs');
const { withRuby } = require(__dirname + '/ruby.js');
const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const R = s => withRuby(esc(s));
const ID = s => `<span class="id">${esc(s)}</span>`;

const css = `
body{margin:0;font-family:"IPAPGothic","IPAGothic","WenQuanYi Zen Hei",sans-serif;color:#1b2733;font-size:10.5pt;line-height:1.95}
.pg{page-break-before:always}.pg:first-child{page-break-before:auto}
h1{font-size:19pt;color:#0e7a52;border-bottom:3px solid #0e7a52;padding-bottom:5px;margin:0 0 3mm}
h1 small{display:block;font-size:9.5pt;font-weight:400;color:#55606c;margin-top:1.5mm}
h2{font-size:13pt;color:#fff;background:#0e7a52;margin:6mm 0 3mm;padding:1.8mm 3mm;border-radius:3px}
h3{font-size:11.5pt;color:#0e7a52;margin:4.5mm 0 1.5mm;border-left:4px solid #0e7a52;padding-left:2.5mm}
p{margin:2mm 0}
.id{display:block;font-size:9pt;color:#6b7784;margin-top:.6mm}
.lead{font-size:10pt;color:#55606c}
table{border-collapse:collapse;width:100%;margin:2.5mm 0;font-size:10pt}
th,td{border:1px solid #bfe0d2;padding:1.8mm 2.4mm;text-align:left;vertical-align:top}
th{background:#eafaf2;color:#0e7a52}
tr{page-break-inside:avoid}
.box{border:2px solid #0e7a52;background:#eafaf2;border-radius:5px;padding:3mm 4mm;margin:3mm 0}
.tip{border-left:4px solid #4338ca;background:#eef2ff;padding:2.5mm 4mm;margin:3mm 0}
.warn{border-left:4px solid #c2410c;background:#fff7ed;padding:2.5mm 4mm;margin:3mm 0}
ul{margin:1.5mm 0 1.5mm 5.5mm;padding:0}
li{margin:1.2mm 0}
.num{display:flex;gap:3mm;margin:3mm 0;break-inside:avoid}
.num .n{flex:none;width:8.5mm;height:8.5mm;border-radius:50%;background:#0e7a52;color:#fff;
  font-weight:bold;text-align:center;line-height:8.5mm;font-size:10.5pt}
.num .t{flex:1}
.scr{background:#f6f8fb;border:1px solid #bfe0d2;border-radius:5px;padding:3mm 4mm;margin:2.5mm 0;font-size:10pt}
.scr b{color:#0e7a52}
.big{font-size:13pt;font-weight:bold;color:#0e7a52}
ruby{ruby-align:center}rt{font-size:6pt;color:#0e7a52;font-weight:400}
h1 rt,h2 rt{font-size:6.8pt;color:inherit;opacity:.85}
h3 rt{font-size:6.2pt}th rt{font-size:5.8pt}
.foot{font-size:9pt;color:#6b7784;border-top:1px solid #bfe0d2;margin-top:5mm;padding-top:2mm}
`;

const P = [];

/* ============ 1ページ目 ============ */
P.push(`<div class="pg">
<h1>${R('新人コースの 使い方')}<small>Cara memakai Kursus Staf Baru ／ ${R('12月に入って、7月のN3に合格するまで')}</small></h1>

<p class="lead">${R('この紙は、あなたが 毎日 何を すればよいかを 書いたものです。')}
${ID('Kertas ini menjelaskan apa yang perlu Anda lakukan setiap hari.')}</p>

<div class="box">
<p class="big">${R('覚えることは 一つだけ。')}</p>
<p>${R('毎日、画面を ひらいて、出てきたものを やる。それだけです。')}<br>
${R('何を どれだけ やるかは、はじめから 決めてあります。自分で 決めなくて いいです。')}</p>
${ID('Yang perlu diingat cuma satu: buka layar setiap hari, lalu kerjakan yang muncul. Isinya sudah ditentukan — Anda tidak perlu memilih sendiri.')}
</div>

<h2>${R('① まず ひらく')}</h2>
<div class="num"><div class="n">1</div><div class="t">
${R('スマホで ブラウザ（Chrome か Safari）を ひらきます。')}
${ID('Buka browser (Chrome atau Safari) di HP Anda.')}</div></div>
<div class="num"><div class="n">2</div><div class="t">
${R('下の 住所を 入れます。')}<br>
<span class="scr" style="display:inline-block;margin:1.5mm 0">https://owlwindkaze-ux.github.io/owltiger1021/</span>
${ID('Masukkan alamat di atas.')}</div></div>
<div class="num"><div class="n">3</div><div class="t">
${R('合言葉 <b>owltiger2026</b> を 入れて「入る」を おします。')}<br>
${R('二回目からは 入れなくて よいです。')}
${ID('Masukkan kata sandi owltiger2026, lalu tekan "Masuk". Setelah itu tidak perlu lagi.')}</div></div>
<div class="num"><div class="n">4</div><div class="t">
${R('メニューの 中の「新人コース」を おします。')}
${ID('Tekan "Kursus Staf Baru" pada menu.')}</div></div>

<div class="tip">
<b>${R('ホーム画面に 入れると、もっと 早く ひらけます。')}</b>${ID('Tambahkan ke layar utama agar lebih cepat dibuka.')}
<ul>
<li>${R('iPhone … 下の 共有ボタン（□に↑）→「ホーム画面に追加」')}</li>
<li>${R('Android … 右上の「⋮」→「ホーム画面に追加」')}</li>
</ul>
</div>

<h2>${R('② 画面に 出るもの')}</h2>
<table>
<tr><th style="width:32%">${R('出るもの')}</th><th>${R('意味')}</th></tr>
<tr><td>${R('試験日まで ◯日')}</td><td>${R('7月のN3の 試験まで、あと 何日か。')}${ID('Sisa hari sampai ujian N3 bulan Juli.')}</td></tr>
<tr><td>${R('今月の ねらい')}</td><td>${R('その月に いちばん 大事なこと。1行だけ 読めば よいです。')}${ID('Hal terpenting bulan ini.')}</td></tr>
<tr><td>${R('今月 やること')}</td><td>${R('3つだけ 出ます。多くしません。')}${ID('Hanya tiga hal. Tidak lebih.')}</td></tr>
<tr><td>${R('月〜日の マス')}</td><td>${R('できた日に おします。緑に なります。')}${ID('Tekan kotak hari yang sudah selesai. Akan berubah hijau.')}</td></tr>
<tr><td>${R('今月 使うもの')}</td><td>${R('その月に ひらく 画面だけが ならびます。')}${ID('Hanya alat yang dipakai bulan ini yang ditampilkan.')}</td></tr>
</table>

<h2>${R('③ 毎日の 進め方')}</h2>
<div class="scr">
<b>${R('平日（仕事の日）')}</b> … ${R('出勤の 前に <b>30分</b>。むずかしければ 帰ってから 15分でも よいです。')}<br>
<b>${R('休みの日')}</b> … ${R('<b>90分</b>。読解45分 ＋ 文型・語彙30分 ＋ 聴解15分。')}<br>
<b>${R('夜勤の日')}</b> … ${R('昼の あいだに 60分。<b>夜勤明けは 休んで ください。</b>')}
</div>
<div class="warn">
<b>${R('できない日が あっても だいじょうぶです。')}</b>
${R('前の日の マスを 無理に うめなくて よいです。<b>今日の 分だけ</b> やってください。')}
${ID('Tidak apa-apa kalau ada hari yang terlewat. Jangan memaksa mengejar hari kemarin — kerjakan bagian hari ini saja.')}
</div>
</div>`);

/* ============ 2ページ目 ============ */
P.push(`<div class="pg">
<h2>${R('④ 「今月 使うもの」の ひらき方')}</h2>
<p>${R('ボタンを おすと、<b>その月に やる ところだけ</b> が ひらきます。レベルを 自分で えらぶ 必要は ありません。')}
${ID('Saat tombol ditekan, yang terbuka hanya bagian bulan itu. Anda tidak perlu memilih level sendiri.')}</p>

<table>
<tr><th style="width:26%">${R('ボタン')}</th><th>${R('おすと どうなるか')}</th></tr>
<tr><td>📚 ${R('漢字・語彙')}</td>
<td>${R('その週の 漢字と 語彙<b>だけ</b>が 出ます。')}<br>
${R('漢字は 書き順を 見て、読みを 声に 出す。語彙は「覚えた」か「要復習」を 必ず おす。')}
${ID('Hanya kanji dan kosakata minggu ini. Tekan "sudah hafal" atau "perlu diulang" setiap kali.')}</td></tr>
<tr><td>📐 ${R('文型・文法')}</td>
<td>${R('その週の 文型<b>だけ</b>が 出ます。例文を 3つ 声に 出して 読んでください。')}
${ID('Hanya pola kalimat minggu ini. Bacalah tiga contoh kalimat dengan suara.')}</td></tr>
<tr><td>📖 ${R('読解')}</td>
<td>${R('文章を 読んで、問いに 答えます。<b>時間を 計って</b> ください。')}
${ID('Baca teks lalu jawab pertanyaannya. Ukur waktunya.')}</td></tr>
<tr><td>🎧 ${R('聴解')}</td>
<td>${R('音を 聞いて 答えます。はじめは「ゆっくり」で よいです。')}
${ID('Dengarkan lalu jawab. Awalnya boleh memakai kecepatan "pelan".')}</td></tr>
<tr><td>📅 ${R('100日コース')}</td>
<td>${R('3月の 終わりから 使います。それまでは 出てきません。')}
${ID('Dipakai mulai akhir Maret. Sebelum itu tidak muncul.')}</td></tr>
<tr><td>✍️ ${R('手書き')}</td>
<td>${R('読めない 漢字を 指で 書いて 調べられます。')}
${ID('Tulis kanji yang tidak terbaca dengan jari untuk mencarinya.')}</td></tr>
</table>

<h2>${R('⑤ 7か月の 流れ')}</h2>
<table>
<tr><th style="width:16%">${R('いつ')}</th><th style="width:34%">${R('すること')}</th><th>${R('その月の おわりに')}</th></tr>
<tr><td>12月</td><td>${R('日本の 生活と 仕事に 慣れる。日本語は 1日15分だけ。')}</td><td>${R('診断テスト（第1回）')}</td></tr>
<tr><td>1月</td><td>${R('N4の 弱いところを うめる。')}</td><td>${R('N4の 語彙648語・文型121項目')}</td></tr>
<tr><td>2月</td><td>${R('N4を 仕上げる。ここまでで 土台が できます。')}</td><td>${R('N4を すべて「覚えた」に')}</td></tr>
<tr><td>3月</td><td>${R('力を 測り直して、N3に 切りかえる。折り返しです。')}</td><td>${R('診断テスト（第2回）')}</td></tr>
<tr><td>${R('3月末〜')}</td><td>${R('100日コースを 始める。ここから 毎日 やることが 決まります。')}</td><td>${R('100日コース 第1〜4週')}</td></tr>
<tr><td>5月</td><td>${R('読解の 速さを 上げる。落ちる人の ほとんどが 読解です。')}</td><td>${R('100日コース 第5〜9週')}</td></tr>
<tr><td>6月</td><td>${R('本番の 形に 体を 慣らす。新しい 教材は もう 増やしません。')}</td><td>${R('100日コース 第10〜13週')}</td></tr>
<tr><td>7月</td><td>${R('直前。増やさず、取り出しやすく する。')}</td><td>${R('100日コース 第14週 → 受験')}</td></tr>
</table>

<h2>${R('⑥ 困ったときは')}</h2>
<table>
<tr><th style="width:38%">${R('こんなとき')}</th><th>${R('こうしてください')}</th></tr>
<tr><td>${R('むずかしくて 進まない')}</td><td>${R('量を 減らして よいです。<b>0にしない</b>ことだけ 守ってください。')}${ID('Boleh dikurangi. Yang penting jangan sampai nol.')}</td></tr>
<tr><td>${R('何日か できなかった')}</td><td>${R('前の分は 追いかけません。今日の 分から 始めます。')}${ID('Jangan mengejar yang lalu. Mulai dari bagian hari ini.')}</td></tr>
<tr><td>${R('画面が 新しく ならない')}</td><td>${R('入口の いちばん下の「🔄 最新にする」を おします。')}${ID('Tekan "🔄 Perbarui" di bagian bawah halaman depan.')}</td></tr>
<tr><td>${R('記録が 消えないか 心配')}</td><td>${R('記録は その端末に 残ります。同じ スマホで ひらいてください。')}${ID('Catatan tersimpan di HP itu sendiri. Bukalah dengan HP yang sama.')}</td></tr>
<tr><td>${R('意味が 分からない')}</td><td>${R('画面の 意味は インドネシア語でも 出ます。分からない 漢字は「手書き」で 調べられます。')}</td></tr>
</table>

<div class="box">
<p class="big">${R('いちばん 大事なこと')}</p>
<p>${R('毎日 少しずつ 続けた人が 合格しています。')}<br>
${R('一日に たくさん やる人より、<b>毎日 やめない人</b>の ほうが 強いです。')}</p>
${ID('Yang lulus adalah orang yang melanjutkan sedikit demi sedikit setiap hari. Bukan yang mengerjakan banyak dalam satu hari, melainkan yang tidak pernah berhenti.')}
</div>

<p class="foot">${R('新人コースの 使い方 ／ Cara memakai Kursus Staf Baru　　合言葉 owltiger2026')}</p>
</div>`);

const html = `<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<title>新人コースの使い方</title><style>${css}</style></head><body>${P.join('\n')}</body></html>`;
fs.writeFileSync(process.env.OUT || '/tmp/howto/shinjin.html', html);
console.log('HTML 出力　ページ', P.length);
