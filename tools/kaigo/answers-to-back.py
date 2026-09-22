# -*- coding: utf-8 -*-
"""紙の教材の「解答」を、回ごとの途中から 巻末へ まとめ直す。

    python3 tools/kaigo/answers-to-back.py        # 点検だけ（何も書きかえない）
    python3 tools/kaigo/answers-to-back.py --write  # 書きかえる

なぜ直すか
    元の Word は「第1章 問題 → 第1章 解答 → 第2章 問題 → …」の順。
    このままだと、実習生に渡す問題用紙を印刷するとき、章のあいだの解答を
    1つずつ飛ばさなければならない（8章なら8回）。必ずどこかで事故が起きる。
    解答を巻末にまとめ、「ここから下は職員用」の行を1本入れれば、
    **その行の前までを印刷する**だけで済む。

何を変えるか（原本との違い）
    ① 並び順       …… 解答が、回の直後から 巻末へ 移る
    ② 見出しが増える …… 元の「**解答**」は太字1行で、どの回のものかは
                        位置でしか分からない。巻末に出すと名前が要るので
                        「### 第1章　…」を こちらで 付ける
    ③ 区切りが増える …… 「ここから下は 職員用です」の行を1本入れる
    ④ 09だけ        …… 読み上げ用スクリプトも 巻末へ 移す
                        （元は「配らないでください」の直後、問題用紙より前にある）
    本文の字は 1字も 変えない。②③で足す見出しだけが 増える。

直さないファイル
    01・06・10 …… もともと解答が巻末にある
    07        …… 解答が無い（評価シート）
    00・11    …… 教材ではない
"""
import collections, io, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
MD = R + 'tools/kaigo/md/'

DIV = '# ここから下は 職員用です'
DIVNOTE = ('**実習生に渡す問題用紙は、この行の前までを 印刷してください。**'
           'この下には 解答（と、教材によっては 読み上げ用スクリプト）が 入っています。')
NOTE = ('※ **解答は 巻末に まとめて あります。**実習生に渡すときは、'
        '「ここから下は 職員用です」の行の **前まで**を 印刷してください。')

# ファイルごとの決めごと
#   mark      : 解答のはじまりの行（完全一致）
#   round     : 回（章）の見出しの形
#   staff_from: ここから下を職員用とする見出し（None なら 解答の直前に区切りを置く）
#   orphan    : 原本に回が無い、はぐれた解答。
#               {その解答が ぶら下がってしまう回の名前: 付ける名前}
#               1つの回に 解答が 2つ以上あれば、2つ目からが はぐれ。
#               番号で指定していたら 1つずらして 取りちがえたので、
#               「どの回にぶら下がっているか」で 指定する形にした。
RULES = {
    '02_章別ミニテスト_全8章.md': dict(
        mark='**解答**', round=r'^# (第\d章.*)$', staff_from='## 指導メモ',
        orphan={'第4章　排泄の介護':
                ['第8章　居室の環境整備（**問題が 原本に 入っていません**）']}),
    '03_N4補習版_全5回.md': dict(
        mark='**解答**', round=r'^# (第\d回.*)$', staff_from='## 正解位置の分布（確認用）',
        extra_mark='## 解答',
        orphan={'第2回　排泄・衣服・入浴・あいさつ【修正版】':
                ['どの回の解答か、**原本に 書かれていません**'
                 '（問題2が「シフト・記録・連絡・確認・有給」なので、'
                 '仕事・報告の回＝収録されていない 第3〜5回の どれかと 思われます）']}),
    '04_書き方テスト_全5回.md': dict(
        mark='**解答**', round=r'^# (第\d回.*)$', staff_from='# 採点の基準'),
    '05_コロケーション演習_全3回.md': dict(
        mark='**解答**', round=r'^# (第\d回.*)$', staff_from='## 使い方の提案'),
    '08_記述特化ワーク_全5回.md': dict(
        mark='## 解答・採点', round=r'^# (第\d回.*)$', staff_from='## 全5回を 終えたら'),
    # 09 は 解答ではなく、読み上げ用スクリプトが 問題用紙より 前にある。
    # 区切りは【解答・解説】の前に置き、スクリプトを その直後へ 移す。
    # 問題用紙・解答用紙は 渡す範囲に 残す。
    '09_聴解テスト_紙版.md': dict(
        mark=None, round=None, staff_from='# **【解答・解説】**',
        move_to_back=['# **【読み上げ用スクリプト】**']),
}


def blocks(lines, starts):
    """starts の各行から、次の「#」で始まる行の前までを 1かたまりとして 取り出す。"""
    out = []
    for s in starts:
        e = s + 1
        while e < len(lines) and not lines[e].startswith('#'):
            e += 1
        out.append((s, e))
    return out


def work(name, rule, write):
    src = io.open(MD + name, encoding='utf-8').read()
    lines = src.split('\n')
    msgs = []

    # すでに かけてある ファイルには 二度と 手を 出さない。
    # 03 は 巻末に 付ける「## 解答」の見出しを、09 は 移した スクリプトの
    # 見出しを、もう一度 拾ってしまい、二重に 動かして 壊す。
    if DIV in src:
        return ['  %-28s すでに 済んでいます（区切りが 入っています）' % name]

    # ---- 動かすかたまりを 見つける ----
    starts = []
    if rule.get('mark'):
        starts += [i for i, l in enumerate(lines) if l == rule['mark']]
    if rule.get('extra_mark'):
        starts += [i for i, l in enumerate(lines) if l == rule['extra_mark']]
    for h in rule.get('move_to_back', []):
        starts += [i for i, l in enumerate(lines) if l == h]
    starts.sort()
    if not starts:
        return ['%s：動かすものが 見つからない（書き方が変わった？）' % name]
    bl = blocks(lines, starts)

    # ---- それぞれに 名前を 付ける ----
    # 直前の「回（章）の見出し」を その解答の名前にする。
    # 同じ回に 解答が 2つ以上 ぶら下がったら、2つ目からは
    # 原本に回が無い「はぐれ」なので、orphan に書いた名前を使う。
    orphan = {k: list(v) for k, v in rule.get('orphan', {}).items()}
    used = collections.Counter()
    named = []
    for n, (s, e) in enumerate(bl, 1):
        if not rule.get('round'):
            named.append((s, e, None))     # 09 のスクリプトは そのまま出す
            continue
        base = None
        for j in range(s - 1, -1, -1):
            m = re.match(rule['round'], lines[j])
            if m:
                base = m.group(1); break
        if base is None:
            return ['%s：%d個目の解答が どの回のものか 分からない' % (name, n)]
        used[base] += 1
        if used[base] == 1:
            label = base
        else:
            if not orphan.get(base):
                return ['%s：「%s」に 解答が %d個 ぶら下がっている。'
                        '原本に 回が 無い はぐれの解答なので、'
                        'orphan に 名前を 書いてください' % (name, base, used[base])]
            label = orphan[base].pop(0)
        named.append((s, e, label))
    left = [k for k, v in orphan.items() if v]
    if left:
        return ['%s：orphan に 書いた名前が 使われていない（%s）'
                '。ぶら下がる回が 変わった？' % (name, '・'.join(left))]

    # ---- 区切りを どこに 置くか ----
    sf = rule.get('staff_from')
    div_at = None
    if sf:
        hit = [i for i, l in enumerate(lines) if l == sf]
        if len(hit) != 1:
            return ['%s：区切りの見出し「%s」が %d個（1個であること）' % (name, sf, len(hit))]
        div_at = hit[0]

    # ---- 組み立て直す ----
    drop = set()
    for s, e, _ in named:
        drop.update(range(s, e))
    body, tail = [], []
    for i, l in enumerate(lines):
        if i in drop:
            continue
        if div_at is not None and i >= div_at:
            tail.append(l)
        else:
            body.append(l)
    # 本文の 最初の回の 見出しの前に 注意書きを 入れる
    if rule.get('round'):
        for i, l in enumerate(body):
            if re.match(rule['round'], l):
                body[i:i] = [NOTE, '']
                break
    else:
        for i, l in enumerate(body):
            if l.startswith('# ') and i > 0:
                body[i:i] = [NOTE, '']
                break

    ans = []
    for s, e, label in named:
        if label is None:
            continue                          # 名前なしは 区切りの すぐ下へ（下で入れる）
        ans += ['### ' + label, ''] + [x for x in lines[s:e] if x != rule.get('mark')]
        while ans and ans[-1] == '':
            ans.pop()
        ans.append('')

    out = [x for x in body]
    while out and out[-1] == '':
        out.pop()
    out += ['', DIV, '', DIVNOTE, '']
    # 名前を付けなかったもの（09 の読み上げ用スクリプト）は、区切りの すぐ下へ。
    # 元の職員用のかたまり（解答・解説など）より 前に置きたいので、ここで入れる。
    plain = [x for s, e, l in named if l is None for x in lines[s:e]]
    if plain:
        while plain and plain[-1] == '':
            plain.pop()
        out += plain + ['']
    if tail:
        t = [x for x in tail]
        while t and t[-1] == '':
            t.pop()
        out += t + ['']
    if any(l is not None for _, _, l in named):
        out += ['## 解答', '']
        out += ans

    new = '\n'.join(out).rstrip('\n') + '\n'

    # ---- 点検：字が 消えていないか ----
    def bare(t):
        t = t.replace(NOTE, '').replace(DIV, '').replace(DIVNOTE, '')
        t = re.sub(r'^### .*$', '', t, flags=re.M)
        t = re.sub(r'^## 解答$', '', t, flags=re.M)
        return re.sub(r'\s+', '', t)
    b1, b2 = bare(src), bare(new)
    if rule.get('mark'):
        b1 = b1.replace(re.sub(r'\s+', '', rule['mark']), '')
        b2 = b2.replace(re.sub(r'\s+', '', rule['mark']), '')
    # 並べ替えるので 文字の順番は 変わる。1字も 消えていないかを
    # 文字の数（多重集合）で 見る。
    c1, c2 = collections.Counter(b1), collections.Counter(b2)
    if c1 != c2:
        lost = c1 - c2
        add = c2 - c1
        msgs.append('%s：字が 変わってしまった（消えた %d字 %s／増えた %d字 %s）'
                    % (name, sum(lost.values()), ''.join(list(lost)[:20]),
                       sum(add.values()), ''.join(list(add)[:20])))

    # ---- 点検：渡す範囲に 答えが 残っていないか ----
    # 実習生に渡すのは「最初の回の見出し」から「区切りの行」の前まで。
    # その前置き（使い方・配点）は職員が読むところなので 見ない。
    front = new.split(DIV)[0].split('\n')
    if rule.get('round'):
        b = next((i for i, l in enumerate(front) if re.match(rule['round'], l)), 0)
    else:
        b = next((i for i, l in enumerate(front) if i and l.startswith('# ')), 0)
    for ln in front[b:]:
        for w in ['解答', '正解', '採点']:
            if w in ln and NOTE not in ln and not ln.startswith('#') \
               and '解答用紙' not in ln and '解答欄' not in ln:
                msgs.append('%s：渡す範囲に「%s」が 残っている → %s' % (name, w, ln[:50]))
    msgs.append('  %-28s 解答 %d個 を 巻末へ（%s）'
                % (name, sum(1 for _, _, l in named if l is not None),
                   '区切り：' + (sf or '解答の直前')))
    if write:
        io.open(MD + name, 'w', encoding='utf-8').write(new)
    return msgs


def main():
    write = '--write' in sys.argv
    bad, log = [], []
    for name, rule in RULES.items():
        for m in work(name, rule, write):
            (log if m.startswith('  ') else bad).append(m)
    print('■ 動かしたもの' if write else '■ 動かす予定のもの')
    for l in sorted(log): print(l)
    print()
    print('=' * 62)
    print('直さないといけない所:', len(bad))
    for b in bad: print('  -', b)
    print('=' * 62)
    if not write:
        print('※ 書きかえていません。--write を付けると 書きかえます。')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
