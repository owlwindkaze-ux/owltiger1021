# -*- coding: utf-8 -*-
"""紙の教材のうち、回ごとに 問題と解答が あるものを 点検する。

    python3 tools/kaigo/check-tests.py

見るところ
  ① 回（章）の数が、名前に 書いてある 数と 合っているか
  ② 回ごとに 解答が あるか（名前で 突き合わせる）
  ③ 4択の 選択肢が ちょうど 4つ あるか
  ④ 設問の数と 解答の数が 合っているか
  ⑤ 正解の番号が 1〜4の 中に あるか
  ⑥ 正解の番号の かたより（教材ごと・回ごと）
  ⑦ 「なぜ」を 問う 設問が 各回に 1つ以上 あるか（00のまとめの方針）
  ⑧ 同じ 選択肢が 2つ以上 ないか
  ⑨ 日本語以外の 文字

**機械では 見つけられない もの（必ず 目で 読むこと）**
  ・正解が 2つに なっている（例：「ボタンを（　）」に「かける」と「とめる」の 両方を 置いた、
    「シーツを すぐに（　）します」に「洗濯」と「交換」の 両方を 置いた）。
    作ったときに 4件 出した。選択肢を 1つずつ 入れて 読み直すしかない。
  ・ほかの回と 同じ設問（再出題）。00のまとめ：再出題は よいが、新作として 出さない。

なぜ作ったか
  00のまとめに「作ったあとに、必ず正解番号を縦に並べて数えてください」と書いてある。
  実際、N4補習版の初版が「1」にかたよって テストとして 成立していなかった。
  目で数えると必ず見落とすので、機械で数える。
"""
import collections, io, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
MD = R + 'tools/kaigo/md/'
BAD = re.compile(r'[Ѐ-ӿ가-힯ऀ-ॿ฀-๿؀-ۿ]')

# (ファイル, 回の見出しの形, いくつ あるべきか, 4択の設問がある大問の見出しの形)
FILES = [
    ('02_章別ミニテスト_全8章.md', r'^# (第\d章.*)$', 8, r'^## (問2)　'),
    ('03_N4補習版_全5回.md', r'^# (第\d回.*)$', 5, r'^## (問題[13456])　'),
    ('04_書き方テスト_全5回.md', r'^# (第\d回.*)$', 5, None),
    ('05_コロケーション演習_全3回.md', r'^# (第\d回.*)$', 3, None),
    ('08_記述特化ワーク_全5回.md', r'^# (第\d回.*)$', 5, None),
]
DIV = '# ここから下は 職員用です'


def main():
    bad, warn = [], []
    for name, rpat, want, qpat in FILES:
        s = io.open(MD + name, encoding='utf-8').read()
        if DIV not in s:
            bad.append('%s：職員用の区切りが ない' % name)
            continue
        front, back = s.split(DIV, 1)
        rounds = re.findall(rpat, front, re.M)
        print('■ %s' % name)
        print('   回 %d個（名前には %d個）%s' % (len(rounds), want, '' if len(rounds) == want else '  ←ちがう'))
        if len(rounds) != want:
            bad.append('%s：回が %d個。名前には %d個と 書いてある' % (name, len(rounds), want))
        keys = re.findall(r'^### (.+)$', back, re.M)
        for r in rounds:
            if not any(r in k or k in r for k in keys):
                bad.append('%s：「%s」の解答が 巻末に ない' % (name, r))
        if BAD.search(s):
            bad.append('%s：日本語以外の文字' % name)
        if not qpat:
            print()
            continue

        # ---- 4択の設問と 解答を 突き合わせる ----
        # 本文を 回ごとに 切り、その中の 大問ごとに 設問を 数える
        cuts = [m.start() for m in re.finditer(rpat, front, re.M)] + [len(front)]
        allpos = collections.Counter()
        for i, r in enumerate(rounds):
            seg = front[cuts[i]:cuts[i + 1]]
            # 解答の行（問2　1-2／2-3… / 問題3　1-2／…）を 拾う
            key = ''
            for k in keys:
                if k == r:
                    j = back.index('### ' + k)
                    key = back[j:].split('\n### ')[0]
            nums = {}
            for m in re.finditer(r'^(問\d|問題\d)　((?:\d+-\d／?)+)$', key, re.M):
                nums[m.group(1)] = [int(x.split('-')[1]) for x in m.group(2).rstrip('／').split('／')]
            for qm in re.finditer(qpat, seg, re.M):
                q = qm.group(1)
                body = seg[qm.end():]
                body = body.split('\n## ')[0]
                items = [l for l in body.split('\n') if l.startswith('1. ')]
                chs = []
                for it in items:
                    # 「　1 あ　2 い　3 う　4 え」の形を 数える
                    c = re.findall(r'[　 ](\d) ', it)
                    chs.append(c)
                got = nums.get(q)
                if got is None:
                    bad.append('%s %s %s：解答の行が 巻末に ない' % (name, r, q))
                    continue
                if len(items) != len(got):
                    bad.append('%s %s %s：設問 %d個／解答 %d個' % (name, r, q, len(items), len(got)))
                for n, c in enumerate(chs, 1):
                    if len(c) != 4:
                        bad.append('%s %s %s の%d：選択肢が %d個' % (name, r, q, n, len(c)))
                for n, a in enumerate(got, 1):
                    if not 1 <= a <= 4:
                        bad.append('%s %s %s の%d：正解が %d（1〜4の外）' % (name, r, q, n, a))
                allpos.update(got)
                # 同じ選択肢が ないか
                for n, it in enumerate(items, 1):
                    op = re.split(r'[　 ]\d ', it)[1:]
                    op = [x.strip() for x in op]
                    if len(set(op)) != len(op):
                        bad.append('%s %s %s の%d：同じ選択肢が ある' % (name, r, q, n))
            # 「なぜ」を 問う 設問。00のまとめの「1回に最低1問」。
            # 原本のまま（第1〜4章・第1回）に 無いものが あるので、
            # 直すかどうかは 人が 決める。ここでは 注意として 出すだけにする。
            if not re.search(r'どうして|ためです|ためです。|なぜ|理由', seg):
                warn.append('%s：「%s」に 理由を 問う 設問が ない（00のまとめ：1回に最低1問）' % (name, r))
            # 回ごとの かたより
            print('   %-28s 正解の番号 %s' % (r, dict(sorted(
                collections.Counter(a for q, g in nums.items() for a in g if 1 <= a <= 4).items()))))
        t = sum(allpos.values())
        if t:
            print('   ぜんぶ %d問　正解の番号 %s（いちばん多い番号は %d%%）'
                  % (t, dict(sorted(allpos.items())), round(100 * max(allpos.values()) / t)))
            if 100 * max(allpos.values()) / t > 35:
                bad.append('%s：正解の番号が かたよって いる（%d%%）'
                           % (name, round(100 * max(allpos.values()) / t)))
        print()

    if warn:
        print('■ 注意（直すかは 人が 決める）')
        for w in warn: print('  -', w)
        print()
    print('=' * 62)
    print('直さないといけない所:', len(bad))
    for b in bad: print('  -', b)
    print('=' * 62)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
