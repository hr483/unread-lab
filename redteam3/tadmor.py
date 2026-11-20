import run
from run import *
TAD=set(r['CONCEPTICON_ID'] for r in csv.DictReader(open(D+'conceptlists/Tadmor-2009-100.tsv'),delimiter='\t'))
P={r['Concepticon_ID']:r['Concepticon_Gloss'] for r in csv.DictReader(open(D+'sagartst/cldf/parameters.csv'))}
print('Holman&Tadmor overlap in CSN', len(TAD&HOL&set(CSN)), 'Tadmor in CSN',len(TAD&set(CSN)),'in CSB',len(TAD&set(CSB)))
print('Holman in CSN not Tadmor:',sorted(P[c] for c in (HOL-TAD)&set(CSN)))
run.HOL=TAD
for lab,langs,reff,cids in [('INH',POS,lambda l:[r for r in DIST if SUB[r]!=SUB[l]],CSB),('KB',KB,lambda l:DIST,CSB),('BOR',['jpn','kor'],lambda l:SIN,CSN),('KOR-DIST',['kor'],lambda l:DIST,CSN)]:
    res=[analyse(l,reff(l),cids) for l in langs]
    print(lab,'Tadmor-tier pooled I %+.3f [%+.3f,%+.3f]'%run.pooled(res,cids,nb=1000), [round(run.I_of(r)[0],3) for r in res])
