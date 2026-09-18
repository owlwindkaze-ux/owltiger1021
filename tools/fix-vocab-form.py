# -*- coding: utf-8 -*-
"""語彙データの手入れ（2026-09-18）

1. 助数詞・接尾語（～円・～回…）に「語形成」の札が無いものが44語あった。
   絞り込みで出てこないので、札を付ける。
2. 〜がち・〜気味・〜だらけ は文型データにも同じものが入っていた。
   語のかたちが「動詞・形容詞に付く」もので、語彙ではなく文型。語彙側から外す。

vocab-data.json（元）と レベル別ファイル（画面が読む方）の両方を同じに直す。
"""
import json, io, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROP = {'〜がち', '〜気味', '〜だらけ'}          # 文型へ移す（語彙から外す）
GOKEI = '語形成'

def load(p):
    return json.load(io.open(os.path.join(HERE, p), encoding='utf-8'))

def save(p, obj):
    with io.open(os.path.join(HERE, p), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write('\n')

def is_tilde(w):
    return '～' in w or '〜' in w

def fix(words):
    """戻り値：（札を付けた数, 外した数, 残った語）"""
    tagged = 0
    kept = []
    for x in words:
        if x['word'] in DROP:
            continue
        if is_tilde(x['word']) and not x.get('category'):
            x['category'] = GOKEI
            x.setdefault('sub', '接頭語・接尾語')
            tagged += 1
        kept.append(x)
    return tagged, len(words) - len(kept), kept

def main():
    total_tag = total_drop = 0

    # --- 元データ ---
    md = load('vocab-data.json')
    t, d, md['words'] = fix(md['words'])
    md['count'] = len(md['words'])
    total_tag += t; total_drop += d
    save('vocab-data.json', md)
    print('vocab-data.json　札 %d語　外した %d語　→ %d語' % (t, d, md['count']))

    # --- 画面が読むレベル別ファイル ---
    idx = load('vocab.json')
    for f in idx['files']:
        j = load(f['file'])
        arr = j['words'] if isinstance(j, dict) and 'words' in j else j
        t, d, kept = fix(arr)
        if isinstance(j, dict) and 'words' in j:
            j['words'] = kept
            if 'count' in j: j['count'] = len(kept)
            out = j
        else:
            out = kept
        f['count'] = len(kept)
        total_tag += t; total_drop += d
        save(f['file'], out)
        print('%-18s 札 %2d語　外した %d語　→ %d語' % (f['file'], t, d, len(kept)))

    n = sum(f['count'] for f in idx['files'])
    idx['count'] = n
    if 'total' in idx: idx['total'] = n      # 見出しの件数はこちらを見ている
    save('vocab.json', idx)
    print('合計　札 %d語　外した %d語　語彙 %d語' % (total_tag, total_drop, idx['count']))

    # --- 例文も外す ---
    sp = os.path.join(HERE, 'sentences.json')
    s = json.load(io.open(sp, encoding='utf-8'))
    sent = s['sentences']                      # 例文は "sentences" の中に入っている
    gone = [w for w in DROP if w in sent]
    for w in gone: del sent[w]
    if gone:
        s['count'] = len(sent)
        with io.open(sp, 'w', encoding='utf-8') as f:
            json.dump(s, f, ensure_ascii=False, indent=1); f.write('\n')
    print('例文を外した語', gone, '　例文 %d本' % len(sent))

main()
