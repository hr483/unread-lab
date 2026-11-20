import logging; logging.disable(logging.CRITICAL)
import csv, sys, numpy as np
import lingpy
D='/home/claude/unread-lab/data/'
NONC=set('V 1 0 _ + -'.split())

def load(ds):
    params={r['ID']:r['Concepticon_ID'] for r in csv.DictReader(open(D+ds+'/cldf/parameters.csv'))}
    out={}  # lang -> cid -> list of (segments, value)
    for r in csv.DictReader(open(D+ds+'/cldf/forms.csv')):
        if r['Loan'].strip().lower()=='true': continue
        cid=params.get(r['Parameter_ID'])
        if not cid: continue
        segs=r['Segments'].split()
        if not segs: continue
        out.setdefault(r['Language_ID'],{}).setdefault(cid,[]).append((segs,r['Value']))
    return out

def classes(segs):
    return lingpy.tokens2class(segs,'dolgo')

def strip_prefix(segs, prefix=True):
    if not prefix or '+' not in segs: return segs
    i=segs.index('+'); first=segs[:i]; rest=segs[i+1:]
    fc=[c for c in classes(first) if c not in NONC] if first else []
    rc=[c for c in classes(rest) if c not in NONC] if rest else []
    if len(fc)<=1 and len(first)<=3 and rc: return rest
    return segs

def code(segs, prefix=True):
    s=strip_prefix(segs,prefix)
    s=[t for t in s if t!='+']
    cl=classes(s)
    cl=[c for c in cl if c not in ('1','0','_','+','-')]
    if not cl: return None
    out=[]
    if cl[0]=='V': out.append('H')
    for c in cl:
        if c!='V': out.append(c)
    out=out[:2]
    if len(out)==1: out.append('-')
    return tuple(out)

def table(data, lang, cids, prefix=True):
    d=data[lang]; t={}
    for c in cids:
        if c in d:
            t[c]=(code(d[c][0][0],prefix), d[c][0][1], ' '.join(d[c][0][0]))
    return t
