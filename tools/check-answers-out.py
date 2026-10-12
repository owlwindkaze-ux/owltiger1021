#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**答えの入ったPDFが、公開の場所に戻っていないか**を点検する（SPEC 2.6-z35）。

このリポジトリは公開で、PDFは**合言葉の外側**にある。
画面からリンクを外しても（2.6-z8）、**住所を知っていれば合言葉なしで開ける**。
そこで 2026-10-12 に、答え・採点・聴解の原稿が入った14本を
**Google ドライブの職員用フォルダへ移した**。

置き場所を間違えて戻すと、**テストそのものが意味を失う**。
作り直した PDF をうっかりリポジトリに入れてしまうのが いちばん起きやすい。
ここで止める。

  python3 tools/check-answers-out.py
"""
import io
import os
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# ここに挙げた名前の PDF は、リポジトリに**あってはいけない**。
# ドライブの「owltiger1021_職員用（答え入り・公開しない）」に置く。
OUT = [
    'N4到達度判定テスト_職員用.pdf',      # 正解と解説
    'N4到達度判定テスト_問題.pdf',        # 事前に見られると判定が無効になる
    '診断テスト_実施と採点.pdf',          # 正解・採点・判定・聴解の原稿
    '診断テスト_第1回_問題.pdf',
    '診断テスト_第2回_問題.pdf',
    '月次確認テスト.pdf',                 # 問題・正解・聴解の原稿
    'kaigo/01_N3実力テスト_第1回.pdf',
    'kaigo/02_章別ミニテスト_全8章.pdf',
    'kaigo/03_N4補習版_全5回.pdf',
    'kaigo/04_書き方テスト_全5回.pdf',
    'kaigo/05_コロケーション演習_全3回.pdf',
    'kaigo/06_根拠づけ演習.pdf',
    'kaigo/08_記述特化ワーク_全5回.pdf',
    'kaigo/09_聴解テスト_紙版.pdf',       # 巻末に聴解の原稿
]

# 画面から、消したはずのファイルを まだ指していないか
LINKPAGES = ['staff/index.html', 'kaigo/index.html', 'index.html', 'shinjin/index.html']


def main():
    bad = []
    here = [f for f in OUT if os.path.exists(R + f)]
    print('■ 答えの入ったPDF %d本が、リポジトリに無いか' % len(OUT))
    if here:
        for f in here:
            print('   × %s が リポジトリにあります' % f)
            bad.append('答え入り：%s を リポジトリから出してください（ドライブの職員用フォルダへ）' % f)
    else:
        print('   どれもありません  OK')

    print('\n■ 画面が、消したファイルを まだ指していないか')
    dead = 0
    for p in LINKPAGES:
        if not os.path.exists(R + p):
            continue
        s = io.open(R + p, encoding='utf-8').read()
        for f in OUT:
            name = os.path.basename(f)
            if ('href="' + name + '"') in s or ('href="../' + name + '"') in s:
                dead += 1
                bad.append('%s が %s を まだ指しています（リンク切れ）' % (p, name))
    print('   切れているリンク %d本' % dead)

    print('\n' + '=' * 62)
    print('直さないといけない所:', len(bad))
    for b in bad:
        print('  -', b)
    print('=' * 62)
    print('※ 画面の問題・模試の答えは、JSONに入っていて外せません'
          '（静的サイトなので、画面が読む＝誰でも読める）。')
    print('※ 消したのは いまのファイルだけで、**古い記録には残っています**。')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
