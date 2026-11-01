import re,glob,sys,collections
pats={
 'Consul-cap':r'\b(?<![.!?]\s)(?<!^)Consuls?\b(?! [A-Z][a-z]+ [A-Z])',
 'Praetor/Tribune/Censor/Dictator-cap':r'(?<![.!?"“]\s)\b(Praetors?|Tribunes?|Censors?|Dictators?)\b',
 'Strategus':r'\b[Ss]trateg(us|i|os|oi)\b',
 'senate-lower':r'\bsenate\b',
 'Senate-cap':r'\bSenate\b',
 'Celt':r'\bCelt(s|ic)?\b',
 'Lacedaemon':r'\bLacedaemonian',
 'feet':r'\b(feet|foot)\b',
}
out=collections.defaultdict(list)
for f in sorted(glob.glob('Polybius_Histories_Book_[0-9][0-9]_modern_English.md')):
    b=f.split('_')[3]; ch=''
    for i,l in enumerate(open(f,encoding='utf-8'),1):
        if l.startswith('## '): ch=l.split(':')[0][3:]; 
        if l.startswith('#'): continue
        for k,p in pats.items():
            for m in re.finditer(p,l):
                out[k].append((f'B{b} {ch} L{i}',l[max(0,m.start()-40):m.end()+40].strip()))
for k,v in out.items():
    print(f'\n== {k}: {len(v)}')
    if len(sys.argv)>1 and k in sys.argv[1:] or len(v)<=25:
        for a,c in v: print(' ',a,'|',c)
