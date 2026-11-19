import csv, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from ccm import load, group_test, holm, SEED, ROOT
ne = load("northeuralex")
LJ = {r["CONCEPTICON_ID"] for r in csv.DictReader(open(os.path.join(ROOT, "data/conceptlists/Tadmor-2009-100.tsv")), delimiter="\t")}
def pair(a, b):
    c = sorted(set(ne[a]) & set(ne[b]) & LJ)
    return dict(pair=f"{a}-{b}", **group_test(ne[a], [ne[b]], c, np.random.default_rng(SEED)))
P = [pair(*x.split("-")) for x in "fin-hun fin-mns eng-hin lit-pes tur-sah tam-tel".split()]
N = [pair(*x.split("-")) for x in "eus-fin eus-tam kat-fin kat-tam heb-fin eus-hun kat-hun heb-tam eus-kat fin-tam heb-kat hun-tam".split()]
cal = sum(r["p"] >= 0.01 for r in P) <= 1 and sum(r["p"] < 0.01 for r in N) <= 1
a = pair("bsk", "ket")
b = [pair("bsk", x) for x in "ell lat lit isl gle rus hye sqi".split()]
for r, h in zip(b, holm([r["p"] for r in b])): r["p_holm"] = h
ctrl = [pair("bsk", x) for x in "hin pes pbu".split()]
out = dict(CAL_003=dict(positives=P, negatives=N, PASS=bool(cal)), a=a, a_PASS=a["p"] < 0.01, b=b,
           b_majority_PASS=sum(r["p_holm"] < 0.01 for r in b) > 4, contact_control=ctrl, interpretable=bool(cal))
json.dump(out, open(os.path.join(ROOT, "runs/run-002.json"), "w"), indent=1, default=str)
print("written runs/run-002.json")
