# -*- coding: utf-8 -*-
"""文型データの整合性チェック。 python check.py で実行。"""
import io, json, sys
man = json.load(io.open('grammar.json', encoding='utf-8'))
items, bad = [], []
for f in man.get('files', []):
    try: items += json.load(io.open(f, encoding='utf-8')).get('grammar', [])
    except IOError: bad.append((f, 'ファイルが無い'))
seen = set()
for g in items:
    i = g.get('id', '?')
    if i in seen: bad.append((i, 'idの重複'))
    seen.add(i)
    for k in ('pattern','level','category','form','meaning_id','meaning_en','note_id','note_ja','examples','quiz'):
        if not g.get(k): bad.append((i, '欠落: ' + k))
    for e in g.get('examples', []):
        for k in ('ja','reading','id','en','scene'):
            if not e.get(k): bad.append((i, '例文の欠落: ' + k))
    for q in g.get('quiz', []):
        t = q.get('type')
        if t == 'choice':
            c = q.get('choices', [])
            if len(c) != 4: bad.append((i, '選択肢が4つでない'))
            if len(set(c)) != len(c): bad.append((i, '選択肢の重複'))
            if not isinstance(q.get('answer'), int) or not 0 <= q['answer'] < len(c): bad.append((i, 'answerが範囲外'))
            # 穴埋め（＿＿＿あり）か、「〜のはどれですか。」のような設問文のどちらかであること
            qt = q.get('q', '').strip()
            if '＿＿＿' not in qt and not qt.endswith('か。'): bad.append((i, '空欄記号も設問文もない'))
            if not q.get('explain_id') or not q.get('explain_en'): bad.append((i, '解説の欠落'))
        elif t == 'order':
            if len(q.get('segments', [])) < 3: bad.append((i, 'segmentsが3未満'))
            if not q.get('hint_id') or not q.get('hint_en'): bad.append((i, 'hintの欠落'))
        else: bad.append((i, '未知のtype: %s' % t))
# 日本語・インドネシア語・英語以外の文字（キリル文字などの混入）を検出する
import re
ALLOW = re.compile(r'^[　-〿぀-ゟ゠-ヿ一-鿿＀-￯'
                   r'A-Za-z0-9 .,!?()\[\]:;/\'"~=+_%&#\-→–—…]*$')
for g in items:
    vals = [g.get(k, '') for k in ('pattern','form','meaning_id','meaning_en','note_id','note_en','note_ja')]
    for e in g.get('examples', []): vals += [e.get(k, '') for k in ('ja','reading','id','en','scene')]
    for q in g.get('quiz', []):
        vals += [q.get(k, '') for k in ('q','explain_id','explain_en','hint_id','hint_en')]
        vals += list(q.get('choices', [])) + list(q.get('segments', []))
    for v in vals:
        if isinstance(v, str) and not ALLOW.match(v):
            bad.append((g.get('id','?'), '想定外の文字: ' + v[:30]))

# 日本語の文（ja・reading・q・choices・segments）に英単語が紛れていないか
#   （カタカナ語は問題ないが、"record" のような英単語の書き残しを検出する）
LATIN = re.compile(r'[A-Za-z]{3,}')
for g in items:
    jp = [e.get('ja','') for e in g.get('examples', [])] + [e.get('reading','') for e in g.get('examples', [])]
    for q in g.get('quiz', []):
        jp += [q.get('q','')] + list(q.get('choices', [])) + list(q.get('segments', []))
    for v in jp:
        if isinstance(v, str) and LATIN.search(v):
            bad.append((g.get('id','?'), '日本語文に英単語: ' + v[:30]))

lv = {}
for g in items: lv[g.get('level')] = lv.get(g.get('level'), 0) + 1
print('項目数 %d  %s' % (len(items), lv))
print('例文 %d  問題 %d' % (sum(len(g.get('examples',[])) for g in items),
                            sum(len(g.get('quiz',[])) for g in items)))
print('不備 %d' % len(bad))
for b in bad[:20]: print('  ', b[0], b[1])
sys.exit(1 if bad else 0)
