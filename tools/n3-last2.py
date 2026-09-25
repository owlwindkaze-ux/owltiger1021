#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""100日コースの直前2週（第13・14週）に、N3模試と直前確認を入れる。

いままで第13・14週は、ほかの12週と まったく同じ形だった
（月〜金の読解＋土曜の通しテスト＋日曜の聴解）。本番の直前に
「新しい文章を5本読む」週が2つ続くことになっていた。

置き方
  第13週に「公休」の日を足し、**N3模試 第1回（140分）**を入れる。
  第14週に「公休」の日を足し、**N3模試 第2回（140分）**を入れる。
  第14週の日曜（最後の日）のうしろに、**直前の確認**を足す。

「公休」にしたのは、模試が140分つづきで必要なので、
仕事のある日には入らないため。曜日のタブに「公休」が1つ増える。

**もとの14週分の教材は 1問も消していない**（88問×14週＝1,226問のまま）。
足しただけなので、読解も聴解も そのまま残っている。

  python3 tools/n3-last2.py            # 何をするかだけ出す
  python3 tools/n3-last2.py --write    # 書きこむ

2度かけても何も動かない（目印で見る）。
"""
import io
import json
import sys

R = '/home/user/owltiger1021/'
F = R + 'n3.html'
MARK = 'n3-moshi-last2'          # かけたかどうかの目印

# 中身は JSON の "v":"…" の中に入る。**ここで二重引用符を使うと文字列が壊れる**
# （一度やって、n3.html の script 全体が SyntaxError で止まった）。属性は単引用符で書く。
MOSHI_LINK = ("<a class='act' href='moshi/?lv=n3' "
              "style='display:inline-block;text-decoration:none'>"
              "📝 N3模試をひらく（140分）</a>")


def day(no, first):
    """模試の日（設問は無い。読むものと入口だけ）"""
    if first:
        head = ('この週は、はじめて<b>本番とまったく同じ形</b>で解きます。'
                '文字・語彙30分 → 文法・読解70分 → 聴解40分の、ぜんぶで140分です。')
        after = ('<b>区分ごとの点が出ます。19点に とどかなかった区分を 書きとめてください。</b>'
                 'その区分だけを、この週の のこりと 第14週で 直します。'
                 '<b>全部やり直す 時間は ありません。</b>')
    else:
        head = ('第1回と同じ形の、<b>最後の通し</b>です。'
                '第1回の点と くらべて、上がったかを 見ます。')
        after = ('<b>ここで まだ19点に とどかない区分が あっても、'
                 '新しい教材は 開かないでください。</b>'
                 '一度やった問題の 見直しだけに してください。'
                 '半分おぼえた語を ふやすより、おぼえた語を 確かにするほうが 点になります。')
    return (
        '{"key":"公休","title":"N3模試 第%d回（本番と同じ140分）",'
        '"blocks":['
        '{"t":"h2","v":"この日にすること"},'
        '{"t":"p","v":"%s"},'
        '{"t":"p","v":"<b>続けて140分 とれる日に 受けてください。</b>'
        '本番は区分ごとに用紙を集めるので、模試も<b>区分をまたいで もどれません。</b>'
        '途中でやめると 点が出ません。仕事の日は むずかしいので、'
        '<b>公休の日</b>に 席と時間を 用意してもらってください。"},'
        '{"t":"p","v":"%s"},'
        '{"t":"h2","v":"点の見かた"},'
        '{"t":"p","v":"区分ごとに60点に 直して 出ます。'
        '<b>合計90点以上で、どの区分も19点以上</b>が 合格の目安です。'
        '<b>合計が90点を こえても、1区分でも19点未満だと 不合格になります。</b>'
        'N3で いちばん 落ちやすいところです。"},'
        '{"t":"p","v":"%s"},'
        '{"t":"h2","v":"このあと すること"},'
        '{"t":"p","v":"%s"}'
        ']}' % (no, head, MOSHI_LINK, MOSHI_LINK, after)
    )


CHOKUZEN = (
    ',{"t":"h2","v":"直前の 確認"},'
    '{"t":"p","v":"<!-- %s --><b>ここから先は、新しいことを しません。</b>'
    '一度 見た問題を 思い出すだけにします。"},'
    '{"t":"p","v":"<b>持っていくもの</b>：受験票 ／ 写真つきの 身分証 ／ '
    'えんぴつ（HB）を 2本以上 ／ 消しゴム ／ 時計（音の出ないもの）。'
    'けいたい電話は 会場では 使えません。"},'
    '{"t":"p","v":"<b>会場までの 行き方と 時間</b>を、前の日までに 一度 調べてください。'
    '電車の 乗りかえと、駅から会場まで 歩く時間も。'
    '日曜は 電車の本数が 少ないことが あります。"},'
    '{"t":"p","v":"<b>前の日は 勉強しないで、早く 寝てください。</b>'
    'いちばん 大事です。ねむいと 聴解が 聞こえません。'
    '聴解は 1回しか 流れないので、ここで 点を 落とすと もどせません。"}'
) % MARK


def check_json(s):
    """足した「公休」の日と「直前の確認」が、JSONとして読めるかを見る。

    n3.html の WEEKS は JS のリテラルだが、足した分は素の JSON なので、
    その部分だけを切り出して json.loads にかければ、引用符の壊れは捕まる。
    """
    for no in (1, 2):
        head = '{"key":"公休","title":"N3模試 第%d回（本番と同じ140分）"' % no
        if head not in s:
            return '第%d回の日が 見つからない' % no
        i = s.index(head)
        # 対応する閉じかっこまでを、かっこの数を数えて切り出す
        depth, j = 0, i
        while j < len(s):
            c = s[j]
            if c == '"':                      # 文字列は とばす
                j += 1
                while j < len(s) and s[j] != '"':
                    j += 2 if s[j] == '\\' else 1
            elif c in '{[':
                depth += 1
            elif c in '}]':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        try:
            d = json.loads(s[i:j + 1])
        except Exception as e:
            return '第%d回の日が JSONとして読めない：%s' % (no, e)
        if d.get('key') != '公休' or not d.get('blocks'):
            return '第%d回の日の 形が おかしい' % no
        if any(b.get('t') == 'q' for b in d['blocks']):
            return '第%d回の日に 設問が 入っている（入れない約束）' % no
    if MARK not in s:
        return '「直前の確認」の目印が 無い'

    # 「直前の確認」が **最後の日の blocks の中** に入っているかを見る。
    # days の配列に直接入れてしまうと「曜日の無い日」ができて 画面が落ちる。
    i = s.index('"14":{"days":[')
    j = s.index('],"answers"', i)
    depth, k, last = 0, i + len('"14":{"days":['), None
    # days の中の いちばん最後の日のオブジェクトを 切り出す
    starts = []
    k = i + len('"14":{"days":[')
    while k < j:
        c = s[k]
        if c == '"':
            k += 1
            while k < j and s[k] != '"':
                k += 2 if s[k] == '\\' else 1
        elif c == '{':
            if depth == 0:
                starts.append(k)
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                last = (starts[-1], k)
        elif c in '[':
            depth += 1
        elif c in ']':
            depth -= 1
        k += 1
    if not last:
        return '第14週の 最後の日が 切り出せない'
    try:
        d = json.loads(s[last[0]:last[1] + 1])
    except Exception as e:
        return '第14週の 最後の日が JSONとして読めない：%s' % e
    if d.get('key') != '日曜':
        return '第14週の 最後の日が 日曜ではない（%r）' % d.get('key')
    if not any(MARK in str(b.get('v', '')) for b in d.get('blocks', [])):
        return '「直前の確認」が 日曜の blocks の中に 入っていない'
    return None


def main():
    write = '--write' in sys.argv
    s = io.open(F, encoding='utf-8').read()

    if MARK in s:
        print('もう入っています（目印 %s あり）。何もしません。' % MARK)
        return 0

    n = 0
    for w, first in ((13, True), (14, False)):
        a = '"%d":{"days":[' % w
        if s.count(a) != 1:
            print('× 第%d週の目印が %d 個。手で見てください' % (w, s.count(a)))
            return 1
        s = s.replace(a, a + day(1 if first else 2, first) + ',', 1)
        n += 1
        print('第%d週に「公休」の日（N3模試 第%d回）を足しました'
              % (w, 1 if first else 2))

    # 第14週の最後の日（日曜）の blocks のうしろに 直前の確認を足す。
    # 入れる場所を まちがえやすい。'],"answers"' は **days の配列を閉じる ]** なので、
    # そこに入れると「曜日の無い日」が1つできて、画面が d.key.replace で落ちる（実際に落とした）。
    # ねらうのは その2つ手前、**最後の日の blocks を閉じる ]**。
    i = s.index('"14":{"days":[')
    j = s.index('],"answers"', i)
    assert s[j - 2:j + 1] == ']}]', '第14週の終わりの形が ちがう：%r' % s[j - 4:j + 2]
    s = s[:j - 2] + CHOKUZEN + s[j - 2:]
    print('第14週の 日曜のうしろに「直前の 確認」を足しました')

    # 足した中身が JSON の文字列を壊していないかを、書く前に見る。
    # 一度、属性を二重引用符で書いて n3.html の script 全体を止めた。
    bad = check_json(s)
    if bad:
        print('\n× 足した中身が こわれています：%s' % bad)
        print('  書きこみません。tools/n3-last2.py の 引用符を 見てください')
        return 1
    print('\n○ 足した日の中身は JSON として読めました')

    if not write:
        print('--write を付けると 書きこみます（いまは 何も 変えていません）')
        return 0

    io.open(F, 'w', encoding='utf-8').write(s)
    print('\nn3.html に 書きこみました（足した日 %d 日）' % n)
    return 0


if __name__ == '__main__':
    sys.exit(main())
