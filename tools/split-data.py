#!/usr/bin/env python3
"""漢字・熟語のデータを、レベルごとのファイルに分ける。

なぜ分けるか
  画面は「いま見るレベル」だけを先に読み込む。全部を1つのファイルにしていると、
  N5だけ勉強したい人の端末にも、N3やN2のデータが毎回届いてしまう。

編集のしかた
  1. 中身を直すときは、まとめ役のファイル（kanji-data.json / vocab-data.json）を直す
  2. このスクリプトを走らせる  →  python3 tools/split-data.py
  3. kanji.json・kanji-n5.json… / vocab.json・vocab-n5.json… が作り直される

レベルを増やすとき（N2など）
  まとめ役のファイルに level:"N2" の項目を足して、このスクリプトを走らせるだけ。
  画面側（kanji.html）は目次を見て動くので、直す必要はない。
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ['N5', 'N4', 'N3', 'N2', 'N1', '介護', '現場', '記録']
SLUG = {'N5': 'n5', 'N4': 'n4', 'N3': 'n3', 'N2': 'n2', 'N1': 'n1',
        '介護': 'kaigo', '現場': 'genba', '記録': 'kiroku'}
VER = '2026-09-14b'


def split(master, key, prefix, index_name):
    src = json.load(open(os.path.join(ROOT, master), encoding='utf-8'))
    items = src[key]
    levels = [lv for lv in ORDER if any(x['level'] == lv for x in items)]
    unknown = sorted({x['level'] for x in items} - set(levels))
    if unknown:
        sys.exit('レベルの並び順に無い値があります: %s（tools/split-data.py の ORDER に足してください）' % unknown)

    files = []
    for lv in levels:
        group = [x for x in items if x['level'] == lv]
        name = '%s-%s.json' % (prefix, SLUG[lv])
        with open(os.path.join(ROOT, name), 'w', encoding='utf-8') as f:
            json.dump({'level': lv, 'count': len(group), key: group}, f, ensure_ascii=False)
        # 1つの字が2つの札を持つことがある（例：「浴」＝介護でもありN2でもある）。
        # その字は level のファイルに入るので、どのファイルに「よその札」が混ざって
        # いるかを目次に書いておく。画面はこれを見て、必要なファイルも読む。
        extra = sorted({a for x in group for a in x.get('also', [])})
        rec = {'file': name, 'level': lv, 'count': len(group)}
        if extra:
            rec['extra'] = extra
            rec['extra_count'] = {a: sum(1 for x in group if a in x.get('also', [])) for a in extra}
        files.append(rec)
        print('  %-18s %5d件  %5.0f KB' % (name, len(group), os.path.getsize(os.path.join(ROOT, name)) / 1024))

    index = {k: v for k, v in src.items() if k != key}
    index['files'] = files
    index['total'] = len(items)
    # 札ごとの本当の数（よその札で入ってくる字も足したもの）
    totals = {}
    for lv in levels:
        totals[lv] = sum(1 for x in items if x['level'] == lv or lv in x.get('also', []))
    for x in items:
        for a in x.get('also', []):
            totals.setdefault(a, sum(1 for y in items if y['level'] == a or a in y.get('also', [])))
    index['level_totals'] = totals
    index['app_version'] = VER
    index['note'] = (index.get('note', '') +
                     ' レベルごとのファイルに分けてあり、使うレベルから順に読み込みます。'
                     ' 中身を直すときは %s を直して tools/split-data.py を走らせてください。' % master).strip()
    with open(os.path.join(ROOT, index_name), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print('  %-18s 目次 %d バイト' % (index_name, os.path.getsize(os.path.join(ROOT, index_name))))


print('漢字')
split('kanji-data.json', 'kanji', 'kanji', 'kanji.json')
print('熟語')
split('vocab-data.json', 'words', 'vocab', 'vocab.json')
print('できました。')
