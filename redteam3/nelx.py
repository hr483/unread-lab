import run
from run import *
TAD=set(r['CONCEPTICON_ID'] for r in csv.DictReader(open(D+'conceptlists/Tadmor-2009-100.tsv'),delimiter='\t'))
HO=set(run.HOL)
for l in N: ALL[l]=N[l]
run.NP=2000
pairs=[('jpn',['cmn']),('kor',['cmn']),('kpv',['rus']),('udm',['rus']),('tat',['rus']),('pes',['arb']),('tur',['arb']),('hin',['pes']),('fin',['hun']),('eng',['deu']),('rus',['pol']),('tur',['uzn'])]
for l,refs in pairs:
    cids=sorted(set(N[l])&set(N[refs[0]]))
    for nm,T in [('Holman',HO),('Tadmor',TAD)]:
        run.HOL=T
        r=analyse(l,refs,cids); I,ns,no=I_of(r)
        print(f"{l}-{refs[0]} {nm:6s} n={len(cids)} nS={ns} ratio={r['obs']/r['nullmean']:.2f} p={r['p']:.4f} I={I:+.3f}")
