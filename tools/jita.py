#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**自動詞・他動詞の対**（`jita.json`）を作る（SPEC 2.6-z66）。

持ち主から「漢字・語彙のメニューに、別に『自動詞・他動詞』を加えたらどうでしょうか」。

介護の記録で いちばん まちがえるところ。

    ✗ ドアを開きました      ○ ドアを開けました
    ✗ 水をこぼれました      ○ 水をこぼしました

**新しい語は作らない。**どの語も すでに語彙にあり、例文も付いている。
ここでやるのは **どれとどれが対か**を決めること。これは人がやるしかない。
機械で拾うと「分かる／分ける」「見る／見せる」のような **対でないもの**が混ざる。

対から外したもの（理由つき）
  分かる／分ける   意味がちがう。対ではない
  見る／見せる     どちらも他動詞
  止む／止める     対は 止まる／止める（とめる）
  足る／足す       意味がちがう
  含む／含める     どちらも他動詞
  着る／着せる     着る は他動詞。「人にしてあげる形」であって 自他の対ではない
  被る／被せる     同上
  預かる／預ける   どちらも他動詞

    python3 tools/jita.py          # 作り直す
    python3 tools/jita.py --list   # 中身を見るだけ
"""
import io
import json
import os
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# （自動詞, 他動詞）。並びは 使う場面の近いものをまとめた
PAIRS = [
    # ── 身のまわり・介助 ──
    ('開く', '開ける'), ('閉まる', '閉める'), ('止まる', '止める'),
    ('入る', '入れる'), ('出る', '出す'), ('上がる', '上げる'), ('下がる', '下げる'),
    ('付く', '付ける'), ('消える', '消す'), ('かかる', 'かける'),
    ('立つ', '立てる'), ('並ぶ', '並べる'), ('乗る', '乗せる'),
    ('戻る', '戻す'), ('残る', '残す'), ('届く', '届ける'),
    ('通る', '通す'), ('進む', '進める'), ('向く', '向ける'),
    ('寄る', '寄せる'), ('帰る', '帰す'), ('離れる', '離す'),
    # ── 事故・ひやり ──
    ('落ちる', '落とす'), ('倒れる', '倒す'), ('起きる', '起こす'),
    ('こぼれる', 'こぼす'), ('割れる', '割る'), ('壊れる', '壊す'),
    ('外れる', '外す'), ('転がる', '転がす'), ('ぶつかる', 'ぶつける'),
    ('挟まる', '挟む'), ('詰まる', '詰める'), ('崩れる', '崩す'),
    ('潰れる', '潰す'), ('裂ける', '裂く'), ('砕ける', '砕く'),
    ('引っ繰り返る', '引っ繰り返す'), ('放れる', '放す'),
    # ── からだ・ようす ──
    ('治る', '治す'), ('直る', '直す'), ('汚れる', '汚す'), ('乾く', '乾かす'),
    ('冷える', '冷やす'), ('温まる', '温める'), ('暖まる', '暖める'),
    ('増える', '増やす'), ('減る', '減らす'), ('変わる', '変える'),
    ('続く', '続ける'), ('育つ', '育てる'), ('生える', '生やす'),
    ('強まる', '強める'), ('弱まる', '弱める'), ('縮む', '縮める'),
    ('広がる', '広げる'), ('広まる', '広める'), ('深まる', '深める'),
    ('高まる', '高める'),
    # ── 仕事・やりとり ──
    ('始まる', '始める'), ('決まる', '決める'), ('集まる', '集める'),
    ('伝わる', '伝える'), ('見つかる', '見つける'), ('片付く', '片付ける'),
    ('まとまる', 'まとめる'), ('散らかる', '散らかす'), ('溜まる', '溜める'),
    ('当てはまる', '当てはめる'), ('助かる', '助ける'), ('起こる', '起こす'),
    ('現れる', '現す'), ('隠れる', '隠す'), ('載る', '載せる'),
    ('映る', '映す'), ('写る', '写す'), ('浮かぶ', '浮かべる'),
    ('流れる', '流す'), ('溶ける', '溶く'), ('焼ける', '焼く'),
    ('燃える', '燃やす'), ('抜ける', '抜く'), ('解ける', '解く'),
    ('繋がる', '繋げる'), ('くっつく', 'くっつける'), ('埋まる', '埋める'),
    ('泊まる', '泊める'), ('建つ', '建てる'), ('着く', '着ける'),
    ('曲がる', '曲げる'), ('退く', '退ける'), ('儲かる', '儲ける'),
]

# 語彙の見出しの読みが その対の読みでないとき、どの読みを使うか。
# （`alt` に入っている読みだけを 指定できる。勝手な読みは 書けない）
READ = {'止める': 'とめる'}

# **同じ語が ふたつの対に出るとき**、語の例文は 片方にしか 合わない。
# 「起こす」は 起きる／起こす（人を起こす）と 起こる／起こす（事故を起こす）の
# 両方に出る。語の例文を そのまま使うと **同じ文が二度ならび、片方は 意味が合わない**
# （敬語の表で 持ち主が見つけたのと 同じ形・2026-11-01）。
# ここだけ その対のための例文を 書く。鍵は （自動詞, 他動詞, どちら側か）。
SENT = {
    ('起こる', '起こす', 'vt'): ('不注意が事故を起こすことがあります。', '起こす'),
}


def main():
    V = {}
    for f in ('vocab-n5.json', 'vocab-n4.json', 'vocab-n3.json', 'vocab-n2.json',
              'vocab-kaigo.json', 'vocab-genba.json', 'vocab-kiroku.json'):
        p = R + f
        if not os.path.exists(p):
            continue
        for w in json.load(io.open(p, encoding='utf-8'))['words']:
            V.setdefault(w['word'], w)
    S = json.load(io.open(R + 'sentences.json', encoding='utf-8'))['sentences']

    def one(word, kind, key=None):
        w = V.get(word)
        if not w:
            print('× 「%s」が語彙にありません' % word); sys.exit(1)
        rd = READ.get(word, w['reading'])
        if rd != w['reading'] and rd not in [a.get('reading') for a in (w.get('alt') or [])]:
            print('× 「%s」の読み「%s」が 語彙にも alt にもありません' % (word, rd)); sys.exit(1)
        ov = SENT.get(key)
        if ov:
            sent, sur = ov
            if sent.count(sur) != 1:
                print('× 「%s」の例文に「%s」が %d回' % (word, sur, sent.count(sur))); sys.exit(1)
            return {'word': word, 'reading': rd, 'level': w['level'], 'kind': kind,
                    'meaning_id': w.get('meaning_id') or '', 'meaning': w.get('meaning') or '',
                    'sentence': sent, 'sur': sur}
        # 読みを `alt` のほうに合わせたときは、**例文も alt のもの**を使う。
        # 「止める」の見出しは やめる で、例文も「たばこを止める。」。
        # 自他の対で要るのは とめる の文（2026-10-31）。
        alt = next((a for a in (w.get('alt') or []) if a.get('reading') == rd), None)
        if alt:
            sent, sur = alt['sentence'], alt.get('sur') or word
        else:
            s = S.get(word)
            if s is None:
                print('× 「%s」に例文がありません' % word); sys.exit(1)
            sent = s[0] if isinstance(s, list) else s
            sur = s[1] if isinstance(s, list) else word
        if sur not in sent:
            print('× 「%s」の例文に「%s」がありません' % (word, sur)); sys.exit(1)
        return {'word': word, 'reading': rd, 'level': w['level'], 'kind': kind,
                'meaning_id': w.get('meaning_id') or '', 'meaning': w.get('meaning') or '',
                'sentence': sent, 'sur': sur}

    rows = []
    seen = set()
    for a, b in PAIRS:
        if (a, b) in seen:
            print('× 対が二度出ています: %s／%s' % (a, b)); sys.exit(1)
        seen.add((a, b))
        rows.append({'vi': one(a, '自動詞', (a, b, 'vi')),
                     'vt': one(b, '他動詞', (a, b, 'vt'))})

    seen_s = {}
    for r in rows:
        for k in ('vi', 'vt'):
            t = r[k]['sentence']
            if t in seen_s:
                print('× 同じ例文が二度出ています（%s と %s）: %s'
                      % (seen_s[t], r[k]['word'], t)); sys.exit(1)
            seen_s[t] = r[k]['word']

    out = {
        'name': '自動詞・他動詞の対（介護版）',
        'app_version': json.load(io.open(R + 'version.json', encoding='utf-8'))['version'],
        'note': ('自動詞は「〜が」、他動詞は「〜を」。記録でいちばんまちがえるところ。'
                 '語・読み・意味・例文は 語彙データと例文データから取っている（二重に持たない）。'
                 '対の決め方は tools/jita.py に書いてある。'),
        'hint_ja': '自動詞は「〜が」、他動詞は「〜を」といっしょに使います。',
        'hint_id': ('Kata kerja intransitif (自動詞) dipakai dengan 「が」, '
                    'kata kerja transitif (他動詞) dengan 「を」.'),
        'count': len(rows),
        'pairs': rows,
    }
    if '--list' in sys.argv:
        for r in rows:
            print('%-8s(%-8s) %-24s ／ %-8s(%-8s) %s'
                  % (r['vi']['word'], r['vi']['reading'], r['vi']['sentence'][:22],
                     r['vt']['word'], r['vt']['reading'], r['vt']['sentence'][:22]))
        return
    io.open(R + 'jita.json', 'w', encoding='utf-8').write(
        json.dumps(out, ensure_ascii=False) + '\n')
    print('○ jita.json を作りました（%d組）' % len(rows))


main()
