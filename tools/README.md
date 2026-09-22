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
| `check-star.py` | **★の組み立て**（`bunpo/star.json`）を点検する。できあがる文を全部出すので、目で読んで確かめる |
| `kaigo/check-tests.py` | **回ごとに問題と解答がある紙の教材**（02・03・04・05・08）を点検する。回の数・解答の有無・選択肢が4つか・設問と解答の数・正解のかたより・理由を問う設問の有無を見る |
| `kaigo/docx2md.py` | **Word（.docx）を Markdown に変える**。見出し・表・箇条書き・太字・行内改行だけを扱う |
| `kaigo/answers-to-back.py` | **解答を巻末へまとめ直す**。回の途中にあった解答を巻末に移し、「ここから下は職員用です」の区切りを入れる。1字も消えていないかを文字の数で確かめる。**一度かけたら もう かけなくてよい**（かけ直しても何も動かない） |
| `kaigo/build.py` | **紙の教材（介護の日本語・全12点）の PDF を作り直す**。`tools/kaigo/md/*.md` が中身の正。Word は元の控え |
| `check-bunshou.py` | **文章の文法**（`bunpo/bunshou.json`）を点検する。空欄と設問の対応・番号の順・選択肢・正解のかたより・本文の長さを見る |
| `check-secrets.py` | **公開するファイルに、外に出してはいけない文字列が入っていないかを点検する**（URLの中の鍵・パスワードらしい書き方）。**外部サイトのリンクを足したら必ず通す** |
| `check-version.py` | **版が全ファイルでそろっているかを点検する**。版を上げたら必ず通す（ここを外して2度 事故を出した） |
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

## 版を上げたときの順番

    # version.json と、各ページの PAGE_VER / VERSION / app_version をそろえる
    python3 tools/check-version.py        # そろっているかを 機械で 確かめる

**一括置換で そろえたつもりが 空振りする**ことがあります（実際に 3ファイル 外しました）。
必ず この道具を 通してください。

**注意**：`alloc.js` を走らせ直すと、**週の割り当てが最初から計算し直されます**。
数語を直しただけのときは、すでに通っている学習者の予定が動いてしまうので、
`plan.json` の中のその語だけを直して `build-weeks.py` を通すほうが安全です。

## 紙の教材（`kaigo/`）を直したときの順番

    # 中身を直すときは tools/kaigo/md/*.md を直す（Word は元の控え）
    python3 tools/kaigo/check-tests.py      # 問題と解答が 合っているかを 点検する
    python3 tools/kaigo/build.py            # md → PDF を作り直す
    python3 tools/check-numbers.py          # 画面の「全12点」と ファイル数を突き合わせる
    python3 tools/check-version.py          # 版が そろっているかを 点検する

**問題を足したら、`check-tests.py` が通っても 必ず目で読むこと。**
「正解が2つある」（例：「ボタンを（　）」に「かける」と「とめる」の両方）は
機械では見つかりません。書き足したとき 4件 出しました。

Word を新しくもらったときだけ、フォルダを渡して md から作り直します。

    python3 tools/kaigo/build.py /path/to/Word版

**注意**：`md` を直したあとに Word から作り直すと、直した分が消えます。
Word を渡すのは、**新しい教材が増えたとき**だけにしてください。
そのときは、解答が回の途中に入った状態に戻るので、`answers-to-back.py` を
もう一度かけてください（`--write` なしで走らせると、何をするかだけ出ます）。

## 外部サイトへのリンクを足すとき

**このリポジトリは公開（public）です。合言葉はブラウザの中で画面を隠しているだけで、
HTMLやMarkdownに書いたことは合言葉なしで誰でも読めます。**

    python3 tools/check-secrets.py        # 鍵やパスワードが まぎれていないかを 見る

- **鍵つきURL（`?k=…`・`?token=…`）は書かない。** ログイン画面など、
  だれが見ても困らないURLだけを載せる。
- `target="_blank" rel="noopener noreferrer"` を付ける。
  `noreferrer` は、こちらのURLを相手のサイトに渡さないため。
- **リンクが生きているかは機械で見られません**（この環境は外に出られません）。
  人が時々開いて確かめてください。

一度、**「鍵つきURLは載せない」と書いた説明文の中に鍵そのものを書いてしまいました**
（公開前に気づいて消しました）。気をつけるだけでは また やるので、道具にしました。

## 道具が出した結果の扱い

**道具が「おかしい」と言った件は、必ず手で確かめてから直すこと。**
以前、`check-ui.mjs` が出した12件が全部その道具自身のまちがい（見ている場所が
ちがった）だったことがあります。
