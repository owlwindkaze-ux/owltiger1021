#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**自動詞・他動詞**（`jita.json`）と**敬語**（`keigo.json`）を点検する（SPEC 2.6-z66）。

この2つは 語彙データと例文データから **作り出している**。
もとの語を 消したり 読みを変えたりすると、**だまって ずれる**。
作り直せば `tools/jita.py` / `tools/keigo.py` が止まるが、
**作り直すのを忘れたまま 公開する**ことがあるので、ここでも見る。

見るところ
  ・語が 語彙データにあるか／読みが 合っているか（`alt` の読みも可）
  ・例文が 例文データと 同じか／文中の形が 例文の中に あるか
  ・自他が 同じ語になっていないか・同じ対が 二度出ていないか
  ・敬語で 尊敬語と謙譲語が 同じ語になっていないか
  ・画面（`kanji.html`）に タブと読み込みが あるか
  ・`app_version` が そろっているか

    python3 tools/check-jitakeigo.py
"""
import io
import json
import os
import sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
ng = []
bad = ng.append

V = {}
for f in ('vocab-n5.json', 'vocab-n4.json', 'vocab-n3.json', 'vocab-n2.json',
          'vocab-kaigo.json', 'vocab-genba.json', 'vocab-kiroku.json'):
    p = R + f
    if os.path.exists(p):
        for w in json.load(io.open(p, encoding='utf-8'))['words']:
            V.setdefault(w['word'], w)
S = json.load(io.open(R + 'sentences.json', encoding='utf-8'))['sentences']
VER = json.load(io.open(R + 'version.json', encoding='utf-8'))['version']


def cell(c, where, same_sent=True):
    """語・読み・例文が もとのデータと 合っているか。

    敬語の表だけは `same_sent=False`。**例文を 行ごとに持つ**ので
    （同じ語が いくつもの行に出るため）、語の例文とは ちがってよい。
    """
    if c is None:
        return
    w = V.get(c['word'])
    if not w:
        bad('%s：「%s」が語彙データにありません' % (where, c['word']))
        return
    reads = [w['reading']] + [a.get('reading') for a in (w.get('alt') or [])]
    if c['reading'] not in reads:
        bad('%s：「%s」の読み「%s」が語彙と合いません（語彙は %s）'
            % (where, c['word'], c['reading'], '・'.join(filter(None, reads))))
    if c.get('level') and c['level'] != w['level']:
        bad('%s：「%s」のレベルが合いません（%s／語彙は %s）'
            % (where, c['word'], c['level'], w['level']))
    if c['sur'] not in c['sentence']:
        bad('%s：「%s」の例文に文中の形「%s」がありません'
            % (where, c['word'], c['sur']))
    # 例文は 例文データか alt のどちらかと 同じはず（自他の表だけ）
    if not same_sent:
        return
    s = S.get(c['word'])
    ok = []
    if s is not None:
        ok.append(s[0] if isinstance(s, list) else s)
    ok += [a.get('sentence') for a in (w.get('alt') or [])]
    if c['sentence'] not in ok:
        bad('%s：「%s」の例文がもとのデータと ちがいます\n        表 : %s\n        もと: %s'
            % (where, c['word'], c['sentence'], '／'.join(filter(None, ok)) or '（無し）'))


# ── 自動詞・他動詞 ──────────────────────────────────
J = json.load(io.open(R + 'jita.json', encoding='utf-8'))
print('■ 自動詞・他動詞 %d組' % len(J['pairs']))
if J.get('app_version') != VER:
    bad('jita.json の app_version %s が version.json %s と ちがいます'
        % (J.get('app_version'), VER))
if J.get('count') != len(J['pairs']):
    bad('jita.json の count %s と 実際 %d が合いません' % (J.get('count'), len(J['pairs'])))
seen, SEENJ = set(), {}
for pr in J['pairs']:
    vi, vt = pr['vi'], pr['vt']
    w = '自他 %s／%s' % (vi['word'], vt['word'])
    if vi['word'] == vt['word']:
        bad('%s：自動詞と他動詞が同じ語です' % w)
    key = (vi['word'], vt['word'])
    if key in seen:
        bad('%s：同じ対が二度出ています' % w)
    seen.add(key)
    if vi.get('kind') != '自動詞' or vt.get('kind') != '他動詞':
        bad('%s：kind が 自動詞／他動詞 になっていません' % w)
    cell(vi, w, same_sent=False)
    cell(vt, w, same_sent=False)
    # **同じ例文を 二度出さない。**同じ語が ふたつの対に出ると
    # （起こす は 起きる／起こす と 起こる／起こす）、語の例文を使うと
    # 同じ文が二度ならび、片方は 意味が合わない（2026-11-01）
    for c in (vi, vt):
        if c['sentence'] in SEENJ:
            bad('自他：同じ例文が二度出ています（%s と %s）\n        %s'
                % (SEENJ[c['sentence']], c['word'], c['sentence']))
        SEENJ[c['sentence']] = c['word']

# ── 敬語 ────────────────────────────────────────
K = json.load(io.open(R + 'keigo.json', encoding='utf-8'))
print('■ 敬語 %d行' % len(K['rows']))
if K.get('app_version') != VER:
    bad('keigo.json の app_version %s が version.json %s と ちがいます'
        % (K.get('app_version'), VER))
if K.get('count') != len(K['rows']):
    bad('keigo.json の count %s と 実際 %d が合いません' % (K.get('count'), len(K['rows'])))
if not K.get('ng_ja'):
    bad('keigo.json に まちがえやすい例（ng_ja）がありません')
SEEN = {}
for r in K['rows']:
    w = '敬語 ' + (r['plain']['word'] if r['plain'] else '?')
    if not r['plain']:
        bad('%s：ふつうの言い方がありません' % w)
    if not r['sonkei'] and not r['kenjou']:
        bad('%s：尊敬語も謙譲語もありません' % w)
    if r['sonkei'] and r['kenjou'] and r['sonkei']['word'] == r['kenjou']['word']:
        bad('%s：尊敬語と謙譲語が同じ語です' % w)
    for c in (r['plain'], r['sonkei'], r['kenjou']):
        cell(c, w, same_sent=False)
    if not str(r.get('scene') or '').strip():
        bad('%s：場面のひとことがありません' % w)
    for c in (r['plain'], r['sonkei'], r['kenjou']):
        if not c:
            continue
        # **同じ例文を 二度出さない。**「いらっしゃる」は 行く・来る・いる の
        # 3行に出るので、語の例文を使うと 同じ文が3回ならび、しかも
        # その行の場面に 合わない（持ち主が見つけた・2026-11-01）。
        if c['sentence'] in SEEN:
            bad('敬語：同じ例文が二度出ています（%s と %s）\n        %s'
                % (SEEN[c['sentence']], r['scene'], c['sentence']))
        SEEN[c['sentence']] = r['scene']

# ── 画面につながっているか ──────────────────────────
HTML = io.open(R + 'kanji.html', encoding='utf-8').read()
for need, what in (('data-tab="jita"', '自動詞・他動詞のタブ'),
                   ('data-tab="keigo"', '敬語のタブ'),
                   ("id=\"p-jita\"", '自動詞・他動詞の画面'),
                   ("id=\"p-keigo\"", '敬語の画面'),
                   ("'jita'", 'タブ一覧の jita'),
                   ("'keigo'", 'タブ一覧の keigo'),
                   ("fetch('jita.json'", 'jita.json の読み込み'),
                   ("fetch('keigo.json'", 'keigo.json の読み込み')):
    if need not in HTML:
        bad('kanji.html に %s がありません（%s）' % (what, need))

# ── 入口メニューから たどれるか ───────────────────────
# タブを足しただけでは、**入口の一覧に出ない**。
# 持ち主から「どこに出来てますか？」と聞かれて 気づいた（2026-10-31）。
TOP = io.open(R + 'index.html', encoding='utf-8').read()
for need, what in (('kanji.html#jita', '自動詞・他動詞'), ('kanji.html#keigo', '敬語')):
    if need not in TOP:
        bad('index.html（入口メニュー）に %s への入口がありません（%s）' % (what, need))

print()
print('=' * 54)
print('おかしいところ: %d件' % len(ng))
for x in ng[:12]:
    print('  -', x)
print('=' * 54)
sys.exit(1 if ng else 0)
