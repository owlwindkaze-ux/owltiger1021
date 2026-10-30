#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**週の割り当てが指している番号が、本当にあるか**を見る（SPEC 2.6-z62）。

2026年10月12日に `bunpo/grammar-n3.json` が 別の中身に 入れ替わり、
番号の付け方も `n3-kuseni` → `n3-001` に 変わった。
`bunpo/weeks.json` は 古い番号のままだったので、
**新人コース 第13〜28週と N2コース 第1〜13週で、文型が1つも出なくなった**。
画面には「第13週の 文型 10項目」と出るのに、中身は「該当なし」。

**18日間、誰も気づかなかった。**どの検査も 番号の指し先を 見ていなかったから。
だから これを足す。指し先が 1つでも 無ければ 鳴る。

    python3 tools/check-ids.py
"""
import collections
import glob
import io
import json
import os
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
ng = []
bad = ng.append

# ── 文型 ─────────────────────────────────────────────
have = {}
for f in sorted(glob.glob(R + 'bunpo/grammar-*.json')):
    for g in json.load(io.open(f, encoding='utf-8'))['grammar']:
        if g['id'] in have:
            bad('文型の番号が ふたつある: %s（%s と %s）'
                % (g['id'], os.path.basename(have[g['id']]), os.path.basename(f)))
        have[g['id']] = f

W = json.load(io.open(R + 'bunpo/weeks.json', encoding='utf-8'))['courses']
print('■ 文型 %d項目／コース %d本' % (len(have), len(W)))
for c in sorted(W):
    zero, miss = [], 0
    for w, ids in sorted(W[c]['weeks'].items(), key=lambda x: int(x[0])):
        if not ids:
            continue
        ok = [i for i in ids if i in have]
        miss += len(ids) - len(ok)
        if not ok:
            zero.append(int(w))
    print('   %s：割り当て %d／指し先の無い番号 %d'
          % (c, sum(len(v) for v in W[c]['weeks'].values()), miss))
    if zero:
        bad('%s：文型が1つも出ない週があります 第%s週'
            % (c, '・'.join(map(str, zero))))
    if miss:
        bad('%s：指し先の無い文型の番号が %d個あります' % (c, miss))

# ── 漢字・語彙 ────────────────────────────────────────
KW = json.load(io.open(R + 'kanji-weeks.json', encoding='utf-8'))['courses']
kan = set()
for f in sorted(glob.glob(R + 'kanji-*.json')):
    try:
        d = json.load(io.open(f, encoding='utf-8'))
    except Exception:
        continue
    for k in d.get('kanji', []):
        kan.add(k['character'])
voc = set()
for f in sorted(glob.glob(R + 'vocab-*.json')):
    try:
        d = json.load(io.open(f, encoding='utf-8'))
    except Exception:
        continue
    for v in d.get('words', []):
        voc.add(v['word'])
print('■ 漢字 %d字／語彙 %d語' % (len(kan), len(voc)))
for c in sorted(KW):
    for key, pool, name in (('kanji', kan, '漢字'), ('vocab', voc, '語彙')):
        zero, miss = [], 0
        for w, xs in sorted(KW[c].get(key, {}).items(), key=lambda x: int(x[0])):
            if not xs:
                continue
            ok = [x for x in xs if x in pool]
            miss += len(xs) - len(ok)
            if not ok:
                zero.append(int(w))
        print('   %s %s：指し先の無いもの %d' % (c, name, miss))
        if zero:
            bad('%s：%sが1つも出ない週があります 第%s週'
                % (c, name, '・'.join(map(str, zero))))
        if miss:
            bad('%s：データに無い%sが %d個 割り当てられています' % (c, name, miss))

print()
print('=' * 54)
print('おかしいところ: %d件' % len(ng))
for x in ng[:12]:
    print('  -', x)
print('=' * 54)
sys.exit(1 if ng else 0)
