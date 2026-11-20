"""EXPLORATORY: '+'-only boundary variant; Puroik (khobwa, Sun & Li) vs sagartst DISTANT on the 76 concepts; seed sensitivity."""
import sys, subprocess
sys.path.insert(0, '/home/claude/unread-lab/redteam2')
import core
from core import *
DISTANT = ['OldChinese','OldBurmese','Lisu','Japhug','Tangut','Zhaba','Limbu','Bahing','Hayu','Hakha','Lushai','Ukhrul']
SUBG = {r['ID']: r['SubGroup'] for r in csv.DictReader(open(f'{DATA}/sagartst/cldf/languages.csv'))}
POS_B = ['Beijing','Rangoon','Bantawa','Bunan','Chepang','Daofu','Garo','Rabha','Jingpho','Dulong','Mikir','Batang','Yidu']
OLD76 = sorted(cids('khobwa') & cids('sagartst'))
sag = coded(load('sagartst'), 'plan'); kh = coded(load('khobwa'), 'plan')
dref = [sag[D] for D in DISTANT]
print('Puroik/Kho-Bwa from khobwa vs sagartst DISTANT, 76 concepts, plan coding (SEEN data, exploratory)')
for L in ['Eastern_Puroik_Sun', 'Eastern_Puroik_Li', 'Rawa', 'Duhumbi', 'Rupa', 'Shergaon']:
    if L in kh:
        r = ccm(kh[L], dref, OLD76); print(f'   {L:20s} n={r["n"]} obs={r["obs"]} null={r["null_mean"]:.1f} ratio={r["ratio"]:.2f} p={r["p"]:.4f}')
pr = sorted((ccm(sag[P], [sag[D] for D in DISTANT if SUBG[D] != SUBG[P]], OLD76)['ratio'], P) for P in POS_B)
print('   CAL positives on same 76:', ', '.join(f'{P}:{x:.2f}' for x, P in pr))
print('   khobwa languages:', sorted(kh))
