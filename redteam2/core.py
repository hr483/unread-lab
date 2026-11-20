"""Independent CCM re-implementation for L-03-002 red team (redteam2).
Written from plan text only."""
import csv, logging, os
logging.disable(logging.CRITICAL)
import lingpy
import numpy as np

DATA = '/home/claude/unread-lab/data'
SEED = 20261119
NPERM = 10000
NONCONS = {'V', '1', '0', '+', '_', '#', '-'}
_cache = {}


def norm_tokens(seg):
    out = []
    for t in seg.split():
        if '/' in t:
            t = t.split('/')[-1]
        if t:
            out.append(t)
    return out


def classes(tokens):
    if not tokens:
        return []
    key = tuple(tokens)
    if key not in _cache:
        try:
            _cache[key] = lingpy.tokens2class(list(tokens), 'dolgo')
        except Exception:
            _cache[key] = ['0'] * len(tokens)
    return _cache[key]


def split_morphs(tokens, boundaries=('+', '_')):
    ms, cur = [], []
    for t in tokens:
        if t in boundaries:
            if cur:
                ms.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        ms.append(cur)
    return ms


def ncons(tokens):
    return sum(1 for c in classes(tokens) if c not in NONCONS)


def is_tone(t):
    return classes([t])[0] in ('1', '0')


def strip_prefix(tokens, variant='plan', count_tones=True, iterate=False):
    """variant: 'none' | 'plan' | 'strict'.
    plan: drop first morpheme with <=1 consonant and <=3 tokens when '+' follows and
    remainder has a consonant.
    strict: same, but only if first morpheme is a bare vowel (0 consonants) or matches
    a known prefix inventory a-, ə-, ka-/kə-, ma-/mə-, aŋ-, ha-."""
    if variant == 'none':
        return tokens
    while True:
        ms = split_morphs(tokens)
        if len(ms) < 2:
            return tokens
        m0 = ms[0]
        rest = [t for m in ms[1:] for t in m + ['+']][:-1]
        ntok = len(m0) if count_tones else sum(1 for t in m0 if not is_tone(t))
        ok = ncons(m0) <= 1 and ntok <= 3 and ncons(rest) >= 1
        if ok and variant == 'strict':
            seg = [t for t in m0 if not is_tone(t)]
            cl = classes(seg)
            bare_vowel = all(c == 'V' for c in cl)
            s = ''.join(seg)
            known = s in ('a', 'ə', 'ka', 'kə', 'ma', 'mə', 'aŋ', 'ha', 'ɑ', 'kɑ', 'mɑ', 'ɑŋ', 'hɑ')
            ok = bare_vowel or known
        if not ok:
            return tokens
        tokens = rest
        if not iterate:
            return tokens


def code(seg, variant='plan', **kw):
    toks = norm_tokens(seg)
    toks = strip_prefix(toks, variant, **kw)
    flat = [t for t in toks if t not in ('+', '_', '#')]
    cl = classes(flat)
    cl = [c for c in cl if c not in ('1', '0')]  # drop tones / unknowns
    if not cl:
        return None
    cons = []
    if cl[0] == 'V':
        cons.append('H')
    cons += [c for c in cl if c not in NONCONS]
    if not cons:
        return None
    if len(cons) == 1:
        return (cons[0], '-')
    return (cons[0], cons[1])


def load(ds, langs=None, loan_ok=False):
    """returns {lang: {cid: (segments, form)}} first non-loan form in file order"""
    pmap = {r['ID']: r['Concepticon_ID'] for r in csv.DictReader(open(f'{DATA}/{ds}/cldf/parameters.csv'))}
    out = {}
    for r in csv.DictReader(open(f'{DATA}/{ds}/cldf/forms.csv')):
        L = r['Language_ID']
        if langs is not None and L not in langs:
            continue
        cid = pmap.get(r['Parameter_ID'])
        if not cid:
            continue
        if not loan_ok and r.get('Loan', '').strip().lower() == 'true':
            continue
        if not r['Segments'].strip():
            continue
        d = out.setdefault(L, {})
        if cid not in d:
            d[cid] = (r['Segments'], r['Form'])
    return out


def coded(data, variant='plan', **kw):
    return {L: {c: code(s, variant, **kw) for c, (s, f) in d.items()} for L, d in data.items()}


def ccm(test, refs, concepts, nperm=NPERM, seed=SEED):
    """test: {cid: code}; refs: list of {cid: code}. Group statistic with one shared permutation."""
    C = [c for c in concepts if test.get(c) is not None]
    n = len(C)
    if n < 2:
        return dict(n=n, obs=0, null_mean=float('nan'), p=1.0, ratio=float('nan'))
    vocab = {}
    def enc(x):
        if x is None:
            return -1
        return vocab.setdefault(x, len(vocab))
    T = np.array([enc(test[c]) for c in C])
    R = np.array([[enc(r.get(c)) if r.get(c) is not None else -2 for c in C] for r in refs])
    obs = int((T[None, :] == R).sum())
    rng = np.random.default_rng(seed)
    perms = np.argsort(rng.random((nperm, n)), axis=1)
    Tp = T[perms]
    null = np.zeros(nperm, dtype=int)
    for row in R:
        null += (Tp == row[None, :]).sum(1)
    p = (int((null >= obs).sum()) + 1) / (nperm + 1)
    nm = float(null.mean())
    return dict(n=n, obs=obs, null_mean=nm, p=p, ratio=obs / nm if nm > 0 else float('inf'),
                npairs=int((R >= 0).sum()))


def holm(ps):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0] * m
    run = 0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (m - k) * ps[i]))
        adj[i] = run
    return adj


def tadmor():
    rows = list(csv.DictReader(open(f'{DATA}/conceptlists/Tadmor-2009-100.tsv'), delimiter='\t'))
    return {r['CONCEPTICON_ID']: r for r in rows}


def cids(ds):
    return {r['Concepticon_ID'] for r in csv.DictReader(open(f'{DATA}/{ds}/cldf/parameters.csv')) if r['Concepticon_ID']}
