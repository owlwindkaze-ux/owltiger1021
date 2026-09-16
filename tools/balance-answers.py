# -*- coding: utf-8 -*-
"""4択問題の「答えの番号」のかたよりを直す。

  python3 tools/balance-answers.py [--dry]

文も、正解の中身も 変えない。選択肢の並びだけを 入れかえる。
番号の少ないものから順に当て、同じ番号が3回続かないようにする。
数や金額が 小さい順に並んでいる選択肢は、並べかえると 不自然なので さわらない。

ずっと同じ番号を押すと どれだけ当たるかを、直す前と後で 出す。
"""
import json, io, re, os, sys, glob, collections

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
DRY = '--dry' in sys.argv
NUMONLY = re.compile(r'^[0-9,０-９]+\s*(円|番|日|人|名|時|分|回|点)?$')

def orderly(ch):
    vals = []
    for c in ch:
        c = c.strip()
        if not NUMONLY.match(c): return False
        vals.append(int(re.sub(r'[^0-9]', '', c) or 0))
    return vals == sorted(vals) and len(set(vals)) == len(vals)

def run(qs, get, setter):
    """qs: 問題のリスト。get(q)->(choices, answer)、setter(q, choices, answer)"""
    cnt = collections.Counter(); last = []; moved = skipped = 0
    for q in qs:
        ch, ans = get(q)
        if orderly(ch):
            cnt[ans] += 1; last = (last + [ans])[-2:]; skipped += 1; continue
        n = len(ch)
        cand = sorted(range(n), key=lambda i: (cnt[i], i))
        pick = next((i for i in cand if not (len(last) == 2 and last[0] == last[1] == i)), cand[0])
        if pick != ans:
            ch = list(ch); ch[ans], ch[pick] = ch[pick], ch[ans]
            setter(q, ch, pick); ans = pick; moved += 1
        cnt[ans] += 1; last = (last + [ans])[-2:]
    return moved, skipped

def report(name, qs, get):
    c = collections.Counter(get(q)[1] for q in qs)
    n = len(qs)
    best = max(c.values()) if c else 0
    return '%-26s %3d問  %s  同じ番号を押し続けたときの最高 %d問（%d%%）' % (
        name, n, dict(sorted(c.items())), best, round(best / n * 100) if n else 0)

total_moved = 0
for f in sorted(glob.glob(R + 'bunpo/grammar-*.json')):
    j = json.load(io.open(f, encoding='utf-8'))
    qs = [q for g in j['grammar'] for q in g.get('quiz', []) if q['type'] == 'choice']
    get = lambda q: (q['choices'], q['answer'])
    def setter(q, ch, a): q['choices'] = ch; q['answer'] = a
    print('前 ' + report(os.path.basename(f), qs, get))
    m, s = run(qs, get, setter)
    print('後 ' + report(os.path.basename(f), qs, get) + '  ／ 並べかえ %d問' % m)
    total_moved += m
    if not DRY:
        json.dump(j, io.open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('\n並べかえた問題', total_moved, '問', '（--dry なので書き込んでいません）' if DRY else '')
