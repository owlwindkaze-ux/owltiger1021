# -*- coding: utf-8 -*-
"""教材に、まぎれては いけない 文字が 入って いないかを 点検する。

    python3 tools/check-script.py

なぜ作ったか
  問題を 書いて いる 途中で、**韓国語・キリル文字・デーバナーガリー文字・英単語**が
  まぎれる ことが **5回** あった（予ते ／ 확認 ／ water ／ closed ／ food ／ бус）。
  どれも 書いた 直後に 気づいて 直したが、**気づかなければ そのまま 実習生に 出る**。
  目で 読んで 見つけるのは 無理なので、機械で 止める。

見るもの
  ① **日本語・ラテン文字いがいの 文字**（韓国語・キリル・タイ・アラビア・デーバナーガリー）。
     これは どの 欄でも まちがい。
  ② **日本語で 書く 欄に まぎれた 英単語**。
     意味・解説の インドネシア語／英語の 欄は 見ない（そこは 英語で 当たり前）。

**はじめ、②を どの欄にも かけて 16,248件 出した。**意味欄は 英語で 当然なので、
規則が 雑だった。日本語で 書く 欄だけを 見るように 直した。
"""
import io, os, re, sys, glob, json

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# ① 日本語・ラテン・記号・絵文字 いがい
# 「ゆるす文字」を 数えあげると、矢印（→）のような ふつうの 記号まで
# 弾いて しまう（実際に 1,341件 出した）。そこで **捕まえたい 文字だけ**を 書く。
OTHER = re.compile(
    '['
    '\uac00-\ud7af\u1100-\u11ff'      # ハングル
    '\u0400-\u04ff\u0500-\u052f'      # キリル
    '\u0900-\u097f'                    # デーバナーガリー
    '\u0e00-\u0e7f'                    # タイ
    '\u0600-\u06ff\u0750-\u077f'      # アラビア
    '\u0590-\u05ff'                    # ヘブライ
    '\u0370-\u03ff'                    # ギリシャ
    ']')

# ② 日本語で 書く 欄（ここに 英単語が あれば まちがい）
# **実習生が 読む ところ**だけを 見る。
# note（作り方のメモ）や name（出典）には ファイル名や URL が 入る。
# そこまで 見ると、まぎれ込みでは ない ものを 拾って しまう。
JA_KEYS = {'q', 'text', 'choices', 'opts', 'script', 'show', 'sentence',
           'explain', 'exp', 'inst', 'label', 'intro',
           'headers', 'rows', 'why', 'head', 'tail', 'parts'}
# 日本語の 文に あっても よい 英字
OK = re.compile(r'^(N[1-5]|JLPT|OJT|PDF|URL|LINE|ID|A|B|C|D|[IVX]+)$', re.I)

def walk(o, key, hit):
    if isinstance(o, str):
        hit.append((key, o))
    elif isinstance(o, dict):
        for k, v in o.items(): walk(v, k, hit)
    elif isinstance(o, list):
        for v in o: walk(v, key, hit)

bad = []
files = ([R + f for f in ['kanji-data.json', 'vocab-data.json', 'sentences.json']]
         + glob.glob(R + 'bunpo/*.json') + glob.glob(R + 'dokkai/*.json')
         + glob.glob(R + 'moshi/*.json'))
n = 0
for p in sorted(set(files)):
    if not os.path.exists(p): continue
    n += 1
    rel = os.path.relpath(p, R)
    try:
        j = json.load(io.open(p, encoding='utf-8'))
    except Exception as e:
        bad.append('%s：読めない（%s）' % (rel, e)); continue
    hit = []
    walk(j, '', hit)
    for k, t in hit:
        for m in OTHER.finditer(t):
            bad.append('%s：日本語いがいの 文字「%s」 … %s'
                       % (rel, m.group(0), t[max(0, m.start() - 16):m.start() + 16]))
        # はじめ「日本語が 入って いる 文だけ」を 見て いたので、
        # 選択肢が **まるごと 英語**（例：closed）の ときに 素通りした。
        # 実習生が 読む 欄なら、まるごと 英語でも おかしい。条件を 外す。
        if k in JA_KEYS:
            for w in re.findall(r'\b[A-Za-z]{2,}\b', t):
                if OK.match(w): continue
                bad.append('%s：日本語の 欄「%s」に 英単語「%s」 … %s' % (rel, k, w, t[:46]))

print('■ 見たファイル %d個' % n)
print()
print('=' * 62)
print('まぎれて いる もの:', len(bad))
for b in bad[:30]: print('  -', b)
if len(bad) > 30: print('  …ほか %d件' % (len(bad) - 30))
print('=' * 62)
sys.exit(1 if bad else 0)
