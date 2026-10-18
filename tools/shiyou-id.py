#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**実習生が読む使用説明書**を作る（日本語ふりがなつき＋インドネシア語）。

持ち主から「**新人のインドネシアの技能実習生が、読んでわかる使用説明書。
日本語はふり仮名付き、インドネシア語での対訳**」。

`tsukaikata.py`（職員が読む日本語だけのもの）とは**別のもの**。
こちらは**来たばかりの実習生が自分で読む**ためのもの。

**ふりがなの付け方 ── データから推測させない**

`vocab-data.json` の読みを当てる方法も考えたが、やめた。
「行く／行う」「生きる／生まれる」のように、**同じ字で読みが変わる**。
読みを間違えた説明書は、実習生には直せない。**無いより悪い。**

だから**本文に直接 `漢字《かんじ》` と書く**。そして
**書き忘れた漢字が1字でもあれば、この道具は止まる。**
（読解のデータと同じ書き方。`dokkai/` で使っている記法。）

**メニューは画面から読む。**日本語とインドネシア語の両方が
`index.html` に入っているので、**画面と説明書で言葉がずれない**。
説明の無いまとまりがあると止まる。

    python3 tools/shiyou-id.py --html FILE
    （そのあと tools/pdf/mkpdf.mjs で PDF に）
"""
import collections
import io
import os
import re
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# ── まとまりごとの説明。見出し（日本語）で引く ───────────────────
# ja … やさしい日本語（漢字には 《》 で読みを付ける）
# id … インドネシア語
GROUP = collections.OrderedDict([
 ('まちがえたところ', {
   'ja': 'まちがえた 問題《もんだい》だけが ここに あつまります。'
         '<b>毎日《まいにち》 ここから はじめて ください。</b>'
         '新《あたら》しい ものを ふやすより、'
         'まちがえた ところを もう一度《いちど》やる ほうが 点《てん》が 上《あ》がります。',
   'id': 'Semua soal yang pernah Anda salah dikumpulkan di sini. '
         '<b>Mulailah dari sini setiap hari.</b> '
         'Mengulang yang salah lebih menaikkan nilai daripada menambah materi baru.'}),
 ('漢字・言葉（語彙）', {
   'ja': 'この システムの <b>中心《ちゅうしん》</b>です。毎日《まいにち》 つかいます。'
         'はじめての 人《ひと》は <b>「フラッシュカード」</b>から。'
         'めくって「おぼえた」「もう一度《いちど》」を おすだけです。',
   'id': '<b>Bagian inti</b> dari sistem ini. Dipakai setiap hari. '
         'Kalau baru pertama kali, mulailah dari <b>"Kartu"</b>. '
         'Cukup balik kartunya lalu tekan "sudah hafal" atau "perlu diulang".'}),
 ('文型（文法）', {
   'ja': '「〜ても いいです」のような <b>文《ぶん》の 形《かたち》</b>を おぼえます。'
         '1つに つき 介護《かいご》の 例文《れいぶん》が 3つ あります。'
         '<b>声《こえ》に 出《だ》して 読《よ》む</b>のが いちばん 早《はや》いです。',
   'id': 'Mempelajari <b>pola kalimat</b> seperti 「〜てもいいです」. '
         'Setiap pola punya 3 contoh kalimat dari tempat kerja kaigo. '
         '<b>Membacanya dengan suara keras</b> adalah cara tercepat.'}),
 ('読解（文章を読む）', {
   'ja': 'お知《し》らせ・シフト表《ひょう》・申《もう》し送《おく》りなどを 読《よ》んで、'
         '4つから 答《こた》えを えらびます。'
         'はじめは <b>時間《じかん》を はかりません。</b>'
         'ゆっくり 読《よ》んで ください。',
   'id': 'Membaca pengumuman, jadwal sif, laporan serah terima, '
         'lalu memilih jawaban dari 4 pilihan. '
         '<b>Awalnya jangan diukur waktunya.</b> Bacalah pelan-pelan.'}),
 ('聴解（聞いて答える）', {
   'ja': '聞《き》いて 答《こた》えます。音《おと》は スマホが 読《よ》みます。'
         'はじめは <b>答《こた》えが 合《あ》わなくて いいです。</b>'
         '音《おと》に なれるのが 先《さき》です。速《はや》さは かえられます。',
   'id': 'Mendengar lalu menjawab. Suaranya dibacakan oleh HP Anda. '
         '<b>Awalnya tidak apa-apa kalau jawabannya salah.</b> '
         'Yang penting terbiasa dengan suaranya dulu. Kecepatan bisa diubah.'}),
 ('N3合格 100日コース', {
   'ja': '試験《しけん》の 100日前《にちまえ》から つかいます。'
         '月《げつ》〜日《にち》の 毎日《まいにち》に 問題《もんだい》が 分《わ》けて あります。'
         '<b>今日《きょう》の 分《ぶん》だけ</b>を やって ください。',
   'id': 'Dipakai mulai 100 hari sebelum ujian. '
         'Soal sudah dibagi untuk setiap hari, Senin sampai Minggu. '
         '<b>Kerjakan bagian hari ini saja.</b>'}),
 ('新人コース（N4 → 7月のN3）', {
   'ja': '<b>あなたが 毎朝《まいあさ》 ひらく ところです。</b>'
         'その 週《しゅう》に やる ことが ぜんぶ 書《か》いて あります。'
         '「今週《こんしゅう》ひらくもの」を おすと、'
         '<b>その 週《しゅう》の 分《ぶん》だけ</b>が 出《で》ます。'
         '何《なに》を やるか 考《かんが》えなくて いいです。',
   'id': '<b>Inilah yang Anda buka setiap pagi.</b> '
         'Semua yang harus dikerjakan minggu itu sudah tertulis. '
         'Kalau menekan "Dipakai minggu ini", '
         '<b>hanya bagian minggu itu</b> yang muncul. '
         'Anda tidak perlu memikirkan harus mengerjakan apa.'}),
 ('参考資料（外部サイト）', {
   'ja': '<b>ほかの サイト</b>です。この システムの 合言葉《あいことば》では 入《はい》れません。'
         '自分《じぶん》で 登録《とうろく》が いります。音声《おんせい》つきの 教材《きょうざい》が あります。',
   'id': '<b>Situs lain</b>, bukan sistem ini. Kata sandi sistem ini tidak berlaku. '
         'Anda perlu mendaftar sendiri. Di sana ada materi yang disertai suara.'}),
 ('N2コース（N3合格者の次のステップ）', {
   'ja': '<b>N3に 合格《ごうかく》してから</b>です。'
         'それまでは <b>ひらかなくて いいです。</b>',
   'id': '<b>Setelah Anda lulus N3.</b> '
         'Sebelum itu, <b>tidak perlu dibuka.</b>'}),
 ('手書きで漢字をさがす', {
   'ja': '<b>仕事中《しごとちゅう》に いちばん つかう 画面《がめん》です。</b>'
         '読《よ》めない 漢字《かんじ》を 指《ゆび》で 書《か》くと、'
         '読《よ》み・意味《いみ》・画数《かくすう》が 分《わ》かります。'
         '記録《きろく》で 読《よ》めない 字《じ》が あったら、ここで しらべて ください。',
   'id': '<b>Layar yang paling sering dipakai saat bekerja.</b> '
         'Tulis kanji yang tidak bisa Anda baca dengan jari, '
         'lalu cara baca, arti, dan jumlah coretannya akan muncul. '
         'Kalau menemukan kanji yang tidak terbaca di catatan, carilah di sini.'}),
])

# はじめての人が おす順番（見出しで指す）
FIRST = ['新人コース（N4 → 7月のN3）', '漢字・言葉（語彙）', 'まちがえたところ']


# 「覚えた」「要復習」の読み。画面の言葉なので ここで ふりがなを 付ける。
BTN_RUBY = {'覚えた': '覚《おぼ》えた', '要復習': '要復習《ようふくしゅう》'}


def marks():
    """**画面に出ている とおりの ボタン名**を kanji.html から読む。

    最初は「✓ おぼえた」「△ もう一度」と 手で書いていた。
    実物は「✓ 覚えた」「↻ 要復習」で、**存在しないボタンを押させる説明書**に
    なっていた（2026-10-17）。説明書と画面がずれる いちばん多い形なので、
    **画面から読む**ことにした。読めなければ止まる。
    """
    t = io.open(R + 'kanji.html', encoding='utf-8').read()
    m = re.search(r"STATE_TXT = \{ known: '(.*?)', review: '(.*?)'", t)
    if not m:
        raise SystemExit('× kanji.html から「覚えた／要復習」のボタン名が読めません。'
                         '作りが変わった可能性があります。')
    out = []
    for raw in m.groups():
        # 画面は 「✓ Sudah hafal ／ 覚えた」の形。**印はインドネシア語側に付いている。**
        left, ja = [x.strip() for x in raw.split('／')]
        sym = left[0] if left[0] in '✓↻△' else ''
        idn = left[1:].strip()
        if ja not in BTN_RUBY:
            raise SystemExit('× ボタン「%s」の読みが ありません。'
                             'tools/shiyou-id.py の BTN_RUBY に足してください。' % ja)
        out.append((sym, BTN_RUBY[ja], idn))
    return out


# 公開している住所。QRもこの住所で作ってある。
URL = 'https://owlwindkaze-ux.github.io/owltiger1021/'


def qr():
    """`tools/qr.svg` を そのまま 貼る。

    **QRの中身は目で見て確かめられない。**だから
    「どの住所で作ったか」をSVGに書いておき、ここで突き合わせる。
    ちがっていれば止める。住所を変えたのにQRが前のまま、が いちばん困る。
    """
    f = R + 'tools/qr.svg'
    if not os.path.exists(f):
        raise SystemExit('× tools/qr.svg が ありません。'
                         'python3 tools/qr.py を先に走らせてください。')
    svg = io.open(f, encoding='utf-8').read()
    i = svg.find('<!-- url: ')
    made = svg[i + 10:svg.index(' -->', i)] if i >= 0 else None
    if made != URL:
        raise SystemExit('× QRの住所が ちがいます。\n  QR : %s\n  本文: %s\n'
                         '  python3 tools/qr.py を走らせ直してください。' % (made, URL))
    return svg[svg.index('<svg'):]


def menu():
    """入口メニューから、見出しとボタンを 日本語・インドネシア語の両方で読む。"""
    s = io.open(R + 'index.html', encoding='utf-8').read()
    out = []
    for m in re.finditer(r'<section class="card[^"]*">(.*?)</section>', s, re.S):
        blk = m.group(1)
        t = re.search(r'<div class="ttl">(.*?)<small>(.*?)</small>', blk, re.S)
        if not t:
            continue
        cl = lambda x: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', x)).strip() \
            .replace('&amp;', '&')
        idn, ja = cl(t.group(1)), cl(t.group(2))
        btns = []
        for a in re.finditer(r'<span class="n">(.*?)</span>\s*<span class="r">(.*?)</span>',
                             blk, re.S):
            n, r = cl(a.group(1)), cl(a.group(2))
            btns.append((n, r.split('／')[0].strip()))
        if ja:
            out.append((ja, idn, btns))
    if len(out) < 5:
        raise SystemExit('× メニューが %d個しか読めませんでした。'
                         'index.html の作りが変わった可能性があります。' % len(out))
    missing = [h for h, _, _ in out if h not in GROUP]
    if missing:
        raise SystemExit('× 説明の無いまとまりがあります: ' + '／'.join(missing)
                         + '\n  tools/shiyou-id.py の GROUP に、'
                           '日本語（ふりがなつき）とインドネシア語で足してください。')
    return out


KANJI = re.compile(r'[一-鿿々]')
RUBY = re.compile(r'([一-鿿々]+)《([ぁ-んー]+)》')


# ── メニューの言葉の読み ───────────────────────────────────────
# 画面（index.html）から読んだ言葉には ふりがなが無いので、ここで付ける。
# **ここに無い言葉が画面に出てきたら、この道具は止まる。**
# ボタンを足したのに読みを書き忘れる、が いちばん起きやすいため。
MENU_RUBY = {
 'まちがえたところ': 'まちがえたところ',
 '漢字・言葉（語彙）': '漢字《かんじ》・言葉《ことば》（語彙《ごい》）',
 '文型（文法）': '文型《ぶんけい》（文法《ぶんぽう》）',
 '読解（文章を読む）': '読解《どっかい》（文章《ぶんしょう》を 読《よ》む）',
 '聴解（聞いて答える）': '聴解《ちょうかい》（聞《き》いて 答《こた》える）',
 'N3合格 100日コース': 'N3合格《ごうかく》 100日《にち》コース',
 '新人コース（N4 → 7月のN3）': '新人《しんじん》コース（N4 → 7月《がつ》のN3）',
 '参考資料（外部サイト）': '参考資料《さんこうしりょう》（外部《がいぶ》サイト）',
 'N2コース（N3合格者の次のステップ）':
     'N2コース（N3合格者《ごうかくしゃ》の 次《つぎ》の ステップ）',
 '手書きで漢字をさがす': '手書《てが》きで 漢字《かんじ》を さがす',
 '漢字一覧': '漢字《かんじ》一覧《いちらん》',
 '語彙（ことば）': '語彙《ごい》（ことば）',
 'フラッシュカード': 'フラッシュカード',
 '練習問題': '練習《れんしゅう》問題《もんだい》',
 '書き順': '書《か》き順《じゅん》',
 '学習状況': '学習《がくしゅう》状況《じょうきょう》',
 '文型一覧': '文型《ぶんけい》一覧《いちらん》',
 '文章一覧': '文章《ぶんしょう》一覧《いちらん》',
 '読む・答える': '読《よ》む・答《こた》える',
 '申し送りを聞く': '申《もう》し送《おく》りを 聞《き》く',
 '職員どうしの会話': '職員《しょくいん》どうしの 会話《かいわ》',
 '利用者さんの言葉': '利用者《りようしゃ》さんの 言葉《ことば》',
 'JLPT形式の練習': 'JLPT形式《けいしき》の 練習《れんしゅう》',
 '今週の学習': '今週《こんしゅう》の 学習《がくしゅう》',
 '今月やること': '今月《こんげつ》 やること',
 'にほんごをまなぼう': 'にほんごを まなぼう',
 'ロードマップ': 'ロードマップ',
 '診断テスト': '診断《しんだん》テスト',
 '手書きで調べる': '手書《てが》きで 調《しら》べる',
}


def mr(w):
    """画面の言葉に ふりがなを 付ける。無ければ 止める。"""
    if w in MENU_RUBY:
        return MENU_RUBY[w]
    if KANJI.search(w):
        raise SystemExit('× 画面の言葉「%s」の読みが ありません。\n'
                         '  tools/shiyou-id.py の MENU_RUBY に足してください。' % w)
    return w


def ruby(t):
    """漢字《かんじ》 を <ruby> に変える。"""
    return RUBY.sub(r'<ruby>\1<rt>\2</rt></ruby>', t)


def check_ruby(html, where):
    """**ふりがなの無い漢字が1字でもあれば止める。**

    実習生が読むものなので、読めない字が残っていたら その人には どうにもできない。
    書き忘れは 必ず起きるので、人の目ではなく 機械で止める。
    """
    # ruby の中身（<ruby>漢字<rt>…）は 読みが付いているので 取り除いてから見る
    s = re.sub(r'<ruby>.*?</ruby>', '', html, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    bad = sorted(set(KANJI.findall(s)))
    if bad:
        # どの行かを 分かるようにして返す
        lines = [ln.strip() for ln in re.split(r'[\n。]', re.sub(r'<[^>]+>', '', html))
                 if any(c in ln for c in bad)]
        raise SystemExit(
            '× ふりがなの無い漢字が あります（%s）: %s\n  %s\n'
            '  本文に 漢字《かんじ》 の形で 読みを 書いてください。'
            % (where, '・'.join(bad), '\n  '.join(lines[:6])))


CSS = r'''
@page { size: A4; margin: 15mm 14mm 16mm; }
body{font-family:"IPAPGothic","IPAGothic","Noto Sans CJK JP",sans-serif;
 color:#1b2733;font-size:10.5pt;line-height:2.0;margin:0}
ruby rt{font-size:.5em;font-weight:400;color:#55606c;line-height:1}
/* **見出しを ページの最後に 1行だけ残さない。**
   日本語の見出しとインドネシア語の副題が ページをまたいで割れていた
   （2026-10-18・4か所）。break-* と page-break-* の両方を書く。 */
h1,h2,h3{break-inside:avoid;page-break-inside:avoid;
 break-after:avoid;page-break-after:avoid}
.grp{break-inside:avoid;page-break-inside:avoid}
p{orphans:2;widows:2}
h1{font-size:19pt;color:#9a3412;border-bottom:3px solid #9a3412;
 padding-bottom:5px;margin:0 0 2mm}
h1 .id{display:block;font-size:11pt;color:#9a3412;font-weight:400;margin-top:1mm}
h2{font-size:13pt;color:#9a3412;margin:7mm 0 3mm;padding:2mm 0 2mm 3mm;
 border-left:5px solid #c2410c;background:#fff7ed;page-break-after:avoid}
h2 .id{display:block;font-size:9.5pt;color:#7c2d12;font-weight:400}
h3{font-size:11pt;margin:5mm 0 1mm;padding-bottom:1mm;border-bottom:1px solid #cfe6dc;
 page-break-after:avoid}
h3 .id{display:block;font-size:9pt;color:#4a5b6b;font-weight:400}
.ja{margin:0 0 1mm}
.id{margin:0 0 3mm;color:#2b4a63;font-size:9.5pt;line-height:1.7}
.pair{page-break-inside:avoid;margin:0 0 3.5mm}
table{border-collapse:collapse;width:100%;margin:0 0 4mm;font-size:9.5pt;
 page-break-inside:avoid}
th,td{border:1px solid #c9d4de;padding:1.5mm 2mm;text-align:left;vertical-align:top}
th{background:#eef4f9;font-weight:700;font-size:9pt}
td .id{margin:0;font-size:8.8pt}
.btn{display:inline-block;border:1px solid #c9d4de;border-radius:3px;
 padding:0 1.5mm;margin:0 1mm .8mm 0;font-size:9pt;background:#f7f9fb}
.qrbox{display:flex;gap:5mm;align-items:center;border:1px solid #c9d4de;
 border-radius:3px;padding:3mm 4mm;margin:0 0 4mm;background:#fbfcfd;
 page-break-inside:avoid}
.qrbox .qr{flex:none;line-height:0}
.qrbox svg{width:30mm;height:30mm;display:block}
.qrbox p{margin:0 0 1mm}
.note{border-left:4px solid #c2410c;background:#fff7ed;padding:2.5mm 3mm;
 margin:0 0 4mm;page-break-inside:avoid}
.note .ja{margin-bottom:1mm}
.note .id{margin-bottom:0}
b{font-weight:700}
footer{margin-top:6mm;border-top:1px solid #cfe6dc;padding-top:2mm;
 font-size:8.5pt;color:#55606c}
'''


def build():
    g = menu()
    o = []
    A = o.append
    P = lambda ja, idn: A('<div class="pair"><p class="ja">%s</p>'
                          '<p class="id">%s</p></div>' % (ruby(ja), idn))

    A('<!doctype html><html lang="ja"><head><meta charset="utf-8">')
    A('<title>使い方／Cara pakai</title><style>%s</style></head><body>' % CSS)
    A('<h1>' + ruby('この アプリの 使《つか》い方《かた》'))
    A('<span class="id">Cara memakai aplikasi ini</span></h1>')

    P('この 紙《かみ》は、<b>はじめて この 画面《がめん》を 見《み》る 人《ひと》</b>の'
      ' ための ものです。画面《がめん》に 出《で》て いる 順番《じゅんばん》に 書《か》いて あります。',
      'Kertas ini untuk <b>orang yang baru pertama kali melihat layar ini</b>. '
      'Urutannya sama dengan urutan di layar.')

    # ── 1 ──────────────────────────────
    A('<h2>1　ひらきます<span class="id">Membuka</span></h2>')
    A('<table><tr><th>' + ruby('日本語《にほんご》') + '</th><th>Bahasa Indonesia</th></tr>')
    for a, b in (
        ('① スマホで この 住所《じゅうしょ》を ひらきます<br>'
         '<code>' + URL.replace('https://', '') + '</code>',
         'Buka alamat ini di HP Anda'),
        ('② 合言葉《あいことば》を 入《い》れます。<b>1回《かい》だけ</b>です。'
         '職員《しょくいん》に 聞《き》いて ください',
         'Masukkan kata sandi. <b>Hanya sekali saja.</b> Tanyakan kepada staf'),
        ('③ メニューが 出《で》ます。ここから ぜんぶへ 行《い》けます',
         'Menu akan muncul. Dari sini Anda bisa pergi ke semuanya'),
    ):
        A('<tr><td>%s</td><td class="id">%s</td></tr>' % (ruby(a), b))
    A('</table>')
    A('<div class="qrbox"><div class="qr">' + qr() + '</div><div>')
    A('<p class="ja">' + ruby(
        '<b>カメラで よみとると、すぐ ひらけます。</b><br>'
        'スマホの カメラを QRに むけて ください。') + '</p>')
    A('<p class="id"><b>Pindai dengan kamera, langsung terbuka.</b><br>'
      'Arahkan kamera HP Anda ke kode QR ini.</p>')
    A('<p class="ja" style="font-size:8.5pt;color:#55606c">'
      + '<code>' + URL + '</code></p>')
    A('</div></div>')
    P('<b>登録《とうろく》は いりません。アプリを 入《い》れなくて いいです。</b>'
      'ホーム画面《がめん》に 追加《ついか》すると、つぎから すぐ ひらけます。',
      '<b>Tidak perlu mendaftar. Tidak perlu memasang aplikasi.</b> '
      'Kalau ditambahkan ke layar utama HP, lain kali bisa langsung dibuka.')

    # ── 2 ──────────────────────────────
    A('<h2>2　まず、これだけ<span class="id">Untuk awal, cukup ini saja</span></h2>')
    P('メニューは <b>%d</b>個《こ》 あります。<b>ぜんぶ つかわなくて いいです。</b>'
      'はじめは この 3つ だけで じゅうぶんです。' % len(g),
      'Ada <b>%d</b> kelompok menu. <b>Anda tidak harus memakai semuanya.</b> '
      'Untuk awal, cukup 3 ini saja.' % len(g))
    A('<table><tr><th style="width:4%%">　</th><th>おす もの</th>'
      '<th>Yang ditekan</th></tr>')
    idmap = {ja: idn for ja, idn, _ in g}
    for i, h in enumerate(FIRST, 1):
        A('<tr><td><b>%d</b></td><td><b>%s</b></td><td class="id"><b>%s</b></td></tr>'
          % (i, ruby(mr(h)), idmap.get(h, '')))
    A('</table>')
    P('ほかは、<b>ひつようになったら</b> ひらけば いいです。',
      'Yang lain cukup dibuka <b>saat Anda membutuhkannya.</b>')

    # ── 3 ──────────────────────────────
    A('<h2>' + ruby('3　メニューの 中身《なかみ》')
      + '<span class="id">Isi menu</span></h2>')
    for ja, idn, btns in g:
        d = GROUP[ja]
        # **見出し・説明・ボタンを 1つの箱に入れる。**
        # 箱ごと次のページへ送られるので、見出しだけが 取り残されない。
        A('<div class="grp">')
        A('<h3>%s<span class="id">%s</span></h3>'
          % (ruby(mr(ja)), idn))
        A('<div class="pair"><p class="ja">%s</p><p class="id">%s</p></div>'
          % (ruby(d['ja']), d['id']))
        if btns:
            A('<p class="ja">' + ''.join(
                '<span class="btn">%s<br><span style="font-size:7.5pt;color:#55606c">%s</span>'
                '</span>' % (ruby(mr(b[0])), b[1]) for b in btns) + '</p>')
        A('</div>')

    # ── 4 ──────────────────────────────
    A('<h2>' + ruby('4　いちばん 大事《だいじ》な こと')
      + '<span class="id">Hal yang paling penting</span></h2>')
    mk = marks()
    P('カードや 一覧《いちらん》で、<b>%s</b> と <b>%s</b> を おす こと。これだけです。'
      % (mk[0][0] + mk[0][1], mk[1][0] + mk[1][1]),
      'Di kartu atau daftar, tekan <b>%s</b> atau <b>%s</b>. Hanya itu.'
      % (mk[0][0] + ' ' + mk[0][2], mk[1][0] + ' ' + mk[1][2]))
    A('<table><tr><th>' + ruby('ボタン') + '</th><th>'
      + ruby('いつ おしますか') + '</th><th>Kapan ditekan</th></tr>')
    for (sym, word, idn), ja, idt in zip(mk, (
        '見《み》て すぐ 読《よ》めた。意味《いみ》が 言《い》えた',
        '少《すこ》しでも まよった'), (
        'Langsung bisa dibaca begitu dilihat. Bisa menyebutkan artinya',
        'Sedikit saja ragu')):
        A('<tr><td><b>%s</b><br><span class="id">%s %s</span></td><td>%s</td>'
          '<td class="id">%s</td></tr>'
          % (ruby(sym + word), sym, idn, ruby(ja), idt))
    A('</table>')
    A('<div class="note">')
    A('<p class="ja">%s</p>' % ruby(
        'この 印《しるし》を おすと、<b>まちがえた 分《ぶん》だけが'
        '「まちがえたところ」に あつまります。</b>'
        'おさないと、試験《しけん》の 前《まえ》に 「どこが 弱《よわ》いか」が 分《わ》かりません。'
        '<b>まよったら %s を おして ください。</b>多《おお》く おしても 損《そん》は しません。'
        % (mk[1][0] + mk[1][1])))
    A('<p class="id">Kalau Anda menekan tanda ini, '
      '<b>hanya yang salah saja yang terkumpul di "Yang Salah".</b> '
      'Kalau tidak ditekan, menjelang ujian Anda tidak akan tahu bagian mana yang lemah. '
      '<b>Kalau ragu, tekan %s.</b> Menekannya terlalu sering pun tidak merugikan.</p>'
      % (mk[1][0] + ' ' + mk[1][2]))
    A('</div>')

    # ── 5 ──────────────────────────────
    A('<h2>' + ruby('5　記録《きろく》は どこに ありますか')
      + '<span class="id">Di mana catatan belajar disimpan?</span></h2>')
    P('<b>あなたの スマホの 中《なか》だけ</b>です。'
      'どこにも 送《おく》られません。',
      '<b>Hanya di dalam HP Anda.</b> Tidak dikirim ke mana pun.')
    P('ですから、<b>スマホを かえると 消《き》えます。</b>'
      '月《つき》に 一度《いちど》、面談《めんだん》の とき に'
      '「学習状況《がくしゅうじょうきょう》」→「💾 バックアップを 保存《ほぞん》」を'
      ' おして ください。共有《きょうゆう》の 画面《がめん》が 出《で》るので、'
      '「ドライブに 保存《ほぞん》」を えらびます。',
      'Karena itu, <b>kalau ganti HP, catatannya hilang.</b> '
      'Sebulan sekali, saat wawancara bulanan, tekan '
      '"Progres" → "💾 Cadangkan". Layar berbagi akan muncul, '
      'lalu pilih "Simpan ke Drive".')
    P('新《あたら》しい スマホでは「📂 バックアップを 読《よ》み込《こ》む」で もどります。',
      'Di HP baru, tekan "📂 Pulihkan" dan catatannya akan kembali.')

    # ── 6 ──────────────────────────────
    A('<h2>6　こまった とき<span class="id">Kalau ada masalah</span></h2>')
    A('<table><tr><th>こうなったら</th><th>こうして ください</th>'
      '<th>Yang harus dilakukan</th></tr>')
    for a, b, c in (
        ('「合言葉《あいことば》が ちがいます」と 出《で》る',
         '<b>半角《はんかく》</b>で 入《い》れて ください',
         'Ketik dengan huruf <b>setengah lebar (hankaku)</b>'),
        ('音《おと》が 出《で》ない',
         '<b>Chrome</b>で ひらいて ください。'
         'LINEの 中《なか》で ひらくと 音《おと》が 出《で》ません',
         'Buka dengan <b>Chrome</b>. Kalau dibuka di dalam LINE, suaranya tidak keluar'),
        ('画面《がめん》が 古《ふる》いまま',
         'いちばん 下《した》の「🔄 最新《さいしん》にする」を おす',
         'Tekan "🔄 Perbarui" di bagian paling bawah'),
        ('何《なに》を やれば いいか 分《わ》からない',
         '<b>新人《しんじん》コース</b>を ひらく。その 週《しゅう》の 分《ぶん》が 出《で》ます',
         'Buka <b>Staf Baru</b>. Bagian untuk minggu itu akan muncul'),
        ('記録《きろく》が 消《き》えた',
         'バックアップが あれば もどせます。なければ もどせません',
         'Kalau ada cadangan, bisa dikembalikan. Kalau tidak ada, tidak bisa'),
    ):
        A('<tr><td>%s</td><td>%s</td><td class="id">%s</td></tr>'
          % (ruby(a), ruby(b), c))
    A('</table>')

    A('<div class="note">')
    A('<p class="ja">%s</p>' % ruby(
        '<b>できなくても 心配《しんぱい》いりません。</b>'
        'まちがえた ところが 分《わ》かるのが、この システムの 役目《やくめ》です。'
        'まちがえた 数《かず》だけ、あなたは 前《まえ》に 進《すす》んで います。'))
    A('<p class="id"><b>Tidak perlu khawatir kalau belum bisa.</b> '
      'Tugas sistem ini justru menunjukkan bagian mana yang masih salah. '
      'Setiap kesalahan berarti Anda sudah maju satu langkah.</p>')
    A('</div>')

    A('<footer>')
    A(ruby('この 紙《かみ》は <code>tools/shiyou-id.py</code> が '
           'メニューを 読《よ》んで 作《つく》って います。'))
    A('<br>Kertas ini dibuat otomatis dari menu aplikasi.')
    A('</footer></body></html>')
    html = '\n'.join(o)
    check_ruby(html[html.index('<body>'):], '使用説明書')
    return html


def main():
    t = build()
    if '--html' in sys.argv:
        p = sys.argv[sys.argv.index('--html') + 1]
        io.open(p, 'w', encoding='utf-8').write(t)
        print('書きました: %s（%d文字）' % (p, len(t)))
    else:
        sys.stdout.write(t)
    return 0


if __name__ == '__main__':
    sys.exit(main())
