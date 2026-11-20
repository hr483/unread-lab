import csv, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from ccm2 import load, group_test, holm, SEED, ROOT
rng = lambda: np.random.default_rng(SEED)
LJ = {r["CONCEPTICON_ID"] for r in csv.DictReader(open(os.path.join(ROOT, "data/conceptlists/Tadmor-2009-100.tsv")), delimiter="\t")}
def P(d): return {p["ID"]: p["Concepticon_ID"] for p in csv.DictReader(open(os.path.join(ROOT, f"data/{d}/cldf/parameters.csv")))}
sun, st, ne, bodt = load("suntb"), load("sagartst"), load("northeuralex"), load("bodtkhobwa")
NEG = "fin hun ekk tam tel kan mal eus kat arb heb tur lit gle".split()
def cal(pos_rows, neg_rows):
    for r, h in zip(pos_rows, holm([r["p"] for r in pos_rows])): r["p_holm"] = h
    rate = sum(r["p_holm"] < 0.01 for r in pos_rows) / len(pos_rows)
    fp = sum(r["p"] < 0.01 for r in neg_rows)
    return dict(positives=pos_rows, negatives=neg_rows, detection_rate=rate, false_positives=fp, PASS=bool(rate >= 0.7 and fp <= 1))
out = {}
# ---- TEST A
CA = sorted(set(P("suntb").values()) & LJ)
DS = "Lisu BlackLahu CaiyuanHani XideYi MileYi Jinuo Achang Atsi RangoonBurmese Maru".split()
POSA = "Jingpho Trung Anong MaerkangrGyalrong DanbaErgong Ersu Namuyi Xumi Guiqiong Muya YajiangQueyu MawoQiang QinghuaPumi".split()
refsA = [sun[x] for x in DS]
pa = [dict(lang=x, **group_test(sun[x], refsA, CA, rng())) for x in POSA]
na = [dict(lang=x, **group_test(ne[x], refsA, CA, rng())) for x in NEG]
calA = cal(pa, na)
sec = [dict(lang=x, **group_test(sun[x], refsA, CA, rng())) for x in "Sulong Darang Idu Kaman BokarLhoba".split()]
for r, h in zip(sec, holm([r["p"] for r in sec])): r["p_holm"] = h
s = sec[0]
ratio = lambda r: r["obs"] / r["null_mean"]
rank = sum(ratio(r) < ratio(s) for r in pa)  # positives weaker than Sulong
contact = [dict(lang=x, **group_test(sun["Sulong"], [sun[x]], CA, rng())) for x in "LhasaTibetan MotuoTsangla BokarLhoba".split()]
out["TEST_A"] = dict(concepts=len(CA), CAL_004=calA, sulong=s, sulong_PASS=s["p"] < 0.01, secondary=sec,
                     positives_weaker_than_sulong=rank, sulong_below_all_positives=rank == 0, contact_report=contact,
                     interpretable=calA["PASS"])
# ---- TEST B
KB76 = set(csv.DictReader.__call__ and [])  # placeholder to keep linters quiet
used76 = set(P("lieberherrkhobwa").values()) & set(P("sagartst").values())
CB = sorted((set(P("bodtkhobwa").values()) & set(P("sagartst").values())) - used76)
sub = {l["ID"]: l["SubGroup"] for l in csv.DictReader(open(os.path.join(ROOT, "data/sagartst/cldf/languages.csv")))}
D = "OldChinese OldBurmese Lisu Japhug Tangut Zhaba Limbu Bahing Hayu Hakha Lushai Ukhrul".split()
POSB = "Beijing Rangoon Bantawa Bunan Chepang Daofu Garo Rabha Jingpho Dulong Mikir Batang Yidu".split()
pb = [dict(lang=x, **group_test(st[x], [st[r] for r in D if sub[r] != sub[x]], CB, rng())) for x in POSB]
nb = [dict(lang=x, **group_test(ne[x], [st[r] for r in D], CB, rng())) for x in NEG]
calB = cal(pb, nb)
mb = [dict(lang=x, **group_test(bodt[x], [st[r] for r in D], CB, rng())) for x in "Duhumbi Jerigaon Khispi Khoina Khoitam Rahung Rupa Shergaon".split()]
for r, h in zip(mb, holm([r["p"] for r in mb])): r["p_holm"] = h; r["signal"] = h < 0.01
out["TEST_B"] = dict(concepts=len(CB), CAL_005=calB, main=mb, n_signal=sum(r["signal"] for r in mb),
                     at_least_5_of_8=sum(r["signal"] for r in mb) >= 5, interpretable=calB["PASS"])
json.dump(out, open(os.path.join(ROOT, "runs/run-003.json"), "w"), indent=1, default=str)
print("written runs/run-003.json")
