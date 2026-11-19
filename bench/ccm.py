"""Consonant-class matching bench (Turchin, Peiros & Gell-Mann 2010).

Implements the method exactly as written in plans/CAL-001_L-03-001_L-08-001.yaml.
"""
import csv, logging, os
import numpy as np

logging.disable(logging.CRITICAL)
from lingpy import tokens2class  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONS = set("PTSKMNRWJH")
SEED = 20261119
NPERM = 10_000


def code(segments: str):
    """First two Dolgopolsky consonant classes; initial vowel counts as H."""
    toks = [t for t in segments.split() if t not in {"+", "_", "◦", "#", "·"}]
    if not toks:
        return None
    try:
        cls = tokens2class(toks, "dolgo")
    except Exception:
        return None
    out = []
    for i, c in enumerate(cls):
        if i == 0 and c == "V":
            out.append("H")
        elif c in CONS:
            out.append(c)
        if len(out) == 2:
            break
    if not out:
        return None
    if len(out) == 1:
        out.append("-")
    return tuple(out)


def load(dataset: str):
    """Return {language: {concepticon_id: code}} using first non-loan form per concept."""
    d = os.path.join(ROOT, "data", dataset, "cldf")
    p2c = {p["ID"]: p["Concepticon_ID"] for p in csv.DictReader(open(os.path.join(d, "parameters.csv")))}
    out = {}
    for f in csv.DictReader(open(os.path.join(d, "forms.csv"))):
        if str(f.get("Loan", "")).strip().lower() in {"true", "1", "yes"}:
            continue
        cid = p2c.get(f["Parameter_ID"])
        if not cid:
            continue
        lang = out.setdefault(f["Language_ID"], {})
        if cid in lang:  # first listed form only
            continue
        c = code(f.get("Segments") or "")
        if c is not None:
            lang[cid] = c
    return out


def _perm_matrix(n, rng):
    return np.argsort(rng.random((NPERM, n)), axis=1)


def group_test(test: dict, refs: list, concepts: list, rng=None):
    """Sum of matches between `test` and every ref, over `concepts`.

    Null: permute test's codes across the concepts where test has a word.
    Returns observed, null mean, p, number of concepts used.
    """
    rng = rng or np.random.default_rng(SEED)
    slots = [c for c in concepts if c in test]
    n = len(slots)
    if n < 10:
        return dict(obs=None, null_mean=None, p=None, n=n)
    # integer-encode codes
    vocab = {}
    enc = lambda x: vocab.setdefault(x, len(vocab))
    t = np.array([enc(test[c]) for c in slots])
    R = np.array([[enc(r[c]) if c in r else -1 for c in slots] for r in refs])  # refs x n
    obs = int(((R == t[None, :]) & (R >= 0)).sum())
    perms = _perm_matrix(n, rng)
    tp = t[perms]  # NPERM x n
    null = np.zeros(NPERM, dtype=int)
    for row in R:
        null += ((tp == row[None, :]) & (row[None, :] >= 0)).sum(axis=1)
    p = (int((null >= obs).sum()) + 1) / (NPERM + 1)
    return dict(obs=obs, null_mean=float(null.mean()), p=p, n=n)


def holm(pvals):
    """Holm-Bonferroni adjusted p-values, same order as input."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj
