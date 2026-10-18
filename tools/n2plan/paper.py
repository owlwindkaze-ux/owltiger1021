#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""紙の月別パック（ドライブ「N2学習教材_2026年9月-12月」全4冊・14単元）を
N2ロードマップの週に割り当て、`n2/weeks.json` の `paper` を作り直す。

**なぜ必要か**（2026-09-27d・SPEC 2.6-z27）
紙のパックとシステムが別々の予定として並走していた。14単元の学習目標を
システムの文型データに当てたところ、月のラベルと合っていたのは3単元だけで、
残り11は1〜3か月ずれ、しかも早い方向・遅い方向の両方にずれていた。
**月をずらしても直らない**（パックは月ごとのテーマ練習で、文型を積み上げ順に
並べていない）。そこで **システムの文型順に単元を並べ替え**、その文型を
習い終わった **あとの週** に置く。紙は演習で、システムが本線。

    python3 tools/build-weeks.py      # 先にこちら（週割りを作り直す）
    python3 tools/n2plan/paper.py
"""
import collections
import io
import json
import os

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'

# 単元 → (冊子, 題, ねらい, その単元が前提にする文型のid)
# 「必ずしも〜ない」は単独の項目ではなく わけではない・とは限らない の説明に入る。
# 「によると」は n4-ni-yoruto（新人コース第12週）。N2コースの週割りには無い。
U = collections.OrderedDict([
 (1,  ('9月後半', '予定・連絡と学習の進め方', '予定の変更、条件、とは限らない、うちに。根拠を本文から探す',
       ['n2-towa-kagiranai', 'n2-nai-uchi-ni'])),
 (2,  ('9月後半', '買い物・選択と理由', '比較、必ずしも〜ない、に応じて。条件を照合する',
       ['n3-ni-oujite', 'n3-wake-dewa-nai', 'n2-towa-kagiranai'])),
 (3,  ('10月', '仕事の改善・手順の理解', 'に基づいて、だけでなく、文の組み立て。原因と結果',
       ['n3-ni-motozuite', 'n3-bakari-de-naku'])),
 (4,  ('10月', '学習方法・継続と変化', 'たびに、につれて、文章の接続。具体例と結論を分ける',
       ['n3-tabi-ni', 'n3-ni-tsurete'])),
 (5,  ('10月', '地域活動・参加と協力', 'にかかわらず、を通じて。意見の共通点と相違点',
       ['n2-ni-kakawarazu', 'n3-nimo-kakawarazu', 'n3-wo-tsuujite'])),
 (6,  ('10月', '働き方・休養と計画の見直し', 'わけにはいかない、一方で。反論と配慮',
       ['n3-wake-niwa-ikanai', 'n2-ippou-de'])),
 (7,  ('11月', '情報の確かめ方・数字と印象', 'によると、とはいえ、にすぎない。情報の条件と根拠',
       ['n3-towa-ie', 'n2-ni-suginai'])),
 (8,  ('11月', '環境・便利さと費用', 'に伴って、反面、ものの。利点と不利益を同時に読む',
       ['n3-ni-tomonatte', 'n2-hanmen', 'n3-mono-no'])),
 (9,  ('11月', 'サービス・相手の立場を考える', 'に対して、ものの、に応じて。例外と原則',
       ['n3-ni-taishite', 'n3-mono-no', 'n3-ni-oujite'])),
 (10, ('11月', '提案・試行と評価', '上で、かねない、にわたって。途中経過と最終判断',
       ['n2-ue-de', 'n3-kanenai', 'n2-ni-watatte'])),
 (11, ('12月', '主張理解の導入', 'にほかならない、だけあって、からといって',
       ['n3-ni-hokanaranai', 'n3-dake-atte', 'n3-kara-to-itte'])),
 (12, ('12月', '主張と反対の面', '一方だ、に限らず、からこそ',
       ['n3-ippou-da', 'n2-ni-kagirazu', 'n3-dakara-koso'])),
 (13, ('12月', '進行と範囲', 'つつある、にわたって、わけではない',
       ['n3-tsutsu-aru', 'n2-ni-watatte', 'n3-wake-dewa-nai'])),
 (14, ('12月', '年末総合', 'わけではない、からこそ、にしても',
       ['n3-wake-dewa-nai', 'n3-dakara-koso', 'n3-ni-shitemo'])),
])
# 冊子の名前。**月の名前はやめた**（2026-10-18）。
# 4か月分として作った冊子を、文型の順に並べ替えて**7か月かけて**配るので、
# 月の名前と実際に使う月が合うのは 14単元のうち **1つだけ**だった。
# 「1月なのに9月の冊子」という矛盾が起きる。Driveの名前も合わせて変えた。
# **名前は単元の範囲から作る。**手で書くと、単元を足したときにずれる。
def pack_name(units):
    return '第%d〜%d単元' % (min(units), max(units))
# **第8週から 1週に1単元。**冊子は「1か月4単元」として作られており、
# 1単元＝A〜Fの6学習日（勤務日4日＋公休2日）＝ちょうど1週間。
# 以前は2週に1単元に薄く延ばしていたが、冊子の月と使う月が
# **+1〜+4か月ずれて**いき、持ち主の判断で冊子どおりに戻した（2026-10-18）。
FIRST, STEP = 8, 1
CHECK_FROM = 36             # 月末確認4回は 模試期（第40週〜）の直前に置く


SHEET_CSS = """
@page { size: A4; margin: 13mm 14mm 13mm; }
body{font-family:"IPAPGothic","IPAGothic","Noto Sans CJK JP",sans-serif;
 color:#16212b;font-size:10pt;line-height:1.6;margin:0}
h1{font-size:16pt;color:#332e91;border-bottom:2.5px solid #4338ca;padding-bottom:3px;
 margin:0 0 1.5mm}
.sub{color:#4a5b6b;font-size:9pt;margin:0 0 2.5mm;line-height:1.6}
table{border-collapse:collapse;width:100%;font-size:10.5pt}
th,td{border:1px solid #c7c9e8;padding:0.9mm 3mm;text-align:left}
th{background:#eef2ff;color:#332e91;font-size:10pt}
td.d{white-space:nowrap;font-variant-numeric:tabular-nums}
tr.ck td{background:#fbfbfd;color:#4a5b6b;font-size:10pt}
tr.bk td{background:#f3f4fb;font-weight:700;color:#332e91;font-size:10pt}
.note{border-left:4px solid #4338ca;background:#eef2ff;padding:1.6mm 3mm;margin:2.2mm 0 0;
 font-size:8.5pt;line-height:1.6}
footer{margin-top:3mm;border-top:1px solid #dfe4ee;padding-top:1.5mm;
 font-size:8pt;color:#6b7686}
"""


def sheet(weeks, start, total):
    """**単元名と、始まる日だけ**の1枚。冊子と一緒に置く。

    持ち主から「単元名と、その単元名が始まる日がわかればいいのでは」。
    週番号は 使う人には要らない。**名前と日付だけ。**

    **並べ方は「使う月」ごと**（2026-10-18d → e で直した）。
    はじめは冊子ごとに並べていたが、持ち主から
    「**予定表になぜ11月がないんですか**」。
    11月の行はあったが、見出しが「**11月の冊子**」で、
    **その冊子を使うのは12月〜1月**。見出しの月と中身の月が合っていないので、
    「11月に何をやるか」が一目で引けなかった。
    **暦の順に並べ、冊子は列に回す。**
    """
    import datetime
    y, m, d = map(int, start.split('-'))
    S = datetime.date(y, m, d)
    W = '月火水木金土日'
    rows = []
    for k in sorted(weeks, key=int):
        v = weeks[k]
        dt = S + datetime.timedelta(days=(int(k) - 1) * 7)
        rows.append((dt, v))
    o = ['<!doctype html><html lang="ja"><head><meta charset="utf-8">',
         '<title>N2 紙のパック 予定表</title><style>%s</style></head><body>' % SHEET_CSS,
         '<h1>N2 紙のパック　いつ どれを やるか</h1>',
         '<p class="sub">その日の <b>月曜から</b> はじめます。1単元＝A〜Fの6学習日'
         '（勤務日4日＋公休2日）＝約4時間。'
         '<b>冊子の名前（9月後半・10月…）は、使う月ではありません。</b>'
         '中に入っている単元の まとまりの名前です。</p>',
         '<table><tr><th style="width:17%">日</th><th>やるもの</th>'
         '<th style="width:21%">どの冊子か</th></tr>']
    cur = None
    for dt, v in rows:
        ym = (dt.year, dt.month)
        if ym != cur:
            o.append('<tr class="bk"><td colspan="3">%d年%d月</td></tr>' % ym)
            cur = ym
        day = '%d/%d（%s）' % (dt.month, dt.day, W[dt.weekday()])
        bk = v.get('pack') or v.get('check')
        if 'unit' in v:
            o.append('<tr><td class="d">%s</td><td><b>第%d単元</b>　%s</td>'
                     '<td>%sの冊子</td></tr>' % (day, v['unit'], v['title'], bk))
        else:
            o.append('<tr class="ck"><td class="d">%s</td>'
                     '<td>月末確認　初見10問（解答25分＋聴解5分）</td>'
                     '<td>%sの冊子</td></tr>' % (day, bk))
    o.append('</table>')
    late = [v for v in weeks.values() if v.get('late')]
    if late:
        o.append('<div class="note"><b>※ つぎの単元は、システムでまだ習っていない'
                 '文型が出ます。</b>その場は<b>解説を読むだけでかまいません</b>。'
                 '先に覚えようとしないでください。<br>'
                 + '／'.join('第%d単元' % v['unit'] for v in late) + '</div>')
    last = max(int(k) for k in weeks)
    end = S + datetime.timedelta(days=(last - 1) * 7 + 6)
    # **「画面だけで進みます」とは書かない。**
    # 持ち主から「**ではなぜ今も画面で進めないんですか**」。
    # そのとおりで、紙がしていて画面ができないことが5つある
    # （週20問のまとまり／手で書く／職員が読み上げる聴解／点が残る／指導者確認）。
    # **足りるようになるのではなく、紙が尽きるだけ。**そう書く（2026-10-18e）。
    o.append('<div class="note"><b>紙は %d/%d/%d で尽きます（4冊ぶん）。</b>'
             '本番は2027年12月なので <b>そのあと約9か月 紙がありません</b>。'
             '画面は代わりになりません（<b>20問のまとまり</b>と'
             '<b>点の記録</b>がないため）。</div>'
             % (end.year, end.month, end.day))
    o.append('<footer>この表は n2/weeks.json から tools/n2plan/paper.py が'
             '作っています。週の割り当てを変えると この表も変わります。</footer>')
    o.append('</body></html>')
    return '\n'.join(o)


def main():
    gw = json.load(io.open(R + 'bunpo/weeks.json', encoding='utf-8'))['courses']['n2']['weeks']
    week_of = {}
    for w, ids in gw.items():
        for i in ids:
            week_of[i] = int(w)
    # その単元が前提にする文型を、システムが習い終わる週（注意書きに使う）
    need = {u: max([week_of.get(i, 0) for i in ids]) for u, (_, _, _, ids) in U.items()}

    # 冊子ごとの単元（冊子の中の並び順のまま）
    books = collections.OrderedDict()
    for u, (pk, _, _, _) in U.items():
        books.setdefault(pk, []).append(u)
    PACK_OF = {u: pk for pk, us in books.items() for u in us}
    LAST_OF = {us[-1]: pk for pk, us in books.items()}   # 冊子の最後の単元

    # **冊子の順（第1→14単元）どおりに置く。**偶数週に単元、空いた奇数週に月末確認。
    weeks = collections.OrderedDict()
    w, late = FIRST, []
    for u in sorted(U):
        weeks[str(w)] = collections.OrderedDict(
            [('unit', u), ('pack', PACK_OF[u]), ('title', U[u][1]), ('aim', U[u][2])])
        if need[u] > w:
            late.append((u, w, need[u]))     # 文型をまだ習っていない単元
            # 画面にも出す。黙っていると「習っていないのに出た」と戸惑う
            weeks[str(w)]['late'] = need[u]
        w += STEP
        if u in LAST_OF:                      # 冊子の最後 → その次の週に月末確認
            weeks[str(w)] = collections.OrderedDict([('check', LAST_OF[u])])
            w += 1
    last = max(int(x) for x in weeks)

    P = R + 'n2/weeks.json'
    j = json.load(io.open(P, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    assert last < j['phases'][3]['from'], '紙が模試期に かかった（第%d週）' % last
    j['paper'] = collections.OrderedDict([
     ('note', '紙のパックの割り当て。**冊子の順（第1→14単元）どおり**に、第%d週から%d週に1単元。'
              '月末確認は その冊子の最後の単元の 次の週。'
              '冊子は月ごとのまとまりとして作られており、'
              '**9〜11月は短い文章、12月に主張理解の長文**という難しさの階段がある。'
              '以前は文型を習い終わった順に並べ替えていたが、'
              '**12月用の長文が2番目に来る**など階段が崩れたのでやめた（2026-10-18）。'
              'もとは tools/n2plan/paper.py。' % (FIRST, STEP)),
     ('folder', 'Google ドライブ ＞ 日本語の勉強 ＞ N2学習教材_全14単元'),
     ('unitdays', 'A〜Fの6学習日（勤務日4日＋公休2日）・合わせて約4時間'),
     ('how', ['A〔40分〕問1〜8　　B〔40分〕問9〜13　　C〔40分〕問16〜19',
              'D〔40分〕問14〜15　　E〔公休90分〕問20と読み直し　　F〔公休45分〕前の単元の直し',
              '聴解は音声がない。指導者が台本を読む。台本は 解いたあとに見る',
              'システムでまだ習っていない文型が出てくることがある。'
              '**その場は解説を読むだけでよい。**先に覚えようとしない']),
     ('weeks', weeks),
    ])
    io.open(P, 'w', encoding='utf-8').write(json.dumps(j, ensure_ascii=False, indent=1) + '\n')

    print('紙のパックの割り当て（冊子の順）')
    for w2, p2 in weeks.items():
        if 'unit' in p2:
            mark = '' if need[p2['unit']] <= int(w2) else \
                   '　← 文型は第%d週に習う（解説を読むだけでよい）' % need[p2['unit']]
            print('  第%-2s週  第%2d単元「%s」（%s）%s'
                  % (w2, p2['unit'], p2['title'], p2['pack'], mark))
        else:
            print('  第%-2s週  月末確認（%s）' % (w2, p2['check']))
    print()
    print('文型が追いついていない単元: %d／%d' % (len(late), len(U)))
    import sys
    if '--sheet' in sys.argv:
        q = sys.argv[sys.argv.index('--sheet') + 1]
        io.open(q, 'w', encoding='utf-8').write(sheet(weeks, j['start'], j['total']))
        print('予定表を書きました: %s' % q)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
