import sys
sys.path.insert(0, '/home/claude/unread-lab/redteam2')
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from attack_b import *
sagraw = load('sagartst')

def contrib(L, dist=DISTANT):
    t = langcode(L); c2 = collections.Counter()
    for c in CB:
        if t.get(c) is None: continue
        for D in dist:
            if (L in KB or SUBG.get(D) != SUBG.get(L)) and sag[D].get(c) == t[c]: c2[c] += 1
    return c2
print('--- each language minus ITS OWN top-k contributing concepts (fair version)')
for k in (5, 10):
    for grp, langs in (('POS', POS_B), ('KB', KB)):
        out = {}
        for L in langs:
            top = [c for c, v in contrib(L).most_common(k)]
            out[L] = ccm(langcode(L), refs_for(L), [c for c in CB if c not in top])
        adj = holm([out[L]['p'] for L in langs])
        print(f'  k={k} {grp}: Holm<0.01 {sum(a<0.01 for a in adj)}/{len(langs)}; ' + ' '.join(f'{L[:5]}:{out[L]["ratio"]:.2f}/{out[L]["p"]:.4f}' for L in langs))

print('--- Duhumbi and Rupa matches with DISTANT, with Tibetan/Tshangla forms shown')
for L in ['Duhumbi', 'Rupa']:
    for c, v in contrib(L).most_common():
        f = bodraw[L][c][1]
        tib = {T: sagraw[T][c][1] for T in CONTACT if c in sagraw.get(T, {})}
        tibm = [T for T in CONTACT if sag[T].get(c) == bod[L][c]]
        dm = [D for D in DISTANT if sag[D].get(c) == bod[L][c]]
        print(f'   {L[:4]} {gl[c][:14]:14s} {f:14s} {str(bod[L][c]):12s} nD={v:2d} {",".join(d[:5] for d in dm):40s} TibTsh-match={",".join(tibm) or "-"} {tib}')
