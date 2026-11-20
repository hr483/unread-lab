import csv, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from ccm2 import load, ROOT
from ccm import group_test, SEED
from stability import per_concept, index, pooled
import numpy as np
def P(d): return {p["ID"]: p["Concepticon_ID"] for p in csv.DictReader(open(os.path.join(ROOT, f"data/{d}/cldf/parameters.csv")))}
STABLE = {r["CONCEPTICON_ID"] for r in csv.DictReader(open(os.path.join(ROOT, "data/conceptlists/Holman-2008-40.tsv")), delimiter="\t")}
st, ne, bodt, kb = load("sagartst"), load("northeuralex"), load("bodtkhobwa"), load("khobwa")
sub = {l["ID"]: l["SubGroup"] for l in csv.DictReader(open(os.path.join(ROOT, "data/sagartst/cldf/languages.csv")))}
D = "OldChinese OldBurmese Lisu Japhug Tangut Zhaba Limbu Bahing Hayu Hakha Lushai Ukhrul".split()
C182 = sorted(set(P("sagartst").values()) & set(P("bodtkhobwa").values()))
C198 = sorted(set(P("sagartst").values()) & set(P("northeuralex").values()))
C76 = sorted(set(P("sagartst").values()) & set(P("khobwa").values()))
def run(lang_data, refs, C):
    sl, m, E = per_concept(lang_data, refs, C)
    I, ns, no = index(sl, m - E, STABLE)
    return (sl, m - E), dict(I=I, n_stable=ns, n_other=no, obs=float(m.sum()), null=float(E.sum()))
out = {}
# inheritance side
POS = "Beijing Rangoon Bantawa Bunan Chepang Daofu Garo Rabha Jingpho Dulong Mikir Batang Yidu".split()
mem, rows = [], []
for x in POS:
    me, r = run(st[x], [st[d] for d in D if sub[d] != sub[x]], C182); mem.append(me); rows.append(dict(lang=x, **r))
pi = pooled(mem, STABLE)
inh_pass = pi["ci90"][0] > 0 and sum(r["I"] > 0 for r in rows) >= 9
# borrowing side
SIN = "Beijing Chaozhou Guangzhou Jieyang Longgang OldChinese Xingning".split()
brows = []
for x in ["jpn", "kor"]:
    g = group_test(ne[x], [st[s] for s in SIN], C198, np.random.default_rng(SEED))
    _, r = run(ne[x], [st[s] for s in SIN], C198)
    brows.append(dict(lang=x, overall_p=g["p"], overall_obs=g["obs"], overall_null=g["null_mean"], **r))
signal = all(r["overall_p"] < 0.01 for r in brows)
bor_status = ("PASS" if all(r["I"] < 0 for r in brows) else "FAIL") if signal else "UNTESTED"
out["CAL_006"] = dict(inheritance_side=dict(rows=rows, pooled=pi, PASS=bool(inh_pass)),
                      borrowing_side=dict(rows=brows, status=bor_status))
# main
mem, rows = [], []
for x in "Duhumbi Jerigaon Khispi Khoina Khoitam Rahung Rupa Shergaon".split():
    me, r = run(bodt[x], [st[d] for d in D], C182); mem.append(me); rows.append(dict(lang=x, **r))
pk = pooled(mem, STABLE)
verdict = "inheritance_like" if pk["ci90"][0] > 0 else ("borrowing_like" if pk["ci90"][1] < 0 else "indeterminate")
mem2, rows2 = [], []
for x in ["Eastern_Puroik_Li", "Eastern_Puroik_Sun", "Rawa"]:
    me, r = run(kb[x], [st[d] for d in D], C76); mem2.append(me); rows2.append(dict(lang=x, **r))
out["L_03_003"] = dict(rows=rows, pooled=pk, verdict=verdict,
                       puroik_secondary=dict(rows=rows2, pooled=pooled(mem2, STABLE)))
json.dump(out, open(os.path.join(ROOT, "runs/run-004.json"), "w"), indent=1, default=str)
print("written runs/run-004.json")
