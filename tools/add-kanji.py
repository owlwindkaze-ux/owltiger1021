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
LEVEL = 'N3'                       # --level= で変える

# ---- 部首 ----
# Kanji alive は **約1,235字しか入っていません**。医療の字（痰・膿・咳・嗽…）は
# 1字も無く、67字のうち47字が落ちました。そこで **KanjiVG の kvg:radical="general"**
# から部首の字を取り、その字を「いま使っている書き方」に直します。
#
# **直さないと「部首でしぼる」が ばらけます。** 既にある1,073字は、いとへんを
# private use の '\ue715' で持っているなど、独特の書き方をしています。
# KanjiVG は '糸' を返すので、そのまま入れると 別のかたまりになってしまいます。
# 下の表は、**既にある1,073字が実際に使っている値**に合わせたものです。
RAD = {
    '月': ('\ue758', 'にくづき', 'meat, flesh'),
    '扌': ('⺘', 'てへん', 'hand'),
    '氵': ('⺡', 'さんずい', 'water'),
    '疒': ('⽧', 'やまいだれ', 'sickness'),
    '口': ('\ue723', 'くちへん', 'mouth'),
    '糸': ('\ue715', 'いとへん', 'thread'),
    '頁': ('⾴', 'おおがい', 'head, page'),
    '言': ('\ue704', 'ごんべん', 'words, to speak, say'),
    '刂': ('⺉', 'りっとう', 'knife, sword'),
    '⻖': ('⻖', 'こざとへん', 'hill, mound'),
    '⻌': ('⻌', 'しんにょう', 'road, walk, to advance'),
    '艹': ('⺾', 'くさかんむり', 'grass'),
    '心': ('⼼', 'こころ', 'heart, mind, spirit'),
    '木': ('\ue720', 'きへん', 'tree, wood'),
    '竹': ('⺮', 'たけかんむり', 'bamboo'),
    '隹': ('⾫', 'ふるとり', 'small bird'),
    '米': ('\ue722', 'こめへん', 'rice'),
    '忄': ('⺖', 'りっしんべん', 'heart, mind, spirit'),
    '彡': ('⼺', 'さんづくり', 'hair-style, light rays'),
    '足': ('⻊', 'あしへん', 'foot, leg'),
    '禾': ('⽲', 'のぎへん', 'grain'),
    '衣': ('⾐', 'ころも', 'clothing'),
    '女': ('\ue732', 'おんなへん', 'woman'),
    '白': ('⽩', 'しろ', 'white'),
    '臣': ('⾂', 'しん', 'retainer, minister'),
    '冖': ('⼍', 'わかんむり', 'cover, crown'),
    '田': ('⽥', 'た', 'rice paddy'),
    '亻': ('⺅', 'にんべん', 'person'),
    '貝': ('\ue716', 'かいへん', 'shell, property, wealth'),
    '尸': ('⼫', 'しかばね', 'corpse, awning'),
    '火': ('⽕', 'ひ', 'fire'),
    '灬': ('⺣', 'れっか', 'fire'),
    '干': ('⼲', 'かん', 'to dry, shield'),
    '亀': ('亀', 'かめ', 'turtle'),
}
# KanjiVG に kvg:radical="general" の印が無い字。手で入れる。
RAD_BY_EYE = {'応': '心', '災': '火', '甲': '田', '為': '灬', '幹': '干'}

MEAN_ID = {
    '暑': ['panas (udara)', 'terik', 'panasnya musim panas'],
    '授': ['memberikan', 'mengajar', 'menganugerahkan'],
    '結': ['mengikat', 'menyimpulkan', 'perjanjian'],
    '案': ['rencana', 'usulan', 'rancangan'],
    '無': ['tidak ada', 'nihil', 'tanpa'],
    '価': ['nilai', 'harga'],
    '独': ['sendiri', 'seorang diri', 'dengan sendirinya'],
    # ---- 記録・申し送りの漢字（2026-09-26c）----
    # 英語の意味と対にして手で書いたもの。元データにインドネシア語は入っていない。
    '痰': ['dahak', 'riak'],
    '診': ['memeriksa (medis)', 'mendiagnosis'],
    '態': ['keadaan', 'sikap', 'bentuk'],
    '検': ['memeriksa', 'pemeriksaan'],
    '膿': ['nanah', 'bernanah'],
    '応': ['menanggapi', 'merespons', 'sesuai'],
    '肢': ['anggota badan (tangan dan kaki)'],
    '咳': ['batuk'],
    '摂': ['mengambil (asupan)', 'mengonsumsi'],
    '第': ['nomor ke-', 'urutan'],
    '納': ['menyerahkan', 'menyimpan', 'membayar'],
    '振': ['mengayunkan', 'menggoyang', 'getaran'],
    '嗽': ['berkumur'],
    '離': ['terpisah', 'melepaskan', 'menjauh'],
    '剥': ['mengelupas', 'terkelupas'],
    '粘': ['lengket', 'kental'],
    '搬': ['mengangkut', 'memindahkan'],
    '顎': ['rahang', 'dagu'],
    '抗': ['melawan', 'anti-'],
    '慢': ['lamban', 'kronis', 'sombong'],
    '濁': ['keruh', 'bunyi bersuara (dakuon)'],
    '影': ['bayangan', 'pengaruh'],
    '撮': ['memotret', 'mengambil gambar'],
    '趾': ['jari kaki'],
    '腸': ['usus'],
    '肪': ['lemak'],
    '陰': ['bayang-bayang', 'negatif', 'tersembunyi'],
    '痕': ['bekas', 'jejak'],
    '創': ['luka', 'menciptakan'],
    '稠': ['kental', 'pekat'],
    '裂': ['robek', 'terbelah'],
    '痒': ['gatal'],
    '掻': ['menggaruk'],
    '緊': ['tegang', 'mendesak', 'darurat'],
    '避': ['menghindar', 'mengungsi'],
    '災': ['bencana', 'musibah'],
    '滑': ['licin', 'tergelincir', 'lancar'],
    '証': ['bukti', 'sertifikat'],
    '腎': ['ginjal'],
    '漏': ['bocor', 'merembes'],
    '嫌': ['tidak suka', 'benci', 'suasana hati'],
    '迫': ['mendesak', 'mendekat'],
    '甲': ['punggung (tangan/kaki)', 'nilai A', 'cangkang'],
    '肛': ['anus', 'dubur'],
    '癒': ['sembuh', 'menyembuhkan'],
    '頻': ['sering', 'berulang kali'],
    '隆': ['menonjol', 'tinggi'],
    '膨': ['menggembung', 'membengkak'],
    '為': ['untuk', 'melakukan', 'demi'],
    '的': ['sasaran', '-nya (akhiran sifat)'],
    '荘': ['vila', 'wisma', 'khidmat'],
    '臥': ['berbaring', 'telentang'],
    '潮': ['pasang surut', 'air laut'],
    '冗': ['berlebihan', 'tidak perlu'],
    '拒': ['menolak', 'menampik'],
    '異': ['berbeda', 'aneh', 'lain'],
    '亀': ['kura-kura', 'penyu'],
    '継': ['melanjutkan', 'mewarisi'],
    '促': ['mendorong', 'mendesak'],
    '頸': ['leher'],
    '貼': ['menempel', 'menempelkan'],
    '幹': ['batang pohon', 'bagian utama'],
    '喀': ['membatukkan keluar', 'mengeluarkan dahak'],
    '渣': ['ampas', 'residu'],
    '菌': ['bakteri', 'kuman', 'jamur'],
    '屈': ['menekuk', 'membungkuk'],
}


def get(url, name):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        with urllib.request.urlopen(url, timeout=120) as r:
            io.open(p, 'wb').write(r.read())
    return io.open(p, 'rb').read()


def radical_of(ch, svg):
    """KanjiVG の kvg:radical="general" から 部首の字を取り、いまの書き方に直す"""
    m = (re.search(r'<g[^>]*kvg:element="([^"]+)"[^>]*kvg:radical="general"', svg)
         or re.search(r'kvg:radical="general"[^>]*kvg:element="([^"]+)"', svg))
    el = m.group(1) if m else RAD_BY_EYE.get(ch)
    if not el:
        return None, '部首の印が KanjiVG に無い（RAD_BY_EYE に足すこと）'
    if el not in RAD:
        return None, '部首「%s」が RAD の表に無い（足すこと）' % el
    c, n, mn = RAD[el]
    return {'character': c, 'name': n, 'meaning': mn}, None


def strokes_of(ch):
    """KanjiVG から 書き順の path を 取り出す。

    KanjiVG のファイルには、部品ごとの <g> と 1画ずつの <path> が入っている。
    要るのは path の d だけ。出てくる順が 書く順。
    """
    svg = get(VG % ord(ch), '%05x.svg' % ord(ch)).decode('utf-8')
    m = re.search(r'viewBox="([^"]+)"', svg)
    vb = m.group(1) if m else None
    ds = re.findall(r'<path[^>]*\sd="([^"]+)"', svg)
    return vb, ds, svg


def main():
    global LEVEL
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    write = '--write' in sys.argv
    # --level=記録 のように レベルの札を指定する（既定は N3）
    for a in sys.argv[1:]:
        if a.startswith('--level='):
            LEVEL = a.split('=', 1)[1]
    # --probe は MEAN_ID を見ずに、元データと書き順が取れるかだけ を見る
    probe = '--probe' in sys.argv
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
        vb, ds, svg = strokes_of(ch)
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
        # 部首は まず Kanji alive、無ければ KanjiVG から
        r = ka.get(ch)
        if r and r.get('rad_name_ja'):
            radical = {'character': r['radical'], 'name': r['rad_name_ja'],
                       'meaning': r['rad_meaning']}
        else:
            radical, why = radical_of(ch, svg)
            if not radical:
                bad.append((ch, why))
                continue
        if not probe and ch not in MEAN_ID:
            bad.append((ch, 'インドネシア語の意味が 書いていない'
                            '（tools/add-kanji.py の MEAN_ID に足すこと）'))
            continue
        # 元データの並びを、いまの kanji-data.json の形に そろえる
        ent = {
            'character': ch,
            'level': LEVEL,
            'strokes': s.get('strokes'),
            'grade': s.get('grade'),
            'freq': s.get('freq'),
            'on': s.get('readings_on', []),
            'kun': s.get('readings_kun', []),
            'meanings': s.get('meanings', []),
            # 部首の字は、元データのまま入れる。private use の字（いとへんなど）も
            # 既にある1,066字が同じものを持っているので、そろえないと
            # 「部首でしぼる」で 別のかたまりに なってしまう。
            'radical': radical,
            'examples': [],                # 用例は下で語彙データから入れる
            'meanings_id': MEAN_ID.get(ch, []),
        }
        add.append((ent, ds))

    # 用例は、**すでにこのシステムにある語**から入れる。
    # 外から用例を持ってくると、押しても開かない語が出る（2.6-z11 と同じ失敗）。
    vw = json.load(io.open(R + 'vocab-data.json', encoding='utf-8'))['words']
    # **どのレベルの語からでも 用例を取る。** 最初は N5/N4/N3 だけにしていたが、
    # 記録の漢字（痰・膿・肢…）は 記録レベルの語にしか出てこないので、
    # **66字のうち33字が用例0**になった。やさしいレベルを先に、短い語を先に出す。
    LV = {'N5': 0, 'N4': 1, 'N3': 2, '介護': 3, '現場': 4, '記録': 5, 'N2': 6}
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

    if probe:
        print('\n（--probe：MEAN_ID は見ていません。書きこみません）')
        return 0
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
