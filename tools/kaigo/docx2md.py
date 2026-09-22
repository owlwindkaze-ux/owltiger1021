# -*- coding: utf-8 -*-
"""Word（.docx）を Markdown に変える。

    python3 tools/kaigo/docx2md.py 入力.docx 出力.md

なぜ作ったか
  紙の教材（介護の日本語・全12点）は Word で作ってある。サイトに置くには PDF に
  したいが、この環境の LibreOffice は起動できない（source file could not be loaded）。
  そこで、すでに使っている md → HTML → PDF の流れに合わせるため、いったん
  Markdown にする。見出し・表・箇条書き・太字・行内改行だけを扱う。

扱うもの
  ・Heading1〜3          → # ## ###
  ・番号付き／箇条書き   → 1. / -（numbering.xml の numFmt を見て決める）
  ::・表                  → Markdown の表（1行目を見出しにする）
  ・<w:br/>              → 段落の中の改行（md2html.py が <br> にする）
  ・太字                 → **…**
"""
import io, os, re, sys, zipfile
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def num_formats(z):
    """numId → 'decimal' / 'bullet' の対応を作る。"""
    try:
        x = ET.fromstring(z.read('word/numbering.xml'))
    except KeyError:
        return {}
    absfmt = {}
    for a in x.findall(W + 'abstractNum'):
        lv = a.find(W + 'lvl')
        f = lv.find(W + 'numFmt') if lv is not None else None
        absfmt[a.get(W + 'abstractNumId')] = f.get(W + 'val') if f is not None else 'bullet'
    out = {}
    for n in x.findall(W + 'num'):
        a = n.find(W + 'abstractNumId')
        out[n.get(W + 'numId')] = absfmt.get(a.get(W + 'val'), 'bullet') if a is not None else 'bullet'
    return out


def run_text(r):
    """1つの run を文字にする。太字は ** で囲む。改行・タブも拾う。"""
    s = ''
    for c in r:
        t = c.tag.replace(W, '')
        if t == 't':
            s += c.text or ''
        elif t == 'br':
            s += '\n'
        elif t == 'tab':
            s += '　'
    if not s:
        return ''
    pr = r.find(W + 'rPr')
    bold = pr is not None and pr.find(W + 'b') is not None
    if bold and s.strip():
        # 前後の空白は ** の外に出す（** 直後に空白があると太字にならない）
        m = re.match(r'^(\s*)(.*?)(\s*)$', s, re.S)
        s = m.group(1) + '**' + m.group(2) + '**' + m.group(3)
    return s


def para(p, fmts):
    st = p.find(W + 'pPr/' + W + 'pStyle')
    style = st.get(W + 'val') if st is not None else ''
    text = ''.join(run_text(r) for r in p.findall(W + 'r')).strip()
    if not text:
        return ''
    m = re.match(r'^Heading(\d)$', style or '')
    if m:
        lv = min(int(m.group(1)), 6)
        return '#' * lv + ' ' + text.replace('\n', ' ')
    numid = p.find(W + 'pPr/' + W + 'numPr/' + W + 'numId')
    if numid is not None:
        fmt = fmts.get(numid.get(W + 'val'), 'bullet')
        head = '1. ' if fmt not in ('bullet',) else '- '
        return head + text.replace('\n', ' ')
    return text


def table(tbl, fmts):
    rows = []
    for tr in tbl.findall(W + 'tr'):
        cells = []
        for tc in tr.findall(W + 'tc'):
            parts = [para(p, fmts) for p in tc.findall(W + 'p')]
            cells.append(' '.join(x for x in parts if x).replace('|', '／').replace('\n', ' '))
        rows.append(cells)
    if not rows:
        return ''
    n = max(len(r) for r in rows)
    rows = [r + [''] * (n - len(r)) for r in rows]
    out = ['| ' + ' | '.join(rows[0]) + ' |', '|' + '---|' * n]
    for r in rows[1:]:
        out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out)


def convert(path):
    z = zipfile.ZipFile(path)
    fmts = num_formats(z)
    body = ET.fromstring(z.read('word/document.xml')).find(W + 'body')
    out = []
    for el in body:
        t = el.tag.replace(W, '')
        if t == 'p':
            s = para(el, fmts)
            if s:
                out.append(s)
        elif t == 'tbl':
            s = table(el, fmts)
            if s:
                out.append(s)
    # 箇条書きが続くところは 空行を はさまない。はさむと md2html.py が
    # 1項目ずつ 別の <ol> にしてしまい、番号が ぜんぶ 1. になる。
    md = ''
    for i, b in enumerate(out):
        if i:
            li = re.match(r'^(1\. |- )', b) and re.match(r'^(1\. |- )', out[i - 1])
            md += '\n' if li else '\n\n'
        md += b
    return md + '\n'


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    md = convert(sys.argv[1])
    io.open(sys.argv[2], 'w', encoding='utf-8').write(md)
    print('%s → %s（%d字）' % (os.path.basename(sys.argv[1]), sys.argv[2], len(md)))
