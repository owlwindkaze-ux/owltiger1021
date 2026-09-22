# -*- coding: utf-8 -*-
"""介護の日本語（紙の教材・全12点）を Word から PDF に作り直す。

    python3 tools/kaigo/build.py [Word版のフォルダ]

流れ
    .docx  →（docx2md.py）→  tools/kaigo/md/*.md  →（md2html.py）→  HTML
           →（mkpdf.mjs・Playwright）→  kaigo/*.pdf

Word のフォルダを渡さなければ、すでにある tools/kaigo/md/*.md から PDF を
作り直します。**中身を直すときは md を直してください。**Word は元の控えです。

なぜ Word から md にするか
    この環境の LibreOffice は起動できない（source file could not be loaded）。
    それに、あとで画面（オンライン）の問題に作り替えるとき、md のほうが扱いやすい。
"""
import io, os, re, subprocess, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MD = os.path.join(ROOT, 'tools', 'kaigo', 'md')
OUT = os.path.join(ROOT, 'kaigo')
VER = '2026-09-22e'
MD2HTML = '/tmp/pdf/md2html.py'
MKPDF = '/tmp/pdf/mkpdf.mjs'


def title_of(name):
    """01_N3実力テスト_第1回 → N3実力テスト 第1回"""
    s = re.sub(r'^\d+_', '', name)
    return s.replace('_', ' ')


def main():
    os.makedirs(MD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if src:
        d2m = os.path.join(ROOT, 'tools', 'kaigo', 'docx2md.py')
        for f in sorted(glob.glob(os.path.join(src, '*.docx'))):
            base = os.path.splitext(os.path.basename(f))[0]
            subprocess.check_call([sys.executable, d2m, f, os.path.join(MD, base + '.md')])
    mds = sorted(glob.glob(os.path.join(MD, '*.md')))
    if not mds:
        print('md がありません。Word版のフォルダを渡してください。')
        return 1
    for m in mds:
        base = os.path.splitext(os.path.basename(m))[0]
        t = title_of(base)
        html = '/tmp/kaigo-%s.html' % base
        pdf = os.path.join(OUT, base + '.pdf')
        foot = '介護の日本語 ／ %s ／ %s' % (t, VER)
        subprocess.check_call([sys.executable, MD2HTML, m, html, t, foot])
        # 「ここから下は 職員用です」は 必ず 次のページから 始める。
        # ここが ページの 途中だと、実習生に渡す分を 印刷するとき 切れ目が 分からない。
        h = io.open(html, encoding='utf-8').read()
        # 10問目の 番号が「0.」に 見えていた。md2html.py の CSS が
        # ul,ol { margin-left:1.4em; padding:0 } で、番号は その 1.4em の中に
        # 出るため、2桁の「10.」が はみ出して 左が 切れる。
        # 印刷して 配る 紙なので、幅を 広げて 直す。
        h = h.replace('</style>',
                      '\nul,ol { margin-left: 0; padding-left: 2.2em; }\n</style>')
        h2 = h.replace('<h1>ここから下は 職員用です</h1>',
                       '<h1 style="page-break-before:always;border-top:3px double #b91c1c;'
                       'color:#b91c1c;padding-top:10px">ここから下は 職員用です</h1>')
        io.open(html, 'w', encoding='utf-8').write(h2)
        subprocess.check_call(['node', MKPDF, html, pdf, foot],
                              env=dict(os.environ, NODE_PATH='/tmp/node_modules'))
    print('\n%d 件を %s に作りました。' % (len(mds), OUT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
