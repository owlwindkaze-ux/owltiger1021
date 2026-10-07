# -*- coding: utf-8 -*-
"""公開するファイルに、外に出してはいけない文字列が 入っていないかを 点検する。

    python3 tools/check-secrets.py

なぜ作ったか
  このリポジトリは **公開（public）** で、合言葉はブラウザの中で画面を隠して
  いるだけ。**HTMLやMarkdownに書いたことは、合言葉なしで誰でも読める。**
  それなのに、外部サイトの鍵つきURLを「載せない」と決めた その説明文の中に、
  鍵そのものを 書いてしまった（2026-09-22e・公開前に気づいて消した）。
  「気をつける」では また やる。機械で 止める。

見るもの
  ・URLの中の 鍵（?k=・?token=・?key=・?auth= のあとに 続く 長い文字列）
  ・パスワードらしい 書き方（password=・passwd=・secret=）

見ないもの
  ・合言葉の SHA-256（`jlpt-kanji-gate-v1` の値）。これは **公開してよい**。
    もとの合言葉は これからは 求められない。画面を隠すためだけに 置いてある。
  ・.git の中、ツールの中（ここは 公開されない／人が読む前提）
"""
import io, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
# 公開されるもの＝サイトに置く HTML・JSON と、PDFのもとになる Markdown
TARGETS = ['.html', '.md', '.json', '.js']
SKIP_DIRS = {'.git', 'node_modules'}
# 合言葉のハッシュは 公開してよい（これだけは 見のがす）
ALLOW = {'ebec3cabb51c7aed2a0e3b893a08691fbadc9ad0eed58fe3c51ebe75d532a48c'}

RULES = [
    (re.compile(r'[?&](k|key|token|auth|sid|session)=([A-Za-z0-9+/=_-]{12,})'),
     'URLの中の鍵'),
    (re.compile(r'(password|passwd|secret|api[_-]?key)\s*[=:]\s*[\'"][^\'"]{6,}',
                re.I), 'パスワードらしい書き方'),
]

# データのファイル（語彙・文型・読解など）は 人が 鍵を 書く所では ないうえ
# 大きいので 見ない。人が 手で 書く ファイルだけを 見る。
SKIP_FILES = re.compile(r'(^|/)(vocab|kanji|tegaki|reading|listening|grammar|'
                        r'moshi|weeks|.*-data)[^/]*\.json$')

bad = []
# ---- 実在の施設名・病院名が まぎれていないか ----
# 施設の実際の申し送り記録から 例文を起こしたため、**実在の病院名が3本
# 入ったまま公開されていた**（2026-10-07 に見つけて直した）。
# 固有名詞を 禁止語として ここに書くと それ自体が公開になるので、
# **「出てよい形」を並べ、それ以外を出す**やり方にする。
NAME = re.compile(r'[一-龥ァ-ヶー]{2,8}(病院|医院|クリニック|診療所|荘|苑|ホーム|'
                  r'の家|園|センター)')
NAME_OK = {
    # 一般名詞として ふつうに出てくる形
    '動物園', '公園', '保育園', '幼稚園', '遊園', '花園', '学園',
    '特別養護老人ホーム', '老人ホーム', '有料老人ホーム', 'グループホーム',
    'ケアホーム', '駅のホーム', 'ホームヘルパー', 'ホーム',
    '総合病院', '大学病院', '国立病院', '市立病院', '県立病院', '救急病院',
    '近くの病院', 'この病院', 'その病院', '町の病院', '歯科医院', '医院',
    'かかりつけの病院', '紹介先の病院', '搬送先の病院',
    '地域包括支援センター', '支援センター', '地域のセンター', 'センター',
    'デイサービスセンター', '保健センター', '診療所', 'クリニック',
    # 「〜の家」は ふつうの言い方で出てくる（先生の家・部屋の家具 など）
    '先生の家', '部屋の家', '自分の家', '本人の家', 'うちの家',
}


def name_hits(text):
    """固有の施設名らしいものを返す。前後の文字で切れた形は見ない"""
    out = []
    for m in NAME.finditer(text):
        g = m.group(0)
        if g in NAME_OK:
            continue
        # 末尾の語（病院・荘 など）だけで成り立つ一般名は見逃す
        if any(g.endswith(ok) and (ok in NAME_OK) for ok in NAME_OK):
            continue
        out.append(g)
    return out



n = 0
for dirpath, dirs, files in os.walk(R):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for name in files:
        if os.path.splitext(name)[1] not in TARGETS:
            continue
        p = os.path.join(dirpath, name)
        rel = os.path.relpath(p, R)
        if SKIP_FILES.search(rel):
            continue
        try:
            s = io.open(p, encoding='utf-8').read()
        except Exception:
            continue
        n += 1
        if rel in ('sentences.json',) or rel.startswith('dokkai/') or rel.startswith('choukai/'):
            for g in name_hits(s):
                bad.append('%s　実在の施設名かもしれません → %s'
                           '（一般名なら tools/check-secrets.py の NAME_OK に足す）' % (rel, g))
        for pat, why in RULES:
            for m in pat.finditer(s):
                hit = m.group(0)
                if any(a in hit for a in ALLOW):
                    continue
                line = s[:m.start()].count('\n') + 1
                bad.append('%s:%d　%s → %s' % (rel, line, why, hit[:60]))

print('■ 見たファイル %d個' % n)
print()
print('=' * 62)
print('外に出してはいけないもの:', len(bad))
for b in bad: print('  -', b)
print('=' * 62)
sys.exit(1 if bad else 0)
