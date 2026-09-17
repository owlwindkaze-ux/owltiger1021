# -*- coding: utf-8 -*-
"""週の割り当て（kanji-weeks.json・bunpo/weeks.json・n2/weeks.json）を、
   割り当ての計算結果（plan.json）から 作り直す。

     node  <新人コースのalloc>  → /tmp/hani/plan.json
     node  <N2コースのalloc>    → /tmp/n2plan/plan.json
     python3 tools/build-weeks.py

   語彙や文型のデータを直したら、かならずこれを通す。
   通さないと、画面の週割りと PDF の範囲表がずれる。
"""
import json, io, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SHINJIN = os.environ.get('SHINJIN_PLAN', '/tmp/hani/plan.json')
N2 = os.environ.get('N2_PLAN', '/tmp/n2plan/plan.json')
for p in (SHINJIN, N2):
    if not os.path.exists(p):
        sys.exit('割り当ての計算結果が ありません: ' + p + '\n  先に alloc を走らせてください。')

H = json.load(io.open(SHINJIN, encoding='utf-8'))          # {kanjiPlan, vocabPlan, gramPlan}
N = json.load(io.open(N2, encoding='utf-8'))               # {plan, PH}
NP = N['plan']

# ---------- 漢字・語彙 ----------
kw = {
 'note': '週ごとの漢字・語彙の割り当て。kanji.html の「今週の分だけ」が読む。'
         'コースは localStorage の jlpt-course で選ぶ。'
         'もとは tools/build-weeks.py（alloc の plan.json から作る）。',
 'courses': {
  'shinjin': {
   'name': '新人コース（12月入職→7月N3）', 'start': '2026-12-07', 'total': 30,
   'kanji': {str(w): [k['character'] for k in H['kanjiPlan'].get(str(w), [])] for w in range(1, 31)},
   'vocab': {str(w): [v['word'] for v in H['vocabPlan'].get(str(w), [])] for w in range(1, 31)},
  },
  'n2': {
   'name': 'N2ロードマップ（2026年9月→2027年12月）', 'start': '2026-08-31', 'total': 66,
   'kanji': {str(w): [k['character'] for k in NP[str(w)]['kanji']] for w in range(1, 67)},
   'vocab': {str(w): [v['word'] for v in NP[str(w)]['vocab']] for w in range(1, 67)},
  }}}
json.dump(kw, io.open(R + 'kanji-weeks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- 文型 ----------
bw = {
 'note': '週ごとの文型の割り当て。bunpo/index.html の「今週の分だけ」が読む。'
         'もとは tools/build-weeks.py。',
 'courses': {
  'shinjin': {
   'name': '新人コース', 'start': '2026-12-07', 'total': 30,
   'weeks': {str(w): [g['id'] for g in H['gramPlan'].get(str(w), [])]
             for w in range(1, 31) if H['gramPlan'].get(str(w))},
  },
  'n2': {
   'name': 'N2ロードマップ', 'start': '2026-08-31', 'total': 66,
   'weeks': {str(w): [g['id'] for g in NP[str(w)]['gram']]
             for w in range(1, 67) if NP[str(w)]['gram']},
  }}}
json.dump(bw, io.open(R + 'bunpo/weeks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- N2の「今週やること」 ----------
nw = json.load(io.open(R + 'n2/weeks.json', encoding='utf-8'))
for w in range(1, 67):
    nw['task'][str(w)] = NP[str(w)]['task']
    nw['counts'][str(w)] = {'k': len(NP[str(w)]['kanji']), 'v': len(NP[str(w)]['vocab']),
                            'g': len(NP[str(w)]['gram'])}
json.dump(nw, io.open(R + 'n2/weeks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- 点検 ----------
VOC = {x['word'] for x in json.load(io.open(R + 'vocab-data.json', encoding='utf-8'))['words']}
KAN = {x['character'] for x in json.load(io.open(R + 'kanji-data.json', encoding='utf-8'))['kanji']}
import glob
GID = set()
for f in glob.glob(R + 'bunpo/grammar-*.json'):
    for g in json.load(io.open(f, encoding='utf-8'))['grammar']: GID.add(g['id'])
bad = []
for cn, c in kw['courses'].items():
    for wk, ws in c['vocab'].items():
        for x in ws:
            if x not in VOC: bad.append('%s第%s週の語「%s」が語彙データに無い' % (cn, wk, x))
    for wk, ks in c['kanji'].items():
        for x in ks:
            if x not in KAN: bad.append('%s第%s週の漢字「%s」が漢字データに無い' % (cn, wk, x))
for cn, c in bw['courses'].items():
    for wk, gs in c['weeks'].items():
        for x in gs:
            if x not in GID: bad.append('%s第%s週の文型「%s」が文型データに無い' % (cn, wk, x))
n_k = sum(len(v) for c in kw['courses'].values() for v in c['kanji'].values())
n_v = sum(len(v) for c in kw['courses'].values() for v in c['vocab'].values())
n_g = sum(len(v) for c in bw['courses'].values() for v in c['weeks'].values())
print('作り直した：漢字 %d字 ／ 語彙 %d語 ／ 文型 %d項目（両コース合計）' % (n_k, n_v, n_g))
print('おかしいところ:', len(bad))
for b in bad[:20]: print('  -', b)
sys.exit(1 if bad else 0)
