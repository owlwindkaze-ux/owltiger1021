#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**尊敬語・謙譲語・丁寧語の対応表**（`keigo.json`）を作る（SPEC 2.6-z66）。

持ち主から「漢字・語彙のメニューに『尊敬語・謙譲語・丁寧語』を加えたら」。

介護では 言いまちがえると 失礼になる。いちばん多いのが **入れちがい**。

    ✗ 利用者さんが 申されました     ○ 利用者さんが おっしゃいました
    ✗ 私が ご覧になります          ○ 私が 拝見します

**尊敬語は相手の動き、謙譲語は自分の動き。**これを1枚の表で見せる。

語・読み・意味・例文は **語彙データと例文データから取る**（二重に持たない）。
どの語が どの段か ── それだけが ここに書いてある。

    python3 tools/keigo.py          # 作り直す
    python3 tools/keigo.py --list   # 中身を見るだけ
"""
import io
import json
import os
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# (ふつうの言い方, 尊敬語（相手の動き）, 謙譲語（自分の動き）, 場面のひとこと)
# 空文字は「決まった形が無い」── 画面では「—」と出し、お／ご〜の形を使う。
ROWS = [
    ('言う', 'おっしゃる', '申す', '申し送り・あいさつ'),
    ('言う', '', '申し上げる', 'あらたまって伝えるとき'),
    ('行く', 'いらっしゃる', '伺う', '訪問・付き添い'),
    ('来る', 'いらっしゃる', '参る', 'ご家族の来訪'),
    ('いる', 'いらっしゃる', 'おる', '居室・申し送り'),
    ('食べる', '召し上がる', 'いただく', '食事介助'),
    ('飲む', '召し上がる', 'いただく', '服薬・水分'),
    ('見る', 'ご覧になる', '拝見する', '写真・お薬の確認'),
    ('する', 'なさる', 'いたす', '何にでも使う'),
    ('知っている', 'ご存じだ', '存じている', '確認するとき'),
    ('もらう', '', 'いただく', 'お願いしたあと'),
    ('あげる', '', '差し上げる', 'お渡しするとき'),
    ('くれる', 'くださる', '', 'していただいたとき'),
    ('会う', '', 'お目にかかる', 'ご家族との面会'),
]

# 丁寧語（だれにでも使う言い方）。表の下に 別に出す。
TEINEI = [
    ('です・ます', 'いちばん基本。利用者さんにも職員にも使う。'),
    ('ございます', '「あります」のていねいな言い方。「受付はこちらでございます」'),
    ('お・ご', '「お名前」「お部屋」「ご家族」。相手のものに付ける。'),
]


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

    def cell(word):
        if not word:
            return None
        w = V.get(word)
        if not w:
            print('× 「%s」が語彙にありません' % word); sys.exit(1)
        s = S.get(word)
        if s is None:
            print('× 「%s」に例文がありません' % word); sys.exit(1)
        sent = s[0] if isinstance(s, list) else s
        sur = s[1] if isinstance(s, list) else word
        if sur not in sent:
            print('× 「%s」の例文に「%s」がありません' % (word, sur)); sys.exit(1)
        return {'word': word, 'reading': w['reading'], 'level': w['level'],
                'meaning_id': w.get('meaning_id') or '', 'meaning': w.get('meaning') or '',
                'sentence': sent, 'sur': sur}

    rows = []
    for plain, son, ken, scene in ROWS:
        rows.append({'plain': cell(plain), 'sonkei': cell(son),
                     'kenjou': cell(ken), 'scene': scene})

    out = {
        'name': '尊敬語・謙譲語・丁寧語の対応表（介護版）',
        'app_version': json.load(io.open(R + 'version.json', encoding='utf-8'))['version'],
        'note': ('尊敬語は相手（利用者さん・ご家族・上の人）の動き、謙譲語は自分の動き。'
                 '語・読み・意味・例文は 語彙データと例文データから取っている（二重に持たない）。'
                 'どの語がどの段かは tools/keigo.py に書いてある。'),
        'hint_ja': '尊敬語は相手の動きに、謙譲語は自分の動きに使います。入れちがえると失礼になります。',
        'hint_id': ('尊敬語 (sonkeigo) untuk tindakan lawan bicara, '
                    '謙譲語 (kenjougo) untuk tindakan diri sendiri. '
                    'Kalau tertukar, menjadi tidak sopan.'),
        'ng_ja': ['✗ 利用者さんが申されました → ○ 利用者さんがおっしゃいました',
                  '✗ 私がご覧になります → ○ 私が拝見します',
                  '✗ 先生がおりますか → ○ 先生はいらっしゃいますか'],
        'teinei': [{'form': a, 'note_ja': b} for a, b in TEINEI],
        'count': len(rows),
        'rows': rows,
    }
    if '--list' in sys.argv:
        for r in rows:
            g = lambda c: (c['word'] + '（' + c['reading'] + '）') if c else '—'
            print('%-14s 尊敬 %-18s 謙譲 %-20s %s'
                  % (g(r['plain']), g(r['sonkei']), g(r['kenjou']), r['scene']))
        return
    io.open(R + 'keigo.json', 'w', encoding='utf-8').write(
        json.dumps(out, ensure_ascii=False) + '\n')
    print('○ keigo.json を作りました（%d行）' % len(rows))


main()
