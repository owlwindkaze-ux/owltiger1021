# tools ／ 作り直すための道具

データを直したあと、**画面と紙をそろえ直す**ための道具です。
順番を守らないと、画面の週割りと PDF の範囲表がずれます。

## 置いてあるもの

| ファイル | 何をするか |
|---|---|
| `fix-vocab-form.py` | 語彙データの手入れ（語形成の札・文型と重なる語の除外） |
| `split-data.py` | まとめ役の `vocab-data.json` を、レベル別ファイルに分ける |
| `hani/alloc.js` | 新人コースの週割りを計算する → `/tmp/hani/plan.json` |
| `hani/gen.js` | 新人コースの `週ごとの学習範囲表` の HTML を作る |
| `hani/test.js`・`hani/testpdf.js` | 月次確認テストを作る |
| `n2plan/alloc.js` | N2コースの週割りを計算する → `/tmp/n2plan/plan.json` |
| `n2plan/gen.js` | N2の `週ごとの学習範囲表` の HTML を作る |
| `n2plan/howto.js` | `N2の勉強のしかた` の HTML を作る |
| `hani/ruby.js` | 範囲表・テスト用のふりがな辞書 |
| `howto/` | 実習生向けの使い方説明書（`howto/README.md` を見てください） |
| `hani/n4hantei*.js` | **N4到達度判定テスト**（第1週・66問）。`-data.js` が問題、`n4hantei.js` が冊子、`-choukai.js` が読み上げ画面への注入、`-check.py` が範囲の点検 |
| `reference/jlpt-format.md` | **JLPTの出題形式（N3・N2）**。公式スライドから起こした大問の一覧・読解の字数の目安・聴解の答え方の流れ・いまの教材との差。**問題を作る前にここを見る** |
| `shindan/` | **診断テスト**（第1回＝第2週／第2回＝第16週）。`build.js`→`render.js` の順に走らせると `/tmp/shindan/out/` に問題冊子と手引きが出る |
| `build-weeks.py` | plan.json から `kanji-weeks.json`・`bunpo/weeks.json`・`n2/weeks.json` を作り直し、**割り当てた語が本当にデータにあるかを点検する** |
| `check-numbers.py` | **画面に書いてある数が、データの数と合っているかを点検する**。教材を足したら必ず通す |
| `check-ui.mjs` | 全画面の絞り込み・タブを実ブラウザで動かして点検する |
| `check-n2.py` | N2の期・問題・模試・レベル・週の負荷を点検する |
| `balance-answers.py` | 正解の番号のかたよりを直す（選択肢の並べかえだけ。文と正解は変えない） |

## 語彙・文型を直したときの順番

    python3 tools/fix-vocab-form.py       # 手入れがあれば
    python3 tools/split-data.py           # レベル別ファイルを作り直す
    node tools/hani/alloc.js              # 週割りを計算し直す（※下の注意）
    node tools/n2plan/alloc.js
    python3 tools/build-weeks.py          # 週のファイルを作り直し、点検する
    node tools/hani/gen.js && node tools/n2plan/gen.js   # 範囲表のHTML
    # → mkpdf で PDF にする
    python3 tools/check-numbers.py        # 画面の数とデータの数を突き合わせる
    node tools/check-ui.mjs               # 実ブラウザで点検（先にサーバを立てる）

**注意**：`alloc.js` を走らせ直すと、**週の割り当てが最初から計算し直されます**。
数語を直しただけのときは、すでに通っている学習者の予定が動いてしまうので、
`plan.json` の中のその語だけを直して `build-weeks.py` を通すほうが安全です。

## 道具が出した結果の扱い

**道具が「おかしい」と言った件は、必ず手で確かめてから直すこと。**
以前、`check-ui.mjs` が出した12件が全部その道具自身のまちがい（見ている場所が
ちがった）だったことがあります。
