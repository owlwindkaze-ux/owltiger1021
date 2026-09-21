# -*- coding: utf-8 -*-
"""N4到達度判定テストの点検。

判定テストは「教えた範囲だけ」から出さなければ意味がない。
範囲の外の漢字を使っていないか、正解の番号がかたよっていないか、
日本語以外の文字がまぎれていないかを、機械で確かめる。

    node tools/hani/n4hantei-dump.js > /tmp/n4t.json
    python3 tools/hani/n4hantei-check.py /tmp/n4t.json
"""
import json, io, os, re, sys, collections

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
T = json.load(io.open(sys.argv[1] if len(sys.argv) > 1 else '/tmp/n4t.json', encoding='utf-8'))

# ---------- 教えた範囲 ----------
# 漢字の一覧（144字＋102字）だけでは狭すぎる。「先輩」「利用者」「具合」のように、
# 漢字の一覧には無くても 語彙として教えている語が たくさんある。
# 読めるかどうかは「その語を習ったか」で決まるので、
# 教えた語に出てくる漢字も 範囲に入れる。
kan = set()
for f in ('kanji-n5.json', 'kanji-n4.json'):
    j = json.load(io.open(R + f, encoding='utf-8'))
    for k in (j['kanji'] if isinstance(j, dict) else j):
        kan.add(k['character'])
for f in ('vocab-n5.json', 'vocab-n4.json', 'vocab-kaigo.json', 'vocab-genba.json'):
    j = json.load(io.open(R + f, encoding='utf-8'))
    for w in (j['words'] if isinstance(j, dict) and 'words' in j else j):
        for c in w['word']:
            if '\u4e00' <= c <= '\u9fff': kan.add(c)

# 人の名前・地名は、漢字の勉強の対象ではないので 別に許す
NAMES = set('田中山佐藤村鈴木林原井上小川口木下清水')
OK = kan | NAMES

# ---------- 集める ----------
def walk(o, path=''):
    """テストの中の 文字列を すべて 取り出す（説明も 含む）"""
    if isinstance(o, dict):
        for k, v in o.items(): yield from walk(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from walk(v, path + '[%d]' % i)
    elif isinstance(o, str):
        yield path, o

texts = list(walk(T))

# ---------- ① 日本語以外の文字 ----------
BAD = re.compile(r'[Ѐ-ӿ가-힯ऀ-ॿ฀-๿؀-ۿ]')
bad_script = [(p, t) for p, t in texts if BAD.search(t)]

# ---------- ② 範囲の外の漢字 ----------
# 学習者が読むところだけを見る（解説 why は 職員用なので 対象外）
seen = collections.Counter()
where = {}
for p, t in texts:
    # why＝解説、script＝聴解の読み上げ原稿。どちらも 職員が 読むもので、
    # 学習者は 読まない。漢字の範囲の 点検からは 外す。
    if '/why' in p or '/script' in p: continue
    for c in t:
        if '一' <= c <= '鿿' and c not in OK:
            seen[c] += 1
            where.setdefault(c, p)

# ---------- ③ 正解の番号のかたより ----------
def answers(o, acc):
    if isinstance(o, dict):
        if 'ans' in o and isinstance(o['ans'], int): acc.append(o['ans'])
        for v in o.values(): answers(v, acc)
    elif isinstance(o, list):
        for v in o: answers(v, acc)
    return acc
ans = answers(T, [])
dist = collections.Counter(ans)

# ---------- ④ 選択肢の重なり・数 ----------
dup = []
def opts(o, path=''):
    if isinstance(o, dict):
        if 'opts' in o and isinstance(o['opts'], list):
            os_ = o['opts']
            if len(set(os_)) != len(os_): dup.append((path, '同じ選択肢が ある', os_))
            if len(os_) not in (3, 4): dup.append((path, '選択肢が %d個' % len(os_), os_))
            if 'ans' in o and not (0 <= o['ans'] < len(os_)):
                dup.append((path, '正解の番号が 範囲の外', o['ans']))
        for k, v in o.items(): opts(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): opts(v, path + '[%d]' % i)
opts(T)

# ---------- 出す ----------
print('■ 問題数', len(ans))
print('■ 正解の番号', dict(sorted(dist.items())),
      '（%d問中、いちばん多い番号は %d%%）' % (len(ans), round(100 * max(dist.values()) / len(ans))))
print()
print('■ 日本語以外の文字:', len(bad_script))
for p, t in bad_script[:5]: print('   -', p, t[:60])
print()
print('■ 範囲の外の漢字:', len(seen), '字')
for c, n in seen.most_common():
    print('   - %s ×%d　（%s）' % (c, n, where[c]))
print()
print('■ 選択肢のおかしい所:', len(dup))
for d in dup[:10]: print('   -', d)

ng = len(bad_script) + len(dup)
print()
print('=' * 58)
print('直さないといけない所:', ng, '／ 範囲の外の漢字:', len(seen), '字（手で確かめる）')
print('=' * 58)
sys.exit(1 if ng else 0)
