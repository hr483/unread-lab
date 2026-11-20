from run import *
NEG=['fin','hun','ekk','tam','tel','kan','mal','eus','kat','arb','heb','tur','lit','gle']
for l in NEG: ALL[l]=N[l]
def sa(lang,refs,cids,seed=20261119,NPm=5000):
    t=table(ALL,lang,cids,PREFIX); cc=[c for c in cids if c in t]; n=len(cc)
    tc=[t[c][0] for c in cc]
    rt={r:table(ALL,r,cc,PREFIX) for r in refs}
    M=np.zeros((n,n))
    for j,c in enumerate(cc):
        for r in refs:
            if c in rt[r] and rt[r][c][0] is not None:
                for i in range(n):
                    if tc[i] is not None and tc[i]==rt[r][c][0]: M[i,j]+=1
    shape=np.array([0 if x is None else (1 if x[1]=='-' else 2) for x in tc])
    obs=np.diag(M).copy(); rng=np.random.default_rng(seed)
    E=np.zeros(n); nl=[]
    for k in range(NPm):
        p=np.arange(n)
        for s in (0,1,2):
            idx=np.where(shape==s)[0]; p[idx]=idx[rng.permutation(len(idx))]
        v=M[p,np.arange(n)]; E+=v; nl.append(v.sum())
    E/=NPm; nl=np.array(nl)
    st=np.array([c in HOL for c in cc]); e=obs-E
    one=sum(obs[j] for j in range(n) if shape[j]==1)
    return obs.sum()/nl.mean(), ((nl>=obs.sum()).sum()+1)/(NPm+1), e[st].mean()-e[~st].mean(), one/obs.sum(), (shape==1)[st].mean(), (shape==1)[~st].mean()
print('label ratio_strat p_strat I_strat frac_matches_1cons share1cons_stable share1cons_other')
for l in ['jpn','kor']:
    print(l,'SIN7','%.2f %.4f %+.3f %.2f %.2f %.2f'%sa(l,SIN,CSN))
    print(l,'DIST12','%.2f %.4f %+.3f %.2f %.2f %.2f'%sa(l,DIST,CSN))
for l in NEG: print(l,'DIST12','%.2f %.4f %+.3f %.2f %.2f %.2f'%sa(l,DIST,CSN))
Is=[]
for l in KB:
    x=sa(l,DIST,CSB); Is.append(x[2]); print(l,'DIST12','%.2f %.4f %+.3f %.2f %.2f %.2f'%x)
print('KB mean I strat %+.3f'%np.mean(Is))
Is=[]
for l in POS:
    x=sa(l,[r for r in DIST if SUB[r]!=SUB[l]],CSB); Is.append(x[2]); print(l,'%.2f %.4f %+.3f %.2f %.2f %.2f'%x)
print('POS mean I strat %+.3f'%np.mean(Is))
