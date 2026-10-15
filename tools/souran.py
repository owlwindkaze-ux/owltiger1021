#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**総覧 第3版**を、そのときのデータから作る（SPEC 2.6-z41）。

**なぜ道具にしたか**

第2版（2026-09-04）は手書きの1枚ものだった。よくできていたが、
**6週間で数字が全部古くなった**。漢字746→1,144、語彙4,558→6,659、
文型376→466、読解45本→80本、聴解48問→143問。
さらに N2コース・新人コース・模試・学習区分・まちがえたところ、
どれも第2版には載っていない。

持ち主から「**以前このような説明がつくられてます。
これに準拠したものを作ってってください**」。
そこで、**第2版の形と見た目はそのまま受けつぎ、中身の数字は
1つも手で書かない**ものに作りかえた。走らせ直せば いつでも最新になる。

**古くなったら止まる仕組み**（第2版が静かに古くなった理由への対策）

1. 画面が増えたのに `TREE` に書き足していなければ **止まる**
2. `TREE` に書いた画面が消えていれば **止まる**
3. メニューのまとまりが5つ未満しか読めなければ **止まる**
4. バックアップに入らない保存キーは、**数えて表に出す**（隠さない）

    python3 tools/souran.py                  # HTMLを画面に出す
    python3 tools/souran.py --html FILE      # HTMLで書き出す
    python3 tools/souran.py --md FILE        # Markdownで書き出す（PDF用）
"""
import collections
import glob
import importlib.util
import io
import json
import os
import re
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
VER = '第3版'
ASOF = '2026-10-15'

# ── 第2版の数（歴史。ここは手書きでよい。動かない値だから） ──────────
V2 = {'date': '2026-09-04', 'kanji': 746, 'vocab': 4558, 'sent': 4338,
      'gram': 376, 'read': 45, 'readq': 98, 'choukai': 48, 'choukai_p': 8,
      'tegaki': 6412, 'menus': 18, 'systems': 6}

# ── 構成図。**ここに無い画面があると、この道具は止まる** ──────────────
# (ならべる文字列, 実際のファイル, 説明)
TREE = [
    ('index.html', 'index.html', '入口メニュー（合言葉・進み具合・全メニュー）', ''),
    (None, None, None, None),
    ('kanji.html', 'kanji.html', '① 漢字・語彙', 'k'),
    ('  kanji-data.json', 'kanji-data.json', '漢字（読み・意味・部首・用例）', ''),
    ('  kanji-strokes.json', 'kanji-strokes.json', '書き順の線データ', ''),
    ('  vocab-data.json', 'vocab-data.json', '言葉（学習区分つき）', ''),
    ('  sentences.json', 'sentences.json', '練習問題の例文', ''),
    ('  kanji-weeks.json', 'kanji-weeks.json', 'コースの週わり（漢字・語彙）', ''),
    ('  vocab-extra.csv', 'vocab-extra.csv', '施設で足した言葉（Excelで編集）', ''),
    (None, None, None, None),
    ('bunpo/index.html', 'bunpo/index.html', '② 文型・文法', 'b'),
    ('dokkai/index.html', 'dokkai/index.html', '③ 読解', 'd'),
    ('choukai/index.html', 'choukai/index.html', '④ 聴解（データは本体に内蔵）', 'c'),
    ('tegaki.html', 'tegaki.html', '⑤ 手書き検索', 't'),
    ('  tegaki-data.json', 'tegaki-data.json', '手書きで引ける漢字・部首287', ''),
    ('fukushu/index.html', 'fukushu/index.html', '⑥ まちがえたところ（7区分を横断）', ''),
    (None, None, None, None),
    ('n3.html', 'n3.html', '⑦ N3合格 100日コース', ''),
    ('shinjin/index.html', 'shinjin/index.html', '⑧ 新人コース（30週）', ''),
    ('n2/index.html', 'n2/index.html', '⑨ N2コース（66週）', ''),
    ('shindan/index.html', 'shindan/index.html', '⑩ N2の診断テスト', ''),
    ('moshi/index.html', 'moshi/index.html', '⑪ 模試（本番と同じ時間）', ''),
    (None, None, None, None),
    ('staff/index.html', 'staff/index.html', '職員だけの入口（実習生の画面からは行けません）', ''),
    ('kaigo/index.html', 'kaigo/index.html', '紙の教材の入口', ''),
    (None, None, None, None),
    ('tools/', 'tools', '検査と生成の道具（公開していません）', ''),
    ('SPEC.md / MANUAL.md / README.md', 'SPEC.md', '仕様書・使用説明書 ＋ PDF版', ''),
]


def J(p):
    return json.load(io.open(R + p, encoding='utf-8'))


def kb(p):
    if os.path.isdir(R + p):
        n = 0
        for root, _, fs in os.walk(R + p):
            n += sum(os.path.getsize(os.path.join(root, f)) for f in fs)
        return n / 1024.
    return os.path.getsize(R + p) / 1024.


def mb(x):
    return '%.1f MB' % (x / 1024.)


def size(x):
    if x >= 1024:
        return '%.1f MB' % (x / 1024.)
    return '%.0f KB' % x if x >= 1 else '1 KB未満'


def base():
    """overview.py が集めている数をそのまま使う。二重に書かない。"""
    s = importlib.util.spec_from_file_location('ov', R + 'tools/overview.py')
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m.gather()


def menu():
    """入口メニューの見出しとボタンを読む。tsukaikata.py と同じ読み方。"""
    s = importlib.util.spec_from_file_location('tk', R + 'tools/tsukaikata.py')
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m.menu()


def choukai():
    """聴解のパートは choukai/index.html の中の DATA をそのまま読む。"""
    s = io.open(R + 'choukai/index.html', encoding='utf-8').read()
    i = s.index('const DATA = [')
    j = s.index('\n];', i)
    return json.loads(s[i + len('const DATA = '):j + 2])


def reading():
    t, lv = collections.Counter(), collections.Counter()
    for p in sorted(glob.glob(R + 'dokkai/reading-*.json')):
        d = json.load(io.open(p, encoding='utf-8'))
        for x in d.get('passages', []):
            t[x.get('type', '?')] += 1
            lv[x.get('level', '?')] += 1
    return t, lv


# ── 保存キーの分け方 ───────────────────────────────────────────────
# **記録**＝消えたら その人の積み上げが消えるもの。
# **設定**＝消えても押し直せば済むもの（速さ・言語・開いた版 など）。
# **ここに無いキーが出てきたら、この道具は止まる。**
# 新しい保存を足したとき、「バックアップに入れるかどうか」を
# 必ず一度は考えさせるため。
RECORD = {
    'jlpt-fixed-v1': 'まちがえたところで「直した」と押した印（読解・聴解・100日・模試）',
    'jlpt-kanji-mywords-v1': '自分で足した言葉',
    'jlpt-moshi-v1': '模試の結果',
    'jlpt-n2-shindan-v1': 'N2診断テストの結果',
    'n3-lastweek': '100日コースの進み',
    'n3-week': '100日コースの「やった」印',
    'n3-week1': '100日コースの「やった」印',
    'shinjin-w': '新人コース30週の「やった」印',
    'n2-week-': 'N2コース66週の「やった」印',
}
SETTING = ('vchk-', 'reloaded-for', 'bunpo-reloaded-for', 'jlpt-kanji-lang',
           'jlpt-kanji-gate-v1', 'jlpt-course', 'jlpt-decks',
           'jlpt-week-open', 'jlpt-review-open', 'jlpt-dokkai-ruby',
           'jlpt-choukai-rate', 'jlpt-choukai-voice', 'jlpt-choukai-howto',
           'jlpt-shindan-voice')


def keys():
    """保存している記録のうち、**バックアップに入らないもの**を挙げる。

    入らないものを黙っているのが いちばん悪い。機種を変えたときに
    消えるのは、その人にとっては「全部消えた」と同じだから。
    """
    s = io.open(R + 'kanji.html', encoding='utf-8').read()
    m = re.search(r'const PKEYS = \[(.*?)\];', s, re.S)
    if not m:
        raise SystemExit('× kanji.html の PKEYS が読めません。作りが変わった可能性があります。')
    pk = re.findall(r"'([^']+)'", m.group(1))
    used = set()
    for p in glob.glob(R + '*.html') + glob.glob(R + '*/index.html'):
        t = io.open(p, encoding='utf-8').read()
        for k in re.findall(r"""(?:getItem|setItem|removeItem)\(\s*['"]([^'"]+)['"]""", t):
            used.add(k)
        # KEY／STORE といった名前に入れてから使うものも拾う
        # （n2-week- のように、あとで週番号をつなげる形があるため）
        for k in re.findall(r"""(?:[A-Z_]*KEY[A-Z_]*|STORE)\s*=\s*['"]([^'"]+)['"]""", t):
            used.add(k)
    unknown = sorted(k for k in used
                     if k not in pk and k not in RECORD
                     and not k.endswith('-lastlv') and not k.startswith(SETTING))
    if unknown:
        raise SystemExit(
            '× 分け方の分からない保存キーがあります: ' + '／'.join(unknown)
            + '\n  tools/souran.py の RECORD（記録）か SETTING（設定）に入れてください。'
            + '\n  記録なら、kanji.html の PKEYS に足してバックアップに入れるかも'
              '決めてください。')
    # 記録なのにバックアップに入っていないものを、重複をまとめて並べる
    out = []
    for k in sorted(RECORD):
        if k in pk or k not in used:
            continue
        if RECORD[k] in [x[1] for x in out]:
            continue
        out.append((k, RECORD[k]))
    return pk, out


def tree():
    """構成図を組む。**画面の数が合わなければ止まる。**"""
    have = set(os.path.relpath(p, R) for p in
               glob.glob(R + '*.html') + glob.glob(R + '*/index.html'))
    listed = set(f for _, f, _, _ in TREE if f and f.endswith('.html'))
    if have - listed:
        raise SystemExit('× 構成図に無い画面があります: ' + '／'.join(sorted(have - listed))
                         + '\n  tools/souran.py の TREE に足してください。')
    if listed - have:
        raise SystemExit('× 構成図にあるのに実物が無い画面: ' + '／'.join(sorted(listed - have))
                         + '\n  tools/souran.py の TREE から外してください。')
    rows = []
    for i, (lab, f, note, cls) in enumerate(TREE):
        if lab is None:
            rows.append(('│', '', ''))
            continue
        last = (i == len(TREE) - 1)
        ind = lab.startswith('  ')
        # 枝の最後の子だけ └ にする（次の行が子でなければ最後）
        nxt = TREE[i + 1][0] if i + 1 < len(TREE) else None
        lastchild = ind and not (nxt or '').startswith('  ')
        nm = lab.strip()
        sz = ''
        if f and f != 'tools' and os.path.exists(R + f) and not os.path.isdir(R + f) \
                and not f.endswith('.md'):
            sz = size(kb(f))
        pre = ('│  ' + ('└ ' if lastchild else '├ ')) if ind \
            else ('└ ' if last else '├ ')
        rows.append((pre, (nm, cls, sz), note))
    return rows


def gather():
    d = base()
    d['menu'] = menu()
    d['buttons'] = sum(len(n) for _, n in d['menu'])
    d['ch'] = choukai()
    d['read_type'], d['read_lv'] = reading()
    d['pkeys'], d['nokeys'] = keys()
    d['tree'] = tree()
    d['sources'] = J('kanji.json')['sources'] + J('vocab.json')['sources']
    d['cats'] = len(J('bunpo/grammar.json')['categories'])
    d['subcats'] = len(J('vocab.json')['subcategories'])
    d['parts'] = len(d['ch'])

    # 大きさ。全部その場で測る
    served = 0
    for root, ds, fs in os.walk(R):
        ds[:] = [x for x in ds if x not in ('.git', 'tools', '.github')]
        served += sum(os.path.getsize(os.path.join(root, f)) for f in fs)
    d['served'] = served / 1024.
    d['html'] = sum(kb(p) for p in sorted(
        os.path.relpath(p, R) for p in glob.glob(R + '*.html') + glob.glob(R + '*/index.html')))
    d['npages'] = len(d['pages'])
    pdfs = glob.glob(R + '*.pdf') + glob.glob(R + 'kaigo/*.pdf')
    d['npdf'] = len(pdfs)
    d['pdfkb'] = sum(os.path.getsize(p) for p in pdfs) / 1024.
    d['first'] = sum(kb(p) for p in ['kanji.html', 'kanji.json', 'kanji-n5.json',
                                     'vocab.json', 'vocab-n5.json', 'sentences.json'])
    d['strokes'] = kb('kanji-strokes.json')
    d['tegakikb'] = kb('tegaki-data.json')
    d['ver'] = J('version.json')['version']
    return d


# ══════════════════════════════════════════════════════════════════
#  HTML
# ══════════════════════════════════════════════════════════════════

CSS = r'''
:root{
  --paper:#fbfcfd; --surface:#f1f5f9; --sunk:#e8eef4; --line:#d7e0ea; --hair:#e6ecf3;
  --ink:#0f1a26; --ink-2:#33475d; --muted:#61748a;
  --kanji:#1d4ed8; --bunpo:#046c50; --dokkai:#6d28d9; --choukai:#b45309;
  --tegaki:#0f766e; --hyaku:#2e4a63;
  --warn:#a4560c; --ok:#0b6b46; --new:#0e7490;
  --mincho:"Zen Old Mincho","Yu Mincho","Hiragino Mincho ProN",serif;
  --gothic:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",system-ui,sans-serif;
  --mono:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#0c1219; --surface:#141d27; --sunk:#1a242f; --line:#2a3644; --hair:#212c38;
    --ink:#e8eef5; --ink-2:#b6c5d4; --muted:#8397ab;
    --kanji:#7ba3ff; --bunpo:#4ec99f; --dokkai:#b191f5; --choukai:#e8a24a;
    --tegaki:#4fc7bd; --hyaku:#8fb4d6; --warn:#e0a35c; --ok:#5cc79a; --new:#5ec2d8;
  }
}
:root[data-theme="dark"]{
  --paper:#0c1219; --surface:#141d27; --sunk:#1a242f; --line:#2a3644; --hair:#212c38;
  --ink:#e8eef5; --ink-2:#b6c5d4; --muted:#8397ab;
  --kanji:#7ba3ff; --bunpo:#4ec99f; --dokkai:#b191f5; --choukai:#e8a24a;
  --tegaki:#4fc7bd; --hyaku:#8fb4d6; --warn:#e0a35c; --ok:#5cc79a; --new:#5ec2d8;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--gothic);font-size:16px;line-height:1.9;font-feature-settings:"palt" 1}
.wrap{max-width:60rem;margin:0 auto;padding:0 1.5rem 5rem}
.mast{position:relative;overflow:hidden;border-bottom:1px solid var(--line);
  background:var(--surface);margin-bottom:3rem}
.mast::before{content:"";position:absolute;inset:0;opacity:.5;
  background-image:
    repeating-linear-gradient(to right,var(--hair) 0 1px,transparent 1px 2.25rem),
    repeating-linear-gradient(to bottom,var(--hair) 0 1px,transparent 1px 2.25rem);
  -webkit-mask-image:linear-gradient(to bottom,#000,transparent 78%);
  mask-image:linear-gradient(to bottom,#000,transparent 78%);pointer-events:none}
.mast-in{position:relative;max-width:60rem;margin:0 auto;padding:3.5rem 1.5rem 2.75rem}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);margin:0 0 1rem}
h1{font-family:var(--mincho);font-weight:700;font-size:clamp(2rem,5.5vw,3.1rem);
  line-height:1.35;letter-spacing:.01em;margin:0 0 .9rem;text-wrap:balance}
h1 ruby rt{font-size:.34em;font-weight:400;color:var(--muted);letter-spacing:0}
.lede{max-width:38rem;margin:0;color:var(--ink-2);font-size:1.02rem}
.mast-meta{display:flex;flex-wrap:wrap;gap:.4rem 1.5rem;margin-top:1.75rem;
  font-family:var(--mono);font-size:.78rem;color:var(--muted)}
.mast-meta b{color:var(--ink-2);font-weight:500}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(8.4rem,1fr));
  background:var(--paper);border:1px solid var(--line);border-right:0;border-bottom:0;
  margin:0 0 3rem}
.fig{padding:1.1rem 1.15rem;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
.fig .n{font-family:var(--mincho);font-weight:600;font-size:1.85rem;line-height:1.1;
  font-variant-numeric:tabular-nums;display:block}
.fig .l{font-size:.78rem;color:var(--muted);margin-top:.35rem;display:block;line-height:1.6}
.fig .d{font-size:.7rem;color:var(--new);margin-top:.2rem;display:block;font-family:var(--mono)}
.fig.k .n{color:var(--kanji)} .fig.b .n{color:var(--bunpo)}
.fig.d2 .n{color:var(--dokkai)} .fig.c .n{color:var(--choukai)} .fig.t .n{color:var(--tegaki)}
section{margin:0 0 3.5rem}
h2{font-family:var(--mincho);font-weight:700;font-size:1.5rem;line-height:1.5;
  margin:0 0 .3rem;padding-top:1.25rem;border-top:2px solid var(--ink);
  display:flex;align-items:baseline;gap:.75rem;text-wrap:balance}
h2 .num{font-family:var(--mono);font-size:.72rem;font-weight:500;color:var(--muted);
  letter-spacing:.1em;flex:none}
.sub{color:var(--muted);font-size:.88rem;margin:0 0 1.75rem}
h3{font-family:var(--gothic);font-weight:700;font-size:1.02rem;
  margin:2.25rem 0 .75rem;padding-left:.7rem;border-left:3px solid var(--line)}
p{margin:0 0 1.1rem;max-width:44rem}
strong{font-weight:700}
a{color:var(--kanji)}
a:focus-visible{outline:2px solid var(--kanji);outline-offset:2px}
.sys{display:grid;gap:1rem;grid-template-columns:1fr}
@media(min-width:38rem){.sys{grid-template-columns:repeat(2,1fr)}}
@media(min-width:62rem){.sys{grid-template-columns:repeat(3,1fr)}}
.card{border:1px solid var(--line);background:var(--surface);padding:1.15rem 1.2rem 1.3rem}
.card .tag{font-family:var(--mono);font-size:.68rem;letter-spacing:.12em;
  text-transform:uppercase;display:block;margin-bottom:.55rem}
.card.k{border-top:3px solid var(--kanji)} .card.k .tag{color:var(--kanji)}
.card.b{border-top:3px solid var(--bunpo)} .card.b .tag{color:var(--bunpo)}
.card.d{border-top:3px solid var(--dokkai)} .card.d .tag{color:var(--dokkai)}
.card.c{border-top:3px solid var(--choukai)} .card.c .tag{color:var(--choukai)}
.card.t{border-top:3px solid var(--tegaki)} .card.t .tag{color:var(--tegaki)}
.card.h{border-top:3px solid var(--hyaku)} .card.h .tag{color:var(--hyaku)}
.card h4{font-family:var(--mincho);font-size:1.2rem;font-weight:600;margin:0 0 .5rem;line-height:1.4}
.card p{font-size:.87rem;color:var(--ink-2);margin:0 0 .8rem;max-width:none}
.card ul{margin:0;padding-left:1.1rem;font-size:.85rem;color:var(--ink-2)}
.card li{margin-bottom:.25rem}
.tw{overflow-x:auto;margin:0 0 1.5rem;border:1px solid var(--line)}
table{border-collapse:collapse;width:100%;font-size:.88rem;background:var(--paper)}
th,td{padding:.6rem .8rem;text-align:left;border-bottom:1px solid var(--hair);
  vertical-align:top;line-height:1.7}
th{background:var(--sunk);font-weight:700;font-size:.76rem;letter-spacing:.05em;
  color:var(--ink-2);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td.num,th.num{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;
  white-space:nowrap}
code{font-family:var(--mono);font-size:.86em;background:var(--sunk);padding:.1em .38em;border-radius:2px}
.up{color:var(--new);font-family:var(--mono);font-size:.8em;white-space:nowrap}
.tree{font-family:var(--mono);font-size:.8rem;line-height:2;background:var(--surface);
  border:1px solid var(--line);padding:1.2rem 1.3rem;overflow-x:auto;margin:0 0 1.5rem;
  white-space:pre;color:var(--ink-2)}
.tree b{color:var(--ink);font-weight:500}
.tree .c-k{color:var(--kanji)} .tree .c-b{color:var(--bunpo)}
.tree .c-d{color:var(--dokkai)} .tree .c-c{color:var(--choukai)} .tree .c-t{color:var(--tegaki)}
.tree .z{color:var(--muted)}
ol.steps{counter-reset:s;list-style:none;margin:0 0 1.5rem;padding:0}
ol.steps li{counter-increment:s;position:relative;padding:0 0 1rem 2.6rem;
  border-bottom:1px solid var(--hair);margin-bottom:1rem}
ol.steps li:last-child{border-bottom:0;margin-bottom:0}
ol.steps li::before{content:counter(s);position:absolute;left:0;top:.1rem;
  font-family:var(--mono);font-size:.78rem;color:var(--paper);background:var(--ink);
  width:1.7rem;height:1.7rem;display:grid;place-items:center}
ol.steps b{display:block;margin-bottom:.15rem}
.plan{display:grid;gap:0;border:1px solid var(--line);margin:0 0 1.5rem}
.row{display:grid;grid-template-columns:1fr;gap:0;border-bottom:1px solid var(--hair)}
.plan .row:last-child{border-bottom:0}
@media(min-width:44rem){.row{grid-template-columns:9.5rem 1fr}}
.when{background:var(--sunk);padding:.85rem 1rem;font-family:var(--mono);font-size:.78rem;
  color:var(--ink-2);line-height:1.7}
.when b{display:block;font-size:.95rem;color:var(--ink);font-family:var(--gothic)}
.what{padding:.85rem 1.1rem;font-size:.9rem;color:var(--ink-2);line-height:1.8}
.what b{color:var(--ink)}
.what .who{font-family:var(--mono);font-size:.7rem;letter-spacing:.06em;color:var(--muted);
  display:block;margin-bottom:.15rem}
.note{border-left:3px solid var(--warn);background:var(--surface);padding:.9rem 1.1rem;
  margin:0 0 1.5rem;font-size:.9rem;color:var(--ink-2)}
.note.priv{border-left-color:var(--ok)}
.note b{color:var(--ink)}
.note p:last-child{margin-bottom:0}
.ok{color:var(--ok);font-weight:700}
.stage{font-family:var(--mono);font-size:.7rem;letter-spacing:.08em;
  border:1px solid var(--line);padding:.1rem .45rem;color:var(--muted);white-space:nowrap}
footer{border-top:1px solid var(--line);margin-top:1rem;padding-top:1.5rem;
  font-size:.8rem;color:var(--muted)}
footer p{max-width:none}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media print{
  body{font-size:10.5pt;line-height:1.75}
  .mast{break-inside:avoid} section{break-inside:auto} h2{break-after:avoid}
  .tw,.tree,.note,.card,.row{break-inside:avoid}
  .wrap{padding-bottom:0}
}
'''


def n(x):
    return '{:,}'.format(x)


def lv(c, order):
    return '／'.join('%s %s' % (k, n(c[k])) for k in order if c.get(k))


def html(d):
    o = []
    A = o.append
    kl = ['N5', 'N4', 'N3', 'N2', '介護', '記録']
    vl = ['N5', 'N4', 'N3', 'N2', '介護', '記録', '現場']
    gl = ['N5', 'N4', 'N3', 'N2', '記録']
    kaigo = d['vocab_lv']['介護'] + d['vocab_lv']['記録'] + d['vocab_lv']['現場']
    sj, n2 = d['courses']['shinjin'], d['courses']['n2']

    def dl(now, was, unit=''):
        if not was or now == was:
            return ''
        return '<span class="d">+%s%s</span>' % (n(now - was), unit)

    A('<!doctype html><html lang="ja"><head><meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width,initial-scale=1">')
    A('<title>介護の日本語 学習システム 総覧</title>')
    A('<link rel="preconnect" href="https://fonts.googleapis.com">')
    A('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    A('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
      'family=Zen+Old+Mincho:wght@400;600;700&family=Zen+Kaku+Gothic+New:wght@400;500;700'
      '&family=IBM+Plex+Mono:wght@400;500&display=swap">')
    A('<style>%s</style></head><body>' % CSS)

    # ── masthead ─────────────────────────────────────────────
    A('<header class="mast"><div class="mast-in">')
    A('<p class="eyebrow">Belajar Bahasa Jepang Kaigo — 総覧 %s</p>' % VER)
    A('<h1><ruby>介護<rt>かいご</rt></ruby>の<ruby>日本語<rt>にほんご</rt></ruby>'
      '学習システム</h1>')
    A('<p class="lede">インドネシアから来た介護の技能実習生が、現場で読める・聞ける・'
      '答えられるようになるための学習システム。漢字・語彙、文型・文法、読解、聴解、'
      '手書き検索、まちがえたところ、それに3つのコースと模試を、'
      'ひとつの入口にまとめてあります。</p>')
    A('<div class="mast-meta">')
    A('<span><b>公開</b> owlwindkaze-ux.github.io/owltiger1021</span>')
    A('<span><b>版</b> %s（%s・画面の版 %s）</span>' % (ASOF, VER, d['ver']))
    A('<span><b>制作</b> 2026-05-19 〜 継続中</span>')
    A('<span><b>運用費</b> ¥0</span>')
    A('</div></div></header>')

    A('<div class="wrap">')

    # ── 数字 ────────────────────────────────────────────────
    A('<div class="figs">')
    for cls, num, lab, dd in (
        ('k', n(d['kanji']), '漢字（書き順つき）', dl(d['kanji'], V2['kanji'])),
        ('k', n(d['vocab']), '言葉・熟語', dl(d['vocab'], V2['vocab'])),
        ('k', n(d['sent']), '練習問題の例文', dl(d['sent'], V2['sent'])),
        ('b', n(d['gram']), '文型', dl(d['gram'], V2['gram'])),
        ('d2', n(d['read']['passages']), '読解の文章（%d問）' % d['read']['questions'],
         dl(d['read']['passages'], V2['read'], '本')),
        ('c', n(d['choukai']), '聴解の設問（%d部）' % d['parts'],
         dl(d['choukai'], V2['choukai'])),
        ('t', n(d['tegaki']), '手書きで引ける漢字', ''),
    ):
        A('<div class="fig %s"><span class="n">%s</span><span class="l">%s</span>%s</div>'
          % (cls, num, lab, dd))
    A('</div>')
    A('<p class="sub" style="margin-top:-2rem;margin-bottom:3rem">'
      '青い数字は <b>第2版（%s）からの増え分</b>です。'
      'この資料の数は、ぜんぶそのときのデータを数えて書いています'
      '（<code>tools/souran.py</code>）。手で書いた数はありません。</p>' % V2['date'])

    # ══ 01 ═════════════════════════════════════════════════
    A('<section><h2><span class="num">01</span>これは何か</h2>')
    A('<p class="sub">誰の、どんな困りごとを解く道具か</p>')
    A('<p>介護施設で働くインドネシア人の技能実習生が、<strong>仕事で実際に出会う日本語</strong>'
      'を勉強するためのものです。市販の教材が「学校・旅行・買い物」を題材にするのに対し、'
      'このシステムは<strong>申し送り・記録・声かけ・掲示物</strong>を題材にしています。</p>')
    A('<p>スマホのブラウザで開くだけで使えます。アプリの導入も、会員登録も、'
      '通信料以外の費用もかかりません。入口メニューは<strong>%d のまとまり・'
      'ボタン %d個</strong>です。</p>' % (len(d['menu']), d['buttons']))
    A('<p>第2版（%s）からの大きな変わり目は3つです。'
      '<strong>①N2まで伸ばした</strong>（漢字・語彙・文型・読解・聴解のすべてにN2が入り、'
      '66週のコースと診断テストが付きました）。'
      '<strong>②「いつ何をやるか」を決め切った</strong>'
      '（入職から7月のN3までの新人コース30週、試験100日前からの100日コース、模試%d回）。'
      '<strong>③覚える語を選り分けた</strong>'
      '（現場の言葉%s語を「覚える／意味が分かる／参考」の3つに分けました）。</p>'
      % (V2['date'], d['moshi'], n(sum(d['study'].values()))))

    A('<div class="sys">')
    cards = [
        ('k', 'System 1', '漢字・語彙',
         '読み・意味・部首・書き順アニメーション。JLPT本試験と同じ5形式の練習問題。',
         ['漢字 %s字（%s）' % (n(d['kanji']), lv(d['kanji_lv'], kl)),
          '言葉 %s語（%s）' % (n(d['vocab']), lv(d['vocab_lv'], vl)),
          '例文 %s本（言葉の%.0f%%）' % (n(d['sent']), 100. * d['sent'] / d['vocab']),
          '小分類 %d。読みは色を変えて大きく出します' % d['subcats']]),
        ('b', 'System 2', '文型・文法',
         '話すときの形に加え、記録の書き方も。すべて介護の場面の例文つき。',
         ['文型 %s項目（%s）' % (n(d['gram']), lv(collections.Counter(d['gram_lv']), gl)),
          '意味のまとまり %d種で引けます' % d['cats'],
          '1項目につき 介護の場面の例文3つ',
          '形・意味・注意点を 日本語・インドネシア語・英語で']),
        ('d', 'System 3', '読解',
         '文章を読んで4択で答える。文章はすべて書き下ろし。',
         ['文章 %d本・設問 %d問' % (d['read']['passages'], d['read']['questions']),
          '／'.join('%s%d' % (k, v) for k, v in d['read_type'].most_common()),
          'レベル別 %s' % lv(d['read_lv'], ['N5', 'N4', 'N3', 'N2']),
          'おすすめボタンで層別に選べます']),
        ('c', 'System 4', '聴解',
         '端末が読み上げる音声を聞いて答える。音声ファイルを持たない設計。',
         ['%dパート・%d問' % (d['parts'], d['choukai']),
          '介護の場面 %d問／JLPT形式 %d問'
          % (sum(len(p['items']) for p in d['ch'] if p['no'] in ('PART 1', 'PART 2', 'PART 3')),
             sum(len(p['items']) for p in d['ch'] if p['no'] not in ('PART 1', 'PART 2', 'PART 3'))),
          'N3 %d問／N2 %d問'
          % (sum(len(p['items']) for p in d['ch'] if p['level'] == 'N3'),
             sum(len(p['items']) for p in d['ch'] if p['level'] == 'N2')),
          '速さ4段階・何度でも聞き直せる']),
        ('t', 'System 5', '手書き検索',
         '読めない漢字を枠に書くと候補が出ます。覚えるためではなく、'
         'その場で調べるための道具。',
         ['収録 %s字（本システム最多）' % n(d['tegaki']),
          '読み・意味・画数・部首',
          '書き順が違っても見つかります',
          '%s。開いたときだけ読み込みます' % size(d['tegakikb'])]),
        ('h', 'System 6', 'まちがえたところ',
         'まちがえた問題だけが、7つの区分を またいで 集まります。'
         '毎日ここから始めるのが いちばん効きます。',
         ['漢字・語彙・文型・読解・聴解を横断',
          '正解と解説つき',
          '紙に印刷できます',
          '新しく足すより、ここを回すほうが点が上がります']),
    ]
    for cls, tag, h4, p, ul in cards:
        A('<article class="card %s"><span class="tag">%s</span><h4>%s</h4><p>%s</p><ul>%s</ul>'
          '</article>' % (cls, tag, h4, p, ''.join('<li>%s</li>' % x for x in ul)))
    A('</div>')

    A('<h3>3つのコース<span class="up"> 第3版で新設</span></h3>')
    A('<p>教材が増えるほど「何から手をつけるか」が分からなくなります。'
      'そこで<strong>日付から逆算して、やることを決め切ったコース</strong>を3本'
      '用意しました。実習生は<strong>毎朝そこを開くだけ</strong>で済みます。</p>')
    A('<div class="tw"><table><thead><tr><th>コース</th><th>いつ</th>'
      '<th class="num">週</th><th>その中で教える量</th><th>向く人</th></tr></thead><tbody>')
    A('<tr><td><b>新人コース</b></td><td>入職（%s）→ 2027年7月のN3</td>'
      '<td class="num">%d</td><td>漢字 %s・語彙 %s・文型 %s</td>'
      '<td>来日したばかりの人。<b>最初にN4の判定テスト</b>があります</td></tr>'
      % (sj['start'], sj['total'], n(sj['kanji']), n(sj['vocab']), n(sj['gram'])))
    A('<tr><td><b>100日コース</b></td><td>試験の100日前から</td>'
      '<td class="num">14</td><td>%s問を 月〜日に割りふり</td>'
      '<td>受験日が決まっている人。土曜は本番と同じ時間の通しテスト</td></tr>' % d['n3q'])
    A('<tr><td><b>N2コース</b></td><td>N3合格（%s）→ 2027年12月のN2</td>'
      '<td class="num">%d</td><td>漢字 %s・語彙 %s・文型 %s</td>'
      '<td>N3に受かった人。<b>受かるまで開かなくていい</b></td></tr>'
      % (n2['start'], n2['total'], n(n2['kanji']), n(n2['vocab']), n(n2['gram'])))
    A('</tbody></table></div>')
    A('<div class="note"><p><b>コースは教材の一部を選んで並べたものです。</b>'
      '新人コースが30週で教えるのは漢字%s字で、入っている%s字の全部ではありません。'
      '7月のN3に間に合う量に絞ってあります。残りは、コースの外から いつでも引けます。</p></div>'
      % (n(sj['kanji']), n(d['kanji'])))
    A('</section>')

    # ══ 02 ═════════════════════════════════════════════════
    A('<section><h2><span class="num">02</span>構造</h2>')
    A('<p class="sub">どのファイルが何をしているか</p>')
    A('<p>特別なサーバーは使っていません。<strong>HTMLファイルとデータファイルを'
      '置いてあるだけ</strong>で、計算はすべて実習生のスマホの中で行われます。'
      'だから壊れにくく、費用がかかりません。'
      '画面は<strong>%d枚</strong>（合わせて %s）です。</p>'
      % (d['npages'], size(d['html'])))
    tr = ['<b>owltiger1021/</b>']
    for pre, cell, note in d['tree']:
        if cell == '':
            tr.append(pre)
            continue
        nm, cls, sz = cell
        tag = '<span class="c-%s"><b>%s</b></span>' % (cls, nm) if cls else '<b>%s</b>' % nm
        pad = ' ' * max(1, 26 - len(nm) - len(pre))
        tr.append('%s%s%s%s%s' % (pre, tag, pad, note,
                                  ('   <span class="z">%s</span>' % sz) if sz else ''))
    A('<div class="tree">' + '\n'.join(tr) + '</div>')

    A('<h3>大きさと読み込み</h3>')
    A('<div class="tw"><table><thead><tr><th>項目</th><th class="num">大きさ</th>'
      '<th>備考</th></tr></thead><tbody>')
    for a, b, c in (
        ('漢字の画面をN5で開いたとき', size(d['first']),
         '写真1枚ぶん。2回目からは端末に残るので通信しません'),
        ('書き順の線データ', size(d['strokes']),
         '書き順を見たときだけ読み込みます'),
        ('手書き検索のデータ', size(d['tegakikb']),
         '手書き検索を開いたときだけ読み込みます（他の画面には影響しません）'),
        ('アプリ本体（画面%d枚の合計）' % d['npages'], size(d['html']),
         '外部ライブラリ・CDNを一切使っていません'),
        ('紙の資料（PDF %d本）' % d['npdf'], size(d['pdfkb']),
         '<b>いまの置き場所で いちばん重いのはここです。</b>実習生の画面は読み込みません'),
        ('公開しているファイル全部', size(d['served']),
         'GitHub Pagesの上限1GBの%.0f%%' % (100. * d['served'] / 1024 / 1024)),
        ('聴解の音声', '0 KB',
         '端末の読み上げ機能を使うため、音声ファイルがありません'),
    ):
        A('<tr><td>%s</td><td class="num">%s</td><td>%s</td></tr>' % (a, b, c))
    A('</tbody></table></div>')
    A('<p>外部の部品を使っていないため、<strong>他社のサービスが止まっても'
      'リンク切れになりません</strong>。海外の遅い回線でも開けます。'
      '<strong>ただし手書き検索だけは例外</strong>で、認識の精度を上げるために'
      ' Google の手書き入力に問い合わせる方式を選べます（後述）。</p>')
    A('<div class="note"><p><b>増え方について正直に：</b>'
      '第2版のとき 13.4 MB だった置き場所は、いま %s です。'
      'うち %s が紙の資料（PDF）で、画面の重さには関係ありません。'
      'それでも上限の%.0f%%しか使っていないので、まだ困りません。'
      'ただし<b>増やし続けてよいという意味ではありません</b>。'
      '古くなった紙はドライブへ出す、という整理を続けます。</p></div>'
      % (size(d['served']), size(d['pdfkb']), 100. * d['served'] / 1024 / 1024))
    A('</section>')

    # ══ 03 ═════════════════════════════════════════════════
    A('<section><h2><span class="num">03</span>仕様</h2>')
    A('<p class="sub">何がどう動くか</p>')

    A('<h3>練習問題（JLPT本試験と同じ5形式）</h3>')
    A('<div class="tw"><table><thead><tr><th>大問</th><th>出し方</th>'
      '<th>まちがいの選択肢の作り方</th></tr></thead><tbody>')
    for a, b, c in (
        ('問題1 漢字読み', '例文の中の語に下線、読みを4択',
         '清濁・長短・促音・拗音を1か所だけ変えた、本試験と同じまぎらわしい読み'),
        ('問題2 表記', '下線部をかなにして、正しい漢字を4択',
         '同じ部首・同じ音読みの漢字で作った偽の熟語（満足／満束／浴足）'),
        ('問題3 文脈規定', '例文の一部を（　）にして語を4択', '同レベル・語長の近い語'),
        ('問題4 言い換え類義', '意味がいちばん近い語を4択', '同じ訳語をもつ語を正解に'),
        ('問題5 用法', 'その語の使い方が正しい文を4択',
         '他の語の例文に、その語を差し替えた誤用文'),
        ('（追加）漢字の読み', '1字で語になる字はそのまま、そうでない字は熟語の中で出題',
         '相手の字が上のレベルならふりがなを付ける'),
    ):
        A('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (a, b, c))
    A('</tbody></table></div>')

    A('<h3>覚える語を選り分ける（学習区分）<span class="up"> 第3版で新設</span></h3>')
    A('<p>現場の言葉は、全部を同じように覚えさせると かえって続きません。'
      '薬の商品名まで書けるようにする必要はないからです。そこで介護・記録・現場の'
      '<strong>%s語</strong>を、<strong>その語で何をするか</strong>で3つに分けました。</p>'
      % n(sum(d['study'].values())))
    A('<div class="tw"><table><thead><tr><th>区分</th><th class="num">語数</th>'
      '<th>何をする語か</th><th>画面での出方</th></tr></thead><tbody>')
    for a, k, c, e in (
        ('覚える', '覚える', '自分で言う・自分で書く', 'カードにも練習問題にも出る'),
        ('意味が分かる', '意味が分かる', '読めればよい。自分では書かない',
         '出るが「覚えた」の分母に入れない'),
        ('参考', '参考', '出てきたら引く（薬の商品名など）', '<b>出さない</b>'),
    ):
        A('<tr><td><b>%s</b></td><td class="num">%s</td><td>%s</td><td>%s</td></tr>'
          % (a, n(d['study'][k]), c, e))
    A('</tbody></table></div>')
    A('<div class="note priv"><p><b>後からいつでも変えられます。</b>'
      'この区分は <code>tools/学習区分.csv</code> という'
      '<b>表計算で開ける1枚の表</b>にあります。「この語は覚えなくていい」と思ったら、'
      'その行の区分を書き換えて走らせ直すだけです。プログラムは触りません。'
      '書いた語が見つからない・区分の名前を間違えた・同じ語を2回書いた、の3つは'
      '<b>その場で止まって教えます</b>。</p></div>')

    A('<h3>聴解（JLPT聴解の形式に対応）</h3>')
    A('<div class="tw"><table><thead><tr><th>パート</th><th>レベル</th>'
      '<th class="num">問数</th></tr></thead><tbody>')
    for p in d['ch']:
        A('<tr><td>%s　%s</td><td>%s</td><td class="num">%d</td></tr>'
          % (p['no'].replace('PART ', ''), p['title'], p['level'], len(p['items'])))
    A('<tr><td><b>合計</b></td><td></td><td class="num"><b>%d</b></td></tr>' % d['choukai'])
    A('</tbody></table></div>')
    A('<p>音声は<strong>端末の読み上げ機能</strong>（Web Speech API）が発音します。'
      '音声ファイルを持たないので、容量も通信量も増えません。'
      '速さは0.7／0.85／1.0／1.15の4段階で、選んだ速さは次回も覚えています。'
      '数字は「二百二号室」のようにかなで読みやすい形で書き、画面には「202号室」と'
      '表示する二重構造にしてあります。</p>')

    A('<h3>読解の内訳</h3>')
    A('<div class="tw"><table><thead><tr><th>形式</th><th class="num">本数</th>'
      '<th>レベル</th><th class="num">本数</th></tr></thead><tbody>')
    ts = d['read_type'].most_common()
    ls = [(k, d['read_lv'][k]) for k in ['N5', 'N4', 'N3', 'N2'] if d['read_lv'][k]]
    for i in range(max(len(ts), len(ls))):
        a = ('<td>%s</td><td class="num">%d</td>' % ts[i]) if i < len(ts) \
            else '<td></td><td class="num"></td>'
        b = ('<td>%s</td><td class="num">%d</td>' % ls[i]) if i < len(ls) \
            else '<td></td><td class="num"></td>'
        A('<tr>%s%s</tr>' % (a, b))
    A('<tr><td><b>合計</b></td><td class="num"><b>%d</b></td><td>設問</td>'
      '<td class="num"><b>%d</b></td></tr>'
      % (d['read']['passages'], d['read']['questions']))
    A('</tbody></table></div>')
    A('<p>一覧の上に<strong>おすすめボタン</strong>があります。'
      '「🏥 現場で読む」を押すと介護の現場のものだけ、'
      '「📝 試験の練習」を押すと試験形式のものだけが並びます。'
      '職員の方が「あなたはこちらを」と指示できるようにするためです。</p>')

    A('<h3>手書き検索</h3>')
    A('<p>読めない漢字を枠に指で書くと、候補が出ます。'
      '<strong>覚えるための練習ではなく、その場で調べるための道具</strong>です。'
      '書き順が違っても見つかります。</p>')
    A('<div class="tw"><table><thead><tr><th>項目</th><th>仕様</th></tr></thead><tbody>')
    A('<tr><td>収録</td><td>漢字 <b>%s字</b>・部首 287。学習用の%s字よりはるかに広く、'
      '記録や書類に出てくる字をほぼ拾えます</td></tr>' % (n(d['tegaki']), n(d['kanji'])))
    A('<tr><td>出るもの</td><td>読み・意味・画数・部首・成り立ち</td></tr>')
    A('<tr><td>認識のしかた</td><td><b>オフライン</b>＝端末の中だけで照合（通信しません）／'
      '<b>オンライン</b>＝Google の手書き入力に問い合わせ（精度が上がります）／'
      '<b>自動</b>＝まずオンライン、だめならオフライン</td></tr>')
    A('<tr><td>データ</td><td><code>tegaki-data.json</code> %s。'
      '<b>手書き検索を開いたときだけ</b>読み込みます</td></tr>' % size(d['tegakikb']))
    A('</tbody></table></div>')
    A('<div class="note"><p><b>通信について正直に：</b>「オンライン」認識を選ぶと、'
      '<b>書いた線の座標が Google に送信されます</b>。文字そのものは送られませんが、'
      '外部に出るのはこのシステムでここだけです。気になる場合は'
      '「<b>オフライン</b>」を選べば、通信は一切発生しません。'
      '画面にもその旨が表示されます。</p></div>')

    A('<h3>学習記録のしくみ</h3>')
    A('<div class="tw"><table><thead><tr><th>項目</th><th>仕様</th></tr></thead><tbody>')
    A('<tr><td>保存場所</td><td>その端末のブラウザの中（<code>localStorage</code>）。'
      'サーバーには一切送りません</td></tr>')
    A('<tr><td>記録される状態</td><td>「覚えた（緑）」「要復習（赤）」。'
      '練習問題で間違えた語は自動で要復習に入ります</td></tr>')
    A('<tr><td>要復習の見かた</td><td><b>まちがえたところ</b>に7区分を横断して集まります。'
      '各画面でも絞り込めます</td></tr>')
    A('<tr><td>書き出し</td><td>① Excel用CSV（漢字%s＋言葉%sの一覧と状態）　'
      '② バックアップJSON（<b>%d系統</b>）</td></tr>'
      % (n(d['kanji']), n(d['vocab']), len(d['pkeys'])))
    A('<tr><td>ドライブへ保存<span class="up"> 追加</span></td>'
      '<td>スマホでは「共有」画面が出て、そこから<b>Google ドライブに直接保存</b>できます。'
      '外部の部品も鍵も使っていません（ブラウザの標準機能だけ）</td></tr>')
    A('<tr><td>読み込み</td><td>バックアップを選ぶと記録が戻ります（機種変更用）</td></tr>')
    A('</tbody></table></div>')
    if d['nokeys']:
        A('<div class="note"><p><b>バックアップに入らない記録が %d種あります。</b>'
          '漢字・語彙・文型・読解・聴解の記録は入りますが、'
          '下のものは<b>機種を変えると消えます</b>。'
          '教材そのものは消えませんが、「どこまで進んだか」は'
          '職員の方の記録表で押さえてください。</p></div>' % len(d['nokeys']))
        A('<div class="tw"><table><thead><tr><th>保存キー</th>'
          '<th>消えると何が失われるか</th></tr></thead><tbody>')
        for k, v in d['nokeys']:
            A('<tr><td><code>%s</code></td><td>%s</td></tr>' % (k, v))
        A('</tbody></table></div>')

    A('<h3>合言葉と公開範囲</h3>')
    A('<p>入口で合言葉を1回入れると、全部の画面が開きます。'
      '検索エンジンには載らない設定（<code>noindex</code>）にしてあります。</p>')
    A('<div class="note"><p><b>正直にお伝えする限界：</b>'
      'この合言葉は「カーテン」であって「鍵」ではありません。'
      '置き場所（GitHub）は<b>公開</b>で、技術のある人がファイルの中を見れば'
      '仕組みは分かります。誰が見ても困らない学習教材だからこの方式で十分ですが、'
      '<b>個人情報を入れる用途には使えません</b>。'
      'そのため<b>答えの入った紙 %d本は、置き場所から外して'
      'Google ドライブに移しました</b>。'
      '戻っていないかを <code>tools/check-answers-out.py</code> が毎回確かめます。</p></div>'
      % d['out'])
    A('</section>')

    # ══ 04 ═════════════════════════════════════════════════
    A('<section><h2><span class="num">04</span>現場の資料をどう教材にしたか</h2>')
    A('<p class="sub">このシステムが市販の教材と違う ただ一つの理由</p>')
    A('<p>施設から、実際の<strong>介護記録の語彙リスト（Excel 4冊・のべ2,327行）</strong>と'
      '<strong>通知システムのお知らせ（98件）</strong>、'
      'それに<strong>申し送りの直し 299件</strong>を提供いただきました。'
      'これを教材に変える作業が、このシステムの中心です。</p>')
    A('<div class="tw"><table><thead><tr><th>いただいた資料</th><th>どう使ったか</th>'
      '<th class="num">成果</th></tr></thead><tbody>')
    for a, b, c in (
        ('介護記録の語彙リスト', '重複を除き、列ずれ307行を修復して語彙に取り込み。'
         '新レベル「記録」を新設', '%s語' % n(d['vocab_lv']['記録'])),
        ('同（例文欄）', '活用形の語は「例文・文中の形・その読み」の3点形式で登録', '637文'),
        ('記録の言い回しの分析', '例文637件を機械的に分析し、記録特有の文型を特定',
         '%d文型' % d['gram_lv']['記録']),
        ('記録に出る漢字', '語彙リストの漢字を拾い、既存のレベルに無い字を新レベル「記録」に',
         '%d字' % d['kanji_lv']['記録']),
        ('通知システムのお知らせ', '形式と場面のみ参考にし、本文は書き下ろして読解教材に',
         '8本16問'),
        ('申し送りの直し 299件', '<b>原文は取り込んでいません。</b>'
         'どの種類の直しが多いかだけを数え、教える順の参考に', '分類のみ'),
        ('介護記録の原文', '<strong>使用していません</strong>'
         '（利用者名・健康情報を含むため）', '—'),
    ):
        A('<tr><td>%s</td><td>%s</td><td class="num">%s</td></tr>' % (a, b, c))
    A('</tbody></table></div>')
    A('<div class="note priv"><p><b>個人情報の扱い：</b>'
      '提供された資料には、実在の利用者名・職員名・業者名・施設名・健康情報が'
      '含まれていました。記録の原文シート（2,151行＋3,882行）は'
      '<b>一切取り込んでいません</b>。'
      '語彙の例文に紛れていた実名は架空名に置き換え、'
      '<b>実在の病院名が例文3本に入っていたのも見つけて直しました</b>。'
      '部屋番号・和暦日付の混入は機械的に検査して0件を確認しています。'
      '公開されているデータに、施設の個人情報は含まれません。</p></div>')

    A('<h3>記録の日本語は、話し言葉と違う</h3>')
    A('<p>記録には、教科書に出てこない書き方があります。'
      '文型の「記録」%d項目は、その対応表として作りました。</p>' % d['gram_lv']['記録'])
    A('<div class="tw"><table><thead><tr><th>記録の書き方</th>'
      '<th>話すときの言い方</th></tr></thead><tbody>')
    for a, b in (('発赤<b>あり</b>／熱<b>なし</b>', '発赤が<b>あります</b>／熱は<b>ありません</b>'),
                 ('むせ込みが<b>見られた</b>', 'むせて<b>いました</b>'),
                 ('良眠された<b>とのこと</b>', 'よく眠れた<b>と聞きました</b>'),
                 ('二人介助<b>にて</b>移乗', '二人<b>で</b>手伝って移りました'),
                 ('吸引<b>実施</b>', '吸引を<b>しました</b>')):
        A('<tr><td>%s</td><td>%s</td></tr>' % (a, b))
    A('</tbody></table></div>')
    A('<p>ただし、<strong>現場の書き方をそのまま手本にはしていません</strong>。'
      '「〜あり」「〜にて」のような名詞止めは記録の正式な書式ですが、'
      '助詞の脱落（更衣行う）や誤字は単なる誤りです。'
      '前者だけを教え、後者は扱わない——という線引きをしてあります。'
      'この区別は、施設側からのご指摘で明確になりました。</p>')
    A('</section>')

    # ══ 05 ═════════════════════════════════════════════════
    A('<section><h2><span class="num">05</span>使い方</h2>')
    A('<p class="sub">実習生と、施設側それぞれの動き</p>')

    A('<h3>実習生がすること</h3>')
    A('<ol class="steps">')
    A('<li><b>Chromeで開いて、合言葉を入れる</b>1回入れれば、次からは省略されます。'
      'ホーム画面に追加すればアプリのように使えます。</li>')
    A('<li><b>自分のコースを開く</b>来たばかりなら<b>新人コース</b>、'
      '受験日が決まったら<b>100日コース</b>、N3に受かったら<b>N2コース</b>。'
      '「今週ひらくもの」を押すと、<b>その週の分だけ</b>が出た状態で開きます。</li>')
    A('<li><b>「✓ 覚えた」「△ 要復習」を押す</b>これがいちばん大事です。'
      '押さないと、試験前に「どこが弱いか」が分かりません。<b>迷ったら △</b>。</li>')
    A('<li><b>翌日は「まちがえたところ」から始める</b>'
      '新しいものを足すより、まちがえた分をもう一度やるほうが点が上がります。</li>')
    A('<li><b>月に一度、バックアップを保存する</b>'
      '記録は端末の中だけなので、機種を変えると消えます。'
      '「学習状況」→「💾 バックアップを保存」→「ドライブに保存」。</li>')
    A('</ol>')
    A('<div class="note"><p><b>配るときに必ず添える一文：</b>'
      '「<b>Chromeで開いてください。LINEの中で開くと、聴解の音が出ません。</b>」'
      '——AndroidでLINEやメールのリンクから開くと、アプリの中の簡易ブラウザが立ち上がり、'
      '読み上げ機能が一切使えません。実際にこれで音が出ない事例がありました。'
      'いまはアプリ側で検出して案内を出しますが、'
      '最初から Chrome で開いてもらうのが確実です。</p></div>')

    A('<h3>入口メニューの全体（画面に出ている順）</h3>')
    A('<div class="tw"><table><thead><tr><th>まとまり</th><th class="num">ボタン</th>'
      '<th>中身</th></tr></thead><tbody>')
    for h, names in d['menu']:
        A('<tr><td><b>%s</b></td><td class="num">%d</td><td>%s</td></tr>'
          % (h, len(names), '／'.join(names) if names else '—'))
    A('<tr><td><b>合計</b></td><td class="num"><b>%d</b></td><td>%d のまとまり</td></tr>'
      % (d['buttons'], len(d['menu'])))
    A('</tbody></table></div>')
    A('<p>この表は<strong><code>index.html</code> を読んで作っています</strong>。'
      'だから画面とこの表の順番がずれません。'
      'ボタンを足して説明を書き忘れると、資料を作る道具が止まります。</p>')

    A('<h3>施設側がすること</h3>')
    A('<div class="tw"><table><thead><tr><th>やりたいこと</th><th>やり方</th>'
      '</tr></thead><tbody>')
    for a, b in (
        ('入ったばかりの人の力を見る',
         '<b>新人コースの第1週にN4の判定テストがあります。</b>'
         'JLPT N4合格者とJFT-Basic（A2）合格者の両方が対象で、'
         '同じ基準で判定し、<b>漢字と土台のどちらが足りないか</b>を分けて見られます'),
        ('施設の言葉を足す',
         '日本語のリストを渡していただければ、ふりがな・インドネシア語訳・例文まで作って'
         '組み込みます。既存の語との重複は自動で除きます'),
        ('覚えなくていい語を外す',
         '<code>tools/学習区分.csv</code> の区分を「参考」に書き換えるだけです'),
        ('読解の文章を足す',
         '実際の掲示物・お知らせを見せていただくと、それに合わせた文章を作ります'
         '（本文は書き下ろし、個人情報は除去）'),
        ('進み具合を見る',
         '実習生の端末で「学習状況」を開く、またはCSVを書き出してもらう'),
        ('次の週へ進める',
         'コースの画面に<b>「◀ 前の週／次の週 ▶」</b>があります。'
         '先の週を見ても、記録は変わりません'),
        ('新しくなったのに変わらない', '入口の「🔄 最新にする」を押す'),
        ('機種変更',
         '古い端末で「バックアップを保存」→ 新しい端末で「読み込む」。'
         '<b>コースの週の印は入りません</b>（前述）'),
        ('答えや聴解の台本を使う',
         '<b>職員だけの入口</b>にあります。実習生の画面からはリンクしていません。'
         '答えの入った紙%d本はドライブにあります' % d['out']),
        ('外に渡す',
         'URLと合言葉を伝える（＝実質公開）／PDFを印刷する。渡す条件は先に決めてください'),
    ):
        A('<tr><td>%s</td><td>%s</td></tr>' % (a, b))
    A('</tbody></table></div>')
    A('</section>')

    # ══ 06 ═════════════════════════════════════════════════
    A('<section><h2><span class="num">06</span>品質をどう確かめているか</h2>')
    A('<p class="sub">「たぶん動く」で終わらせないための手順</p>')
    A('<p>直すたびに<strong>%d本の検査</strong>を走らせます。'
      '全部で1秒ほどです。そのあと<strong>本物のブラウザを自動で動かして</strong>'
      '画面を確かめます。</p>' % len(d['checks']))
    A('<div class="tw"><table><thead><tr><th>検査</th><th>何を見るか</th>'
      '</tr></thead><tbody>')
    what = {
        'check-answers-out.py': '答えの入った紙%d本が置き場所に戻っていないか、'
                                '画面からリンクしていないか' % d['out'],
        'check-bunshou.py': '読解のふりがな記法・選択肢4つ・正解番号・語注・英字混入',
        'check-n2.py': 'N2の漢字・語彙・文型・読解・聴解のつながり',
        'check-numbers.py': '<b>画面に出る分母と、実データの数が合っているか</b>'
                            '（合わないと「覚えた率」が狂います）',
        'check-script.py': '聴解の台本・読み上げ用のかな・数字の二重表記',
        'check-secrets.py': '実名・施設名・業者名・部屋番号・和暦日付・鍵つきURLの混入',
        'check-staff-split.py': '職員だけの中身が、実習生の画面から行けてしまわないか',
        'check-star.py': '例文の見出し語が文中に1回だけ出るか・読みがかなだけか・重複',
        'check-ui.mjs': '本物のブラウザで画面を操作して、出るものが出るか',
        'check-version.py': '各画面の版と <code>version.json</code> がそろっているか',
    }
    for c in d['checks']:
        A('<tr><td><code>%s</code></td><td>%s</td></tr>' % (c, what.get(c, '—')))
    A('</tbody></table></div>')
    A('<div class="note"><p><b>検査は「作ってから足す」のではなく、'
      '「見つけた間違いごとに足す」。</b>'
      '新しい検査を入れたら、<b>わざとその間違いを入れて、止まることを確かめてから</b>'
      '元に戻しています。止まらない検査は、無いのと同じだからです。'
      '実際に見つかったもの：画面の分母が5週間ずれていた／'
      '同じ文型を2回入れていた／実在の病院名が例文3本に入っていた／'
      '商談の文字起こしが5か月間 置き場所に入ったままだった'
      '（検査が <code>.txt</code> を見ていなかった）。</p></div>')

    A('<h3>データの出典</h3>')
    A('<div class="tw"><table><thead><tr><th>データ</th><th>用途</th>'
      '<th>ライセンス</th></tr></thead><tbody>')
    seen = set()
    for s in d['sources']:
        if s['name'] in seen:
            continue
        seen.add(s['name'])
        A('<tr><td>%s</td><td>%s</td><td>%s</td></tr>'
          % (s['name'], s.get('use', '—'), s.get('license', '—')))
    A('<tr><td>『介護の日本語』（日本介護福祉士会）</td><td>場面の参考・'
      '語の取りこぼしの点検（<b>本文の転載なし</b>）</td><td>—</td></tr>')
    A('<tr><td>例文・読解・聴解・介護語彙・訳</td>'
      '<td>本システムのために書き下ろし</td><td>—</td></tr>')
    A('</tbody></table></div>')
    A('<p>読解・聴解の文章は<strong>すべてオリジナル</strong>です。'
      'JLPT過去問は形式の参考としてのみ使い、<strong>本文の転載はしていません</strong>。'
      '市販教材の語彙リストも<strong>「抜けがないか」の点検にだけ</strong>使い、'
      '中身を写してはいません。'
      'N5漢字は、体の部位など基本の23字を編集判断でN4からN5へ移しており、'
      'その理由と対象字を画面に明記しています。</p>')
    A('</section>')

    # ══ 07 ═════════════════════════════════════════════════
    A('<section><h2><span class="num">07</span>いま足りないもの</h2>')
    A('<p class="sub">できないことを、できるふりをしない</p>')
    A('<div class="tw"><table><thead><tr><th>足りないこと</th><th>いまの状況</th>'
      '</tr></thead><tbody>')
    for a, b in (
        ('管理者が全員の進み具合を1か所で見る',
         'できません。記録は各自の端末の中だけです。'
         '見るには端末を見せてもらうか、CSVを書き出してもらいます'),
        ('一人ひとりのアカウント', 'ありません。合言葉1つを全員で共有します'),
        ('練習問題の成績の履歴',
         'その場限りで残りません。「先月60点→今月85点」が見えません'),
        ('設問タイプ別の正解率',
         '<b>読解の設問に「どの型か」の印が付いていません。</b>'
         'そのため「読解が弱い」の中身（語彙不足か／指示語か／時間切れか）を'
         '切り分けられません。印を付けるのが先の作業です'),
        ('コース・模試・診断テストの記録のバックアップ',
         '<b>入りません</b>（%d種）。機種変更では引き継げません。'
         '仕様の03に、何が消えるかの一覧を載せています' % len(d['nokeys'])),
        ('聴解の音声の質',
         '端末の読み上げ機能しだいです。日本語音声が入っていない端末では鳴りません'),
        ('記録の書き方そのものの練習',
         '<b>持ち主の判断で後回し</b>にしています。設計だけ仕様書に残してあります'),
        ('反対語', 'データがありません。足すには画面の作り直しも要ります'),
        ('JLPTレベルの正確さ',
         'JLPTは2010年以降、公式の漢字リストを公表していません。'
         '本システムの区分は<b>目安</b>です'),
        ('合言葉の強さ',
         '「カーテン」です。置き場所は公開なので、'
         '<b>個人情報を入れる用途には使えません</b>'),
        ('30週・66週を通して動かした確認',
         '<b>やりました</b>が、手ざわりの確認（重すぎる週がないか）は'
         '持ち主が実機で進めています'),
    ):
        A('<tr><td>%s</td><td>%s</td></tr>' % (a, b))
    A('</tbody></table></div>')
    A('<div class="note"><p><b>枝が増えすぎることについて正直に：</b>'
      '画面は%d枚、ボタンは%d個になりました。'
      '増やすほど「どこを見ればいいか分からない」が起きます。'
      'だから第3版では、<b>増やすより decide（決め切る）</b>に寄せました'
      '——コースを開けばその日の分だけが出る、'
      'まちがえたところを開けば復習すべきものだけが出る。'
      '<b>メニューの数ではなく、「毎朝どこを開くか」が1つに決まっているか</b>で'
      'このシステムの良し悪しを見てください。</p></div>'
      % (d['npages'], d['buttons']))
    A('</section>')

    # ══ 08 ═════════════════════════════════════════════════
    A('<section><h2><span class="num">08</span>これからの予定</h2>')
    A('<p class="sub">在籍者の受験時期から逆算した順序。締め切りのあるものから</p>')
    A('<div class="plan">')
    for when, sub, who, what in (
        ('2026年 12月', 'いますぐ', '新規実習生・2名 — 12月7日 来日',
         '<b>新人コース30週の開始。</b>第1週のN4判定テストで、'
         '漢字が足りないのか土台が足りないのかを分けて見ます。'
         'そのうえで、重すぎる週（第5・13・17・21週）の量を実際の様子で調整します。'
         '教材はもう揃っているので、ここからは<b>運用の確認</b>だけです。'),
        ('2026年 12月', '受験', 'N3再受験者・1名 — 12月受験',
         '<b>100日コースと模試%d回で仕上げ。</b>'
         '読解が不得意なので「まちがえたところ」を毎日の起点にします。'
         '設問タイプ別の正解率はまだ見えないので、そこは職員の方の目で補います。' % d['moshi']),
        ('2027年 前半', '', 'N3合格者 — 2027年12月のN2',
         '<b>N2コース66週。</b>漢字・語彙・文型・読解・聴解はもう入っています'
         '（漢字%s字・語彙%s語・文型%s）。'
         '残っているのは紙の教材の割りつけと、進み具合の見かたです。'
         '<b>実務者研修（450時間）は日本語で行われる</b>ため、'
         'N2の読む力はその準備にもなります。'
         % (n(d['kanji_lv']['N2']), n(d['vocab_lv']['N2']), n(d['gram_lv']['N2']))),
        ('その先', '', '介護福祉士を目指す方',
         '<b>国家試験むけの専門用語と事例問題。</b>'
         '受験には実務経験3年＋実務者研修が必要で、まだ先です。'
         'N2の一般語彙より<b>介護保険・尊厳の保持・医療的ケアなどの専門用語</b>と、'
         '長い場面設定を読む練習のほうが直結します。'),
    ):
        A('<div class="row"><div class="when"><b>%s</b>%s</div>'
          '<div class="what"><span class="who">%s</span>%s</div></div>'
          % (when, sub, who, what))
    A('</div>')

    A('<h3>そのほか、頼まれれば作れるもの</h3>')
    A('<div class="tw"><table><thead><tr><th>やること</th><th>注意点</th>'
      '<th>目安</th></tr></thead><tbody>')
    for a, b, c in (
        ('読解の設問に型の印を付ける',
         '「読解が弱い」の中身が切り分けられるようになります。'
         'いちばん効く割に小さい作業です', '半日'),
        ('練習問題の成績を残す',
         '「上がっている」が見えることが、続ける一番の力になります', '数時間'),
        ('コースの週の印もバックアップに入れる',
         '機種変更で「どこまで進んだか」が消えなくなります', '数時間'),
        ('記録の書き方システム',
         '正しい書き方だけを教え、誤りは選択肢の中だけに出す設計。'
         '<b>持ち主の判断で後回し中</b>', '1〜2日'),
        ('反対語', 'データ作りと画面の作り直しの両方が要ります', '要検討'),
        ('ベトナム語版／ミャンマー語版',
         '1言語あたり約1万件の翻訳。ミャンマー語は母語話者の確認を推奨します', '要検討'),
        ('管理者画面（誰がどこまで進んだか）',
         '記録を端末の外に置く必要があり、サーバーと個人情報の扱いが発生します。'
         '<b>外部に売るなら必須</b>です', '要検討'),
    ):
        A('<tr><td>%s</td><td>%s</td><td><span class="stage">%s</span></td></tr>' % (a, b, c))
    A('</tbody></table></div>')
    A('<div class="note"><p><b>急ぐ必要はありません。</b>'
      'このシステムは運用費¥0で、放っておいても壊れません。'
      '使ってみて「どこが分かりにくいか」「どの言葉が足りないか」が出てきてから、'
      'そこを直すのが一番効果的です。'
      '第2版から第3版までに入ったものも、そのほとんどが'
      '<b>実際に使った方からのご指摘</b>から生まれました'
      '——読みのひらがなが見えにくい、熟語の意味が見られない、'
      '次の週へ飛べない、どれもご指摘があって初めて分かったものです。</p></div>')
    A('</section>')

    A('<footer>')
    A('<p>この資料は %s 時点の内容です（第1版 2026-08-10 ／ 第2版 %s ／ %s %s）。'
      '数字はすべて <code>tools/souran.py</code> がそのときのデータを数えて書いています。'
      '詳細は <code>SPEC.md</code>（仕様書）と <code>MANUAL.md</code>（使用説明書）、'
      'および「はじめて使う人へ」「このシステムは何か」をご覧ください。</p>'
      % (ASOF, V2['date'], VER, ASOF))
    A('<p>© 2026 owlwindkaze　施設内の学習用システムです。</p>')
    A('</footer></div></body></html>')
    return '\n'.join(o) + '\n'


# ══════════════════════════════════════════════════════════════════
#  Markdown（PDF用）
# ══════════════════════════════════════════════════════════════════

def md(d):
    """HTMLから紙用の Markdown を作る。中身を二重に書かないため、
    見出しと表だけを抜き出す簡単な変換にしてある。"""
    s = html(d)
    s = re.sub(r'(?s)<style>.*?</style>', '', s)
    s = re.sub(r'(?s)<head>.*?</head>', '', s)
    o = []
    A = o.append
    A('# 介護の日本語 学習システム 総覧 %s' % VER)
    A('')
    A('**%s 時点。**数字はすべて `tools/souran.py` がそのときのデータを'
      '数えて書いています。手で書いた数はありません。' % ASOF)
    A('')

    def txt(x):
        x = re.sub(r'<rt>.*?</rt>', '', x)
        x = re.sub(r'<br\s*/?>', ' ', x)
        x = re.sub(r'<b>|</b>|<strong>|</strong>', '**', x)
        x = re.sub(r'<code>|</code>', '`', x)
        x = re.sub(r'<[^>]+>', '', x)
        return re.sub(r'\s+', ' ', x).replace('****', '').strip()

    # figs
    figs = re.findall(r'(?s)<div class="fig[^"]*">(.*?)</div>', s)
    if figs:
        A('| | |')
        A('|---|---|')
        for f in figs:
            nn = txt(re.search(r'class="n">(.*?)</span>', f, re.S).group(1))
            ll = txt(re.search(r'class="l">(.*?)</span>', f, re.S).group(1))
            A('| %s | **%s** |' % (ll, nn))
        A('')

    for sec in re.findall(r'(?s)<section>(.*?)</section>', s):
        h2 = re.search(r'(?s)<h2>(.*?)</h2>', sec)
        if h2:
            A('')
            A('---')
            A('')
            A('## %s' % re.sub(r'^(\d\d)', r'\1　', txt(h2.group(1))))
            A('')
        sub = re.search(r'(?s)<p class="sub">(.*?)</p>', sec)
        if sub:
            A('*%s*' % txt(sub.group(1)))
            A('')
        body = sec[h2.end():] if h2 else sec
        for m in re.finditer(r'(?s)<h3>(.*?)</h3>|<p>(.*?)</p>|<table>(.*?)</table>'
                             r'|<div class="note([^"]*)">(.*?)</div>'
                             r'|<article class="card[^"]*">(.*?)</article>'
                             r'|<ol class="steps">(.*?)</ol>'
                             r'|<div class="row">(.*?)</div>\s*</div>', body):
            if m.group(1) is not None:
                A('### %s' % txt(m.group(1)))
                A('')
            elif m.group(2) is not None:
                t = txt(m.group(2))
                if t:
                    A(t)
                    A('')
            elif m.group(3) is not None:
                tb = m.group(3)
                hd = [txt(x) for x in re.findall(r'(?s)<th[^>]*>(.*?)</th>', tb)]
                if hd:
                    A('| ' + ' | '.join(hd) + ' |')
                    A('|' + '---|' * len(hd))
                for tr in re.findall(r'(?s)<tr>(.*?)</tr>', tb):
                    cells = [txt(x) for x in re.findall(r'(?s)<td[^>]*>(.*?)</td>', tr)]
                    if cells:
                        A('| ' + ' | '.join(cells) + ' |')
                A('')
            elif m.group(5) is not None:
                A('> %s' % txt(m.group(5)))
                A('')
            elif m.group(6) is not None:
                c = m.group(6)
                h4 = re.search(r'(?s)<h4>(.*?)</h4>', c)
                A('**%s**' % txt(h4.group(1)) if h4 else '')
                A('')
                pp = re.search(r'(?s)<p>(.*?)</p>', c)
                if pp:
                    A(txt(pp.group(1)))
                for li in re.findall(r'(?s)<li>(.*?)</li>', c):
                    A('- %s' % txt(li))
                A('')
            elif m.group(7) is not None:
                for i, li in enumerate(re.findall(r'(?s)<li>(.*?)</li>', m.group(7)), 1):
                    A('%d. %s' % (i, txt(li)))
                A('')
            elif m.group(8) is not None:
                r0 = m.group(8)
                w = re.search(r'(?s)class="when">(.*?)</div>', r0)
                h = re.search(r'(?s)class="what">(.*?)$', r0)
                if w and h:
                    A('**%s** — %s' % (txt(w.group(1)), txt(h.group(1))))
                    A('')
    A('')
    A('---')
    A('')
    A('*第1版 2026-08-10 ／ 第2版 %s ／ %s %s。'
      'この紙は `tools/souran.py` が作っています。*' % (V2['date'], VER, ASOF))
    return '\n'.join(o) + '\n'


def main():
    d = gather()
    if '--md' in sys.argv:
        p = sys.argv[sys.argv.index('--md') + 1]
        t = md(d)
        io.open(p, 'w', encoding='utf-8').write(t)
        print('書きました: %s（%d文字）' % (p, len(t)))
    elif '--html' in sys.argv:
        p = sys.argv[sys.argv.index('--html') + 1]
        t = html(d)
        io.open(p, 'w', encoding='utf-8').write(t)
        print('書きました: %s（%d文字）' % (p, len(t)))
    else:
        sys.stdout.write(html(d))
    return 0


if __name__ == '__main__':
    sys.exit(main())
