#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""語彙の「学習区分」を決める（SPEC 2.6-z29・方針はドライブ08）。

  覚える       自分で言う・自分で書く
  意味が分かる   読んで分かればよい。自分では書かない
  参考         出てきたら引く

**区分は この道具の中には書いてありません。`tools/学習区分.csv` に書いてあります。**
Excel や Google スプレッドシートで開いて直せます。直したら

    python3 tools/vocab-study.py --apply

を走らせれば、`vocab-data.json` とレベル別ファイルに入ります。**後から何度でも
変えられます。**プログラムを触る必要はありません。

表の書き方

    種類,名前,区分,覚え書き
    分野,薬・衛生材料,参考,商品名が多い      ← その分野ぜんぶの既定
    語,オムツ,覚える,毎日使う                ← その1語だけ（分野より強い）

**ここに書かなかったものは すべて「覚える」になります。**
分ける軸は 難しさではなく「**その語で何をするか**」。方針が挙げている例を
そのまま 判定の基準点にしています。

  覚える       交換・更衣・発赤・体位交換
  意味が分かる   拘縮・喘鳴・意識混濁
  参考         良肢位・びらん・薬剤名（ソフラチュール）

**迷ったら上に寄せます。**「参考」にした語は実習生が飛ばすので、まちがえると
取り返しがつかない。逆に「覚える」にしすぎても負担が少し増えるだけ。
だから表には **参考と意味が分かるだけを書き**、書き落としは全部「覚える」に残します。

    python3 tools/vocab-study.py            # いまの区分を見る
    python3 tools/vocab-study.py --md FILE  # 確認用の紙（Markdown）を書き出す
    python3 tools/vocab-study.py --apply    # データに入れる（study 欄）
"""
import collections
import io
import json
import os
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
CSV = R + 'tools/学習区分.csv'
LEVELS = ('介護', '記録', '現場')      # 区分を付ける範囲。N5〜N2は試験の語なので全部「覚える」
LABEL = ['覚える', '意味が分かる', '参考']
DEFAULT = '覚える'


def load_csv():
    """表を読む。分野の既定と、語ごとの指定を返す"""
    if not os.path.exists(CSV):
        raise SystemExit('× 表がありません: ' + CSV)
    field, word = {}, {}
    for n, line in enumerate(io.open(CSV, encoding='utf-8'), 1):
        line = line.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        f = [x.strip() for x in line.split(',')]
        if f[0] == '種類':                       # 見出し
            continue
        if len(f) < 3:
            raise SystemExit('× %d行目：列が足りません → %s' % (n, line))
        kind, name, cat = f[0], f[1], f[2]
        if cat not in LABEL:
            raise SystemExit('× %d行目：区分は %s のどれかです → 「%s」'
                             % (n, '／'.join(LABEL), cat))
        if kind == '分野':
            field[name] = cat
        elif kind == '語':
            if name in word:
                raise SystemExit('× %d行目：「%s」を二重に書いています' % (n, name))
            word[name] = cat
        else:
            raise SystemExit('× %d行目：種類は「分野」か「語」です → 「%s」' % (n, kind))
    return field, word


def main():
    field, word = load_csv()
    words = json.load(io.open(R + 'vocab-data.json', encoding='utf-8'))['words']
    target = [x for x in words if x['level'] in LEVELS]
    have = {x['word'] for x in target}

    # 表に書いたのに 語彙に無い語があれば、書きまちがい。ここで止める
    miss = sorted(set(word) - have)
    if miss:
        print('× 語彙データに無い語を表に書いています（%d語）' % len(miss))
        print('   ' + '　'.join(miss))
        return 1
    subs = {x.get('sub') for x in target}
    missf = sorted(set(field) - subs)
    if missf:
        print('× 語彙データに無い分野を表に書いています: ' + '　'.join(missf))
        return 1

    def cat_of(x):
        if x['word'] in word:
            return word[x['word']]
        return field.get(x.get('sub'), DEFAULT)

    out = collections.OrderedDict((k, []) for k in LABEL)
    for x in target:
        out[cat_of(x)].append(x)

    print('■ 学習区分（介護・記録・現場の %d語）' % len(target))
    for k in LABEL:
        print('   %-7s %4d語（%d%%）' % (k, len(out[k]), round(100 * len(out[k]) / len(target))))
    print('\n■ 分野ごと')
    bysub = collections.defaultdict(collections.Counter)
    for k in LABEL:
        for x in out[k]:
            bysub[x.get('sub') or '（分野なし）'][k] += 1
    for s, c in sorted(bysub.items(), key=lambda kv: -sum(kv[1].values())):
        n = sum(c.values())
        if n < 15 and c['覚える'] == n:
            continue                              # 全部「覚える」の小さい分野は省く
        print('   %-12s 計%4d　覚える%4d／意味が分かる%4d／参考%4d'
              % (s, n, c['覚える'], c['意味が分かる'], c['参考']))
    print('\n※ 区分は tools/学習区分.csv で変えられます（Excelで開けます）。')

    if '--md' in sys.argv:
        p = sys.argv[sys.argv.index('--md') + 1]
        io.open(p, 'w', encoding='utf-8').write(markdown(out, len(target)))
        print('確認用の紙を書きました: ' + p)

    if '--apply' in sys.argv:
        apply_to_data(cat_of)
    return 0


def apply_to_data(cat_of):
    """vocab-data.json に study 欄を入れ、レベル別ファイルを作り直す"""
    P = R + 'vocab-data.json'
    j = json.load(io.open(P, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    n = 0
    for x in j['words']:
        if x['level'] in LEVELS:
            c = cat_of(x)
            if c == DEFAULT:
                x.pop('study', None)              # 既定は書かない（ファイルを太らせない）
            else:
                x['study'] = c
                n += 1
        else:
            x.pop('study', None)
    # もとのファイルは1行で書いてある。形を変えると差分が読めなくなるので そろえる
    io.open(P, 'w', encoding='utf-8').write(json.dumps(j, ensure_ascii=False))
    print('\nvocab-data.json に入れました（既定でない語 %d語に study 欄）' % n)
    r = subprocess.run([sys.executable, R + 'tools/split-data.py'],
                       capture_output=True, text=True)
    print((r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else '')


def markdown(out, total):
    def rows(items):
        s = ''
        for x in items:
            s += '| %s | %s | %s | %s |\n' % (
                x['word'], x['reading'], x.get('sub') or '',
                (x.get('meaning_ja') or x.get('meaning') or '').replace('|', '／'))
        return s

    s = '# 語彙の学習区分　%d語\n\n' % total
    s += ('ドライブ08の方針「覚える／意味が分かる／参考」を、介護・記録・現場の語に当てたものです。\n'
          '**区分は `tools/学習区分.csv` に書いてあり、Excelで開いて直せます。**\n\n')
    s += '| 区分 | 語数 | 画面での出方 |\n|---|---|---|\n'
    s += ('| 覚える | %d語 | 週割り・カード・練習問題・「覚えた」の分母に入る |\n' % len(out['覚える']))
    s += ('| 意味が分かる | %d語 | 一覧と検索には出る。練習は意味を選ぶ問題だけ。**分母に入れない** |\n'
          % len(out['意味が分かる']))
    s += ('| 参考 | %d語 | **検索だけ。**週割りにも練習にも出さない |\n\n' % len(out['参考']))
    s += ('**見ていただきたいのは「参考」の%d語です。**'
          'ここに入れた語は実習生が飛ばすので、1つでも混ざっていたら教えてください。\n'
          '**直すのは `tools/学習区分.csv` の1行だけ**です。\n\n' % len(out['参考']))
    for k, head in ((('参考'), '出てきたら引けばよい語。商品名・規格・単位と、介護職員が書かない専門語。'),
                    (('意味が分かる'), '読んで分かればよい語。看護師・医師が書く観察の語と、施設の中だけの言い方。'),
                    (('覚える'), '自分で言う・自分で書く語。**表に書かなかった語は全部ここに残ります。**')):
        s += '---\n\n## %s ── %d語\n\n%s\n\n' % (k, len(out[k]), head)
        s += '| 語 | 読み | 分野 | 意味 |\n|---|---|---|---|\n' + rows(out[k]) + '\n'
    return s


if __name__ == '__main__':
    sys.exit(main())
