import pickle,sys
from run import *
RB,RK=pickle.load(open('res.pkl','rb'))
G={r['CONCEPTICON_ID']:r['CONCEPTICON_GLOSS'] for r in csv.DictReader(open(D+'conceptlists/Holman-2008-40.tsv'),delimiter='\t')}
P={r['Concepticon_ID']:r['Concepticon_Gloss'] for r in csv.DictReader(open(D+'sagartst/cldf/parameters.csv'))}
for lang,r in zip(['jpn','kor'],RB):
    print('=====',lang)
    e=r['m']-r['E']
    for j,c in enumerate(r['cc']):
        if r['m'][j]>0:
            hits=[x for x in SIN if c in r['rt'][x] and r['rt'][x][c][0]==r['t'][c][0]]
            print(f"{'S' if c in HOL else 'O'} {P[c]:14s} {r['t'][c][1]:12s} [{r['t'][c][2]}] {r['t'][c][0]} m={r['m'][j]:.0f} E={r['E'][j]:.2f} e={e[j]:+.2f} :: "+'; '.join(f"{x}:{r['rt'][x][c][1]}" for x in hits))
