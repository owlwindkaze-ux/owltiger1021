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
#
# **例文は 行ごとに書く。**語の例文（`sentences.json`）を そのまま使うと、
# 「いらっしゃる」は 行く・来る・いる の3行に出るので **同じ文が3回**ならぶ。
# しかも その文は 語のための文で、**その行の場面に 合っていない**
# （「訪問・付き添い」の行に「社長は会議室にいらっしゃる。」が出ていた。
#   持ち主が見つけた・2026-11-01）。
# 敬語は **場面で選ぶ**もの。だから 例文だけは 行ごとに持つ。
# 語・読み・意味は これまでどおり 語彙データから取る（二重に持たない）。
#
# （ふつうの言い方, 尊敬語, 謙譲語, 場面）。語のあとの文が その行の例文。
ROWS = [
    (('言う', '申し送りで夜間の様子を言います。'),
     ('おっしゃる', '田中様が「よく眠れた」とおっしゃいました。'),
     ('申す', '初めまして、リナと申します。'),
     'あいさつ・申し送り'),
    (('言う', 'ご家族に電話で言いました。'),
     ('', ''),
     ('申し上げる', '本日のご様子をご家族に申し上げます。'),
     'あらたまって伝えるとき'),
    (('行く', 'これから居室へ行きます。'),
     ('いらっしゃる', '佐藤様はどちらへいらっしゃいますか。'),
     ('伺う', '三時にお部屋へ伺います。'),
     '訪問・付き添い'),
    (('来る', 'ご家族が面会に来ます。'),
     ('いらっしゃる', 'ご家族が面会にいらっしゃいました。'),
     ('参る', 'ただいま参ります。'),
     'ご家族の来訪'),
    (('いる', '田中様は食堂にいます。'),
     ('いらっしゃる', '田中様はホールにいらっしゃいます。'),
     ('おる', '私は事務所におります。'),
     '居室・申し送り'),
    (('食べる', 'ゆっくり食べるように声をかけます。'),
     ('召し上がる', '朝食を全部召し上がりました。'),
     ('いただく', 'お昼はこちらでいただきます。'),
     '食事介助'),
    (('飲む', 'お薬を水で飲みます。'),
     ('召し上がる', 'お茶を少し召し上がりました。'),
     ('いただく', 'お茶をいただきます。'),
     '服薬・水分'),
    (('見る', 'きずの様子を見ます。'),
     ('ご覧になる', '写真をご覧になりますか。'),
     ('拝見する', 'お薬の袋を拝見します。'),
     '写真・お薬の確認'),
    (('する', '午後から散歩をします。'),
     ('なさる', '午後は体操をなさるそうです。'),
     ('いたす', '洗濯はこちらでいたします。'),
     '何にでも使う'),
    (('知っている', 'ご家族の連絡先を知っていますか。'),
     ('ご存じだ', 'この歌をご存じですか。'),
     ('存じている', 'お名前は存じています。'),
     '確認するとき'),
    (('もらう', '友だちから写真をもらいました。'),
     ('', ''),
     ('いただく', 'ご家族から写真をいただきました。'),
     'お願いしたあと'),
    (('あげる', '子どもにお菓子をあげます。'),
     ('', ''),
     ('差し上げる', '新しいタオルを差し上げます。'),
     'お渡しするとき'),
    (('くれる', '友だちが手伝ってくれました。'),
     ('くださる', 'ご家族が写真を持ってきてくださいました。'),
     ('', ''),
     'していただいたとき'),
    (('会う', 'あした、ご家族に会います。'),
     ('', ''),
     ('お目にかかる', '先日、ご家族にお目にかかりました。'),
     'ご家族との面会'),
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

    def cell(pair):
        """語は語彙データから、例文は この行のもの。"""
        word, sent = pair
        if not word:
            return None
        w = V.get(word)
        if not w:
            print('× 「%s」が語彙にありません' % word); sys.exit(1)
        if not sent.strip():
            print('× 「%s」に この行の例文がありません' % word); sys.exit(1)
        # 文中では 活用する。語の はじめの部分が 文に出ていれば よしとし、
        # 太字にする所（sur）は いちばん長く当たったところにする。
        sur = ''
        for n in range(len(word), 0, -1):
            if word[:n] in sent:
                sur = word[:n]
                break
        if not sur:
            print('× 「%s」が例文「%s」の中にありません' % (word, sent)); sys.exit(1)
        if sent.count(sur) != 1:
            print('× 「%s」の例文に「%s」が %d回（1回でないと太字にできない）'
                  % (word, sur, sent.count(sur))); sys.exit(1)
        return {'word': word, 'reading': w['reading'], 'level': w['level'],
                'meaning_id': w.get('meaning_id') or '', 'meaning': w.get('meaning') or '',
                'sentence': sent, 'sur': sur}

    rows, used = [], {}
    for plain, son, ken, scene in ROWS:
        for _w, sent in (plain, son, ken):
            if sent.strip():
                if sent in used:
                    print('× 同じ例文が二度出ています（%s）: %s' % (used[sent], sent))
                    sys.exit(1)
                used[sent] = scene
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
