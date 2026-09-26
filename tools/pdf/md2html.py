#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown（SPEC.md・MANUAL.md など）を、PDF用の HTML に変える。

**なぜリポジトリに置いてあるか**
この道具は もともと作業用の場所（`/tmp`）にしか無く、**場所が消えたときに
PDFを作り直せなくなりました**（2026-09-26）。同じことを、参考書のリストでも
やっています。**作った道具は必ずリポジトリに入れること。**

    python3 tools/pdf/md2html.py SPEC.md /tmp/out/spec.html "仕様書" "owltiger1021 仕様書"

必要なもの： pip install markdown
そのあと tools/pdf/mkpdf.mjs で PDF にします。
"""
import io
import re
import sys

import markdown

CSS = r"""
@page { size: A4; margin: 16mm 14mm 18mm; }
body{font-family:"IPAPGothic","IPAGothic","Noto Sans CJK JP",sans-serif;
 color:#1b2733;font-size:9.5pt;line-height:1.75;margin:0}
h1{font-size:19pt;color:#9a3412;border-bottom:3px solid #9a3412;
 padding-bottom:5px;margin:0 0 5mm;page-break-after:avoid}
h2{font-size:13.5pt;color:#9a3412;margin:7mm 0 3mm;padding:2mm 0 2mm 3mm;
 border-left:5px solid #c2410c;background:#fff7ed;page-break-after:avoid}
h3{font-size:11pt;color:#0e7a52;margin:5mm 0 2mm;border-bottom:1px solid #cfe6dc;
 padding-bottom:1mm;page-break-after:avoid}
h4{font-size:10pt;margin:4mm 0 1.5mm;page-break-after:avoid}
p{margin:0 0 2.5mm}
ul,ol{margin:0 0 2.5mm;padding-left:6mm}
li{margin:0 0 1mm}
table{border-collapse:collapse;width:100%;margin:0 0 3mm;font-size:8.8pt;
 page-break-inside:avoid}
th,td{border:1px solid #c9d4de;padding:1.2mm 2mm;text-align:left;
 vertical-align:top;word-break:break-word}
th{background:#eef4f9;font-weight:700}
code{font-family:"DejaVu Sans Mono",monospace;font-size:8.5pt;
 background:#f2f5f8;padding:0 1mm;border-radius:2px}
pre{background:#f7f9fb;border:1px solid #dde5ec;border-radius:3px;
 padding:2mm 3mm;overflow-wrap:break-word;white-space:pre-wrap;
 font-size:8.5pt;margin:0 0 3mm;page-break-inside:avoid}
pre code{background:none;padding:0}
blockquote{margin:0 0 3mm;padding:1mm 0 1mm 3mm;border-left:4px solid #d5dee7;
 color:#4a5866}
hr{border:0;border-top:1px solid #d5dee7;margin:5mm 0}
b,strong{color:#0b1720}
a{color:#12459c;text-decoration:none}
img{max-width:100%}
"""


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    src, dst = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else ''
    md = io.open(src, encoding='utf-8').read()

    # 生の <b> などは そのまま通す。Markdown のテーブルと 目次は 拡張で扱う。
    html = markdown.markdown(
        md, extensions=['tables', 'fenced_code', 'sane_lists', 'attr_list'],
        output_format='html5')

    # 見出しの直後で 改ページされると 読みにくいので、章の頭だけ 改ページを許す
    html = re.sub(r'<h1>', '<h1 class="top">', html, count=1)

    out = ('<!doctype html><html lang="ja"><head><meta charset="utf-8">'
           '<title>%s</title><style>%s</style></head><body>%s</body></html>'
           % (title or src, CSS, html))
    io.open(dst, 'w', encoding='utf-8').write(out)
    print('wrote %s（%d文字 → %d文字）' % (dst, len(md), len(out)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
