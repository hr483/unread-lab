import csv, json, sys, collections
import numpy as np
sys.path.insert(0, '/home/claude/unread-lab/redteam')
from ccm import *

OUT = {}
kb = load('khobwa'); st = load('sagartst'); nl = load('northeuralex')
par = lambda ds: {r['ID']: r['Concepticon_ID'] for r in csv.DictReader(open(D + ds + '/cldf/parameters.csv'))}
C76 = sorted((set(par('khobwa').values()) & set(par('sagartst').values())) - {''}, key=int)
assert len(C76) == 76
KB = [r['ID'] for r in csv.DictReader(open(D + 'khobwa/cldf/languages.csv'))]
SUB = {r['ID']: r['SubGroup'] for r in csv.DictReader(open(D + 'sagartst/cldf/languages.csv'))}
# broader clade variant for positive_reference (ambiguity A3)
BROAD = {'Rangoon': {'OldBurmese', 'Lisu'}, 'Daofu': {'Japhug', 'Zhaba', 'Tangut'},
         'Mikir': {'Hakha', 'Lushai', 'Ukhrul'}, 'Chepang': {'Limbu', 'Bahing', 'Hayu'},
         'Yidu': set(), 'Bunan': set(), 'Batang': set()}


def posref(p, broad=False):
    r = [d for d in DISTANT if SUB[d] != SUB[p]]
    if broad:
        r = [d for d in r if d not in BROAD.get(p, set())]
    return r


def run_all(kw, mode='first', broad=False, purge_cal=False, tag=''):
    allc = {}
    allc.update(build_codes(st, C76, mode, **kw))
    allc.update(build_codes(kb, C76, mode, **kw))
    allc.update(build_codes(nl, C76, mode, **kw))
    eq = (lambda a, b: a == b) if mode == 'first' else (lambda a, b: bool(a & b))

    def purged(lang):
        t = allc[lang]
        bad = {c for c in t for k in CONTACT if c in allc[k] and eq(t[c], allc[k][c])}
        return {c: v for c, v in t.items() if c not in bad}, len(bad)

    res = {}
    # CAL-001
    pos = []
    for p in POS:
        t = allc[p]
        nd = 0
        if purge_cal:
            t, nd = purged(p)
        r = ccm_test(t, [allc[d] for d in posref(p, broad)], C76, mode)
        r['dropped'] = nd
        r['nref'] = len(posref(p, broad))
        pos.append((p, r))
    adj = holm([r['p'] for _, r in pos])
    for (p, r), a in zip(pos, adj):
        r['holm'] = float(a)
    neg = []
    for g in NEG:
        t = allc[g]
        nd = 0
        if purge_cal:
            t, nd = purged(g)
        r = ccm_test(t, [allc[d] for d in DISTANT], C76, mode)
        r['dropped'] = nd
        neg.append((g, r))
    rate = sum(r['holm'] < 0.01 for _, r in pos) / len(pos)
    nfp = sum(r['p'] < 0.01 for _, r in neg)
    res['CAL'] = dict(pos=pos, neg=neg, rate=rate, nfp=nfp, passed=(rate >= 0.7 and nfp <= 1))
    # L-03
    for variant in ['primary', 'purged']:
        rows = []
        for l in KB:
            t = allc[l]
            nd = 0
            if variant == 'purged':
                t, nd = purged(l)
            r = ccm_test(t, [allc[d] for d in DISTANT], C76, mode)
            r['dropped'] = nd
            rows.append((l, r))
        adj = holm([r['p'] for _, r in rows])
        for (l, r), a in zip(rows, adj):
            r['holm'] = float(a)
        res[variant] = rows
    return res, allc


def fmt(res, title):
    s = [f'### {title}', '']
    c = res['CAL']
    s.append(f"CAL-001: positives Holm<0.01 = {sum(r['holm']<0.01 for _,r in c['pos'])}/13 ({c['rate']:.0%}); negatives raw p<0.01 = {c['nfp']}/14 -> {'PASS' if c['passed'] else 'FAIL'}")
    s.append('')
    s.append('| positive | n | nref | dropped | obs | null mean | raw p | Holm |')
    s.append('|---|---|---|---|---|---|---|---|')
    for p, r in c['pos']:
        s.append(f"| {p} | {r['n']} | {r['nref']} | {r['dropped']} | {r['obs']} | {r['null_mean']:.1f} | {r['p']:.4f} | {r['holm']:.4f} |")
    s.append('')
    s.append('| negative | n | dropped | obs | null mean | raw p |')
    s.append('|---|---|---|---|---|---|')
    for g, r in c['neg']:
        s.append(f"| {g} | {r['n']} | {r['dropped']} | {r['obs']} | {r['null_mean']:.1f} | {r['p']:.4f} |")
    s.append('')
    s.append('| doculect | n | primary obs/null | primary p | primary Holm | purged dropped | purged n | purged obs/null | purged p | purged Holm |')
    s.append('|---|---|---|---|---|---|---|---|---|---|')
    for (l, a), (_, b) in zip(res['primary'], res['purged']):
        s.append(f"| {l} | {a['n']} | {a['obs']}/{a['null_mean']:.1f} | {a['p']:.4f} | {a['holm']:.4f} | {b['dropped']} | {b['n']} | {b['obs']}/{b['null_mean']:.1f} | {b['p']:.4f} | {b['holm']:.4f} |")
    np_ = sum(r['holm'] < 0.01 for _, r in res['primary'])
    nq = sum(r['holm'] < 0.01 for _, r in res['purged'])
    s.append('')
    s.append(f'L-03-001: primary Holm<0.01 = {np_}/22; purged Holm<0.01 = {nq}/22')
    return '\n'.join(s), np_, nq


if __name__ == '__main__':
    configs = [
        ('MAIN: first form, initial vowel = H, subgroup by Sagart SubGroup', dict(), 'first', False, False),
        ('EXPL-a: identical CONTACT purge applied to CAL-001 positives and negatives', dict(), 'first', False, True),
        ('EXPL-b: any-form matching', dict(), 'any', False, False),
        ('EXPL-b2: any-form matching + purge on CAL', dict(), 'any', False, True),
        ('EXPL-c1: initial vowel NOT coded as H', dict(initial_vowel_H=False), 'first', False, False),
        ('EXPL-c2: strip V/CV prefix before first morpheme boundary (all datasets)', dict(prefix_strip=True), 'first', False, False),
        ('EXPL-c3: prefix strip + no initial H', dict(prefix_strip=True, initial_vowel_H=False), 'first', False, False),
        ('EXPL-c4: broader clade removal for positive_reference', dict(), 'first', True, False),
    ]
    which = sys.argv[1:] and [int(x) for x in sys.argv[1:]] or range(len(configs))
    summ = []
    for i in which:
        t, kw, mode, broad, pc = configs[i]
        res, _ = run_all(kw, mode, broad, pc)
        txt, a, b = fmt(res, t)
        open(f'/home/claude/unread-lab/redteam/out_{i}.md', 'w').write(txt)
        pr = dict(res['primary']); pu = dict(res['purged'])
        line = (f"{i} | {t} | CAL {'PASS' if res['CAL']['passed'] else 'FAIL'} {res['CAL']['rate']:.0%} FP={res['CAL']['nfp']} | "
                f"primary {a}/22 purged {b}/22 | Li p={pr['Eastern_Puroik_Li']['p']:.4f}/{pu['Eastern_Puroik_Li']['p']:.4f} "
                f"Sun p={pr['Eastern_Puroik_Sun']['p']:.4f}/{pu['Eastern_Puroik_Sun']['p']:.4f}")
        print(line, flush=True)
        summ.append(line)
    open('/home/claude/unread-lab/redteam/summary_' + '_'.join(map(str, which)) + '.txt', 'w').write('\n'.join(summ))
