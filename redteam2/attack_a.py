"""EXPLORATORY attacks on TEST_A (and prefix rule counts for both tests)."""
import sys, collections
sys.path.insert(0, '/home/claude/unread-lab/redteam2')
from core import *

TAD = tadmor()
DISTANT_SUN = ['Lisu', 'BlackLahu', 'CaiyuanHani', 'XideYi', 'MileYi', 'Jinuo', 'Achang', 'Atsi', 'RangoonBurmese', 'Maru']
POS_A = ['Jingpho', 'Trung', 'Anong', 'MaerkangrGyalrong', 'DanbaErgong', 'Ersu', 'Namuyi', 'Xumi', 'Guiqiong', 'Muya', 'YajiangQueyu', 'MawoQiang', 'QinghuaPumi']
ARU = ['Sulong', 'Darang', 'Idu', 'Kaman', 'BokarLhoba']
CA = sorted(cids('suntb') & set(TAD))
sunraw = load('suntb')
bodraw = load('bodtkhobwa')
OLD76 = cids('khobwa') & cids('sagartst')
CB = sorted((cids('bodtkhobwa') & cids('sagartst')) - OLD76)
KB = ['Duhumbi', 'Jerigaon', 'Khispi', 'Khoina', 'Khoitam', 'Rahung', 'Rupa', 'Shergaon']

# ---- (c) prefix rule firing counts
def classify(seg):
    toks = norm_tokens(seg)
    a = strip_prefix(toks, 'plan')
    if a == toks: return 'none', None
    b = strip_prefix(toks, 'strict')
    m0 = ''.join(t for t in split_morphs(toks)[0] if not is_tone(t))
    return ('inventory' if b != toks else 'non-inventory'), m0
for name, raw, langs, C in [('Sulong (TEST_A 77)', sunraw, ['Sulong'], CA), ('Western Kho-Bwa (8 x 112)', bodraw, KB, CB),
                            ('CAL-004 positives (13 x 77)', sunraw, POS_A, CA)]:
    cnt = collections.Counter(); ex = collections.Counter(); n = 0
    for L in langs:
        for c in C:
            if c not in raw[L]: continue
            n += 1
            k, m0 = classify(raw[L][c][0]); cnt[k] += 1
            if k == 'non-inventory': ex[m0] += 1
    print(f'{name}: forms {n}; prefix stripped {cnt["inventory"]+cnt["non-inventory"]} '
          f'(inventory/bare-vowel {cnt["inventory"]}, other {cnt["non-inventory"]}); top non-inventory first morphemes: {ex.most_common(12)}')
gl = {r['Concepticon_ID']: r['Concepticon_Gloss'] for r in csv.DictReader(open(f'{DATA}/suntb/cldf/parameters.csv'))}
print('Sulong non-inventory strips:')
for c in CA:
    if c in sunraw['Sulong']:
        k, m0 = classify(sunraw['Sulong'][c][0])
        if k == 'non-inventory':
            print(f'   {gl[c]:12s} {sunraw["Sulong"][c][1]:18s} plan={code(sunraw["Sulong"][c][0])} none={code(sunraw["Sulong"][c][0],"none")}')

# ---- rank / strength robustness per variant
for var, kw in [('plan', {}), ('strict', {}), ('none', {}), ('plan', {'iterate': True})]:
    sun = coded(sunraw, var, **kw)
    dref = [sun[L] for L in DISTANT_SUN]
    res = {L: ccm(sun[L], dref, CA) for L in POS_A + ARU}
    # z-score
    def z(L):
        T = sun[L]; C = [c for c in CA if T.get(c) is not None]
        return None
    pr = sorted((res[L]['ratio'], L) for L in POS_A)
    print(f'\n[{var}{kw}] Sulong ratio {res["Sulong"]["ratio"]:.2f} p={res["Sulong"]["p"]:.4f}; weakest positives: ' +
          ', '.join(f'{L}:{r:.2f}' for r, L in pr[:4]) + '; Arunachal: ' + ', '.join(f'{L}:{res[L]["ratio"]:.2f}/p{res[L]["p"]:.4f}' for L in ARU))

# ---- bootstrap over concepts (plan coding): is Sulong reliably below all 13?
sun = coded(sunraw, 'plan')
rng = np.random.default_rng(7)
def ratio_fast(T, refs, C):
    # analytic null mean for permutation: sum_r sum_i P(T[perm i]==r_i) = sum_r sum_i freq_T(r_i)/n
    C = [c for c in C if T.get(c) is not None]
    n = len(C); from collections import Counter
    f = Counter(T[c] for c in C)
    obs = sum(1 for r in refs for c in C if r.get(c) is not None and r[c] == T[c])
    nm = sum(f.get(r[c], 0) / n for r in refs for c in C if r.get(c) is not None)
    return obs / nm if nm else float('nan')
dref = [sun[L] for L in DISTANT_SUN]
B = 1000; below_all = 0; below_n = []; darang_below = 0
for b in range(B):
    C = list(rng.choice(CA, len(CA), replace=True))
    s = ratio_fast(sun['Sulong'], dref, C)
    ps = [ratio_fast(sun[L], dref, C) for L in POS_A]
    k = sum(1 for x in ps if x < s); below_n.append(k)
    below_all += (k == 0)
    darang_below += ratio_fast(sun['Darang'], dref, C) < s
print(f'\nBootstrap (B={B}, concepts resampled): Sulong below all 13 positives in {below_all/B:.0%}; '
      f'median # positives below Sulong {np.median(below_n):.0f}; 90% interval [{np.percentile(below_n,5):.0f},{np.percentile(below_n,95):.0f}]; Darang below Sulong in {darang_below/B:.0%}')

# z-score strength (permutation sd)
print('\nz = (obs-null_mean)/null_sd, plan coding:')
def zscore(T, refs, C, nperm=4000):
    C = [c for c in C if T.get(c) is not None]
    voc = {}; e = lambda x: voc.setdefault(x, len(voc))
    Ta = np.array([e(T[c]) for c in C]); R = np.array([[e(r[c]) if r.get(c) is not None else -2 for c in C] for r in refs])
    obs = (Ta[None] == R).sum(); rg = np.random.default_rng(SEED)
    P = np.argsort(rg.random((nperm, len(C))), 1); Tp = Ta[P]
    nl = sum((Tp == row[None]).sum(1) for row in R)
    return (obs - nl.mean()) / nl.std()
zs = {L: zscore(sun[L], dref, CA) for L in POS_A + ARU}
print('   ' + ', '.join(f'{L}:{zs[L]:.1f}' for L in sorted(zs, key=zs.get)))
