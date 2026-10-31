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
import re
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

# ── 尼語の訳で、**一語だけだと別の意味になる**もの ──────────────
# 「mantan」は `mantan presiden`（前大統領）のように **名詞の前に付ける**形なら
# 正しいが、**一語だけ**だと ふだんの話し言葉では「元恋人」を指す。
# 「旧＝lama, mantan」と書いてあり、持ち主が見つけた（2026-10-30）。
# だから「mantan」は **必ず `~` といっしょ**でなければいけない。
PREFIX_ONLY = {
    'mantan': '一語だけだと「元恋人」の意味になる。`mantan ~` の形で使う',
}
print()
print('■ 一語だけだと別の意味になる尼語')
seen_pref = []


def scan(path):
    d = json.load(io.open(R + path, encoding='utf-8'))

    def go(o):
        if isinstance(o, dict):
            mid = o.get('meaning_id')
            if isinstance(mid, str):
                for w, why in PREFIX_ONLY.items():
                    if not re.search(r'\b%s\b' % w, mid):
                        continue
                    # **訳の中のどこかに `~` があること。**「前に付ける語だ」と
                    # 分かる書き方になっていれば よい。無ければ 一語で立っている。
                    if '~' in mid or '〜' in mid:
                        seen_pref.append((o.get('word') or o.get('character'), mid))
                    else:
                        bad('%s の「%s」で %s が一語で使われています（%s）\n'
                            '        いま: %s'
                            % (path, o.get('word') or o.get('character') or '?',
                               w, why, mid))

    def walk2(o):
        if isinstance(o, dict):
            go(o)
            for v in o.values():
                walk2(v)
        elif isinstance(o, list):
            for v in o:
                walk2(v)
    walk2(d)


for p in ('vocab-data.json', 'vocab-n2.json', 'vocab-n3.json', 'vocab-n4.json',
          'vocab-n5.json', 'vocab-kaigo.json', 'vocab-genba.json', 'vocab-kiroku.json',
          'kanji-data.json', 'kanji-n2.json', 'kanji-n3.json', 'kanji-n4.json',
          'kanji-n5.json', 'kanji-kaigo.json', 'kanji-kiroku.json'):
    if os.path.exists(R + p):
        scan(p)
for w, m in sorted(set(seen_pref)):
    print('   ○ %s　%s' % (w, m))

# ── 「〜」が付く語に 例文と熟語があるか ───────────────────────
# 「〜位」「〜羽」のような 接辞・助数詞は、**そのままでは文に入らない**。
# `sentences.json` では [例文, 文中の形（熟語）, その読み] の3つ組で持つ。
# 熟語が無いと 練習問題で 伏せる所が 無く、問題が作れない。
# 57語が 空のままで、コースの週に 出ていた（持ち主が見つけた・2026-10-31）。
print()
print('■ 「〜」が付く語の 例文と熟語')
VW = json.load(io.open(R + 'vocab-data.json', encoding='utf-8'))['words']
SS = json.load(io.open(R + 'sentences.json', encoding='utf-8'))['sentences']
tilde = [w for w in VW if '〜' in w['word'] or '～' in w['word']]
nosent = [w['word'] for w in tilde if w['word'] not in SS]
notrio, badonce = [], []
for w in tilde:
    v = SS.get(w['word'])
    if v is None:
        continue
    if not isinstance(v, list) or len(v) != 3:
        notrio.append(w['word'])          # 熟語と読みが要る
        continue
    if v[0].count(v[1]) != 1:
        badonce.append(w['word'])         # 文中に1回だけでないと 伏せられない
print('   %d語／例文なし %d／3つ組でない %d／文中に1回でない %d'
      % (len(tilde), len(nosent), len(notrio), len(badonce)))
if nosent:
    bad('「〜」が付く語 %d語に例文がありません（%s…）'
        % (len(nosent), '・'.join(nosent[:6])))
if notrio:
    bad('「〜」が付く語 %d語が [例文, 熟語, 読み] の3つ組ではありません（%s…）'
        % (len(notrio), '・'.join(notrio[:6])))
if badonce:
    bad('「〜」が付く語 %d語で、熟語が例文の中に1回だけ出ていません（%s…）'
        % (len(badonce), '・'.join(badonce[:6])))

print()
print('=' * 54)
print('おかしいところ: %d件' % len(ng))
for x in ng[:12]:
    print('  -', x)
print('=' * 54)
sys.exit(1 if ng else 0)
