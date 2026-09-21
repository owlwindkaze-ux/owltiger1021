# -*- coding: utf-8 -*-
"""文章の文法の問題を点検する。

    python3 tools/check-bunshou.py

見るところ
  ① 本文の空欄の数と、設問の数が 合っているか
  ② 空欄の番号が 1から順に 並んでいるか
  ③ 設問の「（　１　）」が 本文の空欄と 対応しているか
  ④ 選択肢が4つか・同じ選択肢が無いか・正解の番号が 範囲内か
  ⑤ 正解の番号の かたより
  ⑥ 本文の長さ（公式の目安：N4は短め、N3 約300字、N2 約450字）
  ⑦ 日本語以外の文字
  ⑧ 解説（日本語・インドネシア語）が 入っているか
"""
import json, io, os, re, sys, collections

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
D = json.load(io.open(R + 'bunpo/bunshou.json', encoding='utf-8'))
ps = D['passages']

BAD = re.compile(r'[Ѐ-ӿ가-힯ऀ-ॿ฀-๿؀-ۿ]')
NUM = '０１２３４５６７８９'
bad = []
ans = collections.Counter()
lv = collections.Counter()

print('■ 本文と 設問')
for pi, p in enumerate(ps, 1):
    body = p['text']
    holes = re.findall(r'（\s*([０-９0-9]+)\s*）', body)
    n = len(body) - len(re.findall(r'[\n　]', body))
    lv[p['lv']] += 1
    print('%2d [%s] %-16s 本文 %3d字　空欄 %d　設問 %d'
          % (pi, p['lv'], p['title'], n, len(holes), len(p['items'])))
    if len(holes) != len(p['items']):
        bad.append('%s：空欄 %d個 と 設問 %d個が 合わない' % (p['title'], len(holes), len(p['items'])))
    want = [NUM[i + 1] if i + 1 < 10 else str(i + 1) for i in range(len(holes))]
    if holes != want:
        bad.append('%s：空欄の番号が 順番でない（%s）' % (p['title'], ' '.join(holes)))
    for qi, it in enumerate(p['items'], 1):
        num = re.findall(r'[０-９0-9]+', it['q'])
        if not num or num[0] != (NUM[qi] if qi < 10 else str(qi)):
            bad.append('%s：設問%d の見出し「%s」が 番号と 合わない' % (p['title'], qi, it['q']))
        ch = it['choices']
        if len(ch) != 4:
            bad.append('%s 設問%d：選択肢が %d個' % (p['title'], qi, len(ch)))
        if len(set(ch)) != len(ch):
            bad.append('%s 設問%d：同じ選択肢が ある' % (p['title'], qi))
        if not (0 <= it['answer'] < len(ch)):
            bad.append('%s 設問%d：正解の番号が 範囲の外' % (p['title'], qi))
        else:
            ans[it['answer']] += 1
        if not it.get('explain'):
            bad.append('%s 設問%d：日本語の解説が ない' % (p['title'], qi))
        if not it.get('explain_id'):
            bad.append('%s 設問%d：インドネシア語の解説が ない' % (p['title'], qi))
        if BAD.search(it['explain'] + ''.join(ch)):
            bad.append('%s 設問%d：日本語以外の文字' % (p['title'], qi))
    if BAD.search(body):
        bad.append('%s：本文に 日本語以外の文字' % p['title'])

tot = sum(ans.values())
print()
print('■ 数')
print('  本文', len(ps), '　レベル別', dict(lv), '　設問', tot)
print('  正解の番号', dict(sorted(ans.items())),
      '（いちばん多い番号は %d%%）' % round(100 * max(ans.values()) / tot))
print()
print('=' * 60)
print('直さないといけない所:', len(bad))
for b in bad: print('  -', b)
print('=' * 60)
sys.exit(1 if bad else 0)
