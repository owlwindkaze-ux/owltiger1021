#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**週テスト**（`moshi/w-*.json`）を点検する（SPEC 2.6-z57）。

その週に習った分から組み立てたもの。**新しい問題は書いていない。**
だからこそ、**組み立てそこねていないか**を見る必要がある。

見るところ：
  ・1週 **12問以上**（作れる数は週によって違う。20問が標準）
  ・答えの番号が 選択肢の範囲に入っているか／空の選択肢が ないか
  ・聴解に **台本**が あるか
  ・`moshi/index.html` の `sets` と ファイルが 合っているか
  ・**コースの週の数と 合っているか**（抜けている週が ないか）
"""
import glob
import io
import json
import os
import re
import sys

JA = re.compile(r'[\u3041-\u309f\u30a1-\u30fe\u4e00-\u9fff\u3005]')

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
ng = []
bad = ng.append

CO = [('shinjin', 'sjw', '新人コース'), ('n2', 'n2w', 'N2コース')]
idx = io.open(R + 'moshi/index.html', encoding='utf-8').read()
kwc = json.load(io.open(R + 'kanji-weeks.json', encoding='utf-8'))['courses']
gwc = json.load(io.open(R + 'bunpo/weeks.json', encoding='utf-8'))['courses']

for course, key, name in CO:
    files = sorted(glob.glob(R + 'moshi/w-%s-*.json' % course),
                   key=lambda p: int(re.search(r'-(\d+)\.json$', p).group(1)))
    have = [int(re.search(r'-(\d+)\.json$', p).group(1)) for p in files]
    print('■ %s 週テスト %d本' % (name, len(files)))
    for f in files:
        nm = os.path.basename(f)
        d = json.load(io.open(f, encoding='utf-8'))
        n = 0
        for k in d['order']:
            sec = d['sections'][k]
            qs = []
            for x in sec.get('items', []):
                qs.append((x.get('choices') or x.get('opts'),
                           x.get('answer') if 'answer' in x else x.get('ans'), x, k))
            for r in sec.get('read', []):
                for qi in r['qi']:
                    q = r['passage']['questions'][qi]
                    qs.append((q['choices'], q['answer'], q, k))
            if not qs:
                bad('%s %s に問がありません' % (nm, k))
            for ch, a, x, kk in qs:
                n += 1
                if not ch or len(ch) < 2:
                    bad('%s %s 選択肢が少なすぎます' % (nm, kk))
                elif any(not str(c).strip() for c in ch):
                    bad('%s %s 空の選択肢があります' % (nm, kk))
                elif not isinstance(a, int) or not (0 <= a < len(ch)):
                    bad('%s %s 答えの番号が範囲の外（%r／選択肢%d）' % (nm, kk, a, len(ch)))
                if kk.startswith('聴解') and not (x.get('script') or '').strip():
                    bad('%s %s 聴解に台本がありません' % (nm, kk))
                # 画面は問題文をそのまま文字として出す（タグは読めない）
                for fld in ('q', 'explain', 'explain_id', 'script', 'show'):
                    if re.search(r'<[a-zA-Z/]', str(x.get(fld) or '')):
                        bad('%s %s %s にタグが混ざっています' % (nm, kk, fld))
                for c in (ch or []):
                    if re.search(r'<[a-zA-Z/]', str(c)):
                        bad('%s %s 選択肢にタグが混ざっています' % (nm, kk))
                # **問に日本語があるか。**練習問題の画面は 聞いていることを
                # 見出しに出し、問には 手がかりだけを置く。それを そのまま
                # 持ってくると「perbedaan; ketidaksesuaian」のように
                # **尼語の手がかりだけ**の問になる（2026-10-25d）。
                qt = str(x.get('q') or '')
                if not qt.strip():
                    bad('%s %s 問が空です' % (nm, kk))
                elif not JA.search(qt):
                    bad('%s %s 問に日本語がありません（%s）' % (nm, kk, qt[:30]))
                # 漢字・語彙の問（explain_id を持つ）は 日本語と尼語の両方が要る
                if 'explain_id' in x and not kk.startswith('聴解'):
                    if not str(x.get('explain') or '').strip():
                        bad('%s %s 解説（日本語）がありません' % (nm, kk))
                    if not str(x.get('explain_id') or '').strip():
                        bad('%s %s 解説（インドネシア語）がありません' % (nm, kk))
                    if str(x.get('explain') or '').rstrip()[-1:] in ('＝', '：'):
                        bad('%s %s 解説が「＝」で切れています' % (nm, kk))
        # 大問の指示が「つぎの問いに答えなさい。」のままなら、
        # 何を聞かれているのか どこにも書いていない（2026-10-25d）
        for k in d['order']:
            inst = d['sections'][k].get('inst', '')
            if inst.strip() == 'つぎの問いに答えなさい。':
                bad('%s %s 大問の指示が汎用のままです（何を聞くのか書いていない）' % (nm, k))
            if not JA.search(inst):
                bad('%s %s 大問の指示に日本語がありません' % (nm, k))
        # **`lead` は そのまま HTMLとして 画面に出る。**`**…**` と書いても
        # 太字にならず、**星印が そのまま 出る**（50本ぜんぶで そうなっていた・
        # 2026-11-03に 画面で 見つけた）。太字は `<b>` で 書く。
        for pt in d.get('parts', []):
            if '**' in str(pt.get('lead') or ''):
                bad('%s %s の lead に ** が入っています（画面に星印が出ます）'
                    % (nm, pt.get('name')))
        if n < 12:
            bad('%s 問が %d しかありません（12問以上）' % (nm, n))
        if d.get('counts', {}).get('合計') != n:
            bad('%s counts の合計 %s と実際 %d が合いません'
                % (nm, d.get('counts', {}).get('合計'), n))
    # ── 文の組み立て（★）────────────────────────────────
    # 持ち主から「文型の並べ替え（★）を週テストに入れる」、あわせて
    # **「答えの順番が、同一にならないように注意」**（2026-11-03c）。
    # 練習画面は 出すたびに 選択肢を まぜるが、テストは **作ったときの順を
    # ファイルに 焼き付ける**ので、何もしないと 正解が いつも同じ番号に 来る。
    # だから **ぜんぶの★を 集めて、正解の番号の ばらつき**を 見る。
    sdist = [0, 0, 0, 0]
    sn = 0
    for f in files:
        nm = os.path.basename(f)
        d = json.load(io.open(f, encoding='utf-8'))
        st = [d['sections'][k] for k in d['order']
              if (d['sections'].get(k) or {}).get('name') == '文の組み立て']
        gr = [k for k in d['order']
              if (d['sections'].get(k) or {}).get('name') == '文法形式の判断']
        # 文型のある週には ★が 要る（文型が無い週＝新人コース第1〜4週は 無くてよい）
        if gr and not st:
            bad('%s 文型があるのに ★（文の組み立て）がありません' % nm)
        if len(st) > 2:
            bad('%s ★が %d問あります（2問まで）' % (nm, len(st)))
        bare = 0
        for sec in st:
            it = (sec.get('items') or [{}])[0]
            q = str(it.get('q') or '')
            if '★' not in q:
                bad('%s ★の問に ★がありません' % nm)
            if q.count('＿＿') != 3:
                bad('%s ★の問の下線が 3つではありません（%d）' % (nm, q.count('＿＿')))
            ch = it.get('choices') or []
            if len(ch) != 4 or len(set(ch)) != 4:
                bad('%s ★の選択肢が 4つそろっていません' % nm)
            if not str(it.get('explain') or '').startswith('正しい順は'):
                bad('%s ★の解説に 正しい順がありません' % nm)
            # 枠（下線の前後の文）が 無い問は 1枚に1問まで。
            # 無条件に使って **同じ見た目の問が13本**できた（2026-11-03c）
            if q.replace('　', '').replace('＿＿', '').replace('★', '') == '':
                bare += 1
            if isinstance(it.get('answer'), int) and 0 <= it['answer'] < 4:
                sdist[it['answer']] += 1
                sn += 1
        if bare > 1:
            bad('%s 枠のない★が %d問あります（1枚に1問まで）' % (nm, bare))
    if sn >= 20:
        lo = min(sdist) / sn
        if lo < 0.15:
            bad('%s：★の正解の番号が かたよっています %s（どれも15%%以上に）'
                % (name, sdist))
        print('   ★ %d問／正解の番号 %s' % (sn, sdist))

    # 画面の sets と合うか
    m = re.search(r"%s:\s*\{[^}]*?sets:\s*\[([^\]]*)\]" % key, idx, re.S)
    if not m:
        bad('moshi/index.html に %s の sets がありません' % key)
    else:
        sets = [int(x) for x in re.findall(r'\d+', m.group(1))]
        if sets != have:
            bad('%s：画面の sets %s とファイル %s が合いません' % (name, sets, have))
    # コースの週と合うか
    want = sorted(set(
        [int(w) for w, v in gwc[course]['weeks'].items() if v] +
        [int(w) for w, v in kwc[course]['vocab'].items() if v]))
    miss = [w for w in want if w not in have]
    if miss:
        bad('%s：テストの無い週があります 第%s週' % (name, '・'.join(map(str, miss))))
    # **コースの画面が「テストがある週」を どこで切っているか。**
    # 教材が終わった週にも 入口を出していて、第26〜66週・第29〜30週が
    # **開かないところ**へ つながっていた（2026-11-03）。画面の WTMAX と
    # 実際のファイルの 最後の週が ずれたら 同じことが また起きる。
    co = io.open(R + '%s/index.html' % course, encoding='utf-8').read()
    m2 = re.search(r'\bWTMAX\s*=\s*(\d+)', co)
    if not m2:
        bad('%s/index.html に WTMAX がありません（テストの無い週にも入口が出ます）' % course)
    elif have and int(m2.group(1)) != max(have):
        bad('%s/index.html の WTMAX %s と テストの最後の週 第%d週 が合いません'
            % (course, m2.group(1), max(have)))
    print('   週: 第%d〜%d週／教材のある週 %d／テスト %d' %
          (min(have), max(have), len(want), len(have)) if have else '   （無し）')

print()
print('=' * 54)
print('おかしいところ: %d件' % len(ng))
for x in ng[:12]:
    print('  -', x)
print('=' * 54)
sys.exit(1 if ng else 0)
