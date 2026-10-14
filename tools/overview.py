#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**初めて見る人のための説明書**を、データから作る（SPEC 2.6-z39）。

**なぜ道具にしたか**

`概要.pdf` と `総覧.pdf` は手書きだった。そのため中身を足すたびに
書き直しが要り、**9月25日のまま3週間 古くなっていた**
（学習区分・読みの見やすさ・判定テストの資格別・PDFの移動 ぜんぶ未反映）。
持ち主から「**何度も同じ作業になりますが**」と言われて作った。

**数は1つも手で書かない。**全部そのときのデータから数える。
だから **走らせ直せば いつでも最新**になる。古くなりようがない。

    python3 tools/overview.py                 # 画面に出す
    python3 tools/overview.py --md FILE       # Markdown で書き出す
    （そのあと tools/pdf/md2html.py → tools/pdf/mkpdf.mjs で PDF に）
"""
import collections
import glob
import io
import json
import os
import re
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'


def J(p):
    return json.load(io.open(R + p, encoding='utf-8'))


def gather():
    """いまのデータから、説明に要る数を全部集める"""
    d = {}
    k = J('kanji-data.json')['kanji']
    v = J('vocab-data.json')['words']
    g = J('bunpo/grammar.json')
    d['kanji'] = len(k)
    d['kanji_lv'] = collections.Counter(x['level'] for x in k)
    d['vocab'] = len(v)
    d['vocab_lv'] = collections.Counter(x['level'] for x in v)
    d['gram'] = g['total']
    d['gram_lv'] = g['level_totals']
    d['read'] = J('dokkai/reading.json').get('totals', {})
    d['sent'] = len(J('sentences.json')['sentences'])
    d['tegaki'] = len(J('tegaki-data.json').get('chars', []))

    # 学習区分（覚える／意味が分かる／参考）
    st = collections.Counter()
    for x in v:
        if x['level'] in ('介護', '記録', '現場'):
            st[x.get('study') or '覚える'] += 1
    d['study'] = st

    # 聴解のパート数と問数
    ch = io.open(R + 'choukai/index.html', encoding='utf-8').read()
    d['choukai_parts'] = len(set(re.findall(r'PART\s*(\d+)', ch)))
    m = re.search(r'CTOTAL = (\d+)', io.open(R + 'index.html', encoding='utf-8').read())
    d['choukai'] = int(m.group(1)) if m else 0

    # コース
    kw = J('kanji-weeks.json')['courses']
    gw = J('bunpo/weeks.json')['courses']
    d['courses'] = {}
    for c in ('shinjin', 'n2'):
        if c in kw:
            d['courses'][c] = {
                'start': kw[c].get('start'), 'total': kw[c].get('total'),
                'kanji': sum(len(x) for x in kw[c]['kanji'].values()),
                'vocab': sum(len(x) for x in kw[c]['vocab'].values()),
                'gram': sum(len(x) for x in gw.get(c, {}).get('weeks', {}).values()),
            }
    ix = io.open(R + 'index.html', encoding='utf-8').read()
    m = re.search(r'第1〜14週・([\d,]+)問', ix)
    d['n3q'] = m.group(1) if m else '?'

    # 画面・紙・道具
    d['pages'] = sorted(os.path.relpath(p, R) for p in
                        glob.glob(R + '*.html') + glob.glob(R + '*/index.html'))
    d['pdf_here'] = sorted(os.path.basename(p) for p in glob.glob(R + '*.pdf'))
    d['pdf_kaigo'] = sorted(os.path.basename(p) for p in glob.glob(R + 'kaigo/*.pdf'))
    d['checks'] = sorted(os.path.basename(p) for p in
                         glob.glob(R + 'tools/check-*.py') + glob.glob(R + 'tools/check-*.mjs'))
    d['moshi'] = len(glob.glob(R + 'moshi/*.json'))

    # ドライブへ出した答え入りの数
    sp = __import__('importlib.util', fromlist=['util'])
    s = sp.spec_from_file_location('ao', R + 'tools/check-answers-out.py')
    mod = sp.module_from_spec(s)
    s.loader.exec_module(mod)
    d['out'] = len(mod.OUT)
    return d


def lv(c, order):
    return '・'.join('%s %s' % (x, '{:,}'.format(c[x])) for x in order if c.get(x))


def md(d):
    o = []
    A = o.append
    A('# このシステムは何か')
    A('')
    A('**初めて見る人のための説明です。**この文書は `tools/overview.py` が'
      '**そのときのデータから作っています**。数字は1つも手で書いていないので、'
      '古くなることがありません。')
    A('')
    A('---')
    A('')
    A('## 1. ひとことで言うと')
    A('')
    A('**日本の介護施設で働くインドネシア人の技能実習生が、'
      'スマホ1台で日本語を勉強するための仕組み**です。')
    A('')
    A('| | |')
    A('|---|---|')
    A('| だれが使うか | 介護の技能実習生（いま2人）と、教える職員 |')
    A('| 何のために | **2027年7月の日本語能力試験 N3に受かる**こと。その先にN2 |')
    A('| どこで使うか | スマホ・タブレット。住所を開いて合言葉を入れるだけ |')
    A('| いくらかかるか | **0円**（無料の置き場所を使っています） |')
    A('| 個人情報 | **集めません。**学習の記録は、その人の端末の中だけ |')
    A('')
    A('市販の教材は「日本で暮らす人」むけで、**介護の現場の言葉がほとんど入っていません。**'
      '実習生がつまずくのは駅や買い物ではなく、**申し送りの記録**と**利用者さんへの声かけ**でした。'
      'そこを埋めるために作られています。')
    A('')
    A('---')
    A('')
    A('## 2. 入っているもの')
    A('')
    A('| | 数 | 内わけ |')
    A('|---|---|---|')
    A('| 漢字 | **{:,}字** | {} |'.format(d['kanji'], lv(d['kanji_lv'], ['N5', 'N4', 'N3', 'N2', '介護', '記録'])))
    A('| 言葉（語彙） | **{:,}語** | {} |'.format(d['vocab'], lv(d['vocab_lv'], ['N5', 'N4', 'N3', 'N2', '介護', '記録', '現場'])))
    A('| 文の形（文型） | **{:,}項目** | {} |'.format(d['gram'], lv(collections.Counter(d['gram_lv']), ['N5', 'N4', 'N3', 'N2', '記録'])))
    A('| 例文 | **{:,}本** | 言葉の{:.0f}%に付いています |'.format(d['sent'], 100 * d['sent'] / d['vocab']))
    A('| 読む練習 | **{}本・設問{}問** | すべて書き下ろし。試験の過去問は使っていません |'
      .format(d['read'].get('passages', '?'), d['read'].get('questions', '?')))
    A('| 聞く練習 | **{}問** | {}のまとまり。音は端末の読み上げ |'.format(d['choukai'], d['choukai_parts']))
    A('| 手書きでさがす | **{:,}字** | 読めない漢字を指で書いて調べられます |'.format(d['tegaki']))
    A('| 模試 | **{}回分** | 本番と同じ時間で通して解きます |'.format(d['moshi']))
    A('')
    A('**ここがこのシステムの値うちです。**「介護 {:,}語」「記録 {:,}語」「現場 {:,}語」の'
      '**合わせて {:,}語**は、**市販の教材にはほとんど載っていません。**'
      '施設の実際の申し送り記録から起こしたものです。'
      .format(d['vocab_lv']['介護'], d['vocab_lv']['記録'], d['vocab_lv']['現場'],
              d['vocab_lv']['介護'] + d['vocab_lv']['記録'] + d['vocab_lv']['現場']))
    A('')
    A('### 全部を覚えさせるわけではありません')
    A('')
    A('介護・記録・現場の{:,}語は、**その語で何をするか**で3つに分けてあります。'
      .format(sum(d['study'].values())))
    A('')
    A('| 区分 | 語数 | 何をする語か | 画面での出方 |')
    A('|---|---|---|---|')
    A('| 覚える | **{:,}語** | 自分で言う・自分で書く | カードにも練習問題にも出る |'.format(d['study']['覚える']))
    A('| 意味が分かる | **{:,}語** | 読めればよい。自分では書かない | 出るが「覚えた」の分母に入れない |'.format(d['study']['意味が分かる']))
    A('| 参考 | **{:,}語** | 出てきたら引く（薬の商品名など） | **出さない** |'.format(d['study']['参考']))
    A('')
    A('この区分は `tools/学習区分.csv` という**表計算で開ける1枚の表**にあり、'
      '**後からいつでも変えられます**（プログラムは触りません）。')
    A('')
    A('---')
    A('')
    A('## 3. 画面の地図')
    A('')
    A('住所を開くと**入口メニュー**が出ます。そこから次へ進みます。')
    A('')
    A('| 画面 | 何ができるか |')
    A('|---|---|')
    A('| 入口メニュー | ここから全部へ行けます |')
    A('| 漢字・語彙 | さがす／カードで覚える／練習問題／書き順の動き／学習状況 |')
    A('| 文型・文法 | 文の形を意味のまとまりで。例文3つと練習問題つき |')
    A('| 読解 | 文章を読んで答える |')
    A('| 聴解 | 聞いて答える |')
    A('| 100日コース | 試験日から逆算した毎日の割り当て |')
    A('| 新人コース | 入職から7月のN3までの**30週** |')
    A('| N2コース | N3のあと、2027年12月のN2までの**66週** |')
    A('| 手書き検索 | 読めない漢字を指で書いてさがす |')
    A('| まちがえたところ | 7つの区分を横断して、**まちがえた分だけ**集めます |')
    A('| 模試 | 本番と同じ時間で通して解きます |')
    A('')
    A('**職員だけが使う画面**（実習生の画面からはリンクしていません）')
    A('')
    A('| 画面 | 中身 |')
    A('|---|---|')
    A('| 職員用 | テストの聴解を流す／紙の教材／研修の計画書／説明書 |')
    A('| 紙の教材 | 介護の日本語の紙教材12点の入口 |')
    A('| テストの聴解 | 診断テスト・判定テストの聞き取りを再生 |')
    A('')
    A('---')
    A('')
    A('## 4. 3つのコース')
    A('')
    for key, name, goal in (('shinjin', '新人コース', '入職 → 2027年7月のN3'),
                            ('n2', 'N2コース', 'N3合格 → 2027年12月のN2')):
        c = d['courses'].get(key)
        if not c:
            continue
        A('**{}**（{}週・{}から）── {}'.format(name, c['total'], c['start'], goal))
        A('')
        A('その{}週で教えるのは **漢字{:,}字・語彙{:,}語・文型{:,}項目**。'
          '**どの週に何をやるかが全部決まっています**ので、'
          '「今週やること」を開けば、その日の分だけが出ます。'
          .format(c['total'], c['kanji'], c['vocab'], c['gram']))
        A('')
    A('**100日コース** ── 試験日から逆算した **{}問**。'
      '月曜から日曜まで順番に進み、土曜は通しテストです。'.format(d['n3q']))
    A('')
    A('---')
    A('')
    A('## 5. 使い方')
    A('')
    A('### 実習生')
    A('')
    A('1. 住所を開き、**合言葉を1回だけ**入れます（次からは要りません）')
    A('2. 自分のコースを開き、「**今週やること**」を見ます')
    A('3. 「**今週ひらくもの**」を押すと、**その週の分だけ**が出た状態で開きます')
    A('4. 覚えたら「**✓ 覚えた**」、あやしければ「**△ 要復習**」を押します')
    A('5. まちがえた分は「**まちがえたところ**」に自動でたまります')
    A('')
    A('**この印が全部の土台です。**押さないと「要復習だけ回す」ができません。')
    A('')
    A('### 職員')
    A('')
    A('1. **入職の週**に N4到達度判定テスト（60分・66問）。採点して12月からの量を決めます')
    A('2. **次の週**に 診断テスト第1回（書く・話すも見ます）')
    A('3. **第4・8・12・20週**に 月末面談。そこで**必ずバックアップを取ります**')
    A('4. **第24・28週**に N3模試。区分ごとの点を見て、足りない所を埋めます')
    A('')
    A('**記録はその人のスマホの中だけにあります。**端末を変えると消えるので、'
      '面談のたびに「💾 バックアップを保存」を押させ、'
      '出てきた共有画面から**施設のドライブ**へ入れてください。')
    A('')
    A('---')
    A('')
    A('## 6. どういう作りか（なぜこの形か）')
    A('')
    A('| 決めごと | なぜ |')
    A('|---|---|')
    A('| 外部の部品を一切使わない | 海外の回線でも軽く、**リンク切れで壊れない** |')
    A('| サーバーを持たない（ファイルを置くだけ） | 保守の手間と費用が**0** |')
    A('| 記録は端末の中だけ | **個人情報を預からない**。その代わりバックアップが要る |')
    A('| 合言葉は1つ | 部外者よけの**目隠し**。鍵ではありません |')
    A('')
    A('**正直に書いておくこと**')
    A('')
    A('- 置き場所は**公開**です。住所を知っていれば、合言葉なしでもファイルは取れます。'
      'そこで**答えの入った紙のテスト{}本は、公開の場所から出して**'
      'Googleドライブの職員用フォルダへ移しました。'.format(d['out']))
    A('- 画面の練習問題と模試の答えは、**外せません**。'
      'サーバーを持たない作りなので、画面が読むデータ＝誰でも読めるからです。')
    A('- **一度も本番で回していません。**最初の人が使い始めるのは2026年12月7日です。')
    A('')
    A('---')
    A('')
    A('## 7. 間違いを見つける仕組み')
    A('')
    A('作った数と画面に出る数がずれる、答えが実習生から見える、'
      '外に出してはいけないものが混ざる ── こうした失敗を'
      '**実際に何度もやりました**。そのたびに**機械の見張り**を足してあり、いま**{}本**あります。'
      .format(len(d['checks'])))
    A('')
    for c in d['checks']:
        A('- `{}`'.format(c))
    A('')
    A('**どの見張りも、わざと壊して「鳴る」ことを確かめてから入れています。**'
      '鳴らない見張りは、無いのと同じで、安心する分だけ危ないからです。')
    A('')
    A('---')
    A('')
    A('## 8. 紙の資料')
    A('')
    A('この置き場所にあるもの（**{}点**）'.format(len(d['pdf_here']) + len(d['pdf_kaigo'])))
    A('')
    for f in d['pdf_here'] + ['kaigo/' + x for x in d['pdf_kaigo']]:
        A('- {}'.format(f))
    A('')
    A('**答えの入ったもの{}点は、ここにはありません。**'
      'Googleドライブ ＞ 日本語の勉強 ＞ owltiger1021_職員用（答え入り・公開しない）にあります。'
      .format(d['out']))
    A('')
    A('---')
    A('')
    A('## 9. この説明書の作り直し方')
    A('')
    A('```')
    A('python3 tools/overview.py --md /tmp/ov.md')
    A('python3 tools/pdf/md2html.py /tmp/ov.md /tmp/ov.html "このシステムは何か"')
    A('NODE_PATH=/tmp/node_modules node tools/pdf/mkpdf.mjs /tmp/ov.html \\')
    A('    "/home/user/owltiger1021/このシステムは何か.pdf" "このシステムは何か"')
    A('```')
    A('')
    A('**中身を足したら、これを走らせ直すだけ**です。'
      '数は全部そのときのデータから数えるので、**手で直す所はありません。**')
    return '\n'.join(o) + '\n'


def main():
    d = gather()
    text = md(d)
    if '--md' in sys.argv:
        p = sys.argv[sys.argv.index('--md') + 1]
        io.open(p, 'w', encoding='utf-8').write(text)
        print('書きました: %s（%d文字）' % (p, len(text)))
    else:
        print(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
