"""EXPLORATORY attacks on TEST_B (and CAL-005)."""
import sys, json, collections
sys.path.insert(0, '/home/claude/unread-lab/redteam2')
from core import *
VARIANT = sys.argv[1] if len(sys.argv) > 1 else 'plan'
NEG = ['fin', 'hun', 'ekk', 'tam', 'tel', 'kan', 'mal', 'eus', 'kat', 'arb', 'heb', 'tur', 'lit', 'gle']
sag = coded(load('sagartst'), VARIANT)
bodraw = load('bodtkhobwa')
bod = coded(bodraw, VARIANT)
nel = coded(load('northeuralex', set(NEG)), VARIANT)
TAD = tadmor()
gl = {r['Concepticon_ID']: r['Concepticon_Gloss'] for r in csv.DictReader(open(f'{DATA}/sagartst/cldf/parameters.csv'))}
DISTANT = ['OldChinese', 'OldBurmese', 'Lisu', 'Japhug', 'Tangut', 'Zhaba', 'Limbu', 'Bahing', 'Hayu', 'Hakha', 'Lushai', 'Ukhrul']
SUBG = {r['ID']: r['SubGroup'] for r in csv.DictReader(open(f'{DATA}/sagartst/cldf/languages.csv'))}
POS_B = ['Beijing', 'Rangoon', 'Bantawa', 'Bunan', 'Chepang', 'Daofu', 'Garo', 'Rabha', 'Jingpho', 'Dulong', 'Mikir', 'Batang', 'Yidu']
KB = ['Duhumbi', 'Jerigaon', 'Khispi', 'Khoina', 'Khoitam', 'Rahung', 'Rupa', 'Shergaon']
OLD76 = cids('khobwa') & cids('sagartst')
CB = sorted((cids('bodtkhobwa') & cids('sagartst')) - OLD76)
CONTACT = ['OldTibetan', 'Lhasa', 'MotuoMenba']

def refs_for(L, dist=DISTANT):
    return [sag[D] for D in dist if L in KB or L in NEG or SUBG.get(D) != SUBG.get(L)]

def langcode(L):
    if L in KB: return bod[L]
    if L in NEG: return nel[L]
    return sag[L]

def summary(title, langs, concepts_fn, dist=DISTANT):
    out = {}
    for L in langs:
        C = concepts_fn(L)
        out[L] = ccm(langcode(L), refs_for(L, dist), C)
    adj = holm([out[L]['p'] for L in langs])
    n01 = sum(1 for a in adj if a < 0.01)
    raw01 = sum(1 for L in langs if out[L]['p'] < 0.01)
    rs = [out[L]['ratio'] for L in langs]
    print(f'{title}: Holm<0.01 {n01}/{len(langs)}, raw<0.01 {raw01}; ratios ' + ' '.join(f'{L[:5]}:{out[L]["ratio"]:.2f}/{out[L]["p"]:.4f}/n{out[L]["n"]}' for L in langs))
    return out

print('VARIANT', VARIANT, 'concepts', len(CB))
summary('BASE KB', KB, lambda L: CB)

# ---- per-concept contribution to Kho-Bwa matches
cnt = collections.Counter()
for L in KB:
    for c in CB:
        k = bod[L].get(c)
        if k is None: continue
        for D in DISTANT:
            if sag[D].get(c) == k: cnt[c] += 1
print('Top concepts by KB-DISTANT matches (summed over 8 doculects):')
for c, v in cnt.most_common(15):
    print(f'   {gl[c]:15s} {v:3d}  KB(Duhumbi)={bodraw.get("Duhumbi",{}).get(c,("",""))[1]} code={bod["Duhumbi"].get(c)}')
tot = sum(cnt.values())
top10 = sum(v for c, v in cnt.most_common(10))
print(f'   total {tot}, top10 concepts carry {top10} ({top10/tot:.0%})')

# ---- (a) contact filter
def contact_filter(L, thr='majority', contact=CONTACT):
    test = langcode(L)
    keep = []
    for c in CB:
        k = test.get(c)
        drop = False
        if k is not None:
            for T in contact:
                if T == L: continue
                t = sag[T].get(c)
                if t is None or t != k: continue
                dvals = [sag[D].get(c) for D in DISTANT if sag[D].get(c) is not None]
                m = sum(1 for d in dvals if d == t)
                if thr == 'majority':
                    widespread = len(dvals) > 0 and m > len(dvals) / 2
                elif thr == 'third':
                    widespread = len(dvals) > 0 and m >= len(dvals) / 3
                elif thr == 'any2':
                    widespread = m >= 2
                elif thr == 'any1':
                    widespread = m >= 1
                if not widespread:
                    drop = True
        if not drop:
            keep.append(c)
    return keep

for thr in ['majority', 'third', 'any2', 'any1']:
    print(f'--- (a) contact filter, spare if Tib/Tsh form matches DISTANT [{thr}]')
    dropped = {L: len(CB) - len(contact_filter(L, thr)) for L in POS_B + KB}
    print('   concepts dropped: ' + ' '.join(f'{L[:5]}:{dropped[L]}' for L in POS_B + KB))
    summary('   CAL-005 pos filtered', POS_B, lambda L: contact_filter(L, thr))
    summary('   CAL-005 pos filtered, Batang uses MotuoMenba only', ['Batang'], lambda L: contact_filter(L, thr, ['MotuoMenba']))
    summary('   KB filtered', KB, lambda L: contact_filter(L, thr))
    summary('   KB filtered +Bokar(Tani) as contact', KB, lambda L: contact_filter(L, thr, CONTACT + ['Bokar']))

# random-drop control: drop the same number of concepts at random from KB (100 draws), median p/ratio
rng = np.random.default_rng(1)
print('--- random-drop control (same #dropped as majority filter, 50 draws, median ratio)')
for L in KB:
    keep = contact_filter(L, 'majority'); nd = len(CB) - len(keep)
    rs = []
    for _ in range(50):
        C = list(rng.choice(CB, len(CB) - nd, replace=False))
        rs.append(ccm(bod[L], refs_for(L), C, nperm=1000)['ratio'])
    print(f'   {L}: dropped {nd}, random-drop median ratio {np.median(rs):.2f}')

# ---- (b) concept composition
def bscore(cs):
    v = [float(TAD[c]['BORROWED_SCORE']) for c in cs if c in TAD]
    return len(v), (np.mean(v) if v else float('nan'))
print('--- (b) composition')
for name, cs in [('old76', sorted(OLD76)), ('held112', CB)]:
    n, m = bscore(cs)
    print(f'   {name}: in Leipzig-Jakarta(Tadmor100) {n}/{len(cs)}; mean BORROWED_SCORE (higher = less borrowed) {m:.3f}')
LJ = [c for c in CB if c in TAD]
print('   LJ concepts in 112:', ', '.join(gl[c] for c in LJ))
print('   non-LJ concepts in 112:', ', '.join(gl[c] for c in CB if c not in TAD))
summary('   CAL-005 pos on LJ∩112', POS_B, lambda L: LJ)
summary('   NEG on LJ∩112', NEG, lambda L: LJ)
summary('   KB on LJ∩112', KB, lambda L: LJ)
NONLJ = [c for c in CB if c not in TAD]
summary('   CAL-005 pos on 112 minus LJ', POS_B, lambda L: NONLJ)
summary('   KB on 112 minus LJ', KB, lambda L: NONLJ)
