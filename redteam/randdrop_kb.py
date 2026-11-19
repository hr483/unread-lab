import sys; sys.path.insert(0,'/home/claude/unread-lab/redteam')
import numpy as np
from ccm import *
from run import C76, KB, kb, st, nl
A={}
for d in (st,kb,nl): A.update(build_codes(d,C76,'first'))
rng=np.random.default_rng(1); hits=[]
for l in KB:
    t=A[l]; nd=len({c for c in t for k in CONTACT if c in A[k] and A[k][c]==t[c]}); keys=list(t); pv=[]
    for d in range(50):
        drop=set(rng.choice(keys,nd,replace=False))
        pv.append(ccm_test({c:v for c,v in t.items() if c not in drop},[A[r] for r in DISTANT],C76,seed=d)['p'])
    pv=np.array(pv); print(l,nd,'median p %.4f'%np.median(pv),'frac p<=0.01/22: %.2f'%np.mean(pv<0.01/22))
