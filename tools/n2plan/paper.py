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
PACKS = ['9月後半', '10月', '11月', '12月']
FIRST, STEP = 8, 2          # 第8週から 2週に1単元（1単元＝A〜Fの6学習日・約4時間）
CHECK_FROM = 36             # 月末確認4回は 模試期（第40週〜）の直前に置く


def main():
    gw = json.load(io.open(R + 'bunpo/weeks.json', encoding='utf-8'))['courses']['n2']['weeks']
    week_of = {}
    for w, ids in gw.items():
        for i in ids:
            week_of[i] = int(w)

    # その単元が前提にする文型を、システムが習い終わる週
    need = {}
    for u, (_, _, _, ids) in U.items():
        need[u] = max([week_of.get(i, 0) for i in ids])

    # 前提の早い順に並べ、習い終わった **次の週以降** に 2週おきで置く
    order = sorted(U, key=lambda u: (need[u], u))
    weeks, w = collections.OrderedDict(), FIRST
    for u in order:
        w = max(w, need[u] + 1)
        pack, ttl, aim, _ = U[u]
        weeks[str(w)] = collections.OrderedDict(
            [('unit', u), ('pack', pack), ('title', ttl), ('aim', aim)])
        w += STEP
    last = max(int(x) for x in weeks)
    assert last < CHECK_FROM, '単元が月末確認の週まで はみ出した（第%d週）' % last
    for i, pack in enumerate(PACKS):
        weeks[str(CHECK_FROM + i)] = collections.OrderedDict([('check', pack)])

    P = R + 'n2/weeks.json'
    j = json.load(io.open(P, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    assert CHECK_FROM + len(PACKS) - 1 < j['phases'][3]['from'], '月末確認が模試期に かかった'
    j['paper'] = collections.OrderedDict([
     ('note', '紙の月別パックの割り当て。単元の順番は システムの文型順に 並べ替えてある。'
              '紙の「9月後半・10月…」は ファイルの名前で、予定ではない。'
              'もとは tools/n2plan/paper.py。'),
     ('folder', 'Google ドライブ ＞ 日本語の勉強 ＞ N2学習教材_2026年9月-12月'),
     ('unitdays', 'A〜Fの6学習日（勤務日4日＋公休2日）・合わせて約4時間'),
     ('how', ['A〔40分〕問1〜8　　B〔40分〕問9〜13　　C〔40分〕問16〜19',
              'D〔40分〕問14〜15　　E〔公休90分〕問20と読み直し　　F〔公休45分〕前の単元の直し',
              '聴解は音声がない。指導者が台本を読む。台本は 解いたあとに見る',
              '習っていない文型が出てきたら、解説を読むだけにする。先に覚えようとしない']),
     ('weeks', weeks),
    ])
    io.open(P, 'w', encoding='utf-8').write(json.dumps(j, ensure_ascii=False, indent=1) + '\n')

    print('紙のパックの割り当て（システムの文型順）')
    for w2, p in weeks.items():
        if 'unit' in p:
            print('  第%-2s週  第%2d単元「%s」（%sの冊子）　前提の文型は第%d週まで'
                  % (w2, p['unit'], p['title'], p['pack'], need[p['unit']]))
        else:
            print('  第%-2s週  月末確認（%sの冊子）' % (w2, p['check']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
