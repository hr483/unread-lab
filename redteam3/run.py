import sys, json, csv
from ccm3 import *
PREFIX = '--noprefix' not in sys.argv
S=load('sagartst');B=load('bodtkhobwa');K=load('khobwa');N=load('northeuralex')
assert not set(S)&set(B); ALL={**K,**S,**B}
for l in ('jpn','kor'): ALL[l]=N[l]
cs=lambda X:set(c for l in X for c in X[l])
SUB={r['ID']:r['SubGroup'] for r in csv.DictReader(open(D+'sagartst/cldf/languages.csv'))}
HOL=set(r['CONCEPTICON_ID'] for r in csv.DictReader(open(D+'conceptlists/Holman-2008-40.tsv'),delimiter='\t'))
DIST=['OldChinese','OldBurmese','Lisu','Japhug','Tangut','Zhaba','Limbu','Bahing','Hayu','Hakha','Lushai','Ukhrul']
SIN=['Beijing','Chaozhou','Guangzhou','Jieyang','Longgang','OldChinese','Xingning']
POS=['Beijing','Rangoon','Bantawa','Bunan','Chepang','Daofu','Garo','Rabha','Jingpho','Dulong','Mikir','Batang','Yidu']
KB=['Duhumbi','Jerigaon','Khispi','Khoina','Khoitam','Rahung','Rupa','Shergaon']
PU=['Eastern_Puroik_Li','Eastern_Puroik_Sun','Rawa']
CSB=sorted(cs(S)&cs(B)); CSN=sorted(cs(S)&cs(N)); CSK=sorted(cs(S)&cs(K))
NP=10000

def analyse(lang, refs, cids, seed=20261119):
    t=table(ALL,lang,cids,PREFIX)
    cc=[c for c in cids if c in t]
    tc=[t[c][0] for c in cc]
    rt={r:table(ALL,r,cc,PREFIX) for r in refs}
    n=len(cc)
    # M[i,j]= number of refs whose code for concept j equals test word i
    M=np.zeros((n,n))
    for j,c in enumerate(cc):
        for r in refs:
            if c in rt[r] and rt[r][c][0] is not None:
                rc=rt[r][c][0]
                for i in range(n):
                    if tc[i] is not None and tc[i]==rc: M[i,j]+=1
    m=np.diag(M).copy()
    rng=np.random.default_rng(seed)
    Esum=np.zeros(n); null=np.zeros(NP)
    for k in range(NP):
        p=rng.permutation(n)
        v=M[p,np.arange(n)]
        Esum+=v; null[k]=v.sum()
    E=Esum/NP
    obs=m.sum()
    pval=((null>=obs).sum()+1)/(NP+1)
    return dict(cc=cc,m=m,E=E,Eexact=M.mean(0),obs=obs,nullmean=null.mean(),p=pval,t=t,rt=rt)

def I_of(res, idx=None):
    cc=res['cc']; e=res['m']-res['E']
    st=np.array([c in HOL for c in cc])
    return e[st].mean()-e[~st].mean(), st.sum(), (~st).sum()

def pooled(results, cids, nb=2000, seed=20261120):
    # bootstrap concepts within tier over the full concept set, same resample for all members
    st=[c for c in cids if c in HOL]; ot=[c for c in cids if c not in HOL]
    rng=np.random.default_rng(seed)
    Is=[I_of(r)[0] for r in results]
    em=[]
    for r in results:
        e=dict(zip(r['cc'],r['m']-r['E'])); em.append(e)
    boots=[]
    for b in range(nb):
        s=rng.choice(len(st),len(st)); o=rng.choice(len(ot),len(ot))
        vals=[]
        for e in em:
            sv=[e[st[i]] for i in s if st[i] in e]; ov=[e[ot[i]] for i in o if ot[i] in e]
            vals.append(np.mean(sv)-np.mean(ov))
        boots.append(np.mean(vals))
    boots=np.array(boots)
    return np.mean(Is), np.percentile(boots,5), np.percentile(boots,95)

def report(name, langs, refsf, cids):
    print('=== '+name, 'nconcepts',len(cids),'stable in set',sum(c in HOL for c in cids))
    res=[]
    for l in langs:
        refs=refsf(l); r=analyse(l,refs,cids); res.append(r)
        I,ns,no=I_of(r)
        e=r['m']-r['E']; st=np.array([c in HOL for c in r['cc']])
        print(f"{l:20s} nref={len(refs):2d} n={len(r['cc'])} (S{ns}/O{no}) obs={r['obs']:.0f} null={r['nullmean']:.2f} ratio={r['obs']/r['nullmean']:.2f} p={r['p']:.4f} I={I:+.3f} eS={e[st].mean():+.3f} eO={e[~st].mean():+.3f} mS={r['m'][st].sum():.0f} mO={r['m'][~st].sum():.0f}")
    P=pooled(res,cids)
    print(f"POOLED I={P[0]:+.3f} 90%CI [{P[1]:+.3f},{P[2]:+.3f}]  npos={sum(I_of(r)[0]>0 for r in res)}/{len(res)}")
    return res

if __name__=='__main__':
    print('PREFIX',PREFIX)
    report('INHERITANCE', POS, lambda l:[r for r in DIST if SUB[r]!=SUB[l]], CSB)
    RB=report('BORROWING', ['jpn','kor'], lambda l:SIN, CSN)
    RK=report('KHO-BWA', KB, lambda l:DIST, CSB)
    report('PUROIK', PU, lambda l:DIST, CSK)
    import pickle; pickle.dump((RB,RK),open('/home/claude/unread-lab/redteam3/res%s.pkl'%('' if PREFIX else '_np'),'wb'))
