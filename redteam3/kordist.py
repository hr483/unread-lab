from run import *
P={r['Concepticon_ID']:r['Concepticon_Gloss'] for r in csv.DictReader(open(D+'sagartst/cldf/parameters.csv'))}
NEG=['fin','hun','ekk','tam','tel','kan','mal','eus','kat','arb','heb','tur','lit','gle']
for l in NEG: ALL[l]=N[l]
D11=[x for x in DIST if x!='OldChinese']
for l in ['kor','jpn']:
    r=analyse(l,D11,CSN); I=I_of(r)
    print(l,'vs DISTANT-OC: ratio %.2f p %.4f I %+.3f'%(r['obs']/r['nullmean'],r['p'],I[0]))
    if l=='kor':
        for j,c in enumerate(r['cc']):
            if r['m'][j]>0:
                hits=[x for x in D11 if c in r['rt'][x] and r['rt'][x][c][0]==r['t'][c][0]]
                print('  %s %-16s %-10s %s m=%d E=%.2f :: %s'%('S' if c in HOL else 'O',P[c],r['t'][c][1],r['t'][c][0],r['m'][j],r['E'][j],'; '.join(x+':'+r['rt'][x][c][1] for x in hits)))
print('--- 14 negatives vs DISTANT12, 198 concepts (sagartst x northeuralex)')
out=[]
for l in NEG:
    r=analyse(l,DIST,CSN); I=I_of(r)[0]; out.append((l,r['obs']/r['nullmean'],r['p'],I))
    print('%s ratio %.2f p %.4f I %+.3f'%out[-1])
