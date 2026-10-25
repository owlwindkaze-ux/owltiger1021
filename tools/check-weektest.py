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
                # 漢字・語彙の問（inst がこの形）は 日本語と尼語の両方が要る
                if sec.get('inst') == 'つぎの問いに答えなさい。':
                    if not str(x.get('explain') or '').strip():
                        bad('%s %s 解説（日本語）がありません' % (nm, kk))
                    if not str(x.get('explain_id') or '').strip():
                        bad('%s %s 解説（インドネシア語）がありません' % (nm, kk))
                    if str(x.get('explain') or '').rstrip()[-1:] in ('＝', '：'):
                        bad('%s %s 解説が「＝」で切れています' % (nm, kk))
        if n < 12:
            bad('%s 問が %d しかありません（12問以上）' % (nm, n))
        if d.get('counts', {}).get('合計') != n:
            bad('%s counts の合計 %s と実際 %d が合いません'
                % (nm, d.get('counts', {}).get('合計'), n))
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
    print('   週: 第%d〜%d週／教材のある週 %d／テスト %d' %
          (min(have), max(have), len(want), len(have)) if have else '   （無し）')

print()
print('=' * 54)
print('おかしいところ: %d件' % len(ng))
for x in ng[:12]:
    print('  -', x)
print('=' * 54)
sys.exit(1 if ng else 0)
