"""Build per-book Phase 6 work files in work/phase6/book_NN.md (read-only on the book files)."""
import re, glob, csv, collections, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ROOT)
os.makedirs('work/phase6', exist_ok=True)

seams = collections.defaultdict(list)
for r in csv.DictReader(open('work/reports/seam_report.csv', encoding='utf-8')):
    seams[r['book']].append(r)
qb = collections.defaultdict(list)
cur = None
for l in open('work/reports/quote_balance.txt', encoding='utf-8'):
    m = re.match(r'## Polybius_Histories_Book_(\d\d)_', l)
    if m: cur = m.group(1); continue
    if cur and l.strip().startswith('L'): qb[cur].append(l.rstrip())

AUTH = {'Athenaeus': r'Athen(a|ae)us|Ἀθήναι', 'Strabo': r'Strabo|Στράβων', 'Plutarch': r'Plutarch|Πλούταρχ',
        'Stephanus of Byzantium': r'Stephan(us|os)|Στέφανος', 'Suidas': r'Suid(as|a)|Σουίδας',
        'Josephus': r'Josephus', 'Pliny': r'Pliny', 'Diodorus': r'Diodor'}
ETH = re.compile(r'\b(Celt\w*|Gaul\w*|Gallic|Galatian\w*|Lacedaemonian\w*|Spartan\w*)\b')
RUBRIC = re.compile(r'^(?:[IVXL]+\.\s|\*{3,}|\[?\d+;\d+\])')
ELL = re.compile(r'[\]\w”’]\.\.\.|…')
SAYS = re.compile(r'\b(Polybius (says|writes|states|tells|remarks|relates|reports|declares|asserts|calls)|according to Polybius|says Polybius|writes Polybius)', re.I)

def chapters(text):
    out = []; cur = None
    for i, l in enumerate(text.split('\n'), 1):
        if l.startswith('## '):
            cur = [l, i, []]; out.append(cur)
        elif cur is not None: cur[2].append((i, l))
    return out

for f in sorted(glob.glob('Polybius_Histories_Book_[0-9][0-9]_modern_English.md')):
    bk = f.split('_')[3]; bn = int(bk)
    text = open(f, encoding='utf-8').read()
    chs = chapters(text)
    o = [f'# Phase 6 work file — Book {bn}\n',
         'Line numbers are a snapshot; locate by quoted context (Grep), not by number, after you start editing.\n']
    o.append(f'\n## A. Seams (seam_report.csv, {len(seams[bk])} rows)\n')
    for r in seams[bk]: o.append(f"- L{r['line']} [{r['category']}] {r['detail']} :: {r['context'][:110]}")
    o.append(f'\n## B. Unbalanced curly quotes (judge: multi-paragraph speeches are legitimate)\n')
    o += [f'- {x}' for x in qb[bk]] or ['- none']
    o.append('\n## C. Attached ellipses / stray rubrics / bracket markers\n')
    n = 0
    for h, ln, body in chs:
        for i, l in body:
            if ELL.search(l) or RUBRIC.match(l.strip()):
                o.append(f'- L{i} (under {h[3:60]}): {l.strip()[:120]}'); n += 1
    if not n: o.append('- none')
    o.append('\n## D. Testimonia evidence (attribute ONLY where explicit; else ESCALATE)\n')
    if bn >= 7:
        n = 0
        for h, ln, body in chs:
            m = re.match(r'## Book \d+ Chapter (\S+?):', h)
            if not m: continue
            ch = m.group(1)
            src = f'source/book_{bk}/chapter_{ch.zfill(2) if ch.isdigit() else ch}.md'
            ev = []
            if os.path.exists(src):
                s = open(src, encoding='utf-8').read()
                for a, p in AUTH.items():
                    mm = re.search(p, s)
                    if mm: ev.append(f'{a}: …{s[max(0,mm.start()-60):mm.end()+60].replace(chr(10)," ")}…')
            says = any(SAYS.search(l) for _, l in body)
            if ev or says or bn == 34:
                n += 1
                o.append(f'- Ch {ch} | english-says-pattern={says} | src={src if os.path.exists(src) else "MISSING"}')
                for e in ev: o.append(f'    - evidence {e}')
        if not n: o.append('- none')
    else: o.append('- (Books 1–6 are continuous narrative; none)')
    o.append('\n## E. Ethnonym occurrences (Celt/Gaul/Galatian, Lacedaemonian/Spartan)\n')
    for h, ln, body in chs:
        hits = [(i, l) for i, l in body if ETH.search(l)]
        if hits:
            o.append(f'### {h[3:70]}')
            for i, l in hits:
                words = ', '.join(sorted({m.group(0) for m in ETH.finditer(l)}))
                o.append(f'- L{i}: {words} :: {ETH.sub(lambda m: "«"+m.group(0)+"»", l.strip())[:230]}')
    open(f'work/phase6/book_{bk}.md', 'w', encoding='utf-8').write('\n'.join(o) + '\n')
    print(bk, len(o))
