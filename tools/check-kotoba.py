#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**要注意語の例文**を見張る（SPEC 2.6-z59）。

JLPT N3・N4には「泥棒・戦争・自殺・殺す・殴る・爆発・犯罪・死体」のような
**事件やけがの語**が正規に入っている。試験に出るので外せない。
外せないが、**例文は選べる**。介護施設の実習生が練習問題で読むものなので、
生々しい文ではなく、**ふせぐ・気をつける・言い方を知る**の形にしてある。

ここで見るのは、その例文が **人が決めたとおりのまま**かどうか。
ちがっていたら鳴る。悪いとは決めつけない ──
**人が見て、よければこのファイルの文を書きかえる**ための見張り。

    python3 tools/check-kotoba.py
"""
import io
import json
import os
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# 人が決めた例文。ここを直すときは、**なぜ直すのかをSPECに書く**。
OK = {
    '泥棒': '泥棒に入られないように、戸じまりを確かめます。',
    '戦争': '利用者さんから戦争の話をうかがいました。',
    '自殺': '自殺をふせぐ相談まどぐちです。',
    '殺す': '虫を殺す薬です。',
    '殴る': '人を殴ってはいけません。',
    '爆発': 'ガスの爆発をふせぐため、火の元を確かめます。',
    '犯罪': '犯罪をふせぐ活動です。',
    '死体': '「死体」はかたい言い方です。施設では「ご遺体」と言います。',
}

ng = []
bad = ng.append

S = json.load(io.open(R + 'sentences.json', encoding='utf-8'))['sentences']

print('■ 要注意語の例文 %d語' % len(OK))
for w, want in sorted(OK.items()):
    got = S.get(w)
    if got is None:
        bad('%s の例文がありません（語そのものが消えた？）' % w)
        continue
    # 配列のときは [例文, 文中の形, その読み]
    txt = got[0] if isinstance(got, list) else got
    mark = '○' if txt == want else '✗'
    print('   %s %s　%s' % (mark, w, txt))
    if txt != want:
        bad('%s の例文が変わっています\n        いま: %s\n        決めた: %s' % (w, txt, want))
    # 練習問題は 文中の語を 伏せて出す。だから語（配列のときは
    # [例文, 文中の形, 読み] の**文中の形**）が 文の中に無いといけない。
    # 「殴る」は文中では「殴って」なので、見出し語そのままでは見つからない。
    need = got[1] if isinstance(got, list) and len(got) > 1 else w
    if need not in txt:
        bad('%s（文中の形「%s」）が例文の中にありません'
            '（練習問題で語を伏せられません）' % (w, need))

# 語そのものが語彙データから消えていないか（消すのは決めていない）
VD = json.load(io.open(R + 'vocab-data.json', encoding='utf-8'))
words = set()


def walk(o):
    if isinstance(o, dict):
        if 'word' in o:
            words.add(o['word'])
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(VD)
gone = [w for w in OK if w not in words]
if gone:
    bad('語彙データから消えています %s（JLPTの正規の語なので残す）' % '・'.join(gone))

print()
print('=' * 54)
print('おかしいところ: %d件' % len(ng))
for x in ng[:12]:
    print('  -', x)
print('=' * 54)
sys.exit(1 if ng else 0)
