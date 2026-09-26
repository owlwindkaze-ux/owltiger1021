#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""漢字データに 字を足す。

**なぜ必要になったか**
『日本語総まとめ N3』巻末リストと突き合わせたところ、リストの470字のうち
**29字が `kanji-data.json` に無い**ことが分かった（2026-09-26）。しかも
そのうち26字は、**すでにコースの語彙で使っている**。
「暑い」「授業」「結婚」はN5、「案内」「無理」はN4の語なのに、
**その字の札が1枚も無い**状態だった。

**どこから取るか**
`kanji-data.json` の `sources` に書いてあるのと同じところから取ります。
勝手に書くと、ほかの1,066字と 質がそろいません。

  読み・意味・画数  KANJIDIC2 / kanji-data（CC BY-SA 4.0）
  部首              Kanji alive（CC BY 4.0）
  書き順            KanjiVG（CC BY-SA 3.0）

**インドネシア語の意味（`meanings_id`）だけは、元データにありません。**
1,066字ぜんぶに入っていて、無いと実習生の画面が英語だけになります
（`meanOf` が英語に落ちる）。そこで **この中に手で書いてあります**（`MEAN_ID`）。
字を増やすときは、ここにも書いてください。**書いたら人が読んで確かめること。**

**足すもの**
  kanji-data.json    字の札（読み・意味・画数・部首・用例）
  kanji-strokes.json 書き順（これを忘れると、その字だけ書き順が出ない）
  kanji-n3.json など レベル別ファイル（split-data.py が作り直す）

  python3 tools/add-kanji.py 暑 授 結 案 無 価 独          # 何をするかだけ
  python3 tools/add-kanji.py --write 暑 授 結 案 無 価 独   # 書きこむ

そのあと必ず：

  python3 tools/split-data.py
  python3 tools/build-weeks.py
  python3 tools/check-numbers.py
"""
import io
import json
import os
import re
import sys
import urllib.request

R = '/home/user/owltiger1021/'
KD = R + 'kanji-data.json'
KS = R + 'kanji-strokes.json'
CACHE = '/tmp/addkanji'
SRC = 'https://raw.githubusercontent.com/davidluzgouveia/kanji-data/master/kanji.json'
KA = ('https://raw.githubusercontent.com/kanjialive/kanji-data-media/master/'
      'language-data/ka_data.csv')
VG = 'https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/%05x.svg'

# インドネシア語の意味。英語の意味と 1つずつ 対にして 手で書いたもの。
MEAN_ID = {
    '暑': ['panas (udara)', 'terik', 'panasnya musim panas'],
    '授': ['memberikan', 'mengajar', 'menganugerahkan'],
    '結': ['mengikat', 'menyimpulkan', 'perjanjian'],
    '案': ['rencana', 'usulan', 'rancangan'],
    '無': ['tidak ada', 'nihil', 'tanpa'],
    '価': ['nilai', 'harga'],
    '独': ['sendiri', 'seorang diri', 'dengan sendirinya'],
}


def get(url, name):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        with urllib.request.urlopen(url, timeout=120) as r:
            io.open(p, 'wb').write(r.read())
    return io.open(p, 'rb').read()


def strokes_of(ch):
    """KanjiVG から 書き順の path を 取り出す。

    KanjiVG のファイルには、部品ごとの <g> と 1画ずつの <path> が入っている。
    要るのは path の d だけ。出てくる順が 書く順。
    """
    svg = get(VG % ord(ch), '%05x.svg' % ord(ch)).decode('utf-8')
    m = re.search(r'viewBox="([^"]+)"', svg)
    vb = m.group(1) if m else None
    ds = re.findall(r'<path[^>]*\sd="([^"]+)"', svg)
    return vb, ds


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    write = '--write' in sys.argv
    if not args:
        print(__doc__)
        return 1
    chars = [c for a in args for c in a]

    kd = json.load(io.open(KD, encoding='utf-8'))
    have = {k['character'] for k in kd['kanji']}
    ks = json.load(io.open(KS, encoding='utf-8'))

    src = json.loads(get(SRC, 'kanji.json').decode('utf-8'))
    import csv
    ka = {r['kanji']: r for r in csv.DictReader(
        io.StringIO(get(KA, 'ka_data.csv').decode('utf-8')))}

    add, skip, bad = [], [], []
    for ch in chars:
        if ch in have:
            skip.append(ch)
            continue
        s = src.get(ch)
        if not s:
            bad.append((ch, '元データに無い'))
            continue
        vb, ds = strokes_of(ch)
        if vb != ks['viewBox']:
            bad.append((ch, 'viewBox が ちがう（%s）' % vb))
            continue
        if not ds:
            bad.append((ch, '書き順が 取れない'))
            continue
        if s.get('strokes') and len(ds) != s['strokes']:
            bad.append((ch, '画数が 合わない（元 %s／書き順 %d）'
                        % (s['strokes'], len(ds))))
            continue
        r = ka.get(ch)
        if not r or not r.get('rad_name_ja'):
            bad.append((ch, '部首が 取れない（部首でしぼる欄から 落ちる）'))
            continue
        if ch not in MEAN_ID:
            bad.append((ch, 'インドネシア語の意味が 書いていない'
                            '（tools/add-kanji.py の MEAN_ID に足すこと）'))
            continue
        # 元データの並びを、いまの kanji-data.json の形に そろえる
        ent = {
            'character': ch,
            'level': 'N3',                 # 総まとめ N3 の巻末リストの字
            'strokes': s.get('strokes'),
            'grade': s.get('grade'),
            'freq': s.get('freq'),
            'on': s.get('readings_on', []),
            'kun': s.get('readings_kun', []),
            'meanings': s.get('meanings', []),
            # 部首の字は、元データのまま入れる。private use の字（いとへんなど）も
            # 既にある1,066字が同じものを持っているので、そろえないと
            # 「部首でしぼる」で 別のかたまりに なってしまう。
            'radical': {'character': r['radical'],
                        'name': r['rad_name_ja'],
                        'meaning': r['rad_meaning']},
            'examples': [],                # 用例は下で語彙データから入れる
            'meanings_id': MEAN_ID[ch],
        }
        add.append((ent, ds))

    # 用例は、**すでにこのシステムにある語**から入れる。
    # 外から用例を持ってくると、押しても開かない語が出る（2.6-z11 と同じ失敗）。
    vw = json.load(io.open(R + 'vocab-data.json', encoding='utf-8'))['words']
    LV = {'N5': 0, 'N4': 1, 'N3': 2}
    for ent, _ in add:
        c = ent['character']
        cand = [w for w in vw if c in w['word'] and w['level'] in LV]
        cand.sort(key=lambda w: (LV[w['level']], len(w['word'])))
        for w in cand[:4]:
            ent['examples'].append({
                'word': w['word'], 'reading': w['reading'],
                'meaning': w['meaning'], 'jlpt': w['level'],
                'meaning_id': w.get('meaning_id', ''),
            })

    print('\n■ 漢字データに 足す')
    for ent, ds in add:
        print('  %s  %s画 ／ 音 %s ／ 訓 %s ／ 意味 %s'
              % (ent['character'], ent['strokes'],
                 '・'.join(ent['on']) or '—', '・'.join(ent['kun']) or '—',
                 ', '.join(ent['meanings'][:3])))
        print('      書き順 %d画分 ／ 部首 %s（%s）／ ID %s'
              % (len(ds), ent['radical']['name'], ent['radical']['meaning'],
                 ', '.join(ent['meanings_id'])))
        print('      用例 %s'
              % ('・'.join(e['word'] + '(' + e['jlpt'] + ')'
                           for e in ent['examples']) or 'なし'))
    if skip:
        print('\n  すでにある（何もしない）: ' + '　'.join(skip))
    if bad:
        print('\n  × 足せない:')
        for c, why in bad:
            print('    %s … %s' % (c, why))

    noex = [e['character'] for e, _ in add if not e['examples']]
    if noex:
        print('\n  ⚠ 用例が0の字: ' + '　'.join(noex)
              + '　→ 語彙データに その字を使う語が無い。先に語を足すこと')

    if not write:
        print('\n--write を付けると 書きこみます（いまは 何も 変えていません）')
        return 1 if bad else 0
    if bad:
        print('\n足せないものが あるので 書きこみません')
        return 1

    for ent, ds in add:
        kd['kanji'].append(ent)
        ks['strokes'][ent['character']] = ds
    kd['count'] = len(kd['kanji'])
    json.dump(kd, io.open(KD, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(ks, io.open(KS, 'w', encoding='utf-8'), ensure_ascii=False)
    print('\n書きこみました：漢字 %d字 → %d字' % (len(have), kd['count']))
    print('このあと split-data.py → build-weeks.py → check-numbers.py を通すこと')
    return 0


if __name__ == '__main__':
    sys.exit(main())
