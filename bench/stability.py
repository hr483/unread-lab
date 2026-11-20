"""Stability-profile test (plans/L-03-003.yaml)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from ccm import SEED, NPERM

def per_concept(test, refs, concepts):
    """Return concepts used, m_c (observed matches per concept) and E_c (permutation mean)."""
    slots = [c for c in concepts if c in test]
    vocab = {}
    enc = lambda x: vocab.setdefault(x, len(vocab))
    t = np.array([enc(test[c]) for c in slots])
    R = np.array([[enc(r[c]) if c in r else -1 for c in slots] for r in refs])
    m = ((R == t[None, :]) & (R >= 0)).sum(axis=0)
    rng = np.random.default_rng(SEED)
    perms = np.argsort(rng.random((NPERM, len(slots))), axis=1)
    tp = t[perms]
    E = np.zeros(len(slots))
    for row in R:
        E += ((tp == row[None, :]) & (row[None, :] >= 0)).mean(axis=0)
    return slots, m.astype(float), E

def index(slots, e, stable):
    s = np.array([c in stable for c in slots])
    return float(e[s].mean() - e[~s].mean()), int(s.sum()), int((~s).sum())

def pooled(members, stable, B=2000, seed=20261120):
    """members: list of (slots, e). Bootstrap concepts within tier, same resample for all members."""
    allc = sorted(set().union(*[set(sl) for sl, _ in members]))
    S = [c for c in allc if c in stable]; O = [c for c in allc if c not in stable]
    maps = [dict(zip(sl, e)) for sl, e in members]
    def I_for(sc, oc):
        vals = []
        for mp in maps:
            es = [mp[c] for c in sc if c in mp]; eo = [mp[c] for c in oc if c in mp]
            if es and eo:
                vals.append(np.mean(es) - np.mean(eo))
        return float(np.mean(vals))
    point = I_for(S, O)
    rng = np.random.default_rng(seed)
    boots = [I_for(list(rng.choice(S, len(S))), list(rng.choice(O, len(O)))) for _ in range(B)]
    lo, hi = np.percentile(boots, [5, 95])
    return dict(I=point, ci90=[float(lo), float(hi)], n_stable=len(S), n_other=len(O))
