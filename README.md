# Kanji JLPT N5–N3 ／ JLPT N3 漢字学習ツール

日本語能力試験 N5・N4・N3 の漢字 **612字** を、**読み・意味（インドネシア語／英語）・用例・書き順アニメーション**で学べる無料の学習ツールです。
Alat belajar gratis untuk **612 kanji JLPT N5–N3**: cara baca, arti dalam **Bahasa Indonesia**, contoh kata, dan **animasi urutan coretan**.

**▶ 公開URL / Link:** https://owlwindkaze-ux.github.io/owltiger1021/

---

## 使い方 ／ Cara pakai

URLを開くだけです。インストール不要、スマホ・パソコン両対応。
Cukup buka link di atas. Tanpa instalasi, bisa di HP maupun komputer.

| タブ | Tab | できること |
|---|---|---|
| 一覧 | Daftar | 612字をカード表示。検索（漢字・読み・意味・用例）、レベル/画数/頻度で並べ替え。カードをタップで詳細 |
| フラッシュカード | Kartu | 「漢字→読み」「漢字→意味」「読み→漢字」「意味→漢字」の4モード。覚えた／要復習で仕分け |
| 書き順 | Urutan Coretan | 1画ずつの連続図（新しい画は赤）。文字をタップすると1画ずつアニメーションで書きます |
| 学習状況 | Progres | レベル別の到達率、要復習リスト、記録の書き出し |

### 詳細画面（カードをタップ）
- 開くと **自動で1画ずつ書き順アニメーション**が再生されます（もう一度見るには文字か「再生」をタップ）
- 音読み・訓読み、意味（インドネシア語＋英語）、用例（ふりがな・JLPTレベル付き）、部首

### キーボード操作（パソコン、フラッシュカード）
`Space`/`Enter` 答えを見る ・ `→`/`←` 次/前 ・ `1` まだ ・ `2` 覚えた ・ `Esc` 閉じる

### 学習記録
記録はブラウザ（端末内 localStorage）にのみ保存されます。サーバーには送信されません。
Catatan belajar hanya disimpan di perangkat Anda, tidak dikirim ke server.

---

## 収録内容 ／ Isi data

| レベル | 字数 | 備考 |
|---|---|---|
| N5 | 79字 | 入門 |
| N4 | 166字 | 初級 |
| N3 | 367字 | 中級 |
| **合計** | **612字** | N3までの累計 |

各漢字に：音読み・訓読み／意味（インドネシア語・英語）／画数・学年・使用頻度順位／部首／用例 平均約4語（ふりがな・意味・JLPTレベル付き）／**KanjiVG による実際の筆順データ**

> **注意：** 日本語能力試験（JLPT）は2010年の新形式移行以降、**公式の漢字リストを公表していません**。本ツールのレベル区分は、広く使われているデータセット（KANJIDIC2 / WaniKani 由来）の分類に基づく目安です。教材によって N2/N3 の境界が異なる字があります（例：橋 は本データでは N2 扱い）。

---

## ファイル構成

| ファイル | 内容 |
|---|---|
| `index.html` | アプリ本体（HTML/CSS/JS 単一ファイル、外部ライブラリなし） |
| `kanji-data.json` | 漢字612字のデータ（読み・意味・用例・部首など） |
| `kanji-strokes.json` | 書き順データ（KanjiVG のパス、612字ぶん） |

### ローカルで動かす場合
```bash
git clone https://github.com/owlwindkaze-ux/owltiger1021.git
cd owltiger1021
git checkout claude/japanese-n3-kanji-AaKYe
python -m http.server 8000     # → ブラウザで http://localhost:8000
```
※ JSONを読み込むため、ファイルを直接ダブルクリックで開くのではなく、上のようにローカルサーバー経由で開いてください。

### 漢字を追加・修正するには
`kanji-data.json` の `kanji` 配列を編集します（1字ぶんの形）：
```json
{
  "character": "新", "level": "N4", "strokes": 13,
  "on": ["しん"], "kun": ["あたら.しい", "あら.た"],
  "meanings": ["new"], "meanings_id": ["baru"],
  "radical": {"character": "斤", "name": "おのづくり", "meaning": "axe"},
  "examples": [{"word": "新聞", "reading": "しんぶん", "meaning": "newspaper",
                "meaning_id": "surat kabar", "jlpt": "N5"}]
}
```
書き順も追加する場合は `kanji-strokes.json` の `strokes` に、その漢字の SVG パスを筆順どおりの配列で追加します（KanjiVG から取得可）。

---

## 品質について ／ Kualitas data

- 画数は **KANJIDIC2・Kanji alive・KanjiVG の3つの独立したデータで完全一致**を確認済み（612字すべて、不一致0件）
- 全612字に読み・意味・用例（平均3.98語）・筆順データが揃っていることを自動検証済み
- ブラウザ実機テスト（Chromium）24項目に合格：表示・検索・絞り込み・アニメーション・記録保存・スマホ表示
- インドネシア語訳は、漢字・読み・用例の**日本語の文脈ごと**に作成（英語だけを見て訳すと「権利→kanan（右）」のような同形異義語の誤訳が起きるため）
- 独立した第三者レビューで **175字・866文字列を抽出検査 → 正確度 約99.3%、重大な誤り0件**。指摘された箇所は修正済み
- 誤訳を見つけた場合は `kanji-data.json` の該当箇所（`meanings_id` / `meaning_id`）を修正してください

---

## データ出典とライセンス ／ Sumber data & lisensi

本ツールは以下のオープンデータを利用しています。再配布の際は各ライセンスの表示義務にご注意ください。

| データ | 用途 | ライセンス |
|---|---|---|
| [kanji-data](https://github.com/davidluzgouveia/kanji-data)（[KANJIDIC2](https://www.edrdg.org/wiki/index.php/KANJIDIC_Project) / EDRDG 由来） | 読み・意味・画数・学年・頻度・JLPTレベル | CC BY-SA 4.0 |
| [Kanji alive](https://github.com/kanjialive/kanji-data-media)（University of Chicago） | 用例・部首 | CC BY 4.0 |
| [KanjiVG](http://kanjivg.tagaini.net)（Ulrich Apel） | 書き順（筆画データ） | CC BY-SA 3.0 |
| [open-anki-jlpt-decks](https://github.com/jamsinclair/open-anki-jlpt-decks)（tanos.co.uk 由来） | 用例のJLPTレベル判定 | CC BY 4.0 |

`kanji-strokes.json` は KanjiVG の派生物のため **CC BY-SA 3.0** で提供されます。
