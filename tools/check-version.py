# -*- coding: utf-8 -*-
"""版（バージョン）が 全部の ファイルで そろっているかを 点検する。

  見ないもの：`tools/kaigo/build.py` の VER。これは **紙を作った日**で、
  サイトの版とは 意味が ちがう。そろえようとすると、中身が 変わっていない
  PDF 12本を 作り直すことに なり、履歴（.git）が むだに ふくらむ。

    python3 tools/check-version.py

なぜ作ったか
  版を上げるとき、ファイルが 9つ あるので 必ず どこかが 残る。
  2度 やった。1度目は bunpo/index.html の VERSION が 2026-09-04 のままで、
  文型の画面に「古い版が残っています」の帯が 出っぱなしに なっていた。
  2度目は 一括置換の書き方を まちがえて（'a;' を 'b;' に、と 書いたが
  実際の文字は "a';" だった）3つのファイルが 空振りした。**目では 気づけない。**

  ここが そろっていないと、学習者の画面に 黄色い帯が 出るか、
  毎回 むだに 1回 読み直す。
"""
import io, json, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
WANT = json.load(io.open(R + 'version.json', encoding='utf-8'))['version']

# (ファイル, 探す形)
SPOTS = [
    ('index.html', r"var PAGE_VER = '([^']+)'"),
    ('fukushu/index.html', r"var PAGE_VER = '([^']+)'"),
    ('moshi/index.html', r"var PAGE_VER = '([^']+)'"),
    ('n2/index.html', r"var PAGE_VER = '([^']+)'"),
    ('shinjin/index.html', r"var PAGE_VER = '([^']+)'"),
    ('kaigo/index.html', r"var PAGE_VER = '([^']+)'"),
    ('staff/index.html', r"var PAGE_VER = '([^']+)'"),
    ('n3.html', r"var PAGE_VER = '([^']+)'"),
    ('bunpo/index.html', r"const VERSION = '([^']+)'"),
    ('dokkai/index.html', r"const VERSION = '([^']+)'"),
    ('kanji.html', r"const VERSION = '([^']+)'"),
    ('bunpo/grammar.json', r'"app_version": "([^"]+)"'),
]

bad = []
print('■ version.json の 版：%s' % WANT)
for f, pat in SPOTS:
    s = io.open(R + f, encoding='utf-8').read()
    m = re.search(pat, s)
    got = m.group(1) if m else None
    ok = got == WANT
    print('  %-24s %-14s %s' % (f, got or '（見つからない）', 'OK' if ok else '←ちがう'))
    if not ok:
        bad.append('%s：%s（version.json は %s）' % (f, got or '見つからない', WANT))

# 画面に 版を 書いてある所（footer など）も 見る
for f in ['kaigo/index.html', 'staff/index.html']:
    s = io.open(R + f, encoding='utf-8').read()
    for m in re.finditer(r'>(\d{4}-\d{2}-\d{2}[a-z]?)<', s):
        if m.group(1) != WANT:
            bad.append('%s：画面に 書いてある版 %s が ちがう' % (f, m.group(1)))

print()
print('=' * 62)
print('そろっていない所:', len(bad))
for b in bad: print('  -', b)
print('=' * 62)
sys.exit(1 if bad else 0)
