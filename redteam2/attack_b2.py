"""EXPLORATORY attacks on TEST_B part 2: concept classes, reference leave-outs, redundancy."""
import sys
sys.path.insert(0, '/home/claude/unread-lab/redteam2')
from attack_b import *  # reruns base prints; fine

G2C = {v: k for k, v in gl.items()}
def ids(names): return {G2C[n] for n in names if n in G2C}
NURSERY = ids(['MOTHER', 'FATHER'])
NUMERALS = ids(['TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN', 'TWENTY'])
CULTURE = ids(['WHEAT', 'BARLEY', 'HORSE', 'GOAT', 'SHEEP', 'PIG', 'NEEDLE (FOR SEWING)', 'BUY', 'SOW SEEDS', 'PLANT (SOMETHING)', 'SEED', 'COUNT', 'STEAL', 'YELLOW', 'GREEN'])
PRON = ids(['WE (INCLUSIVE)', 'YOU', 'HE OR SHE OR IT', 'THAT', 'HERE', 'WHERE'])
print('sizes nursery/num/culture/pron', len(NURSERY), len(NUMERALS), len(CULTURE), len(PRON))
for name, drop in [('minus nursery', NURSERY), ('minus numerals', NUMERALS), ('minus culture', CULTURE),
                   ('minus pronouns/deictics', PRON), ('minus all four classes', NURSERY | NUMERALS | CULTURE | PRON)]:
    C = [c for c in CB if c not in drop]
    print(f'--- {name}: {len(C)} concepts')
    summary('   POS', POS_B, lambda L: C)
    summary('   KB', KB, lambda L: C)
    summary('   NEG', NEG, lambda L: C)

top = [c for c, v in cnt.most_common(10)]
C = [c for c in CB if c not in top]
print('--- minus KB top-10 matching concepts (selected on KB, so biased against KB)')
summary('   POS', POS_B, lambda L: C)
summary('   KB', KB, lambda L: C)

print('--- DISTANT leave-outs')
for drop in [['Japhug', 'Zhaba'], ['Japhug', 'Zhaba', 'Tangut'], ['OldChinese', 'OldBurmese', 'Lisu'], ['Hakha', 'Lushai', 'Ukhrul']]:
    dist = [d for d in DISTANT if d not in drop]
    print('  without', drop)
    summary('   POS', POS_B, lambda L: CB, dist)
    summary('   KB', KB, lambda L: CB, dist)
# single-ref: which DISTANT languages carry KB
print('--- KB (Duhumbi, Rupa) vs each DISTANT language singly; POS median ratio for same ref')
for D in DISTANT:
    rd = ccm(bod['Duhumbi'], [sag[D]], CB); rr = ccm(bod['Rupa'], [sag[D]], CB)
    pr = [ccm(sag[P], [sag[D]], CB, nperm=2000)['ratio'] for P in POS_B if SUBG[P] != SUBG[D]]
    print(f'   {D:11s} Duhumbi obs={rd["obs"]:2d} r={rd["ratio"]:.2f} p={rd["p"]:.4f} | Rupa obs={rr["obs"]:2d} r={rr["ratio"]:.2f} p={rr["p"]:.4f} | POS median r={np.median(pr):.2f}')

# redundancy among 8 doculects
print('--- pairwise code identity among KB doculects on 112')
M = np.zeros((8, 8))
for i, a in enumerate(KB):
    for j, b in enumerate(KB):
        sh = [c for c in CB if bod[a].get(c) is not None and bod[b].get(c) is not None]
        M[i, j] = np.mean([bod[a][c] == bod[b][c] for c in sh])
print('   mean off-diagonal identity %.2f, min %.2f' % (M[~np.eye(8, dtype=bool)].mean(), M[~np.eye(8, dtype=bool)].min()))
for i, a in enumerate(KB): print('   ', a[:8].ljust(8), ' '.join(f'{x:.2f}' for x in M[i]))

# excess retained under majority contact filter
print('--- excess matches (obs - null) retained under majority contact filter')
for L in POS_B + KB:
    b = ccm(langcode(L), refs_for(L), CB); f = ccm(langcode(L), refs_for(L), contact_filter(L, 'majority'))
    print(f'   {L:9s} base excess {b["obs"]-b["null_mean"]:6.1f}  filtered {f["obs"]-f["null_mean"]:6.1f}  retained {(f["obs"]-f["null_mean"])/(b["obs"]-b["null_mean"]):.0%}')
