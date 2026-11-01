import re
targets={}
for l in open('work/reports/p7_senate_review.md',encoding='utf-8'):
    m=re.match(r'- Book_ Book (\d+) Chapter (\d+) L(\d+): ',l)
    if not m: continue
    b,c,n=map(int,m.groups())
    if b>=21 or (b,n) in {(1,177),(6,1007),(15,97),(15,187)}:
        targets.setdefault(b,set()).add(n)
total=0;keep=[]
for b,ns in targets.items():
    f=f'Polybius_Histories_Book_{b:02d}_modern_English.md'
    lines=open(f,encoding='utf-8',newline='').read().split('\n')
    for n in ns:
        new=re.sub(r'\bsenate\b','Senate',lines[n-1])
        assert new!=lines[n-1],(b,n)
        lines[n-1]=new;total+=1
    open(f,'w',encoding='utf-8',newline='').write('\n'.join(lines))
print(total,'lines')
