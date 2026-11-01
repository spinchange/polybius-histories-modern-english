"""Phase 8 coverage check: every Greek chapter in source/ has a heading in the right
book file, in order, with no extras. No paragraph-count parity."""
import re,glob,sys,os
BASE=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H=re.compile(r'^## Book (\d+) Chapter (\w+)')
bad=0;tot=0
for d in sorted(glob.glob(os.path.join(BASE,'source','book_[0-9][0-9]'))):
    b=int(d[-2:])
    src=[re.match(r'chapter_(\w+)\.md',os.path.basename(p)).group(1) for p in sorted(glob.glob(d+'/chapter_*.md'),key=lambda p:(int(re.search(r'chapter_(\d+)',p).group(1)),p))]
    f=os.path.join(BASE,f'Polybius_Histories_Book_{b:02d}_modern_English.md')
    heads=[]
    for l in open(f,encoding='utf-8'):
        m=H.match(l)
        if m:
            if int(m.group(1))!=b: print(f'B{b}: heading for wrong book: {l.strip()}');bad+=1
            heads.append(m.group(2))
    norm=lambda x:[s.lstrip('0') or '0' for s in x]
    s,h=norm(src),norm(heads)
    tot+=len(s)
    if not src:
        print(f'B{b}: no source chapters (note only); English headings={len(h)}'); continue
    ms=[c for c in s if c not in h]; ex=[c for c in h if c not in s]
    if ms or ex: print(f'B{b}: missing={ms} extra={ex}');bad+=1
    common=[c for c in h if c in s]
    if common!=[c for c in s if c in h]: print(f'B{b}: order mismatch');bad+=1
    if len(set(h))!=len(h): print(f'B{b}: duplicate headings');bad+=1
print(f'{tot} source chapters checked; {bad} problem(s)')
sys.exit(1 if bad else 0)
