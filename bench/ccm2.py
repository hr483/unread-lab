"""CCM bench v2: identical to bench/ccm.py except the prefix rule adopted from the
red team (redteam/ccm.py strip_prefix), copied verbatim in behaviour:
drop a leading morpheme with <=1 consonant and <=3 tokens when a '+' follows it
and the remainder contains a consonant. Applied to every dataset."""
import csv, logging, os
import numpy as np
logging.disable(logging.CRITICAL)
from lingpy import tokens2class  # noqa: E402
from ccm import group_test, holm, SEED, NPERM, ROOT  # noqa: F401,E402

CONS = set("PTSKMNRWJH")

def _cls(t):
    try:
        return tokens2class([t], "dolgo")[0]
    except Exception:
        return "0"

def strip_prefix(toks):
    if "+" not in toks:
        return toks
    i = toks.index("+")
    first, rest = toks[:i], toks[i + 1:]
    n_cons = sum(_cls(t) in CONS for t in first)
    if n_cons <= 1 and len(first) <= 3 and any(_cls(t) in CONS or _cls(t) == "V" for t in rest if t != "+"):
        if any(_cls(t) in CONS for t in rest):
            return rest
    return toks

def code(segments, prefix=True):
    toks = [t for t in segments.split() if t not in {"_", "◦", "#", "·"}]
    if prefix:
        toks = strip_prefix(toks)
    toks = [t for t in toks if t != "+"]
    if not toks:
        return None
    out = []
    for i, t in enumerate(toks):
        c = _cls(t)
        if not out and i == 0 and c == "V":
            out.append("H")
        elif c in CONS:
            out.append(c)
        if len(out) == 2:
            break
    if not out:
        return None
    return (out[0], out[1] if len(out) > 1 else "-")

def load(dataset, prefix=True):
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
        if cid in lang:
            continue
        c = code(f.get("Segments") or "", prefix)
        if c is not None:
            lang[cid] = c
    return out
