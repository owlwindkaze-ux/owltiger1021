#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**N2の紙のパックの画面版**（`moshi/n2u-*.json`）を点検する（SPEC 2.6-z54）。

紙と画面で**中身がずれる**のがいちばん困る。紙は20問、画面も20問でなければ
「画面でやったから紙はやらなくていい」が成り立たない。

見るところ：
  ・1単元 **ちょうど20問**（言語知識10・読解5・聴解5）
  ・答えの番号が 選択肢の範囲に入っているか
  ・選択肢が 2つ以上あるか／空の選択肢が ないか
  ・聴解の問に **台本（script）**が あるか（無いと 読み上げられない）
  ・`moshi/index.html` の sets と ファイルの数が 合っているか
"""
import glob
import io
import json
import os
import re
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
ng = []


def bad(m):
    ng.append(m)
    print('  ×', m)


files = sorted(glob.glob(R + 'moshi/n2u-*.json'),
               key=lambda p: int(re.search(r'n2u-(\d+)', p).group(1)))
print('■ 紙のパックの画面版 %d本' % len(files))
for f in files:
    nm = os.path.basename(f)
    d = json.load(io.open(f, encoding='utf-8'))
    tot = {'言語知識': 0, '読解': 0, '聴解': 0}
    for key in d['order']:
        s = d['sections'][key]
        g = s.get('group') or ('聴解' if key.startswith('聴解')
                               else '読解' if key in ('問題10', '問題11', '問題12',
                                                      '問題13', '問題14')
                               else '言語知識')
        qs = []
        for x in s.get('items', []):
            qs.append((x.get('choices') or x.get('opts'),
                       x.get('answer') if 'answer' in x else x.get('ans'), x))
        for r in s.get('read', []):
            for qi in r['qi']:
                q = r['passage']['questions'][qi]
                qs.append((q['choices'], q['answer'], q))
        if not qs:
            bad('%s %s に 問が ありません' % (nm, key))
        for ch, a, x in qs:
            tot[g] += 1
            if not ch or len(ch) < 2:
                bad('%s %s 選択肢が 少なすぎます' % (nm, key))
            elif any(not str(c).strip() for c in ch):
                bad('%s %s 空の選択肢が あります' % (nm, key))
            elif not isinstance(a, int) or not (0 <= a < len(ch)):
                bad('%s %s 答えの番号が 範囲の外（%r／選択肢%d）' % (nm, key, a, len(ch)))
            if key.startswith('聴解') and not (x.get('script') or '').strip():
                bad('%s %s 聴解に 台本が ありません' % (nm, key))
    n = sum(tot.values())
    ok = (n == 20 and tot['言語知識'] == 10 and tot['読解'] == 5 and tot['聴解'] == 5)
    print('  %-12s 言語知識%2d 読解%2d 聴解%2d ／ 計%2d  %s'
          % (nm, tot['言語知識'], tot['読解'], tot['聴解'], n, 'OK' if ok else '×'))
    if not ok:
        bad('%s 問の数が 合いません（紙は 言語知識10・読解5・聴解5の ちょうど20問）' % nm)
    c = d.get('counts', {})
    if c.get('合計') != n:
        bad('%s counts の合計 %s と 実際 %d が 合いません' % (nm, c.get('合計'), n))

s = io.open(R + 'moshi/index.html', encoding='utf-8').read()
m = re.search(r"n2u:\s*\{[^}]*?sets:\s*\[([^\]]*)\]", s, re.S)
if not m:
    bad('moshi/index.html に n2u の sets が ありません')
else:
    sets = [int(x) for x in re.findall(r'\d+', m.group(1))]
    have = [int(re.search(r'n2u-(\d+)', p).group(1)) for p in files]
    if sets != have:
        bad('画面の sets %s と ファイル %s が 合いません' % (sets, have))

print()
print('=' * 54)
print('おかしいところ: %d件' % len(ng))
print('=' * 54)
sys.exit(1 if ng else 0)
