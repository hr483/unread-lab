"""Red-team independent re-implementation of CAL-001 and L-03-001 (CCM test).
Written from plans/CAL-001_L-03-001_L-08-001.yaml only.
"""
import csv, logging, json, sys
import numpy as np
logging.disable(logging.CRITICAL)
from lingpy import tokens2class

D = '/home/claude/unread-lab/data/'
SEED = 20261119
NPERM = 10000

DISTANT = ['OldChinese', 'OldBurmese', 'Lisu', 'Japhug', 'Tangut', 'Zhaba', 'Limbu',
           'Bahing', 'Hayu', 'Hakha', 'Lushai', 'Ukhrul']
CONTACT = ['OldTibetan', 'Lhasa', 'MotuoMenba', 'Bokar']
POS = ['Beijing', 'Rangoon', 'Bantawa', 'Bunan', 'Chepang', 'Daofu', 'Garo', 'Rabha',
       'Jingpho', 'Dulong', 'Mikir', 'Batang', 'Yidu']
NEG = ['fin', 'hun', 'ekk', 'tam', 'tel', 'kan', 'mal', 'eus', 'kat', 'arb', 'heb', 'tur', 'lit', 'gle']

NONCONS = {'V', '1', '+', '_', '0', '-'}
_cache = {}


def tclass(tok):
    if tok not in _cache:
        try:
            _cache[tok] = tokens2class([tok], 'dolgo')[0]
        except Exception:
            _cache[tok] = '0'
    return _cache[tok]


def strip_prefix(toks):
    """Variant: drop a leading morpheme that is V or CV-shaped (<=1 consonant, <=3 segs)
    when a morpheme boundary '+' follows it."""
    if '+' not in toks:
        return toks
    i = toks.index('+')
    first = toks[:i]
    rest = toks[i + 1:]
    cons = [t for t in first if tclass(t) not in NONCONS]
    if len(cons) <= 1 and len(first) <= 3 and any(tclass(t) not in NONCONS | {'+'} for t in rest):
        return rest
    return toks


def code(toks, initial_vowel_H=True, prefix_strip=False):
    toks = [t for t in toks if t]
    if prefix_strip:
        toks = strip_prefix(toks)
    cls = [tclass(t) for t in toks]
    # first segmental (non-boundary, non-tone) token
    seg = [c for c in cls if c not in {'+', '_', '1', '0', '-'}]
    if not seg:
        return None
    cons = []
    if seg[0] == 'V' and initial_vowel_H:
        cons.append('H')
    cons += [c for c in seg if c != 'V']
    if not cons:
        return ('H', '-') if not initial_vowel_H else None
    return (cons[0], cons[1] if len(cons) > 1 else '-')


def load(ds):
    par = {r['ID']: r['Concepticon_ID'] for r in csv.DictReader(open(D + ds + '/cldf/parameters.csv'))}
    out = {}
    for r in csv.DictReader(open(D + ds + '/cldf/forms.csv')):
        if r['Loan'].strip().lower() == 'true':
            continue
        cid = par[r['Parameter_ID']]
        if not cid:
            continue
        out.setdefault(r['Language_ID'], {}).setdefault(cid, []).append(r['Segments'].split())
    return out


def build_codes(data, concepts, mode='first', **kw):
    """mode first: code of the first listed form (tuple). mode any: frozenset of codes of all forms."""
    res = {}
    for lang, d in data.items():
        res[lang] = {}
        for c in concepts:
            if c not in d:
                continue
            cs = [code(t, **kw) for t in d[c]]
            cs = [x for x in cs if x is not None]
            if not cs:
                continue
            res[lang][c] = cs[0] if mode == 'first' else frozenset(cs)
    return res


def ccm_test(test, refs, concepts, mode='first', nperm=NPERM, seed=SEED, return_null=False):
    """test: dict cid->code; refs: list of dict cid->code. Group sum with one shared permutation."""
    K = [c for c in concepts if c in test]
    n = len(K)
    if n == 0:
        return dict(obs=0, p=1.0, n=0)
    if mode == 'first':
        vocab = {}
        enc = lambda x: vocab.setdefault(x, len(vocab))
        T = np.array([enc(test[c]) for c in K])
        R = np.array([[enc(r[c]) if c in r else -1 for c in K] for r in refs])
        obs = int((R == T[None, :]).sum())
        rng = np.random.default_rng(seed)
        null = np.empty(nperm, dtype=int)
        B = 1000
        for s in range(0, nperm, B):
            m = min(B, nperm - s)
            perms = np.argsort(rng.random((m, n)), axis=1)
            P = T[perms]  # m x n
            null[s:s + m] = (R[None, :, :] == P[:, None, :]).sum(axis=(1, 2))
    else:
        # any-form: match matrix M[i,j] = number of refs where test word i shares a code with ref at slot j
        M = np.zeros((n, n), dtype=int)
        for r in refs:
            for j, cj in enumerate(K):
                if cj not in r:
                    continue
                for i, ci in enumerate(K):
                    if test[ci] & r[cj]:
                        M[i, j] += 1
        obs = int(np.trace(M))
        rng = np.random.default_rng(seed)
        null = np.empty(nperm, dtype=int)
        cols = np.arange(n)
        for s in range(0, nperm, 1000):
            m = min(1000, nperm - s)
            perms = np.argsort(rng.random((m, n)), axis=1)
            null[s:s + m] = M[perms, cols[None, :]].sum(axis=1)
    p = (int((null >= obs).sum()) + 1) / (nperm + 1)
    out = dict(obs=obs, p=p, n=n, null_mean=float(null.mean()))
    if return_null:
        out['null'] = null
    return out


def holm(ps):
    ps = np.asarray(ps, float)
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    run = 0.0
    for k, i in enumerate(order):
        run = max(run, (m - k) * ps[i])
        adj[i] = min(1.0, run)
    return adj
