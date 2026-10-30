#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**文型の練習問題**（`bunpo/grammar-*.json` の `quiz`）を点検する（SPEC 2.6-z63）。

2026年10月12日に上げられた N3のファイルには、**答えにならない問題**が
2種類 入っていた。中を見るまで 誰も気づかなかった。

  ① 選択肢が **全部英語**（128問）
     1 while ~ / before ~ changes ← 正解
     2 not while ~ / before ~ changes      ← 正解に not を付けただけ
     3 a simple past event / 4 a direct command  ← 128問すべて同じ文字列

  ② **答えが問題文の中に そのまま書いてある**（69問以上）
     問：次の場面に合う文型を選んでください：忘れないうちに記録を書きます。
     1 〜うちに ← 正解

②は ふつうの穴うめ問題（「記録を見ると、…トイレに＿＿＿に違いない。」）とは
形が ちがう。見分け方は **選択肢が 文型の名前そのもの（〜が付く）であること**。
助詞1字が 文のほかの所にも出てくるのは あたりまえなので、鳴らさない。

    python3 tools/check-bunpo.py
"""
import collections
import glob
import io
import json
import os
import re
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
JA = re.compile(r'[ぁ-んァ-ヶ一-鿿々]')
EN = re.compile(r'[A-Za-z]{3,}')
ng = []
bad = ng.append

n = 0
lv = collections.Counter()
for f in sorted(glob.glob(R + 'bunpo/grammar-*.json')):
    nm = os.path.basename(f)
    for g in json.load(io.open(f, encoding='utf-8'))['grammar']:
        for q in g.get('quiz', []):
            if q.get('type') != 'choice':
                continue
            n += 1
            lv[g['level']] += 1
            c = q.get('choices') or []
            a = q.get('answer')
            qt = str(q.get('q', ''))
            where = '%s %s' % (nm, g['pattern'])
            if not isinstance(a, int) or not (0 <= a < len(c)):
                bad('%s 答えの番号が範囲の外（%r／選択肢%d）' % (where, a, len(c)))
                continue
            if len(c) != 4:
                bad('%s 選択肢が%dつです（4つのはず）' % (where, len(c)))
            if len(set(map(str, c))) != len(c):
                bad('%s 同じ選択肢が2つあります' % where)
            if any(not str(x).strip() for x in c):
                bad('%s 空の選択肢があります' % where)
            if all(not JA.search(str(x)) for x in c):
                bad('%s 選択肢に日本語がありません（%s）' % (where, ' / '.join(map(str, c))[:46]))
            if any(EN.search(str(x)) for x in c):
                bad('%s 選択肢に英語がまじっています' % where)
            if not JA.search(qt):
                bad('%s 問題文に日本語がありません' % where)
            # ②答えが問題文の中にある。**文型の名前を選ばせる形のときだけ**見る
            if all('〜' in str(x) or '～' in str(x) for x in c):
                core = str(c[a]).replace('〜', '').replace('～', '').strip()
                if core and core in qt:
                    bad('%s 答え「%s」が問題文の中にそのまま書いてあります\n'
                        '        %s' % (where, c[a], qt[:56]))

print('■ 文型の選択問題 %d問' % n)
for L in ('N5', 'N4', 'N3', 'N2', '記録'):
    print('   %-3s %4d問' % (L, lv[L]))
print()
print('=' * 54)
print('おかしいところ: %d件' % len(ng))
for x in ng[:12]:
    print('  -', x)
print('=' * 54)
sys.exit(1 if ng else 0)
