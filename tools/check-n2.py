# -*- coding: utf-8 -*-
"""N2ロードマップの中身を、期ごとに点検する。

  python3 tools/check-n2.py

見るところ
  A 期ごとの中身   …… 各期に何が置いてあるか。空の週・二重に配った教材がないか
  B 問題そのもの   …… 答えの番号・選択肢の重複・説明の有無・日本語以外の文字
  C 模試           …… 3回で問題が重ならないか。模試の読解が「初見」か
  D レベル         …… 模試に出す語・文型・聴解が N2 のものか
  E 週の分量       …… 1週にのせた量が 現実的か
"""
import json, io, re, os, sys, collections

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
ng_all = []
def ng(sec, msg): ng_all.append('[%s] %s' % (sec, msg))

J = lambda p: json.load(io.open(R + p, encoding='utf-8'))
W = J('n2/weeks.json')
READ = J('dokkai/reading-n2.json')['passages']
GRAM = J('bunpo/grammar-n2.json')['grammar']
VOC = {w['word']: w for w in J('vocab-data.json')['words']}
html = io.open(R + 'choukai/index.html', encoding='utf-8').read()
a = html.index('const DATA = ['); b = html.index('\n];', a)
CHOU = json.loads(html[a + len('const DATA = '):b + 2])
MOSHI = [J('moshi/moshi-%d.json' % n) for n in (1, 2, 3)]

# 日本語の欄で 本当に困るのは「よその国の文字」が混ざること。
# 時刻の「10:00」や「1,500」、矢印や丸かっこは ふつうに使うので 通す。
FOREIGN = re.compile(r'[\u0400-\u04ff\uac00-\ud7af\u0e00-\u0e7f\u0600-\u06ff'
                     r'\u0370-\u03ff\u0530-\u058f\u0900-\u097f]')
JA_OK = lambda s: not FOREIGN.search(str(s))

print('=' * 66)
print('A 期ごとの中身')
print('=' * 66)
for ph in W['phases']:
    ws = list(range(ph['from'], ph['to'] + 1))
    # 「やることが無い週」＝ 行も無く、漢字・語彙・文型の割り当ても無い週。
    # 第1期は 漢字19字・語彙103語・文型10項目が その週の仕事なので、
    # 行が無くても 空ではない。
    empty = [w for w in ws if not W['task'].get(str(w))
             and not any(W['counts'][str(w)].values())]
    kinds = collections.Counter()
    for w in ws:
        for t in W['task'].get(str(w), []):
            if t.startswith('読解'): kinds['読解'] += 1
            elif t.startswith('聴解'): kinds['聴解'] += 1
            elif '模試' in t: kinds['模試'] += 1
            else: kinds['そのほか'] += 1
    kanji = sum(W['counts'][str(w)]['k'] for w in ws)
    vocab = sum(W['counts'][str(w)]['v'] for w in ws)
    gram = sum(W['counts'][str(w)]['g'] for w in ws)
    print('第%d期 %s（第%d〜%d週・%d週）' % (ph['no'], ph['name'], ph['from'], ph['to'], len(ws)))
    print('   ねらい: %s' % ph['aim'])
    print('   漢字%d字 語彙%d語 文型%d項目 ／ 行の数 %s'
          % (kanji, vocab, gram, dict(kinds)))
    if empty: ng('A', '第%d期に やることの無い週: %s' % (ph['no'], empty))
    # 各期に「その期のねらいに合うもの」があるか
    if ph['no'] in (2,) and not kinds['読解']: ng('A', '第2期に読解の行がない')
    if ph['no'] == 3 and not kinds['模試']: ng('A', '第3期に模試の行がない')
    if ph['no'] == 4 and not (kinds['読解'] and kinds['聴解']): ng('A', '第4期に読解／聴解の行がない')

# 教材を二重に配っていないか（読解の題）
titles = collections.Counter()
for w in range(1, 67):
    for t in W['task'].get(str(w), []):
        m = re.match(r'読解 N2を1本（.+?「(.+?)」', t)
        if m: titles[m.group(1)] += 1
dup = {k: v for k, v in titles.items() if v > 1}
print('\n読解の題を 何回 配ったか: 1回だけ %d本 ／ 2回以上 %d本' % (sum(1 for v in titles.values() if v == 1), len(dup)))
if dup: print('   2回以上:', dup)

print()
print('=' * 66)
print('B 問題そのもの（答えの番号・選択肢・説明・文字）')
print('=' * 66)

CJK = re.compile(r'[\u3040-\u30ff\u4e00-\u9fff]')

def check_q(tag, q, choices, ans, exps, pos, id_exps=()):
    """exps は日本語の説明、id_exps はインドネシア語の説明。
       日本語の欄にローマ字の記号が混ざる／インドネシア語の欄に
       かな漢字が混ざるのは、書きまちがいなので見つける。"""
    if not (0 <= ans < len(choices)): ng('B', tag + ' 答えが範囲外')
    if len(set(choices)) != len(choices): ng('B', tag + ' 選択肢が重複: ' + str(choices))
    if any(c != c.strip() for c in choices): ng('B', tag + ' 選択肢の前後に空白')
    if not any(exps) and not any(id_exps): ng('B', tag + ' 説明がない')
    for s in [q] + list(choices) + [e for e in exps if e]:
        if s and not JA_OK(s):
            ng('B', tag + ' 日本語の欄に よその国の文字: ' + repr(FOREIGN.findall(str(s))[:6]))
    for s in [e for e in id_exps if e]:
        if CJK.search(str(s)):
            ng('B', tag + ' インドネシア語の欄に かな漢字: ' + repr(CJK.findall(str(s))[:6]))
    pos[ans] += 1

for name, items in (('読解N2', None), ):
    pass
pos = collections.Counter()
for p in READ:
    for i, q in enumerate(p['questions']):
        check_q('読解 %s#%d' % (p['id'], i + 1), q['q'], q['choices'], q['answer'], [q.get('explain')], pos)
print('読解N2 %d問  答えの位置 %s' % (sum(pos.values()), dict(sorted(pos.items()))))

pos = collections.Counter()
for part in CHOU:
    for i, it in enumerate(part['items']):
        check_q('聴解 %s#%d' % (part['no'], i + 1), it['q'], it['opts'], it['ans'],
                [it.get('exp')], pos, [it.get('expId')])
        src = part['items'][it['sameAudioAs']] if it.get('sameAudioAs') is not None else it
        if not src.get('show'): ng('B', '聴解 %s#%d 台本の表示がない' % (part['no'], i + 1))
print('聴解   %d問  答えの位置 %s' % (sum(pos.values()), dict(sorted(pos.items()))))

pos = collections.Counter()
for g in GRAM:
    for i, q in enumerate(g.get('quiz', [])):
        if q['type'] != 'choice': continue
        check_q('文型 %s#%d' % (g['id'], i + 1), q['q'], q['choices'], q['answer'],
                [q.get('explain_id')], pos)   # 文型の explain_id は日本語で書いてある 
print('文型N2 %d問  答えの位置 %s' % (sum(pos.values()), dict(sorted(pos.items()))))

print()
print('=' * 66)
print('C 模試（3回で重ならないか・初見か）')
print('=' * 66)
seen_q, seen_read, seen_chou = collections.Counter(), collections.Counter(), collections.Counter()
for m in MOSHI:
    pos = collections.Counter(); n = 0
    for key in m['order']:
        s = m['sections'][key]
        if 'read' in s:
            for r in s['read']:
                seen_read[r['passage']['id']] += 1
                for qi in r['qi']:
                    q = r['passage']['questions'][qi]
                    seen_q[(r['passage']['id'], qi)] += 1
                    pos[q['answer']] += 1; n += 1
        else:
            for i, it in enumerate(s['items']):
                key2 = it.get('part', key) + '/' + str(it.get('i', i))
                if 'part' in it: seen_chou[key2] += 1
                ans = it.get('ans', it.get('answer'))
                ch = it.get('opts', it.get('choices'))
                check_q('模試%d %s#%d' % (m['no'], key, i + 1), it['q'], ch, ans,
                        [it.get('exp'), it.get('explain')], pos,
                        [it.get('explain_id'), it.get('expId')])
                n += 1
    print('第%d回 %d問  答えの位置 %s  区分 %s'
          % (m['no'], n, dict(sorted(pos.items())), m['counts']))
    lo = min(pos.values()); hi = max(pos.values())
    if hi > lo * 2: ng('C', '第%d回 答えの番号が かたよっている %s' % (m['no'], dict(pos)))

d1 = {k: v for k, v in seen_q.items() if v > 1}
d2 = {k: v for k, v in seen_chou.items() if v > 1}
print('読解の設問が2回以上出た:', d1 if d1 else 'なし')
print('聴解の問題が2回以上出た:', d2 if d2 else 'なし')
if d1: ng('C', '模試で同じ読解の設問を2回出している')
if d2: ng('C', '模試で同じ聴解の問題を2回出している')

# 模試の読解が、その時点で「初見」か
studied_before_40 = set()
for w in range(1, 40):
    for t in W['task'].get(str(w), []):
        m2 = re.match(r'読解 N2を1本（.+?「(.+?)」', t)
        if m2: studied_before_40.add(m2.group(1))
bad = [pid for pid in seen_read
       if next(p['title'] for p in READ if p['id'] == pid).split('《')[0] in
       {t.split('《')[0] for t in studied_before_40}]
print('模試の読解のうち、第40週までに読んでいたもの:', bad if bad else 'なし（すべて初見）')
if bad: ng('C', '模試の読解が初見でない: %s' % bad)

print()
print('=' * 66)
print('D レベル（模試に出るものが N2 か）')
print('=' * 66)
lv = collections.Counter(); notn2 = []
for m in MOSHI:
    for key in ('問題1', '問題2', '問題5', '問題6'):
        for it in m['sections'][key]['items']:
            w = re.search(r'「(.+?)」', it.get('explain', '') or '')
            if not w: continue
            word = w.group(1)
            if word in VOC:
                lv[VOC[word]['level']] += 1
                if VOC[word]['level'] != 'N2': notn2.append(word)
print('模試の文字・語彙で使った語のレベル:', dict(lv))
if notn2: ng('D', 'N2でない語を使っている: %s' % sorted(set(notn2)))
parts_used = set()
for m in MOSHI:
    for key in ('聴解1', '聴解2', '聴解3', '聴解4', '聴解5'):
        for it in m['sections'][key]['items']: parts_used.add(it['part'])
lvs = {p['no']: p['level'] for p in CHOU}
bad = [p for p in parts_used if lvs.get(p) != 'N2']
print('模試の聴解で使ったパート:', sorted(parts_used, key=lambda x: int(x.split()[1])))
print('  そのうち N2でないもの:', bad if bad else 'なし')
if bad: ng('D', '模試の聴解に N2以外のパートが入っている: %s' % bad)

print()
print('=' * 66)
print('E 週の分量')
print('=' * 66)
heavy = []
for w in range(1, 67):
    c = W['counts'][str(w)]
    lines = len(W['task'].get(str(w), []))
    # 平日5日でならした1日の量
    per = c['k'] / 5.0 + c['v'] / 5.0 * 0.3 + c['g'] / 5.0
    if c['k'] > 25 or c['v'] > 130 or c['g'] > 15: heavy.append((w, c, lines))
print('1週の上限（漢字25字・語彙130語・文型15項目）を超えた週:', len(heavy))
for w, c, lines in heavy[:8]: print('   第%d週 %s 行%d' % (w, c, lines))
mx = max(range(1, 67), key=lambda w: W['counts'][str(w)]['v'])
print('いちばん語彙の多い週: 第%d週 %s' % (mx, W['counts'][str(mx)]))

print()
print('=' * 66)
print('結果：おかしいところ %d件' % len(ng_all))
for x in ng_all: print('  -', x)
print('=' * 66)
sys.exit(1 if ng_all else 0)
