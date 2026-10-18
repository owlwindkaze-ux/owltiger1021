#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""N2の紙のパック（ドライブのGoogleドキュメント）を、**読みやすい紙**に組み直す。

持ち主から「**教材が見にくい。最初の説明はみんな必要ですか。
問題同士の行間も詰まっていて見にくい**」。

**見にくい原因は2つ**（中を読んで分かった）。

1. **選択肢が1行に4つ**並んでいる。
   `1　…　　2　…　　3　…　　4　…` が20問続く。
2. **最初の説明が長い。**半分以上が**職員向け**だった
   （月10公休・早出6回・1単元235分・月19時間、聴解の録音の分け方、
   読み上げない箇所、参照した公式情報…）。
   学習者に要るのは**名前欄と答え方の5行**ほど。

**中身（問題文・選択肢）は1字も変えない。**変えるのは並べ方だけ。

    # ドキュメントの本文を そのまま テキストで保存してから
    python3 tools/n2paper.py 入力.txt 出力.html [--unit 1]
    NODE_PATH=/tmp/node_modules node tools/pdf/mkpdf.mjs 出力.html 出力.pdf "…"

**原文はリポジトリに入れない。**施設の教材なので、作業用の場所に置く。
"""
import io
import re
import sys

CSS = r'''
@page { size: A4; margin: 16mm 15mm 17mm; }
body{font-family:"IPAPGothic","IPAGothic","Noto Sans CJK JP",sans-serif;
 color:#16212b;font-size:11pt;line-height:1.95;margin:0}
h1{font-size:17pt;color:#332e91;border-bottom:3px solid #4338ca;
 padding-bottom:4px;margin:0 0 3mm}
h1 small{display:block;font-size:10pt;color:#4a5b6b;font-weight:400;margin-top:1.5mm}
h2{font-size:12.5pt;color:#332e91;margin:8mm 0 4mm;padding:2mm 3mm;
 background:#eef2ff;border-left:5px solid #4338ca;break-after:avoid;page-break-after:avoid}
.head{border:1px solid #c7c9e8;background:#fbfcfd;padding:3mm 4mm;margin:0 0 5mm;
 font-size:10pt;line-height:1.9}
.head b{color:#332e91}
.head .ln{display:block;margin-top:2mm}
.q{break-inside:avoid;page-break-inside:avoid;margin:0 0 7mm;
 border-bottom:1px dashed #d7dbe8;padding-bottom:4mm}
.q:last-child{border-bottom:0}
.qn{display:inline-block;background:#4338ca;color:#fff;font-size:9.5pt;
 padding:.4mm 2.2mm;border-radius:2px;margin-right:2mm}
.qt{font-size:9.5pt;color:#4a5b6b}
.qb{margin:2.5mm 0 3mm;line-height:2.0}
.psg{background:#f7f8fa;border:1px solid #dfe4ee;padding:3mm 4mm;margin:0 0 3.5mm;
 line-height:2.05;font-size:10.5pt;break-inside:avoid;page-break-inside:avoid}
ol.ch{list-style:none;margin:0 0 3.5mm;padding:0}
ol.ch li{margin:0 0 2.2mm;padding-left:8mm;text-indent:-8mm;line-height:1.9}
/* **text-indent は inline-block の中にも効く。**
   li の text-indent:-8mm が 丸の中の数字にも掛かり、
   **数字が丸の外へ押し出されて、空の丸だけが並んでいた**（2026-10-18）。
   丸の中は 0 に戻す。 */
ol.ch .n{display:inline-block;width:5.5mm;text-align:center;text-indent:0;
 border:1px solid #9aa4bb;border-radius:50%;font-size:9pt;margin-right:2.5mm;
 color:#332e91;line-height:5.5mm;vertical-align:.5mm}
.ans{font-size:10pt;color:#4a5b6b}
.ans .box{display:inline-block;border-bottom:1.5px solid #16212b;width:22mm;
 margin:0 2mm;height:1.1em}
.rec{border:1px solid #c7c9e8;padding:3mm 4mm;margin:6mm 0 0;font-size:10pt;line-height:2.2}
.rec b{color:#332e91}
footer{margin-top:7mm;border-top:1px solid #dfe4ee;padding-top:2mm;
 font-size:8.5pt;color:#6b7686}
'''

# **学習者に要る案内だけ。**残りは職員用なので 指導者用の紙へ。
HEAD = '''<div class="head">
<b>なまえ（Nama）</b>　＿＿＿＿＿＿＿＿＿＿＿＿＿＿
<b>はじめた日</b>　＿＿＿＿年＿＿月＿＿日
<span class="ln">① <b>さいしょは 辞書と 答えを 見ないで 解きます。</b>
解き直すときは 使ってかまいません。<br>
<i>Kerjakan dahulu tanpa kamus atau kunci jawaban.</i></span>
<span class="ln">② 答えは <b>1〜4から一つ</b>。聴解の「即時応答」だけ <b>1〜3から一つ</b>。</span>
<span class="ln">③ <b>★</b>の問題は、四つを全部つかって文を作り、
<b>★の場所に入る番号</b>を書きます。</span>
<span class="ln">④ 聴解は <b>1回だけ</b>聞いて答えます。答えてから 台本を見ます。</span>
</div>'''


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('\\_', '_'))


def rich(t):
    """**強調** と 【語】 を そのまま 生かす"""
    t = esc(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = t.replace('【', '<b>【').replace('】', '】</b>')
    return t


CH = re.compile(r'(?:^|　)([1-4１-４])　')


def is_choices(ln):
    """「1　… 　2　… 　3　…」の行か"""
    return len(CH.findall(ln)) >= 3 and ln.lstrip().startswith(('1　', '1 '))


def split_choices(ln):
    parts = re.split(r'　{2,}(?=[1-4]　)|(?<=。)　+(?=[1-4]　)', ln.strip())
    out = []
    for p in parts:
        m = re.match(r'^([1-4])　(.*)$', p.strip())
        if m:
            out.append((m.group(1), m.group(2).strip()))
    if len(out) < 2:                      # 1行に詰まっている形
        out = []
        for m in re.finditer(r'([1-4])　(.*?)(?=(?:　+[1-4]　)|$)', ln.strip()):
            out.append((m.group(1), m.group(2).strip()))
    return out


def unit_blocks(text, want):
    """第N単元 の かたまりを 取り出す"""
    ms = list(re.finditer(r'^# \*\*第(\d+)単元　(.+?)\*\*$', text, re.M))
    if not ms:
        raise SystemExit('× 「# **第N単元　…**」の見出しが 見つかりません。')
    for i, m in enumerate(ms):
        if int(m.group(1)) != want:
            continue
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        return int(m.group(1)), m.group(2), text[m.end():end]
    raise SystemExit('× 第%d単元が 見つかりません（あるのは %s）'
                     % (want, '・'.join(m.group(1) for m in ms)))


def build(num, title, body):
    o = []
    A = o.append
    A('<!doctype html><html lang="ja"><head><meta charset="utf-8">')
    A('<title>第%d単元</title><style>%s</style></head><body>' % (num, CSS))
    goal = re.search(r'^学習目標：(.+)$', body, re.M)
    A('<h1>第%d単元　%s<small>%s</small></h1>'
      % (num, esc(title), esc(goal.group(1)) if goal else ''))
    A(HEAD)

    lines = body.split('\n')
    i, inq, pend = 0, False, []

    def flush():
        """ためておいた 問題の中身を 出す"""
        if not pend:
            return
        A('<div class="qb">' + '</div><div class="qb">'.join(pend) + '</div>')
        pend.clear()

    while i < len(lines):
        ln = lines[i].rstrip()
        i += 1
        if not ln.strip():
            continue
        m = re.match(r'^## \*\*(.+?)\*\*$', ln)
        if m:
            if inq:
                A('</div>')
                inq = False
            t = m.group(1)
            if t.startswith(('解答・学習記録', 'E・Fで行う')):
                A('<div class="rec"><b>%s</b><br>' % esc(t))
                while i < len(lines) and not lines[i].startswith('#'):
                    x = lines[i].rstrip(); i += 1
                    if x.strip():
                        A(rich(x) + '<br>')
                A('</div>')
                continue
            A('<h2>%s</h2>' % esc(t))
            continue
        m = re.match(r'^\*\*(問\d+|確認\d+)　(.+?)\*\*$', ln)
        if m:
            if inq:
                A('</div>')
            A('<div class="q"><span class="qn">%s</span>'
              '<span class="qt">%s</span>' % (esc(m.group(1)), esc(m.group(2))))
            inq = True
            continue
        if re.match(r'^(A実施日|学習目標)', ln):
            continue
        if is_choices(ln):
            flush()
            A('<ol class="ch">')
            for n, t in split_choices(ln):
                A('<li><span class="n">%s</span>%s</li>' % (n, rich(t)))
            A('</ol>')
            continue
        if ln.startswith('答え：') or ln.startswith('解答：'):
            flush()
            A('<p class="ans">答え<span class="box"></span>'
              'わかり方　□ じしんが ある　□ じしんが ない</p>')
            continue
        if ln.lstrip().startswith('〔'):
            flush()
            A('<div class="psg">%s</div>' % rich(ln))
            continue
        pend.append(rich(ln))
    flush()
    if inq:
        A('</div>')
    A('<footer>この紙は ドキュメントの中身を 並べ直したものです。'
      '問題・選択肢の 文は 変えていません。'
      '（職員向けの進め方・聴解の実施方法は 指導者用の紙にあります）</footer>')
    A('</body></html>')
    return '\n'.join(o)


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) < 2:
        raise SystemExit(__doc__)
    want = 1
    if '--unit' in sys.argv:
        want = int(sys.argv[sys.argv.index('--unit') + 1])
    text = io.open(a[0], encoding='utf-8').read()
    num, title, body = unit_blocks(text, want)
    html = build(num, title, body)
    io.open(a[1], 'w', encoding='utf-8').write(html)
    nq = html.count('class="qn"')
    print('書きました: %s（第%d単元「%s」・問%d）' % (a[1], num, title, nq))
    if nq < 10:
        raise SystemExit('× 問題が %d問しか 取れていません。'
                         'ドキュメントの作りが 変わった可能性があります。' % nq)
    return 0


if __name__ == '__main__':
    sys.exit(main())
