#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**どの画面からも 戻れるか**を点検する（SPEC 2.6-z56）。

持ち主から「**各画面からの戻るボタンがない**」。調べたら、
「☰ メニュー」は どの画面にもあったが **いちばん上にあって、
下へスクロールすると 画面から消えていた**。固定していたのは `moshi/` だけ。
文型一覧は **66,901px**（スマホで85画面ぶん）あり、
**下まで行くと 戻る手段が 無くなっていた。**

`back.js` を入れて直したが、**画面を足したときに 入れ忘れる**のが
いちばん起きやすい。だから機械で見張る。

見るところ：
  ・入口以外の画面すべてに `back.js` が 入っているか
  ・道（`back.js` ／ `../back.js`）が フォルダの深さと 合っているか
  ・`back.js` が ちゃんと そこに あるか
"""
import glob
import io
import os
import re
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
ng = []

if not os.path.exists(R + 'back.js'):
    ng.append('back.js が ありません')

pages = sorted(set(glob.glob(R + '*.html') + glob.glob(R + '*/index.html')))
print('■ 戻るボタン')
for p in pages:
    rel = os.path.relpath(p, R)
    if rel == 'index.html':
        print('  %-22s —（入口そのもの）' % rel)
        continue
    s = io.open(p, encoding='utf-8').read()
    m = re.search(r'<script[^>]*src="((?:\.\./)?back\.js)"', s)
    want = '../back.js' if '/' in rel else 'back.js'
    if not m:
        print('  %-22s ✗ back.js が 入っていません' % rel)
        ng.append('%s に back.js が 入っていません' % rel)
    elif m.group(1) != want:
        print('  %-22s ✗ 道が ちがいます（%s → %s）' % (rel, m.group(1), want))
        ng.append('%s の back.js の道が ちがいます' % rel)
    else:
        print('  %-22s OK' % rel)

print()
print('=' * 54)
print('おかしいところ: %d件' % len(ng))
for x in ng:
    print('  -', x)
print('=' * 54)
sys.exit(1 if ng else 0)
