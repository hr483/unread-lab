import pickle
from run import *
RB,RK=pickle.load(open('res.pkl','rb'))
P={r['Concepticon_ID']:r['Concepticon_Gloss'] for r in csv.DictReader(open(D+'sagartst/cldf/parameters.csv'))}
inv={v:k for k,v in P.items()}
LOAN={'jpn':['LIVER','SUN','TWO','TODAY','SIX','THREE','MEAT'],
      'kor':['LIVER','MOUNTAIN','MIDDLE','SHEEP','HUNDRED','SOFT','SMOKE (EXHAUST)','THINK (REFLECT)']}
CHP=['I','THOU','WE','MOTHER','FATHER']
NUM=['ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN','EIGHT','NINE','TEN','HUNDRED']
def Iex(r,drop):
    e=r['m']-r['E']; cc=r['cc']
    k=np.array([P[c] not in drop for c in cc]); st=np.array([c in HOL for c in cc])
    a=e[k&st]; b=e[k&~st]
    rng=np.random.default_rng(20261120); bs=[]
    for _ in range(2000):
        bs.append(rng.choice(a,len(a)).mean()-rng.choice(b,len(b)).mean())
    return a.mean()-b.mean(), np.percentile(bs,5), np.percentile(bs,95), len(a), len(b)
for lang,r in zip(['jpn','kor'],RB):
    e=r['m']-r['E']; cc=r['cc']
    for tier in ['S','O']:
        sel=[j for j,c in enumerate(cc) if (c in HOL)==(tier=='S')]
        L=sum(e[j] for j in sel if P[cc[j]] in LOAN[lang] and r['m'][j]>0)
        C=sum(e[j] for j in sel if P[cc[j]] in CHP and r['m'][j]>0)
        N=sum(e[j] for j in sel if P[cc[j]] not in LOAN[lang]+CHP and r['m'][j]>0)
        Z=sum(e[j] for j in sel if r['m'][j]==0)
        mL=sum(r['m'][j] for j in sel if P[cc[j]] in LOAN[lang]); mC=sum(r['m'][j] for j in sel if P[cc[j]] in CHP); mN=sum(r['m'][j] for j in sel if P[cc[j]] not in LOAN[lang]+CHP)
        print(lang,tier,'n=%d'%len(sel),'excess: loan %+.2f (m=%d) chanceprone %+.2f (m=%d) native-other %+.2f (m=%d) nonmatch %+.2f | mean e %+.3f'%(L,mL,C,mC,N,mN,Z,e[sel].mean()))
    for name,drop in [('all',[]),('-loans',LOAN[lang]),('-pron/nursery',CHP),('-numerals',NUM),('-loans-pron',LOAN[lang]+CHP),('-native(keep loans only)',None)]:
        if drop is None:
            drop=[P[c] for j,c in enumerate(cc) if r['m'][j]>0 and P[c] not in LOAN[lang]]
        print('   I %-26s %+.3f  90%%CI [%+.3f,%+.3f] nS=%d nO=%d'%((name,)+Iex(r,drop)))
    # group p after dropping loans
    keep=[c for c in r['cc'] if P[c] not in LOAN[lang]]
    rr=analyse(lang,SIN,keep); print('   overall after dropping loan concepts: obs=%d null=%.2f ratio=%.2f p=%.4f'%(rr['obs'],rr['nullmean'],rr['obs']/rr['nullmean'],rr['p']))
    # OC vs modern
    oc=sum(1 for c in r['cc'] if c in r['rt']['OldChinese'] and r['rt']['OldChinese'][c][0]==r['t'][c][0] and r['t'][c][0])
    print('   matches with OldChinese:',oc,' with 6 modern Sinitic:',int(r['obs'])-oc)
