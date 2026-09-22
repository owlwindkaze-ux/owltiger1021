# -*- coding: utf-8 -*-
"""画面に書いてある数が、データの数と合っているかを点検する。

この種のずれを何度も出している（入口の「読解45本」「聴解57問」「文型457」、
新人コースの「語彙662語」「文型117項目」、漢字画面の説明文「612字」など）。
教材を足すたびに手で直していると、必ずどこかが残る。ここで一度に点検する。

    python3 tools/check-numbers.py

出るのは「データではこう、画面ではこう」という対応だけ。直すのは手で行う。
"""
import json, io, os, re, glob, sys, collections

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
def L(p): return json.load(io.open(R + p, encoding='utf-8'))

# ---------- データの数を出す ----------
kan = L('kanji-data.json')['kanji']
KC = collections.Counter()
for x in kan:
    KC[x['level']] += 1
    for a in x.get('also', []): KC[a] += 1
KTOTAL = len(kan)

vidx = L('vocab.json')
VTOTAL = sum(f['count'] for f in vidx['files'])
VC = {f['level']: f['count'] for f in vidx['files']}

GC = collections.Counter()
for f in glob.glob(R + 'bunpo/grammar-*.json'):
    for g in L(os.path.relpath(f, R))['grammar']:
        GC[g['level']] += 1
        for a in g.get('also', []): GC[a] += 1
GTOTAL = sum(1 for f in glob.glob(R + 'bunpo/grammar-*.json')
             for g in L(os.path.relpath(f, R))['grammar'])

DB = DQ = 0
for f in sorted(glob.glob(R + 'dokkai/reading-*.json')):
    j = L(os.path.relpath(f, R))
    ps = j['passages'] if isinstance(j, dict) and 'passages' in j else j
    DB += len(ps); DQ += sum(len(p.get('questions', [])) for p in ps)

ch = io.open(R + 'choukai/index.html', encoding='utf-8').read()
CD = json.loads(re.search(r'DATA\s*=\s*(\[[\s\S]*?\n\]);', ch).group(1))
CTOTAL = sum(len(p['items']) for p in CD)
CJLPT = sum(len(p['items']) for p in CD[3:])      # 4つ目からが JLPT形式

n3 = io.open(R + 'n3.html', encoding='utf-8').read()
# 書き方が 2通り混ざっている（"t": "q" と "t":"q"）ので、空白を見ないで数える
NQ = len(re.findall(r'"t"\s*:\s*"q"', n3))

teg = L('tegaki-data.json')
TCHARS = len(teg['chars'])

print('■ データの数')
print('  漢字 %d字  %s' % (KTOTAL, dict(KC)))
print('  語彙 %d語  %s' % (VTOTAL, VC))
print('  文型 %d項目  %s' % (GTOTAL, dict(GC)))
print('  読解 %d本・%d問' % (DB, DQ))
print('  聴解 %d問（うちJLPT形式 %d問）' % (CTOTAL, CJLPT))
print('  100日コース %d問' % NQ)
print('  手書き %d字' % TCHARS)
KAIGO = len(glob.glob(R + 'kaigo/*.pdf'))
print('  紙の教材 %d点' % KAIGO)

# ---------- 画面に書いてある数と突き合わせる ----------
# (ファイル, 探す形, あるべき数, 何の数か)
CHECKS = [
    ('index.html', r'const GTOTAL = (\d+)',        GTOTAL, '文型の合計'),
    ('index.html', r'全(\d+)点 ・ 印刷して実施',      KAIGO,  '紙の教材の点数'),
    ('kaigo/index.html', r'全(\d+)点・印刷して使います', KAIGO, '紙の教材の点数（紙メニュー）'),
    ('index.html', r'文の形。(\d+)文型',             GTOTAL, '文型の合計（説明文）'),
    ('index.html', r'DTOTAL = (\d+)',              DB,     '読解の本数'),
    ('index.html', r'CTOTAL = (\d+)',              CTOTAL, '聴解の問数'),
    ('index.html', r'VTOTAL = (\d+)',              VTOTAL, '語彙の控え'),
    ('index.html', r'読んだ文章 0 / (\d+) 本',      DB,     '読解の本数（表示）'),
    ('index.html', r'答えた問題 0 / (\d+) 問',      CTOTAL, '聴解の問数（表示）'),
    ('index.html', r'読んで答える。(\d+)本・(\d+)問', (DB, DQ), '読解の説明'),
    ('index.html', r'即時応答など\）。(\d+)問',      CTOTAL, '聴解の説明'),
    ('index.html', r'5形式(\d+)問',                CJLPT,  'JLPT形式の問数'),
    ('index.html', r'第1〜14週・([\d,]+)問',        NQ,     '100日コースの問数'),
    ('index.html', r'収録 ([\d,]+)字',              TCHARS, '手書きの字数'),
    ('shinjin/index.html', r"n:'(\d+)項目を8週で'",  GC['N4'], '新人コース N4文型'),
    ('shinjin/index.html', r"n:'(\d+)語を8週で'",    VC['N4'], '新人コース N4語彙'),
    ('shinjin/index.html', r'N4の語彙(\d+)語・文型(\d+)項目',
                                       (VC['N4'], GC['N4']), '新人コース 第2期のねらい'),
    ('shinjin/index.html', r"n:'(\d+)字を4週で一周'", KC['N5'], '新人コース N5漢字'),
    ('shinjin/index.html', r"n:'(\d+)字を8週で'",    KC['N4'], '新人コース N4漢字'),
    ('shinjin/index.html', r"n:'(\d+)字を18週で'",   KC['N3'], '新人コース N3漢字'),
]

bad = []
print('\n■ 画面の数')
for f, pat, want, what in CHECKS:
    s = io.open(R + f, encoding='utf-8').read()
    m = re.search(pat, s)
    if not m:
        bad.append('%s：%s が 見つからない（書き方が変わった？）' % (f, what)); continue
    got = tuple(int(g.replace(',', '')) for g in m.groups())
    wants = want if isinstance(want, tuple) else (want,)
    ok = got == wants
    print('  %-20s %-22s 画面 %s ／ データ %s  %s'
          % (f, what, '・'.join(map(str, got)), '・'.join(map(str, wants)), 'OK' if ok else '←ちがう'))
    if not ok:
        bad.append('%s：%s が 画面 %s ／ データ %s'
                   % (f, what, '・'.join(map(str, got)), '・'.join(map(str, wants))))

print('\n' + '=' * 62)
print('合っていないところ:', len(bad))
for b in bad: print('  -', b)
print('=' * 62)
sys.exit(1 if bad else 0)
