# 実習生向けの使い方説明書

`新人コースの使い方.pdf` と `N2コースの使い方.pdf` を作るもとです。
N4を超える漢字にふりがなを付け、要点にインドネシア語を添えます。

    node tools/howto/shinjin.js      # → /tmp/howto/shinjin.html
    node tools/howto/n2.js           # → /tmp/howto/n2.html
    node /tmp/pdf/mkpdf.mjs /tmp/howto/shinjin.html "新人コースの使い方.pdf" "新人コースの使い方"

`ruby.js` はふりがなの辞書です。語の単位で登録します（1字ずつだと読みが変わるため）。

## 作り直したら 必ず確かめること

1. **ルビ漏れ** … `R()` で包み忘れた所にはルビが付きません。見出しの副題や
   表のセルで漏れやすいので、作ったあとに「ルビの無いN4超えの漢字」を数えます。
2. **数字** … 語数・項目数はデータから取って書いています。データを直したら
   紙の数字もずれます。`vocab.json`・`bunpo/grammar.json`・`n2/weeks.json` と
   突き合わせてください。
