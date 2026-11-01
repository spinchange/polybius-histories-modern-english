"""Aggregate Phase 4 findings. Writes work/phase4/aggregate.json and confirm batches for Sonnet-tier findings."""
import json, glob, os, re, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); os.chdir(ROOT)

def chapter_text(b, c):
    f = f'Polybius_Histories_Book_{int(b):02d}_modern_English.md'
    s = open(f, encoding='utf-8').read().replace('\r\n', '\n')
    for blk in re.split(r'^(?=## Book \d+ Chapter )', s, flags=re.M)[1:]:
        h, _, body = blk.partition('\n')
        m = re.match(r'## Book \d+ Chapter (\S+?):', h)
        if m and m.group(1) == str(c): return body
    return None

def greek(b, c):
    c = str(c)
    for name in (c.zfill(2) if c.isdigit() else c, c, c.zfill(3) if c.isdigit() else c):
        p = f'source/book_{int(b):02d}/chapter_{name}.md'
        if os.path.exists(p):
            s = open(p, encoding='utf-8').read(); i = s.find('## Greek'); j = s.find('## English Reference')
            return s[i + 8:j if j > 0 else None].strip()
    return ''

flat = []; units = collections.Counter(); cache = {}
for f in sorted(glob.glob('work/phase4/findings/*.json')):
    bid = os.path.basename(f)[:-5]; tier = bid.split('_')[0]
    d = json.load(open(f, encoding='utf-8'))
    for u in d['units']:
        units[(tier, u['verdict'])] += 1
        for x in u.get('findings', []):
            b, c = u['book'], str(u['chapter'])
            key = (b, c)
            if key not in cache: cache[key] = chapter_text(b, c)
            txt = cache[key] or ''
            n = txt.count(x['quote'])
            flat.append(dict(batch=bid, tier=tier, book=b, chapter=c, unit_verdict=u['verdict'],
                             quote=x['quote'], problem=x['problem'], proposed_fix=x.get('proposed_fix', ''),
                             touches_syntax=bool(x.get('touches_syntax')), confidence=x.get('confidence', ''),
                             quote_matches=n))
for i, x in enumerate(flat): x['id'] = f'F{i:04d}'
json.dump(flat, open('work/phase4/aggregate.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('units', dict(units))
print('findings', len(flat))
print(collections.Counter((x['tier'], x['confidence']) for x in flat))
print('quote_matches!=1:', sum(1 for x in flat if x['quote_matches'] != 1))
print('empty proposed_fix:', sum(1 for x in flat if not x['proposed_fix'].strip()))

# confirm batches for Sonnet-tier findings (and any Opus-tier low-confidence/unmatched ones stay for human)
os.makedirs('work/phase4/confirm', exist_ok=True)
for fpath in glob.glob('work/phase4/confirm/*.md'): os.remove(fpath)
son = [x for x in flat if x['quote_matches'] == 1 and x['proposed_fix'].strip() and ((x['tier'] == 'sonnet' and (x['confidence'] in ('high', 'medium') or x['touches_syntax'])) or (x['tier'] == 'opus' and x['confidence'] in ('high', 'medium')))]
by_ch = collections.OrderedDict()
for x in son: by_ch.setdefault((x['book'], x['chapter']), []).append(x)
batches = []; cur = []; size = 0; prevb = None
for (b, c), xs in by_ch.items():
    g = greek(b, c); e = cache[(b, c)] or ''
    sz = len(g) + len(e)
    if cur and (b != prevb or size + sz > 40000 or len(cur) >= 14): batches.append(cur); cur = []; size = 0
    cur.append(((b, c), g, e, xs)); size += sz; prevb = b
if cur: batches.append(cur)
for k, bt in enumerate(batches, 1):
    t = [f'# Confirm batch confirm_{k:03d}\n']
    for (b, c), g, e, xs in bt:
        t.append(f'\n## UNIT Book {b} Chapter {c}\n\n### Greek\n{g}\n\n### English (current)\n{e}\n\n### Candidate findings (from a Sonnet pass; may be wrong)\n')
        for x in xs:
            t.append(f"- **{x['id']}** [{x['confidence']}, syntax={x['touches_syntax']}]\n  - quote: {x['quote']}\n  - problem: {x['problem']}\n  - proposed_fix: {x['proposed_fix']}\n")
    open(f'work/phase4/confirm/confirm_{k:03d}.md', 'w', encoding='utf-8').write(''.join(t))
print('confirm batches', len(batches), 'sonnet findings in them', len(son))
