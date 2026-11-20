from run import *
def conc(lang,refs,cids,seed=20261119):
    t=table(ALL,lang,cids,PREFIX); cc=[c for c in cids if c in t]; n=len(cc)
    rt={r:table(ALL,r,cc,PREFIX) for r in refs}
    M=np.zeros((n,n))
    for j,c in enumerate(cc):
        for r in refs:
            if c in rt[r] and rt[r][c][0] is not None:
                for i in range(n):
                    if t[cc[i]][0] is not None and t[cc[i]][0]==rt[r][c][0]: M[i,j]+=1
    obs=np.diag(M); rng=np.random.default_rng(seed)
    nm=[];ns=[]
    for k in range(10000):
        v=M[rng.permutation(n),np.arange(n)]; nm.append(v.sum()); ns.append((v>0).sum())
    oc=(obs>0).sum(); 
    return dict(n=n,ratio=obs.sum()/np.mean(nm),cratio=oc/np.mean(ns),nconc=oc,mult=obs.sum()/max(oc,1),p=((np.array(nm)>=obs.sum()).sum()+1)/10001,pc=((np.array(ns)>=oc).sum()+1)/10001)
def show(lbl,lang,refs,cids):
    d=conc(lang,refs,cids)
    print(f"{lbl:34s} nref={len(refs):2d} n={d['n']:3d} ratio={d['ratio']:.2f} p={d['p']:.4f} | matched concepts={d['nconc']:2d} concept-ratio={d['cratio']:.2f} p_c={d['pc']:.4f} mult={d['mult']:.2f}")
    return d
print('--- jpn/kor vs Sinitic (plan) and vs DISTANT (Kho-Bwa ref set)')
for l in ['jpn','kor']:
    show(l+' vs SIN7',l,SIN,CSN)
    show(l+' vs DISTANT12',l,DIST,CSN)
    show(l+' vs DISTANT minus OldChinese',l,[x for x in DIST if x!='OldChinese'],CSN)
    show(l+' vs OldChinese only',l,['OldChinese'],CSN)
print('--- Kho-Bwa')
for l in KB:
    show(l+' vs DISTANT12',l,DIST,CSB)
    show(l+' vs SIN7',l,SIN,CSB)
print('--- positives vs DISTANT-minus-subgroup')
for l in POS:
    show(l,l,[r for r in DIST if SUB[r]!=SUB[l]],CSB)
