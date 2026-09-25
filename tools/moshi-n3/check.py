# -*- coding: utf-8 -*-
"""N3模試を 点検する。 python3 tools/moshi-n3/check.py

見るところ
  ① 大問の数・問数が 本番の形と 合っているか
  ② 選択肢の数（4択／聴解の発話表現・即時応答は 3択）
  ③ 正解の番号が 範囲内か・かたよって いないか
  ④ 同じ選択肢が 2つ 入って いないか
  ⑤ 解説が 入って いるか
  ⑥ 読解の 本文の 長さ（公式の目安：短文150〜200字・中文350字・長文550字）
  ⑦ 読解の 本文が 読解教材・100日コースと 重なって いないか（一度読んだ文章は 使わない）
  ⑧ 日本語以外の 文字
"""
import json, io, os, re, sys, glob, collections

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
BAD = re.compile(r'[Ѐ-ӿ가-힯ऀ-ॿ฀-๿؀-ۿ]')
WANT = {"文字・語彙": 35, "文法": 23, "読解": 16, "聴解": 28}
LEN = {"読解4": (150, 210), "読解5": (330, 430), "読解6": (520, 640)}

def body(p):
    t = re.sub(r'\s', '', p.get('text', ''))
    return len(t)

def main():
    bad, warn = [], []
    files = sorted(glob.glob(R + 'moshi/n3-*.json'))
    if not files:
        print('N3模試が ありません'); return 1
    # 読んだことのある本文（読解教材・100日コース）
    seen = set()
    for f in glob.glob(R + 'dokkai/reading-*.json'):
        j = json.load(io.open(f, encoding='utf-8'))
        ps = j['passages'] if isinstance(j, dict) and 'passages' in j else j
        for p in ps: seen.add(re.sub(r'\s', '', p.get('text', ''))[:40])
    n3 = io.open(R + 'n3.html', encoding='utf-8').read()
    for m in re.finditer(r'"t": "passage", "v": "(.{0,400}?)"', n3):
        seen.add(re.sub(r'<[^>]+>|\s', '', m.group(1))[:40])

    for f in files:
        j = json.load(io.open(f, encoding='utf-8'))
        name = os.path.basename(f)
        print('■ %s　%s' % (name, j.get('title')))
        pos = collections.Counter(); tot = 0
        for k in j['order']:
            s = j['sections'][k]
            items = s.get('items') or []
            reads = s.get('read') or []
            n = sum(len(r['qi']) for r in reads) if reads else len(items)
            tot += n
            print('   %-6s %-22s %2d問' % (k, s['name'], n))
            # 選択肢と 正解
            qs = [(x.get('choices') or x.get('opts'), x.get('answer', x.get('ans'))) for x in items]
            for r in reads:
                for qi in r['qi']:
                    q = r['passage']['questions'][qi]
                    qs.append((q['choices'], q['answer']))
            for ch, a in qs:
                if ch is None or a is None:
                    bad.append('%s %s：選択肢か 正解が ない' % (name, k)); continue
                want = 3 if k in ('聴解4', '聴解5') else 4
                if len(ch) != want:
                    bad.append('%s %s：選択肢が %d個（%d個であること）' % (name, k, len(ch), want))
                if len(set(ch)) != len(ch):
                    bad.append('%s %s：同じ選択肢が ある' % (name, k))
                if not (0 <= a < len(ch)):
                    bad.append('%s %s：正解の番号が 範囲の外' % (name, k))
                else:
                    pos[a] += 1
            for x in items:
                if not (x.get('explain') or x.get('exp')):
                    bad.append('%s %s：解説が ない' % (name, k))
            # 本文の 長さ・重なり
            for r in reads:
                p = r['passage']
                if not p.get('table'):
                    L = body(p)
                    lo, hi = LEN.get(k, (0, 9999))
                    if not (lo <= L <= hi):
                        warn.append('%s %s「%s」本文 %d字（目安 %d〜%d字）'
                                    % (name, k, p['title'], L, lo, hi))
                head = re.sub(r'\s', '', p.get('text', ''))[:40]
                if head and head in seen:
                    bad.append('%s %s「%s」は すでに 教材に ある 本文' % (name, k, p['title']))
        # 区分ごとの 問数
        got = {'文字・語彙': 0, '文法': 0, '読解': 0, '聴解': 0}
        for k in j['order']:
            s = j['sections'][k]
            n = sum(len(r['qi']) for r in (s.get('read') or [])) or len(s.get('items') or [])
            g = ('文字・語彙' if k.startswith('語彙') else '文法' if k.startswith('文法')
                 else '読解' if k.startswith('読解') else '聴解')
            got[g] += n
        for g, w in WANT.items():
            if got[g] != w:
                bad.append('%s：%s が %d問（本番の形は %d問）' % (name, g, got[g], w))
        t = sum(pos.values())
        print('   合計 %d問　区分 %s' % (tot, got))
        print('   正解の番号 %s（いちばん多い番号は %d%%）'
              % (dict(sorted(pos.items())), round(100 * max(pos.values()) / t)))
        if 100 * max(pos.values()) / t > 35:
            bad.append('%s：正解の番号が かたよって いる（%d%%）'
                       % (name, round(100 * max(pos.values()) / t)))
        if BAD.search(io.open(f, encoding='utf-8').read()):
            bad.append('%s：日本語以外の 文字' % name)
        print()
    if warn:
        print('■ 注意'); [print('  -', w) for w in warn]; print()
    print('=' * 62)
    print('直さないといけない所:', len(bad))
    for b in bad: print('  -', b)
    print('=' * 62)
    print('※ 「正解が2つ成り立つ」は 機械では 見つけられません。必ず 目で 読むこと。')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())
