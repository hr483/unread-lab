import sys, json
sys.path.insert(0, '/home/claude/unread-lab/redteam2')
from core import *

VARIANT = sys.argv[1] if len(sys.argv) > 1 else 'plan'
KW = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
NEG = ['fin', 'hun', 'ekk', 'tam', 'tel', 'kan', 'mal', 'eus', 'kat', 'arb', 'heb', 'tur', 'lit', 'gle']

sun = coded(load('suntb'), VARIANT, **KW)
sag_raw = load('sagartst')
sag = coded(sag_raw, VARIANT, **KW)
bod = coded(load('bodtkhobwa'), VARIANT, **KW)
nel = coded(load('northeuralex', set(NEG)), VARIANT, **KW)
TAD = tadmor()

def show(name, r, extra=''):
    print(f"  {name:20s} n={r['n']:3d} pairs={r.get('npairs',0):4d} obs={r['obs']:4d} null={r['null_mean']:7.2f} ratio={r['ratio']:5.2f} p={r['p']:.5f} {extra}")

def battery(title, tests, refsets, concepts, neg=True, holm_line=True):
    print('==', title)
    res = {}
    for t in tests:
        res[t] = ccm(tests[t], refsets[t], concepts)
    ps = [res[t]['p'] for t in tests]
    adj = holm(ps)
    for (t, a) in zip(tests, adj):
        res[t]['holm'] = a
        show(t, res[t], f'holm={a:.4f}')
    return res

def calib(title, pos, posrefs, negrefs, concepts):
    r = battery(title + ' positives', pos, posrefs, concepts)
    npass = sum(1 for t in r if r[t]['holm'] < 0.01)
    print(f'  positives Holm<0.01: {npass}/{len(r)} (need >= {0.7*len(r):.1f})')
    rn = {}
    print('  negatives:')
    for L in NEG:
        rn[L] = ccm(nel[L], negrefs, concepts)
        show(L, rn[L])
    nneg = sum(1 for L in rn if rn[L]['p'] < 0.01)
    print(f'  negatives raw p<0.01: {nneg}/14 (max 1)')
    print('  CAL PASS' if npass >= 0.7 * len(r) and nneg <= 1 else '  CAL FAIL')
    return r, rn

# ---------------- TEST A
DISTANT_SUN = ['Lisu', 'BlackLahu', 'CaiyuanHani', 'XideYi', 'MileYi', 'Jinuo', 'Achang', 'Atsi', 'RangoonBurmese', 'Maru']
POS_A = ['Jingpho', 'Trung', 'Anong', 'MaerkangrGyalrong', 'DanbaErgong', 'Ersu', 'Namuyi', 'Xumi', 'Guiqiong', 'Muya', 'YajiangQueyu', 'MawoQiang', 'QinghuaPumi']
CA = sorted(cids('suntb') & set(TAD))
print('TEST_A concepts:', len(CA))
dref = [sun[L] for L in DISTANT_SUN]
rA, _ = calib('CAL-004', {L: sun[L] for L in POS_A}, {L: dref for L in POS_A}, dref, CA)
print('== TEST_A main: Sulong vs DISTANT_SUN')
sul = ccm(sun['Sulong'], dref, CA); show('Sulong', sul)
ratios = sorted([(rA[L]['ratio'], L) for L in POS_A])
below = sum(1 for x, _ in ratios if x < sul['ratio'])
print(f'  Sulong ratio {sul["ratio"]:.3f}; positives with lower ratio: {below}/13; rank among 14 (1=highest): {14-below}')
print('  positive ratios:', ', '.join(f'{L}:{x:.2f}' for x, L in ratios))
SEC = ['Sulong', 'Darang', 'Idu', 'Kaman', 'BokarLhoba']
battery('TEST_A secondary', {L: sun[L] for L in SEC}, {L: dref for L in SEC}, CA)
print('== TEST_A contact report: Sulong vs [LhasaTibetan, MotuoTsangla, BokarLhoba]')
show('group', ccm(sun['Sulong'], [sun[L] for L in ['LhasaTibetan', 'MotuoTsangla', 'BokarLhoba']], CA))
for L in ['LhasaTibetan', 'MotuoTsangla', 'BokarLhoba']:
    show(L, ccm(sun['Sulong'], [sun[L]], CA))

# ---------------- TEST B
DISTANT = ['OldChinese', 'OldBurmese', 'Lisu', 'Japhug', 'Tangut', 'Zhaba', 'Limbu', 'Bahing', 'Hayu', 'Hakha', 'Lushai', 'Ukhrul']
SUBG = {r['ID']: r['SubGroup'] for r in csv.DictReader(open(f'{DATA}/sagartst/cldf/languages.csv'))}
POS_B = ['Beijing', 'Rangoon', 'Bantawa', 'Bunan', 'Chepang', 'Daofu', 'Garo', 'Rabha', 'Jingpho', 'Dulong', 'Mikir', 'Batang', 'Yidu']
CB = sorted((cids('bodtkhobwa') & cids('sagartst')) - (cids('khobwa') & cids('sagartst')))
print('TEST_B concepts:', len(CB))
posrefs = {L: [sag[D] for D in DISTANT if SUBG[D] != SUBG[L]] for L in POS_B}
for L in POS_B:
    print('   ', L, SUBG[L], 'refs', len(posrefs[L]))
dB = [sag[D] for D in DISTANT]
rB, _ = calib('CAL-005', {L: sag[L] for L in POS_B}, posrefs, dB, CB)
KB = ['Duhumbi', 'Jerigaon', 'Khispi', 'Khoina', 'Khoitam', 'Rahung', 'Rupa', 'Shergaon']
r = battery('TEST_B main', {L: bod[L] for L in KB}, {L: dB for L in KB}, CB)
print('  Holm<0.01:', sum(1 for L in r if r[L]['holm'] < 0.01), '/8')
pr = sorted(rB[L]['ratio'] for L in POS_B)
print('  CAL-005 positive ratios: min %.2f median %.2f max %.2f' % (pr[0], pr[6], pr[-1]))
