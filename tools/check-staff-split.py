# -*- coding: utf-8 -*-
"""職員用のものが、実習生の見る画面から たどれないかを 点検する。

    python3 tools/check-staff-split.py

なぜ作ったか
  答え・判定の目安・聴解の読み上げスクリプトが 入ったものは、実習生が
  先に 見ると テストが 成立しなくなる。ところが 2026-09-22f まで、
  入口メニューにも 新人コースにも 職員用の欄が 並んでいて、
  **押せば 開く**状態だった。合言葉は 全ページ 共通なので、
  一度 入れた端末では そのまま 通る。

  リンクを1本 足すだけで また 元に戻る。目では 気づけないので 機械で見る。

見かた
  実習生の入口（index.html）から たどれる ページを ぜんぶ 追いかけ、
  そこから 職員用のもの への リンクが 出ていないかを 見る。

**これは「隠す」点検であって、「守る」点検ではない。**
  このサイトは GitHub Pages の無料公開で、リポジトリも公開。
  **URLを知っていれば 合言葉なしで 誰でも 開ける。**
  本当に守るには、答えの入ったファイルを サイトから 外すしかない。
"""
import io, os, re, sys
from urllib.parse import urldefrag

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# 職員用＝実習生から たどれては いけないもの
STAFF = [
    'staff/', 'kaigo/', 'shindan/',
    'N4到達度判定テスト_職員用.pdf', 'N4到達度判定テスト_問題.pdf',
    '月次確認テスト.pdf', '診断テスト_実施と採点.pdf',
    '診断テスト_第1回_問題.pdf', '診断テスト_第2回_問題.pdf',
    '新人研修プログラム.pdf',
]
START = 'index.html'          # 実習生が 最初に 見る 画面


def links(path):
    """そのHTMLの中の href を 全部 出す（外部サイト・アンカーだけのものは のぞく）"""
    try:
        s = io.open(R + path, encoding='utf-8').read()
    except Exception:
        return []
    out = []
    for m in re.finditer(r'href="([^"]+)"', s):
        h = m.group(1)
        if h.startswith(('http://', 'https://', 'mailto:', '#')):
            continue
        out.append(urldefrag(h)[0])
    return [x for x in out if x]


def norm(base, href):
    p = os.path.normpath(os.path.join(os.path.dirname(base), href))
    p = p.replace(os.sep, '/')
    # 「./index.html」と「index.html」が 別物に 見えると、同じ件が 2回 出る
    return p[2:] if p.startswith('./') else p


bad, seen, order = [], set(), []
queue = [START]
while queue:
    page = queue.pop(0)
    if page in seen:
        continue
    seen.add(page)
    order.append(page)
    for h in links(page):
        t = norm(page, h)
        hit = next((x for x in STAFF if t == x.rstrip('/') or t.startswith(x)
                    or t.endswith('/' + x) or t == x), None)
        if hit:
            bad.append('%s → %s（職員用）' % (page, t))
            continue
        # os.path.normpath は 末尾の「/」を 落とす。そのため
        # href="shinjin/" が "shinjin" に なり、追いかけそこねていた。
        # フォルダなら index.html を 見に行く。
        if t.endswith('.html') and os.path.exists(R + t):
            queue.append(t)
        elif os.path.isdir(R + t) and os.path.exists(R + t + '/index.html'):
            # href="../" のような 書き方だと t が「.」に なる。
            # そのまま つなぐと「./index.html」に なり、同じページが 2回 出る。
            queue.append(norm(t + '/', 'index.html'))

print('■ 実習生から たどれる ページ（%d枚）' % len(order))
for p in order:
    print('   ', p)
print()
print('=' * 62)
print('実習生から たどれてしまう 職員用のもの:', len(bad))
for b in bad: print('  -', b)
print('=' * 62)
print('※ これは「隠せているか」の点検です。URLを直接 開けば 誰でも 見られます。')
sys.exit(1 if bad else 0)
