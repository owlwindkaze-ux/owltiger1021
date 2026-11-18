#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**正解の番号が かたよっていないか**を点検する（SPEC 2.6-z81）。

持ち主から「**100日コースの問題の解答で、選択が1ばかりが見られる。
同じ番号が続いた解答になってないか**」（2026-11-18）。

数えたら そのとおりだった。

    ドリル420問 … **1番が 75.5%**、4番は **1問だけ**
    **40日ぶん、その日の6問が 全部1番**

原因は 作り方。**正解を1番目に書いて、そのあとに はずれを足していた。**
1番ばかり選べば 4分の3 当たる。**力をはからない問題**になっていた。

ここで見るのは 3つ：
  ① 正解の番号の 割合（どれかが 15%未満、または 40%超なら 鳴る）
  ② **その日の問が ぜんぶ同じ番号**になっていないか
  ③ 同じ番号が **4問以上 続いて**いないか

★の問（週テスト）は `check-weektest.py` が 同じことを見ている。
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
ng = []
bad = ng.append

# n3.html の `var WEEKS = …` は **JavaScript** なので、nodeに読ませて JSONで受け取る。
# （本文のHTMLに波かっこが入っていて、文字列として切り出すと こわれる）
JS = r'''
import { readFileSync } from 'fs';
const s = readFileSync(process.argv[2], 'utf8');
const h = s.indexOf('var WEEKS = ');
const e = s.indexOf('\n', s.indexOf(';', h));
console.log(JSON.stringify(Function(s.slice(h, e) + '; return WEEKS;')()));
'''


def load_weeks():
    with tempfile.NamedTemporaryFile('w', suffix='.mjs', delete=False) as f:
        f.write(JS)
        p = f.name
    try:
        out = subprocess.run(['node', p, R + 'n3.html'],
                             capture_output=True, text=True, timeout=120)
        if out.returncode:
            bad('n3.html から 問題を 読み出せません：%s' % out.stderr.strip()[:120])
            return None
        return json.loads(out.stdout)
    finally:
        os.unlink(p)


def main():
    W = load_weeks()
    if W is None:
        return
    rows = []          # (週, 曜日, 並び順, 正解, 選択肢の数)
    for wk in sorted(W, key=int):
        A = W[wk].get('answers') or {}
        for day in W[wk]['days']:
            ans = A.get(day['key']) or {}
            for i, b in enumerate(day.get('blocks') or []):
                if b.get('t') != 'q':
                    continue
                key = b['id'] if b['id'] in ans else 'd' + str(b['id'])
                v = ans.get(key)
                if not (isinstance(v, list) and v and isinstance(v[0], int)):
                    continue
                n = len(b.get('opts') or [])
                rows.append((int(wk), day['key'], i, v[0], n))
                if n and not (1 <= v[0] <= n):
                    bad('第%s週 %s %s：正解の番号 %s が 選択肢%d個の外'
                        % (wk, day['key'], b['id'], v[0], n))

    four = [r for r in rows if r[4] == 4]
    print('■ 100日コース 正解の番号')
    print('   問 %d（うち 選択肢4つ %d）' % (len(rows), len(four)))
    if not four:
        bad('選択肢4つの問が 見つかりません（読み方が変わった？）')
        return

    # ① 割合
    cnt = [0, 0, 0, 0]
    for r in four:
        cnt[r[3] - 1] += 1
    t = len(four)
    print('   ' + '  '.join('%d番 %d (%.1f%%)' % (i + 1, c, 100 * c / t)
                            for i, c in enumerate(cnt)))
    for i, c in enumerate(cnt):
        pc = 100 * c / t
        if pc < 15 or pc > 40:
            bad('正解の番号が かたよっています：%d番が %.1f%%（15〜40%%に）'
                % (i + 1, pc))

    # ② その日が ぜんぶ同じ番号 ／ ③ 4問以上の連続
    byday = {}
    for r in four:
        byday.setdefault((r[0], r[1]), []).append((r[2], r[3]))
    allsame, longrun = [], []
    for k, v in sorted(byday.items()):
        v.sort()
        if len(v) >= 4 and len({a for _, a in v}) == 1:
            allsame.append('第%d週 %s（%d問すべて %d番）' % (k[0], k[1], len(v), v[0][1]))
        cur, ln = None, 0
        for _, a in v:
            ln = ln + 1 if a == cur else 1
            cur = a
            if ln >= 4:
                longrun.append('第%d週 %s（%d番が %d問続く）' % (k[0], k[1], a, ln))
                break
    print('   その日がぜんぶ同じ番号の日 %d ／ 4問以上続いた日 %d'
          % (len(allsame), len(longrun)))
    for x in allsame:
        bad('その日の問が ぜんぶ同じ番号です：%s' % x)
    for x in longrun:
        bad('同じ番号が 続きすぎです：%s' % x)

    print()
    print('=' * 54)
    print('おかしいところ: %d件' % len(ng))
    for x in ng[:12]:
        print('  -', x)
    print('=' * 54)


main()
sys.exit(1 if ng else 0)
