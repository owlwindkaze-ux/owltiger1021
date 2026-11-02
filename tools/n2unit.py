#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**N2の紙のパックを 画面版にする**（`moshi/n2u-*.json`）（SPEC 2.6-z70）。

持ち主から「**N2の単元を画面に入れる**」。第1単元だけ手で作ってあった（z54）。
残り13単元を 手で写すと 260問。**写し落としが いちばん怖い**ので、
ドライブの2つの文書から **組み立てる**。

  学習者用問題        … 問題文・選択肢・本文
  指導者用解答・解説   … 正解・解説・聴解台本

**新しい問題は1問も書かない。**中身は紙と同じ。並べ方だけ画面の形にする。

  python3 tools/n2unit.py 学習者用.txt 指導者用.txt [--check]

**原文はリポジトリに入れない**（施設の教材）。作業用の場所に置いて走らせる。

紙の問20問は、画面ではこう並ぶ（第1単元と同じ形）。

  問1〜8   → 問題1〜8（1問ずつ）
  問9・10  → 問題9  文章の文法（本文つき・2問）
  問11     → 問題10 内容理解（短文）
  問12・13 → 問題11 内容理解（中文）
  問14・15 → 問題12 読解（情報検索／統合理解／主張理解）
  問16〜20 → 聴解1〜5
"""
import io
import json
import os
import re
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# 紙の「種類」→ 画面の大問名と指示文
KIND = {
    '漢字読み': ('漢字読み', '＿＿の言葉の読み方として最もよいものを、一つえらびなさい。'),
    '表記': ('表記', '＿＿の言葉を漢字で書くとき、最もよいものを一つえらびなさい。'),
    '語形成': ('語形成', '（　）に入れるのに最もよいものを、一つえらびなさい。'),
    '文脈規定': ('文脈規定', '（　）に入れるのに最もよいものを、一つえらびなさい。'),
    '言い換え類義': ('言い換え類義', '＿＿の言葉に意味が最も近いものを、一つえらびなさい。'),
    '用法': ('用法', 'つぎの言葉の使い方として最もよいものを、一つえらびなさい。'),
    '文の文法1': ('文法形式の判断', 'つぎの文の（　）に入れるのに最もよいものを、一つえらびなさい。'),
    '文の組み立て': ('文の組み立て', '★に入る最もよいものを、一つえらびなさい。'),
}
READ_INST = 'つぎの文章を読んで、質問に答えなさい。'
INFO_INST = 'つぎの案内を見て、質問に答えなさい。'
CHOU = [('課題理解', '話を聞いて、このあとまず何をするかをえらびなさい。'),
        ('ポイント理解', '話を聞いて、質問に答えなさい。'),
        ('概要理解', '話を聞いて、話し手が最も言いたいことをえらびなさい。'),
        ('即時応答', '短い問いかけを聞いて、返事をえらびなさい。'),
        ('統合理解', '説明と会話を聞いて、質問に答えなさい。')]


def units(text):
    """「# **第N単元　…**」で切り分ける。月末確認は 画面版にしない。"""
    ms = list(re.finditer(r'^# \*\*第(\d+)単元　(.+?)\*\*$', text, re.M))
    out = []
    for i, m in enumerate(ms):
        end = len(text)
        nxt = re.search(r'^# \*\*', text[m.end():], re.M)
        if nxt:
            end = m.end() + nxt.start()
        out.append((int(m.group(1)), m.group(2), text[m.end():end]))
    return out


def questions(body):
    """「**問N　種類**」ごとに、中の行を集める。"""
    ms = list(re.finditer(r'^\*\*問(\d+)　(.+?)\*\*$', body, re.M))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(body)
        chunk = body[m.end():end]
        lines = [x.strip() for x in chunk.split('\n') if x.strip()]
        out.append({'no': int(m.group(1)), 'kind': m.group(2), 'lines': lines})
    return out


CH1 = re.compile(r'^[1-4]　')


def split_q(lines):
    """問の中身を 本文・問題文・選択肢に分ける。"""
    psg, stem, ch = [], [], []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('答え：') or ln.startswith('解答：'):
            break
        if ln.startswith('〔'):
            psg.append(ln); i += 1; continue
        if CH1.match(ln):
            # 1行にまとまっている形
            parts = re.split(r'　{2,}(?=[1-4]　)', ln)
            if len(parts) >= 3:
                ch = [re.sub(r'^[1-4]　', '', p).strip() for p in parts]
                i += 1
                continue
            # 1行ずつ 分かれている形
            got = [re.sub(r'^1　', '', ln).strip()]
            j = i + 1
            while j < len(lines) and len(got) < 4:
                mm = re.match(r'^([2-4])　(.+)$', lines[j])
                if not mm or int(mm.group(1)) != len(got) + 1:
                    break
                got.append(mm.group(2).strip()); j += 1
            if len(got) >= 3:
                ch = got; i = j; continue
        stem.append(ln); i += 1
    return psg, stem, ch


def keys_and_notes(tbody):
    """指導者用から 正解番号・解説・聴解台本を取り出す。"""
    key = {}
    m = re.search(r'^## \*\*正答一覧\*\*$(.+?)^## ', tbody, re.M | re.S)
    if m:
        for a, b in re.findall(r'(\d+)＝(\d)', m.group(1)):
            key[int(a)] = int(b) - 1
    note = {}
    for mm in re.finditer(r'^\*\*問(\d+)　(.+?)　正解：(\d)\*\*$(.*?)(?=^\*\*問|\Z)',
                          tbody, re.M | re.S):
        n = int(mm.group(1))
        key.setdefault(n, int(mm.group(3)) - 1)
        body = [x.strip() for x in mm.group(4).split('\n') if x.strip()]
        body = [x for x in body if not x.startswith(('正解の内容：', '完成順序：', '完成文：'))]
        # 「ID: …」から後ろは インドネシア語。日本語の欄に残さない
        txt = ' '.join(body)
        txt = re.split(r'ID:', txt)[0].strip()
        note[n] = txt
    scr = {}
    m = re.search(r'^## \*\*聴解台本.*?\*\*$(.+?)(?=^## |\Z)', tbody, re.M | re.S)
    if m:
        for mm in re.finditer(r'^\*\*問(\d+)　.+?\*\*$(.*?)(?=^\*\*問|\Z)',
                              m.group(1), re.M | re.S):
            raw = [x.strip() for x in mm.group(2).split('\n') if x.strip()]
            body, opts = [], []
            for x in raw:
                if x.startswith('〔'):          # 指導者への指示。読み上げない
                    continue
                if CH1.match(x):
                    # **問18〜20は 選択肢が音声**なので、学習者用には無い。
                    # 台本の中の選択肢を 画面の選択肢として使う（2026-11-02）。
                    parts = re.split(r'　{2,}(?=[1-4]　)', x)
                    if len(parts) >= 3:
                        opts = [re.sub(r'^[1-4]　', '', p).strip() for p in parts]
                    else:
                        opts.append(re.sub(r'^[1-4]　', '', x).strip())
                    continue
                body.append(x)
            scr[int(mm.group(1))] = {'lines': body, 'opts': opts}
    return key, note, scr


SPEAK = re.compile(r'^(男|女|客|店員|先生|係|職員|担当|司会|母|父)(の人)?[：:]')
NUM = str.maketrans('一二三四五六七八九十', '12345678910'[:10])


def show_of(lines):
    """台本から、画面に出す読みやすい形を作る。
    話し手の行だけを残す。説明・質問の行は 読み上げ用にだけ使う。"""
    talk = [x for x in lines if SPEAK.match(x)]
    return '\n'.join(talk if talk else lines)


def build(num, title, qbody, tbody):
    key, note, scr = keys_and_notes(tbody)
    qs = {q['no']: q for q in questions(qbody)}
    miss = [n for n in range(1, 21) if n not in qs]
    if miss:
        print('× 第%d単元：問%s が 学習者用に ありません' % (num, '・'.join(map(str, miss))))
        sys.exit(1)
    aim = ''
    m = re.search(r'^学習目標：(.+)$', qbody, re.M)
    if m:
        aim = m.group(1).strip()

    S, order = {}, []

    def add(k, label, name, inst, body):
        S[k] = {'label': label, 'name': name, 'inst': inst}
        S[k].update(body)
        order.append(k)

    def item(n):
        psg, stem, ch = split_q(qs[n]['lines'])
        if len(ch) < 3:
            print('× 第%d単元 問%d：選択肢が %d個しか取れません' % (num, n, len(ch)))
            sys.exit(1)
        if n not in key:
            print('× 第%d単元 問%d：正解が 指導者用に ありません' % (num, n))
            sys.exit(1)
        # **本文が何段落もあるとき**、2段落目から後ろも 本文。
        # 質問は いちばん最後の行。前は 2段落目を 質問だと思って出していた
        # （「先輩に相談すると、…」が 設問になっていた・2026-11-02）。
        para = list(psg)
        if psg and len(stem) > 1:
            para += stem[:-1]
            stem = stem[-1:]
        q = ' '.join(stem) or '　'
        kind = qs[n]['kind']
        # 【　】は 紙の印。画面の模試は ＿＿ ではさむ（engine の書き方に合わせる）
        if kind in ('漢字読み', '表記', '言い換え類義'):
            q = re.sub(r'【(.+?)】', r'＿\1＿', q)
        # 大問の指示に 書いてあることは 問から落とす
        q = q.replace('の使い方として最もよいものはどれですか。', '')
        if kind == '文章の文法':
            m2 = re.search(r'【\d+】', q)
            if m2:
                q = m2.group(0)
        return para, {'q': q.strip() or '　', 'choices': ch, 'answer': key[n],
                      'explain': note.get(n, '')}

    # ── 問1〜8 ────────────────────────────────────
    for n in range(1, 9):
        kind = qs[n]['kind']
        name, inst = KIND.get(kind, (kind, 'つぎの問いに答えなさい。'))
        _, it = item(n)
        add('問題%d' % n, '問題%d' % n, name, inst, {'items': [it]})

    # ── 問9・10 文章の文法（本文つき）─────────────────
    psg9, it9 = item(9)
    _, it10 = item(10)
    ptxt = ''
    if psg9:
        ptxt = '\n　'.join(re.sub(r'^〔[^〕]*〕', '', x).strip() for x in psg9)
    add('問題9', '問題9', '文章の文法',
        'つぎの文章を読んで、【9】【10】に入る最もよいものを、一つえらびなさい。',
        {'passage': {'title': '〔9・10共通〕', 'text': '　' + ptxt},
         'items': [it9, it10]})

    # ── 読解（問11／問12・13／問14・15）──────────────
    def read_sec(k, label, name, inst, ns):
        psg, first = item(ns[0])
        text = ''
        if psg:
            text = '\n　'.join(re.sub(r'^〔[^〕]*〕', '', x).strip() for x in psg)
        qlist = [first]
        for n in ns[1:]:
            qlist.append(item(n)[1])
        add(k, label, name, inst,
            {'group': '読解',
             'read': [{'passage': {'title': name, 'text': '　' + text,
                                   'questions': qlist},
                       'qi': list(range(len(qlist)))}]})

    read_sec('問題10', '問題10', '内容理解（短文）', READ_INST, [11])
    read_sec('問題11', '問題11', '内容理解（中文）', READ_INST, [12, 13])
    k14 = qs[14]['kind']
    nm14 = '情報検索' if '情報検索' in k14 else (
        '主張理解（長文）' if '長文' in k14 else '統合理解')
    read_sec('問題12', '問題12', nm14,
             INFO_INST if nm14 == '情報検索' else READ_INST, [14, 15])

    # ── 聴解（問16〜20）──────────────────────────
    for i, n in enumerate(range(16, 21)):
        name, inst = CHOU[i]
        sc = scr.get(n)
        if not sc or not sc['lines']:
            print('× 第%d単元 問%d：聴解台本が ありません' % (num, n)); sys.exit(1)
        lines = sc['lines']
        psg, stem, ch = split_q(qs[n]['lines'])
        opts = ch if len(ch) >= 3 else sc['opts']
        if len(opts) < 3:
            print('× 第%d単元 問%d：選択肢が %d個しか取れません' % (num, n, len(opts)))
            sys.exit(1)
        if n not in key:
            print('× 第%d単元 問%d：正解が 指導者用に ありません' % (num, n)); sys.exit(1)
        # **問題文は 台本の中の質問の行**。学習者用は「音声を聞いてください。」だけ。
        qline = ''
        if name == '即時応答':
            qline = lines[-1]                   # 短い問いかけ そのもの
        else:
            for x in reversed(lines):
                if x.endswith(('か。', 'か')) and not SPEAK.match(x):
                    qline = x
                    break
        if not qline:
            qline = lines[-1]
        add('聴解%d' % (i + 1), '聴解 問題%d' % (i + 1), name, inst,
            {'group': '聴解',
             'items': [{'q': qline, 'opts': opts, 'ans': key[n],
                        'exp': note.get(n, ''),
                        'script': ''.join(lines),
                        'show': show_of(lines)}]})

    total = sum(len(S[k].get('items', [])) +
                sum(len(r['qi']) for r in S[k].get('read', [])) for k in order)
    return {
        'no': num, 'title': '第%d単元　%s' % (num, title), 'aim': aim,
        'minutes': {'言語知識・読解': 47, '聴解': 8},
        'counts': {'言語知識': 10, '読解': 5, '聴解': 5, '合計': total},
        'parts': [
            {'name': '言語知識・読解', 'minutes': 47,
             'sections': [k for k in order if not k.startswith('聴解')],
             'next': '聴解へ進む（約8分）',
             'lead': '紙の冊子の A・B・D にあたります。'
                     '問1〜8が12分、問9〜13が20分、問14〜15が15分の目安です。'},
            {'name': '聴解', 'minutes': 8,
             'sections': [k for k in order if k.startswith('聴解')],
             'lead': '紙の冊子の C・E にあたります。まず1回で答えてみてください。'},
        ],
        'order': order, 'sections': S,
    }


def main():
    if len(sys.argv) < 3:
        raise SystemExit('使い方: python3 tools/n2unit.py 学習者用.txt 指導者用.txt [--check]')
    qtext = io.open(sys.argv[1], encoding='utf-8').read()
    ttext = io.open(sys.argv[2], encoding='utf-8').read()
    qu = {n: (t, b) for n, t, b in units(qtext)}
    tu = {n: b for n, _t, b in units(ttext)}
    both = sorted(set(qu) & set(tu))
    if not both:
        raise SystemExit('× 同じ番号の単元が 両方の文書に ありません')
    for n in both:
        d = build(n, qu[n][0], qu[n][1], tu[n])
        p = R + 'moshi/n2u-%d.json' % n
        if '--check' in sys.argv:
            old = json.load(io.open(p, encoding='utf-8')) if os.path.exists(p) else None
            same = old == d
            print('第%2d単元 %-28s %2d問  %s'
                  % (n, d['title'][5:], d['counts']['合計'],
                     'いまのファイルと同じ' if same else '（ちがう）'))
            continue
        io.open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False) + '\n')
        print('第%2d単元 %-28s %2d問  → moshi/n2u-%d.json'
              % (n, d['title'][5:], d['counts']['合計'], n))


main()
