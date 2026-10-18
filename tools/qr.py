#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""住所のQRコードを作る（SPEC 2.6-z48）。

**なぜ画像をリポジトリに置くのか**

QRは外部のサービスで作ることもできるが、**使わない**。
①住所を外へ送ることになる ②そのサービスが止まると作り直せない
③このシステムは「外部の部品を一切使わない」という作りで通している。

そこで**ここで一度だけ作って `tools/qr.svg` に置く**。
そうすれば、紙を作る側（`shiyou-id.py`）は **segno が入っていなくても動く**。

**古くならない仕組み**：SVGの中に、**どの住所で作ったか**を書いておく。
紙を作るときに住所と突き合わせ、**ちがっていれば止まる**。
住所を変えたのにQRが前のまま、が いちばん困るため。

    pip install segno
    python3 tools/qr.py          # tools/qr.svg を作り直す
"""
import io
import os
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# 公開している住所。ここを変えたら、必ずこの道具を走らせ直すこと。
URL = 'https://owlwindkaze-ux.github.io/owltiger1021/'
OUT = R + 'tools/qr.svg'
MARK = '<!-- url: %s -->'


def url_of(svg):
    """SVGに書いてある「どの住所で作ったか」を返す"""
    i = svg.find('<!-- url: ')
    if i < 0:
        return None
    return svg[i + len('<!-- url: '):svg.index(' -->', i)]


def main():
    try:
        import segno
    except ImportError:
        return print('× segno が ありません。pip install segno を先に。') or 1
    q = segno.make(URL, error='m')
    # 枠（border）は4が規格。読み取り機が外枠を必要とするので 減らさない。
    svg = q.svg_inline(scale=10, border=4, dark='#1b2733')
    # **viewBox を足す。**これが無いと、紙の側で大きさを指定したときに
    # 縮まずに **切り取られる**（左上の角だけになる）。実際そうなった。
    import re as _re
    m = _re.search(r'width="(\d+)" height="(\d+)"', svg)
    if not m:
        return print('× SVGの大きさが読めません') or 1
    w, h = m.group(1), m.group(2)
    if 'viewBox' not in svg:
        svg = svg.replace(m.group(0),
                          '%s viewBox="0 0 %s %s"' % (m.group(0), w, h), 1)
    io.open(OUT, 'w', encoding='utf-8').write(MARK % URL + '\n' + svg)
    print('書きました: %s' % OUT)
    print('  住所: %s' % URL)
    print('  大きさ: %d マス' % (q.symbol_size(scale=1, border=0)[0]))
    return verify(q)


def verify(q):
    """**作ったQRを、機械で読み返す。**

    QRは目で見ても中身が分からない。住所を1字まちがえても気づけず、
    実習生が**開けない紙**を配られることになる。だから読み返す。
    道具が入っていなければ、**入れてくださいと言うだけ**にして止めない
    （紙を作る側は この確認が無くても動くため）。
    """
    try:
        import zxingcpp
        from PIL import Image
    except ImportError:
        print('△ 読み返しは していません。'
              '確かめるなら pip install zxing-cpp pillow')
        return 0
    import io as _io
    png = q.png_data_uri(scale=6, border=4)
    import base64
    raw = base64.b64decode(png.split(',', 1)[1])
    img = Image.open(_io.BytesIO(raw)).convert('RGB')
    r = zxingcpp.read_barcode(img)
    got = r.text if r else None
    if got != URL:
        return print('× 読み返しに 失敗しました。\n  読めた: %s\n  のはず: %s'
                     % (got, URL)) or 1
    print('  読み返し: OK（%s）' % got)
    return 0


if __name__ == '__main__':
    sys.exit(main())
