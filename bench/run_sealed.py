"""Runs CAL-001, L-03-001, CAL-002 and L-08-001 exactly as sealed. Writes runs/*.json."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from ccm import load, group_test, holm, SEED, ROOT  # noqa: E402

DISTANT = ["OldChinese", "OldBurmese", "Lisu", "Japhug", "Tangut", "Zhaba", "Limbu", "Bahing", "Hayu", "Hakha", "Lushai", "Ukhrul"]
CONTACT = ["OldTibetan", "Lhasa", "MotuoMenba", "Bokar"]
POS = ["Beijing", "Rangoon", "Bantawa", "Bunan", "Chepang", "Daofu", "Garo", "Rabha", "Jingpho", "Dulong", "Mikir", "Batang", "Yidu"]
NEG = ["fin", "hun", "ekk", "tam", "tel", "kan", "mal", "eus", "kat", "arb", "heb", "tur", "lit", "gle"]

kb, st, ne = load("khobwa"), load("sagartst"), load("northeuralex")
import csv
sub = {l["ID"]: l["SubGroup"] for l in csv.DictReader(open(os.path.join(ROOT, "data/sagartst/cldf/languages.csv")))}
kb_c = set().union(*[set(v) for v in kb.values()])
st_c = set().union(*[set(v) for v in st.values()])
CONCEPTS = sorted(kb_c & st_c)
out = {"concepts_used": len(CONCEPTS)}

def rng():
    return np.random.default_rng(SEED)

# ---------------- CAL-001
cal = []
for x in POS:
    refs = [st[r] for r in DISTANT if sub[r] != sub[x]]
    cal.append(dict(lang=x, kind="positive", n_refs=len(refs), **group_test(st[x], refs, CONCEPTS, rng())))
for x in NEG:
    cal.append(dict(lang=x, kind="negative", n_refs=len(DISTANT), **group_test(ne[x], [st[r] for r in DISTANT], CONCEPTS, rng())))
pos = [r for r in cal if r["kind"] == "positive"]
for r, a in zip(pos, holm([r["p"] for r in pos])):
    r["p_holm"] = a
pos_rate = sum(r["p_holm"] < 0.01 for r in pos) / len(pos)
neg_fp = sum(r["p"] < 0.01 for r in cal if r["kind"] == "negative")
out["CAL-001"] = dict(rows=cal, positive_detection_rate=pos_rate, negative_false_positives=neg_fp,
                      PASS=bool(pos_rate >= 0.70 and neg_fp <= 1))

# ---------------- L-03-001
def run_l03(purge):
    rows = []
    for lang in sorted(kb):
        concepts = CONCEPTS
        dropped = 0
        if purge:
            keep = []
            for c in CONCEPTS:
                if c in kb[lang] and any(c in st[k] and st[k][c] == kb[lang][c] for k in CONTACT):
                    dropped += 1
                    continue
                keep.append(c)
            concepts = keep
        rows.append(dict(lang=lang, dropped_for_contact=dropped, **group_test(kb[lang], [st[r] for r in DISTANT], concepts, rng())))
    for r, a in zip(rows, holm([r["p"] for r in rows])):
        r["p_holm"] = a
        r["signal"] = a < 0.01
    return rows

out["L-03-001"] = dict(primary=run_l03(False), purged=run_l03(True),
                       interpretable=out["CAL-001"]["PASS"])

# ---------------- CAL-002 + L-08-001 (NorthEuraLex, all shared concepts per pair)
def pair(a, b):
    concepts = sorted(set(ne[a]) & set(ne[b]))
    return dict(pair=f"{a}-{b}", **group_test(ne[a], [ne[b]], concepts, rng()))

C2P = [("fin", "hun"), ("fin", "mns"), ("eng", "hin"), ("lit", "pes"), ("tur", "sah"), ("tam", "tel")]
C2N = [("eus", "fin"), ("eus", "tam"), ("kat", "fin"), ("kat", "tam"), ("heb", "fin"), ("eus", "hun"), ("kat", "hun"), ("heb", "tam")]
c2p = [pair(*x) for x in C2P]; c2n = [pair(*x) for x in C2N]
cal2_pass = sum(r["p"] >= 0.01 for r in c2p) <= 1 and sum(r["p"] < 0.01 for r in c2n) <= 1
out["CAL-002"] = dict(positives=c2p, negatives=c2n, PASS=bool(cal2_pass))

a = pair("bsk", "ket")
b = [pair("bsk", x) for x in ["ell", "lat", "lit", "isl", "gle", "rus", "hye", "sqi"]]
for r, adj in zip(b, holm([r["p"] for r in b])):
    r["p_holm"] = adj
ctrl = [pair("bsk", x) for x in ["hin", "pes", "pbu"]]
out["L-08-001"] = dict(a_bsk_ket=a, a_PASS=a["p"] < 0.01,
                       b_bsk_IE=b, b_majority_PASS=sum(r["p_holm"] < 0.01 for r in b) > len(b) / 2,
                       contact_control=ctrl, interpretable=out["CAL-002"]["PASS"])

os.makedirs(os.path.join(ROOT, "runs"), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, "runs/run-001.json"), "w"), indent=1, default=str)
print("written runs/run-001.json")
