# -*- coding: utf-8 -*-
"""文の文法2（★の組み立て）の問題を点検する。

    python3 tools/check-star.py

見るところ
  ① head＋parts（正しい順）＋tail が、ちゃんとした1文になっているか（目で読む用に出す）
  ② ★の位置が 部品の数の中にあるか
  ③ 部品が 2〜9字か（長すぎ・短すぎは 答えが見えてしまう）
  ④ 同じ部品が2つ以上ないか（並べ替えの答えが1通りに定まらなくなる）
  ⑤ つないだ文型が 文型データにあるか
  ⑥ 日本語以外の文字がまぎれていないか
  ⑦ ★の位置のかたより（ぜんぶ2番目、などになっていないか）
"""
import json, io, os, re, sys, glob, collections

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
D = json.load(io.open(R + 'bunpo/star.json', encoding='utf-8'))
items = D['items']

PAT = set()
for f in glob.glob(R + 'bunpo/grammar-*.json'):
    for g in json.load(io.open(f, encoding='utf-8'))['grammar']:
        PAT.add(g['pattern'])

BAD = re.compile(r'[Ѐ-ӿ가-힯ऀ-ॿ฀-๿؀-ۿ]')

bad = []
star_pos = collections.Counter()
lv = collections.Counter()
print('■ できあがる文（目で読んで確かめてください）')
for i, it in enumerate(items, 1):
    s = it['head'] + ''.join(it['parts']) + it['tail']
    lv[it['lv']] += 1
    star_pos[it['star']] += 1
    print('%3d [%s] %-22s %s' % (i, it['lv'], it['pat'], s))
    if not (0 <= it['star'] < len(it['parts'])):
        bad.append('%d：★の位置が 部品の数の外' % i)
    if len(it['parts']) != 4:
        bad.append('%d：部品が %d個（4個であること）' % (i, len(it['parts'])))
    for p in it['parts']:
        if not (1 <= len(p) <= 9):
            bad.append('%d：部品「%s」の長さが %d字' % (i, p, len(p)))
    if len(set(it['parts'])) != len(it['parts']):
        bad.append('%d：同じ部品が 2つ以上ある（答えが1通りに定まらない）' % i)
    if it['pat'] not in PAT:
        bad.append('%d：文型「%s」が 文型データに無い' % (i, it['pat']))
    if BAD.search(s + it.get('why', '')):
        bad.append('%d：日本語以外の文字' % i)

print()
print('■ 数')
print('  問題', len(items), '　レベル別', dict(lv))
print('  ★の位置', dict(sorted(star_pos.items())),
      '（いちばん多い位置は %d%%）' % round(100 * max(star_pos.values()) / len(items)))
print()
print('=' * 60)
print('直さないといけない所:', len(bad))
for b in bad: print('  -', b)
print('=' * 60)
sys.exit(1 if bad else 0)
