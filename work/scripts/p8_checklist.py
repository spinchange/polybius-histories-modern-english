"""Phase 8 per-book checklist (deterministic parts). Reports only."""
import re,glob,collections
rep=collections.defaultdict(list)
for f in sorted(glob.glob('Polybius_Histories_Book_[0-9][0-9]_modern_English.md')):
    b=f.split('_')[3]; ch='front'
    para_start=True
    for i,l in enumerate(open(f,encoding='utf-8'),1):
        s=l.rstrip('\n')
        if s.startswith('## '):
            ch=s[3:].split(':')[0]
            if not re.match(r'## Book \d+ Chapter \w+: \S',s): rep['untitled-heading'].append(f'B{b} L{i}: {s}')
            continue
        if s.startswith('#') or not s.strip(): continue
        t=s.lstrip('*_"“‘\'( ')
        if t and t[0].islower(): rep['lowercase-start'].append(f'B{b} {ch} L{i}: {s[:80]}')
        if re.search(r'\[[^\]]*\]\s*\[[^\]]*\]',s): rep['adjacent-brackets'].append(f'B{b} {ch} L{i}: {s[:80]}')
        for m in re.finditer(r'\[([^\]]*)\]',s):
            if m.group(1)!='...' and re.search(r'text|missing|lacuna|break|gap|fragment',m.group(1),re.I):
                rep['nonstandard-lacuna'].append(f'B{b} {ch} L{i}: [{m.group(1)}]')
        if re.search(r'\*\*\*|…|(?<!\.)\.\.\.(?!\.)',s): rep['stray-ellipsis'].append(f'B{b} {ch} L{i}: {s[:80]}')
        if s.count('“')!=s.count('”'): rep['curly-quote-unbalanced'].append(f'B{b} {ch} L{i}')
        if s.count('(')!=s.count(')'): rep['paren-unbalanced'].append(f'B{b} {ch} L{i}: {s[:80]}')
        if re.search(r'\s{2,}\S',s) and not s.startswith('    '): rep['double-space'].append(f'B{b} {ch} L{i}')
        if re.search(r'ï¿½|�|Ã',s): rep['mojibake'].append(f'B{b} {ch} L{i}')
        if re.search(r'[Ͱ-Ͽἀ-῿]',s): rep['greek-in-english'].append(f'B{b} {ch} L{i}: {s[:60]}')
with open('work/reports/p8_checklist.txt','w',encoding='utf-8') as o:
    for k,v in rep.items():
        o.write(f'\n== {k}: {len(v)}\n'+'\n'.join('  '+x for x in v[:60])+'\n')
print({k:len(v) for k,v in rep.items()})
