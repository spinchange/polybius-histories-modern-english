import re,glob,csv
ROME=re.compile(r'\b(Rome|Roman|Romans|consuls?|praetors?|Scipio|Flaminin\w*|Paullus|Titus|Lentulus)\b')
FOREIGN=re.compile(r'\b(Carthagin\w*|Rhod\w*|Achae\w*|Aetol\w*|Syracus\w*|Boeot\w*|Messen\w*|Locri\w*|Cret\w*|Macedon\w*|Spartan\w*|Lacedaemon\w*|Thebes|Theban\w*|Athen\w*|Argive|Epirot\w*|Egypt\w*|Alexandria\w*|Tarentin\w*|Capua\w*|Cartha\w*)\b')
log=[];review=[]
for f in sorted(glob.glob('Polybius_Histories_Book_[0-9][0-9]_modern_English.md')):
    lines=open(f,encoding='utf-8',newline='').read().split('\n')
    ch='';chg=False
    for i,l in enumerate(lines):
        if l.startswith('#'):
            ch=l.split(':')[0].lstrip('# ');continue
        n=l
        n=re.sub(r'(?<=[a-z,] )Strategus\b','strategus',n)
        n=re.sub(r'(?<=[a-z,] )Strategi\b','strategi',n)
        if re.search(r'\bsenate\b',n):
            if ROME.search(n) and not FOREIGN.search(n):
                n=re.sub(r'\bsenate\b','Senate',n)
            elif re.search(r'\bthe Roman senate\b',n) or ch.startswith('Book 6 ') and not FOREIGN.search(n):
                n=re.sub(r'\bsenate\b','Senate',n)
            else:
                review.append((f[-24:-20],ch,i+1,l.strip()[:230]))
        if n!=l:
            log.append((f.split('_')[3],ch,i+1)); lines[i]=n; chg=True
    if chg: open(f,'w',encoding='utf-8',newline='').write('\n'.join(lines))
csv.writer(open('work/reports/p7_conformance_applied.csv','w',newline='')).writerows([('book','chapter','line')]+log)
with open('work/reports/p7_senate_review.md','w',encoding='utf-8') as o:
    o.write('# Lowercase "senate" left for review (context unclear or non-Roman)\n\n')
    for b,c,n,t in review: o.write(f'- B{b} {c} L{n}: {t}\n')
print(len(log),'lines changed;',len(review),'senate left for review')
