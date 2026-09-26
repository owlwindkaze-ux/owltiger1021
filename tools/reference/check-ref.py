#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""参考書のリストと、このシステムのデータを 突き合わせる。

置いてあるリスト（`tools/reference/`）

  soumatome-n3-kanji.csv          『日本語総まとめ N3』巻末の漢字リスト
                                  （画数／漢字／熟語・言葉。1,292件）
  nihongonomori-n3-300.txt        『日本語の森』N3重要語彙300（284語）
  drive-n3kanji-600kanzen.txt     ドライブ「N3漢字600字 完全版」（実体150字）
  drive-n3kanji-hinshutsu600.txt  ドライブ「N3頻出漢字600字 詳細リスト」（実体477字）

**「600字」などの数は あてになりません。**中で同じ行が何度も繰り返されていたり、
N3を超える字（胃・腸・肺・臓・腐・奪）が混ざっていたりします。
**必ず数え直してから使ってください。**

**リストは必ずここに保存すること。** 一度、突き合わせをしたのに もらった
ファイルを保存せず、**同じ照合を二度とやり直せなくなった**（2026-09-23）。

出るもの
  ① リストにある漢字で、システムの漢字データに無いもの
  ② リストにある漢字で、データにはあるが「この30週で習う」範囲（N5+N4+N3）に
     入っていないもの
  ③ リストにある熟語・言葉で、語彙データに無いもの

  python3 tools/reference/check-ref.py           # まとめだけ
  python3 tools/reference/check-ref.py --list    # 足りないものを 全部出す
"""
import io
import json
import re
import sys
import unicodedata

R = '/home/user/owltiger1021/'
REF = R + 'tools/reference/soumatome-n3-kanji.csv'

# リストの書き方をそろえる。
#   〇〇化・～冊・1対2 … 語形を示す記号。外して見る
#   昨日／昨日 … 読みが2つある書き方。「／」で分ける
#   緑（色）・（お）祭り … かっこは任意の部分。付き／無しの両方で見る
STRIP = str.maketrans('', '', '〇～　 ')


def variants(w):
    """その語として認めてよい書き方を すべて返す"""
    out = set()
    for part in w.split('／'):
        part = part.strip()
        if not part:
            continue
        part = re.sub(r'^\d+対\d+$', '対', part)          # 1対2 → 対
        for base in (part.translate(STRIP),
                     re.sub(r'[（(].*?[）)]', '', part.translate(STRIP)),
                     re.sub(r'[（()）]', '', part.translate(STRIP))):
            if not base:
                continue
            # 御 と ご は 同じ（データは「朝御飯」、本は「朝ご飯」と書く）。
            # 語の途中にも出るので、頭だけでなく 全部を入れ替えて見る。
            for x in {base, base.replace('御', 'ご'), base.replace('ご', '御')}:
                out.add(x)
                # お／ご／御 を外した形（お湯→湯、ご飯→飯、ご存じ→存じ）
                out.add(re.sub(r'^(お|ご|御)', '', x))
                # 「する」を外した形（保存する→保存）
                out.add(re.sub(r'する$', '', x))
    return {x for x in out if x}


# 骨組みが漢字1字のものは、機械では判断できません。
#   「曲がる」はデータの「曲る」と同じ語だが、「曲」（きょく＝音楽）は別の語。
#   骨組みはどちらも「曲」なので、機械では見分けられない。
# そこで**目で1つずつ見て**、同じ語だと確かめた分だけ ここに書いています。
# ここに無い1字ものは「無い」に数えます（見落としを出す側より、多めに出す側に寄せる）。
SAME_BY_EYE = {
    '〇〇化',      # データ「〜化」
    '他の',        # データ「他」
    '汗をかく',    # データ「汗」（言い回しで、語としては ある）
    '曲がる',      # データ「曲る」（送りがなのちがい）
    '存じません',  # データ「ご存じ」
    'ご存じです',  # データ「ご存じ」
    '～両',        # データ「両〜」
    '終わる',      # データ「終る」（送りがなのちがい）
    '答え',        # データ「答」（こたえ・N4）
}


def skeleton(w):
    """漢字だけを取り出した形。送りがなの書き方のちがいを 吸収するため。

    支払い と 支払、答え と 答、お湯 と 湯 は、**同じ語を別の書き方で**
    書いたもので、無いわけではない。ここを見ないと「無い」を数えすぎる
    （最初に 170語と出したが、実際はこの分だけ多かった）。
    """
    return ''.join(c for c in w if '\u4e00' <= c <= '\u9fff')


def load_ref():
    ls = [l.rstrip('\n') for l in io.open(REF, encoding='utf-8') if l.strip()]
    cur, rows = None, []
    for l in ls[1:]:                                      # 1行目は見出し
        f = l.split(',')
        if len(f) == 3:
            cur, w = f[1], f[2]
        elif len(f) == 2:
            cur, w = f[0], f[1]
        else:
            w = f[0]
        rows.append((cur, w))
    return rows


def main():
    show = '--list' in sys.argv
    rows = load_ref()

    kd = json.load(io.open(R + 'kanji-data.json', encoding='utf-8'))['kanji']
    vw = json.load(io.open(R + 'vocab-data.json', encoding='utf-8'))['words']
    HAVE_K = {k['character']: k['level'] for k in kd}
    COURSE = {c for c, lv in HAVE_K.items() if lv in ('N5', 'N4', 'N3')}
    HAVE_V, HAVE_SK = set(), {}
    for w in vw:
        HAVE_V |= variants(w['word'])
        sk = skeleton(w['word'])
        if sk:
            HAVE_SK.setdefault(sk, w['word'])

    # ---- ① ② 漢字 ----
    ks = []
    for k, _ in rows:
        if k and k not in ks:
            ks.append(k)
    nodata = [k for k in ks if k not in HAVE_K]
    outside = [k for k in ks if k in HAVE_K and k not in COURSE]

    print('\n■ 『日本語総まとめ N3』巻末リスト と システムの突き合わせ')
    print('  リストの漢字 %d字 ／ 熟語・言葉 のべ%d件' % (len(ks), len(rows)))
    print('  システムの漢字 %d字（うち N5+N4+N3 が %d字）／ 語彙 %d語'
          % (len(HAVE_K), len(COURSE), len(vw)))

    print('\n① 漢字データに 無い字：%d字' % len(nodata))
    if nodata:
        print('   ' + '　'.join(nodata))
    print('② データにはあるが、30週で習う範囲（N5+N4+N3）の外：%d字' % len(outside))
    if outside:
        for k in outside:
            print('   %s（%s）' % (k, HAVE_K[k]))

    # ---- ③ 熟語・言葉 ----
    miss, diff, seen = [], [], set()
    for k, w in rows:
        if w in seen:
            continue
        seen.add(w)
        if variants(w) & HAVE_V:
            continue
        sk = skeleton(w)
        # 漢字1字だけの骨組みは、あてになりません。
        #   「石けん」の骨組みは「石」で、データの「石」（いし）に当たってしまう。
        #   「曲がる」も「曲る」ではなく「曲」に当たる。
        # そこで2字以上に限り、1字のものは手で見た分だけ SAME に書いています。
        if w in SAME_BY_EYE:
            continue
        if sk and len(sk) >= 2 and sk in HAVE_SK:
            diff.append((k, w, HAVE_SK[sk]))      # あるが 書き方がちがうだけ
        else:
            miss.append((k, w))
    print('\n③ 語彙データに 無い 熟語・言葉：%d語（リストの重複なし %d語のうち）'
          % (len(miss), len(seen)))
    if show:
        for k, w in miss:
            print('   %-4s %s' % (k or '', w))
    else:
        print('   （--list を付けると 全部出ます）')
        for k, w in miss[:30]:
            print('   %-4s %s' % (k or '', w))
        if len(miss) > 30:
            print('   … ほか %d語' % (len(miss) - 30))
    print('\n④ あるが、書き方が ちがうだけ：%d語（足す必要は ありません）' % len(diff))
    for k, w, h in (diff if show else diff[:12]):
        print('   リスト「%s」　→　データ「%s」' % (w, h))
    if not show and len(diff) > 12:
        print('   … ほか %d語' % (len(diff) - 12))

    print('\n' + '=' * 62)
    print('漢字：無い %d字／範囲外 %d字　　語彙：無い %d語（書き方ちがい %d語は別）' %
          (len(nodata), len(outside), len(miss), len(diff)))
    print('=' * 62)
    print('※ ここで「無い」と出ても、入れるべきとは限りません。'
          '助数詞（～冊・～個）は語形成、文型と重なる語は文型で教えています。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
