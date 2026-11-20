import pickle
from run import *
P={r['Concepticon_ID']:r['Concepticon_Gloss'] for r in csv.DictReader(open(D+'sagartst/cldf/parameters.csv'))}
DROP={'I','THOU','WE','YOU','MOTHER','FATHER'}
def grp(langs,reff,cids,drop):
    cids=[c for c in cids if P[c] not in drop]
    res=[analyse(l,reff(l),cids) for l in langs]
    return pooled(res,cids,nb=1000), [round(I_of(r)[0],3) for r in res]
for drop,lab in [(set(),'all'),(DROP,'-pron/kin')]:
    print(lab,'INH',grp(POS,lambda l:[r for r in DIST if SUB[r]!=SUB[l]],CSB,drop))
    print(lab,'KB ',grp(KB,lambda l:DIST,CSB,drop))
    print(lab,'BOR',grp(['jpn','kor'],lambda l:SIN,CSN,drop))
