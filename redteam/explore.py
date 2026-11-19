import sys, collections
import numpy as np
sys.path.insert(0, '/home/claude/unread-lab/redteam')
from ccm import *
from run import C76, KB, posref, kb, st, nl

out = []
P = lambda *a: (out.append(' '.join(str(x) for x in a)), print(*a, flush=True))


def codes(kw):
    a = {}
    for d in (st, kb, nl):
        a.update(build_codes(d, C76, 'first', **kw))
    return a


def cond_purge_test(t, refs, contacts, concepts, nperm=NPERM, seed=SEED):
    """Symmetric purge: count DISTANT matches only at concepts where the test word matches no CONTACT word,
    recomputing the purge inside every permutation."""
    K = [c for c in concepts if c in t]
    vocab = {}
    enc = lambda x: vocab.setdefault(x, len(vocab))
    T = np.array([enc(t[c]) for c in K])
    R = np.array([[enc(r[c]) if c in r else -1 for c in K] for r in refs])
    Cn = np.array([[enc(r[c]) if c in r else -2 for c in K] for r in contacts])

    def stat(Pm):
        m = (R[None] == Pm[:, None]).sum(1)
        keep = ~(Cn[None] == Pm[:, None]).any(1)
        return (m * keep).sum(1)
    obs = int(stat(T[None])[0])
    rng = np.random.default_rng(seed)
    null = np.concatenate([stat(T[np.argsort(rng.random((1000, len(K))), axis=1)]) for _ in range(nperm // 1000)])
    return obs, (int((null >= obs).sum()) + 1) / (nperm + 1), float(null.mean())


for label, kw in [('first form, initial V=H', {}), ('prefix-stripped', dict(prefix_strip=True))]:
    A = codes(kw)
    P(f'\n## EXPL-d symmetric (in-permutation) purge, {label}')
    ps = []
    for p in POS:
        o, pv, nm = cond_purge_test(A[p], [A[d] for d in posref(p)], [A[k] for k in CONTACT], C76)
        ps.append(pv)
        P(f'| {p} | {o} | {nm:.1f} | {pv:.4f} |')
    h = holm(ps)
    P('positives Holm<0.01:', int((h < 0.01).sum()), '/13')
    ps = []
    for g in NEG:
        o, pv, nm = cond_purge_test(A[g], [A[d] for d in DISTANT], [A[k] for k in CONTACT], C76)
        ps.append(pv)
    P('negatives raw p<0.01:', sum(p < 0.01 for p in ps), '/14; min p', min(ps))
    ps = {}
    for l in KB:
        o, pv, nm = cond_purge_test(A[l], [A[d] for d in DISTANT], [A[k] for k in CONTACT], C76)
        ps[l] = (o, nm, pv)
    h = holm([v[2] for v in ps.values()])
    P('Kho-Bwa Holm<0.01:', int((h < 0.01).sum()), '/22; raw p<0.01:', sum(v[2] < 0.01 for v in ps.values()))
    for l in ['Eastern_Puroik_Li', 'Eastern_Puroik_Sun', 'Duhumbi', 'Khispi']:
        P(f'  {l}: obs {ps[l][0]} null {ps[l][1]:.1f} p {ps[l][2]:.4f}')

    # false-positive check on Kho-Bwa data itself: Kho-Bwa vs the 14 unrelated NEG languages as a reference set
    ps = [ccm_test(A[l], [A[g] for g in NEG], C76)['p'] for l in KB]
    P(f'FP check ({label}): Kho-Bwa vs NEG set, raw p<0.01: {sum(p<0.01 for p in ps)}/22, min p {min(ps):.4f}')
    # and Kho-Bwa vs CONTACT (expected positive: contact + inheritance)
    ps = [ccm_test(A[l], [A[k] for k in CONTACT], C76)['p'] for l in KB]
    P(f'Kho-Bwa vs CONTACT ({label}): Holm<0.01 {int((holm(ps)<0.01).sum())}/22')

# Random-drop control: drop the same number of concepts as the purge, chosen at random
A = codes({})
P('\n## EXPL-e random concept drop matched to purge size (first form), 200 draws x 2000 perms')
rng = np.random.default_rng(1)
for grp, langs, refsf in [('positives', POS, posref), ('khobwa', KB, lambda x: DISTANT)]:
    res = []
    for l in langs:
        t = A[l]
        bad = {c for c in t for k in CONTACT if c in A[k] and A[k][c] == t[c]}
        nd = len(bad)
        keys = list(t)
        pv = []
        for d in range(200):
            drop = set(rng.choice(keys, nd, replace=False)) if nd else set()
            tt = {c: v for c, v in t.items() if c not in drop}
            pv.append(ccm_test(tt, [A[r] for r in refsf(l)], C76, nperm=2000, seed=d)['p'])
        res.append((l, nd, float(np.median(pv)), float(np.mean(np.array(pv) < 0.01 / len(langs)))))
    for r in res:
        P(f'| {r[0]} | drop {r[1]} | median p {r[2]:.4f} | frac p<{0.01/len(langs):.5f}: {r[3]:.2f} |')

# Concept drivers of Kho-Bwa matches with DISTANT (primary) and what purge removes
P('\n## concept drivers (primary, first form)')
par = {r['Concepticon_ID']: r['Name'] for r in csv.DictReader(open(D + 'khobwa/cldf/parameters.csv'))}
cnt = collections.Counter(); pur = collections.Counter()
for l in KB:
    t = A[l]
    for c in t:
        m = sum(1 for d in DISTANT if A[d].get(c) == t[c])
        if m:
            cnt[c] += m
            if any(A[k].get(c) == t[c] for k in CONTACT):
                pur[c] += m
tot = sum(cnt.values())
P('total doculect-ref matches', tot, '; removed by purge', sum(pur.values()))
for c, v in cnt.most_common(15):
    ex = collections.Counter(A[l].get(c) for l in KB).most_common(2)
    P(f'| {par[c]} | {v} | purged {pur[c]} | top codes {ex} |')

# initial-H share
hs = [sum(1 for c in A[l] if A[l][c][0] == 'H') / len(A[l]) for l in KB]
hd = [sum(1 for c in A[l] if A[l][c][0] == 'H') / len(A[l]) for l in DISTANT]
P(f'\nshare of codes with C1=H: Kho-Bwa mean {np.mean(hs):.2f} (range {min(hs):.2f}-{max(hs):.2f}); DISTANT mean {np.mean(hd):.2f}')
pre = []
for l in KB:
    n = sum(1 for c in kb[l] if c in C76 and '+' in kb[l][c][0])
    pre.append(n)
P(f'Kho-Bwa first forms containing a morpheme boundary (+), of 76 concepts: mean {np.mean(pre):.1f}, range {min(pre)}-{max(pre)}')
open('/home/claude/unread-lab/redteam/explore_out.txt', 'w').write('\n'.join(out))
