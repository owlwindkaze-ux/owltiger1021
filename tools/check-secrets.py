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
# **.txt と .csv を見ていなかった。**そのせいで 他社の商談の文字起こしが
# 何か月も main に置かれたまま 気づけなかった（2026-10-12c）。
# 置き場所を間違えるのは、たいてい 教材ではない形のファイルである。
TARGETS = ['.html', '.md', '.json', '.js', '.txt', '.csv']
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



# ---- 仕事の記録・個人名が まぎれていないか ----
# 2026-10-12、**他社との商談の文字起こし**（実在の社名・役職者4人の実名）と、
# そこから作ったメール・議題の3本が **main に置いたまま公開されていた**。
# 日本語学習とも勤怠システとも関係のない、道具を試したときの実物だった。
# 置き場所を間違えたものは、**ファイル名で止める**のがいちばん確実。
WORKFILES = {
    'meeting-transcript.txt',          # 商談の文字起こし
    'followup-email.txt',              # そこから作ったお礼メール
    'next-actions.txt',
    'next-agenda.txt',
}
# **言葉だけで探すと 読解の教材に当たる。**
# n3.html には「先方」「見積書」が27か所あるが、これはN3の読解の本文で、
# 消してはいけないもの。そこで**次の3つが そろったときだけ**鳴らす。
#   ① 拡張子が .txt（教材は .json と .html。.txt に教材は無い）
#   ② 「商談」か「面談」が出る
#   ③ 役職つきの名前（〜部長・〜課長 など）が出る
# 文字起こしは この3つが必ずそろい、教材は そろわない。
WORK_MEET = re.compile(r'(商談|面談|打ち合わせ)')
WORK_NAME = re.compile(r'[一-龥]{2,4}(部長|課長|社長|専務|常務|係長|主任)')


def work_hits(rel, text):
    out = []
    if os.path.basename(rel) in WORKFILES:
        out.append('仕事の記録そのもの（%s）' % os.path.basename(rel))
    if rel.endswith('.txt') and WORK_MEET.search(text):
        nm = sorted({m.group(0) for m in WORK_NAME.finditer(text)})
        if nm:
            out.append('商談・面談の記録かもしれません（%s）' % '・'.join(nm[:4]))
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
        for g in work_hits(rel, s):
            bad.append('%s　%s（公開の場所に置かない）' % (rel, g))
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
