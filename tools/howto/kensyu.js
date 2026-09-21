const fs = require('fs');
const W1 = new Date(2026, 11, 7);
const md = d => (d.getMonth()+1) + '/' + d.getDate();
const mon = w => new Date(W1.getTime() + (w-1)*7*86400000);
const sun = w => new Date(mon(w).getTime() + 6*86400000);

const PHASES = [
  { from:1, to:4, name:'第1期　ならし', min:'1日15分',
    aim:'日本の生活と仕事に慣れる。日本語は「毎日ふれる」ことだけを守る。ここで詰め込むと1月以降が続かない。',
    task:['漢字 N5　平日1日5字（週25字）　※102字を4週で一周',
          '語彙 N5　平日1日10語（週50語）',
          '聴解　週3問（「ゆっくり」）　※答えが合わなくてよい。音に慣れる',
          '仕事で聞こえた言葉を1日1つメモ　※翌日、先輩に読み方を聞く'] },
  { from:5, to:12, name:'第2期　N4を仕上げる', min:'1日30分',
    aim:'N4の漢字・語彙・文型をひととおり「覚えた」にする。ここが土台。',
    task:['文型 N4　平日1日3項目（週15項目）　※121項目を8週で',
          '漢字 N4　平日1日4字（週18字）　※144字を8週で',
          '語彙 N4　平日1日17語（週83語）　※648語を8週で',
          '読解 N4　週2本　※18本を8週で。時間は計らない',
          '聴解　週6問（「すこし速く」）　※48問を8週で一周'] },
  { from:13, to:16, name:'第3期　N3へ切りかえる', min:'1日50分',
    aim:'N3の漢字・語彙・文型を始める。読解はここから時間を計る。',
    task:['漢字 N3　平日1日4字（週21字）　※367字を18週で',
          '語彙 N3　平日1日11語（週56語）　※1,000語を18週で',
          '文型 N3　平日1日2項目（週8項目）　※150項目を18週で',
          '読解 N3　週1本（時間を計る）　※短文3分・中文4分30秒が目安',
          '聴解　週6問（「ふつう」）　※2周目。1回だけ聞いて答える'] },
  { from:17, to:30, name:'第4期　100日コース', min:'1日60分',
    aim:'月〜日の日課をそのまま進める。土曜は必ず時間を計る。新しい教材は増やさない。',
    task:['100日コース　月〜日を順番に（1週88問）',
          '漢字 N3　平日1日4字（週21字）　※続ける',
          '語彙 N3　平日1日11語（週56語）　※続ける',
          '文型 N3　平日1日2項目（週8項目）　※続ける',
          '土曜の通しテストは50分で解ききる　※本番と同じ時間'] }
];
const STAFF = {
  1:'<b>N4到達度判定テスト（60分・66問）</b>。入職時点のN4を判定し、部ごとの正答率から12月からの量を決める',
  2:'診断テスト 第1回（筆記50分＋聴解15分＋口頭5分）。書く・話すを含めて様子を見る。入職から2週間を過ぎないうちに',
  4:'月末面談30分：12月をふりかえる。生活の困りごとも聞く',
  8:'月末面談30分：N4の進みを確認。おくれていれば量を減らす',
  12:'月末面談30分：N4が仕上がったか確認。第1週の判定テストと見くらべる',
  16:'診断テスト 第2回（第1回と同じ形）。伸びを第1回と並べて見る',
  20:'月末面談30分：100日コースの土曜テストの点を並べる',
  24:'模試①：土曜の通しテストを本番と同じ時間・同じ席で。50分',
  28:'模試②：読解＋聴解を続けて。本番の順で',
  30:'直前確認：持ち物・会場・時間。前日は勉強させない'
};
const phaseOf = w => PHASES.find(p => w >= p.from && w <= p.to);

let rows = '';
for (let w = 1; w <= 30; w++) {
  const p = phaseOf(w);
  const first = w === p.from;
  const n100 = p.from === 17 ? '第' + (w - 16) + '週' : '';
  rows += `<tr${STAFF[w] ? ' class="hi"' : ''}>` +
    `<td class="c">${w}</td><td class="c">${md(mon(w))}〜${md(sun(w))}</td>` +
    `<td>${first ? '<b>' + p.name + '</b><br><span class="s">' + p.min + '</span>' : (n100 ? '100日コース ' + n100 : '')}</td>` +
    `<td>${STAFF[w] || '<span class="s">' + '金曜10分：学習状況を見る' + '</span>'}</td></tr>`;
}

const css = `
body{margin:0;font-family:"IPAPGothic","IPAGothic","WenQuanYi Zen Hei",sans-serif;
  color:#1b2733;font-size:10pt;line-height:1.65}
.pg{page-break-before:always}.pg:first-child{page-break-before:auto}
h1{font-size:18pt;color:#9a3412;border-bottom:3px solid #9a3412;padding-bottom:5px;margin:0 0 4mm}
h2{font-size:13pt;color:#9a3412;margin:6mm 0 3mm;padding:2mm 0 2mm 3mm;border-left:5px solid #c2410c;background:#fff7ed;
  page-break-after:avoid}
h3{font-size:11pt;color:#0e7a52;margin:4mm 0 2mm;page-break-after:avoid}
p{margin:2mm 0}
.lead{font-size:9.5pt;color:#55606c}
table{border-collapse:collapse;width:100%;margin:2mm 0 4mm;font-size:9pt}
th,td{border:1px solid #d8c3b4;padding:1.4mm 2mm;text-align:left;vertical-align:top}
th{background:#fdf0e6}
td.c{text-align:center;white-space:nowrap}
.s{font-size:8.5pt;color:#6b7784}
tr.hi td{background:#fffaf3}
ul{margin:1mm 0 3mm 1.2em;padding:0}li{margin:.8mm 0}
.box{border:2px solid #c2410c;background:#fff7ed;border-radius:5px;padding:3mm 4mm;margin:3mm 0}
.box b{color:#9a3412}
.tip{border-left:4px solid #0e7a52;background:#f2fbf7;padding:2.5mm 4mm;margin:3mm 0;font-size:9.5pt}
.sheet td{height:9mm}
tr{page-break-inside:avoid}
`;

const phaseCards = PHASES.map(p => `
<h3>${p.name}（第${p.from}〜${p.to}週　${md(mon(p.from))}〜${md(sun(p.to))}）　${p.min}</h3>
<p class="lead">${p.aim}</p>
<ul>${p.task.map(t => '<li>' + t + '</li>').join('')}</ul>`).join('');

const html = `<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>新人研修プログラム</title><style>${css}</style></head><body>

<div class="pg">
<h1>新人職員 日本語研修プログラム</h1>
<p class="lead">対象：2026年12月入職（N4取得）の職員2名　／　目標：2027年7月4日 JLPT N3 合格<br>
期間：2026年12月7日（第1週）〜 2027年7月4日（第30週）　全30週</p>

<div class="box"><b>この計画の考え方</b><br>
① <b>12月は詰め込まない。</b>来日直後は生活の立ち上げで消耗している。ここで無理をさせると1月以降が続かない。<br>
② <b>週ごとの数は、手もとの教材数を週で割って出している。</b>「N4漢字144字 ÷ 8週 = 週18字」のように、
　終わりから逆算した数なので、この量を守れば量的には必ず間に合う。<br>
③ <b>おくれたら、量を減らして続ける。</b>取り返そうとして増やすと、たいてい止まる。
　面談で減らす判断をするのは職員の仕事。</div>

<h2>1　全体の流れ</h2>
${phaseCards}

<h2>2　1日の使い方（目安）</h2>
<div class="box"><b>学習の中心は、職場で行う勉強会です。</b><br>
仕事の日の学習は、本人まかせにしない。勤務シフトに合わせて、次の時間に職員が付いて行う。<br>
・<b>日勤の日 … 8：45〜9：25（40分）</b>　出勤前。9：30の始業までに終える。<br>
・<b>早出の日 … 16：45〜17：30（45分）</b>　16：30の退勤のあと。早出は3月から。<br>
夜勤はない。仕事の日に家で長くやらせる設計にはしていない。</div>
<p>1日の量は下のとおり。<b>仕事の日は、その量を勉強会の中で終わらせる。</b>入りきらない分だけを家に回す。</p>
<table><thead><tr><th>期</th><th>1日の量</th><th>勉強会で</th><th>家で（仕事の日）</th><th>中身</th></tr></thead><tbody>
<tr><td>第1期</td><td>15分</td><td>15分</td><td>0分</td><td>漢字5字＋語彙10語。聴解は週3回だけ。残りの時間は質問と発音に使う</td></tr>
<tr><td>第2期</td><td>30分</td><td>30分</td><td>0分</td><td>文型3項目＋漢字4字＋語彙17語。読解と聴解は休みの日</td></tr>
<tr><td>第3期</td><td>50分</td><td>40分</td><td>10分（寝る前）</td><td>勉強会＝文型2項目＋語彙11語＋漢字4字／家＝語彙の見直し。読解1本は週1で勉強会に入れる</td></tr>
<tr><td>第4期</td><td>60分</td><td>40分</td><td>20分（寝る前）</td><td>勉強会＝100日コースの日課／家＝漢字4字＋語彙11語。土曜だけ50分続けて取る</td></tr>
<tr><td>全期</td><td>90分</td><td colspan="2">休みの日は勉強会なし</td><td>読解45分＋文型・語彙30分＋聴解15分。本人ひとりで行う。マスを押させる</td></tr>
</tbody></table>
<div class="tip"><b>早出の日は、朝に勉強させないこと。</b>7：30出勤は早い。勉強会を16：45に置いてあるのはそのため。
早出の日の「家で」は任意にしてよい（眠ければ0でよい）。
<b>おくれても、量を減らして続ける。0にしないこと</b>が大事です。</div>

<h2>3　職員がすること</h2>
<table><thead><tr><th>いつ</th><th>何を</th><th>時間</th></tr></thead><tbody>
<tr><td>仕事の日 毎日</td><td><b>勉強会</b>。日勤は8：45〜9：25、早出は16：45〜17：30。画面の「今週使うもの」を開かせ、出た分だけやらせる。その場で質問を受ける</td><td>40〜45分</td></tr>
<tr><td>毎週 金曜</td><td>学習状況タブを見て、先週の記録を確認する。声はかけるが、しかることはしない</td><td>10分</td></tr>
<tr><td>毎月 末</td><td>面談。できたこと→つまずき→来月の量、の順で聞く</td><td>30分</td></tr>
<tr><td>第1週</td><td><b>N4到達度判定テスト</b>。入職時点でN4がどれだけあるかを、線を引いて判定する。結果で12月からの量を決める</td><td>60分</td></tr>
<tr><td>第2週</td><td>診断テスト 第1回。<b>書く・話す</b>を含めて様子を見る。判定テストとは見るところが違うので、両方行う。<b>入職から2週間を過ぎないうちに</b></td><td>70分</td></tr>
<tr><td>第16週</td><td>診断テスト 第2回（第1回と同じ形）。第1回と並べて伸びを見る</td><td>70分</td></tr>
<tr><td>第24週・第28週</td><td>模試（本番と同じ時間・同じ席で）</td><td>60分</td></tr>
<tr><td>第30週</td><td>直前確認（持ち物・会場・時間）</td><td>15分</td></tr>
</tbody></table>
</div>

<div class="pg">
<h2>4　週ごとの予定表</h2>
<p class="lead">色のついた行が、職員が動く週です。</p>
<table><thead><tr><th style="width:8%">週</th><th style="width:17%">日にち</th><th style="width:33%">学習</th><th>職員がすること</th></tr></thead>
<tbody>${rows}</tbody></table>
</div>

<div class="pg">
<h2>5　面談シート（コピーして使ってください）</h2>
<p class="lead">氏名　　　　　　　　　　　　　　　　　　　実施日　　　　年　　月　　日　　　第　　週</p>
<table class="sheet"><tbody>
<tr><th style="width:26%">今月できたこと</th><td></td></tr>
<tr><th>つまずいたところ</th><td></td></tr>
<tr><th>生活で困っていること</th><td></td></tr>
<tr><th>学習時間（1日平均）</th><td>　　　分　／　目安　　　　分　　　→　□ ちょうどよい　□ 多い　□ 少ない</td></tr>
<tr><th>来月の量</th><td>□ このまま　□ 減らす（　　　　　　）　□ 増やす（　　　　　　）</td></tr>
<tr><th>職員のメモ</th><td></td></tr>
</tbody></table>

<div class="tip"><b>面談の順番を変えないでください。</b>
「できたこと」から始めます。つまずきから入ると、次から本当のことを言わなくなります。
量が多すぎるときは<b>職員から減らす</b>と言ってください。本人からは言い出せません。</div>

<h2>6　記録表（週ごと・2名分）</h2>
<p class="lead">毎週金曜に、学習状況タブを見て記入します。◯＝できた　△＝半分　×＝できなかった</p>
<table class="sheet"><thead><tr><th style="width:10%">週</th><th style="width:20%">日にち</th>
<th style="width:35%">Aさん</th><th>Bさん</th></tr></thead><tbody>
${Array.from({length:15},(_,i)=>{const w=i+1;return `<tr><td class="c">${w}</td><td class="c">${md(mon(w))}〜</td><td></td><td></td></tr>`;}).join('')}
</tbody></table>
</div>

<div class="pg">
<h2>6　記録表（つづき）</h2>
<table class="sheet"><thead><tr><th style="width:10%">週</th><th style="width:20%">日にち</th>
<th style="width:35%">Aさん</th><th>Bさん</th></tr></thead><tbody>
${Array.from({length:15},(_,i)=>{const w=i+16;return `<tr><td class="c">${w}</td><td class="c">${md(mon(w))}〜</td><td></td><td></td></tr>`;}).join('')}
</tbody></table>

<h2>7　うまくいかないときの手当て</h2>
<table><thead><tr><th style="width:30%">こうなったら</th><th>こうする</th></tr></thead><tbody>
<tr><td>2週続けて手が止まった</td><td>量を半分にする。やめさせない。「毎日ふれる」だけ残す</td></tr>
<tr><td>聴解だけ伸びない</td><td>速さを「ゆっくり」に戻す。スクリプトを見ながら聞く回を作る</td></tr>
<tr><td>読解が時間内に終わらない</td><td>解けた数より<b>どこで止まったか</b>を見る。語彙不足か、戻り読みか</td></tr>
<tr><td>漢字が書けない</td><td>手書きシステムで1日3字。読めれば試験は通るので、優先度は下げてよい</td></tr>
<tr><td>早出で朝の時間が取れない</td><td>その日は帰ってから。土日でまとめない（かえって続かない）</td></tr>
<tr><td>第16週の診断で伸びていない</td><td>100日コースに入る前に、第2期をもう4週やり直す。7月をあきらめて12月に切りかえる判断も、この時点でする</td></tr>
</tbody></table>

<div class="box"><b>いちばん大事なこと</b><br>
30週のうち、<b>何週かは必ず止まります。</b>止まったときに責めないでください。
量を減らして続けたほうが、結果として遠くまで行きます。
この計画は、<b>週に2〜3日できなくても間に合う</b>ように余裕をとってあります。</div>
</div>

</body></html>`;
fs.writeFileSync('/tmp/kensyu/kensyu.html', html);
console.log('HTML 出力');
