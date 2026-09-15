# -*- coding: utf-8 -*-
"""画面に出る文字列（インドネシア語・日本語）を抜き出して点検用のCSVを作る。

  python extract-ui.py

出力: ui-strings.csv（Excelでそのまま開けるUTF-8 BOM付き）
アプリのファイルは一切変更しない。読み取るだけ。
"""
import io, os, re, csv

TARGETS = [
    ('文型アプリ', os.path.join('..', 'bunpo', 'index.html')),
    ('漢字アプリ', os.path.join('..', 'index.html')),
]
OUT = 'ui-strings.csv'

def has_latin(s):
    return re.search(r'[A-Za-z]{2,}', s) is not None

def clean(s):
    s = s.replace('&amp;', '&').replace('&times;', '×').replace('&lt;', '<').replace('&gt;', '>')
    return re.sub(r'\s+', ' ', s).strip()

def split_pair(s):
    """「Masuk ／ 入る」を（尼語, 日本語）に分ける"""
    if '／' in s:
        a, b = s.split('／', 1)
        return clean(a), clean(b)
    return (clean(s), '') if has_latin(s) else ('', clean(s))

rows, seen = [], set()

for app, path in TARGETS:
    src = io.open(path, encoding='utf-8').read()
    # <style> は対象外。<script> は利用者に見えるメッセージがあるので残す
    body = re.sub(r'<style.*?</style>', '', src, flags=re.S)
    script = ''.join(re.findall(r'<script.*?</script>', body, flags=re.S))
    html = re.sub(r'<script.*?</script>', '', body, flags=re.S)

    found = []
    # HTMLの文字（タグの間）
    for m in re.findall(r'>([^<>{}]+)<', html):
        found.append(('画面の文字', m))
    # 属性（入力欄の説明文など）
    for attr in ('placeholder', 'title', 'alt'):
        for m in re.findall(attr + r'="([^"]+)"', html):
            found.append(('入力欄の説明', m))
    # JavaScript の中の文字列（利用者に見えるメッセージ）
    for m in re.findall(r"'([^'\\\n]{3,120})'|\"([^\"\\\n]{3,120})\"", script):
        s = m[0] or m[1]
        if '／' in s or (has_latin(s) and re.search(r'[ぁ-んァ-ヶ一-龠]', s)):
            found.append(('メッセージ', s))

    for kind, raw in found:
        s = clean(raw)
        if len(s) < 2 or not (has_latin(s) or '／' in s):
            continue
        if re.fullmatch(r'[\w\-.#/&;:%,()\[\]{}=+*|]+', s):   # コードらしきものは除く
            continue
        idn, jpn = split_pair(s)
        if not idn:
            continue
        key = (app, idn, jpn)
        if key in seen:
            continue
        seen.add(key)
        rows.append([app, kind, idn, jpn, ''])

with io.open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['アプリ', '場所', 'インドネシア語（画面の表示）', '日本語（併記）', '直したい表現があれば記入'])
    w.writerows(rows)

print('%s に %d 件書き出しました' % (OUT, len(rows)))
for app, _ in TARGETS:
    print('  %s: %d 件' % (app, sum(1 for r in rows if r[0] == app)))
