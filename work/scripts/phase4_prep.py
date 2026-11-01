"""Build Phase 4 verification batches: work/phase4/batches/{opus,sonnet}_NNN.md
Each chapter: Greek (from source/, crib excluded) + current English. Run AFTER step-1 fixes."""
import re, glob, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); os.chdir(ROOT)
out = 'work/phase4/batches'; os.makedirs(out, exist_ok=True); os.makedirs('work/phase4/findings', exist_ok=True)
for f in glob.glob(out + '/*.md'): os.remove(f)

def num(c):
    m = re.match(r'\d+', c); return int(m.group()) if m else -1
OPUS = {1: [(1,4),(62,64)], 3: [(6,12),(47,56),(107,118)], 6: [(0,999)], 9: [(22,26)], 10: [(2,20)],
        12: [(25,28)], 15: [(6,19)], 18: [(28,32)], 31: [(23,30)], 36: [(9,17)], 38: [(0,999)], 39: [(0,999)]}
SKIP = {(37,'1'),(38,'2'),(39,'2'),(39,'3')}  # Phase 3 fresh retranslations; 39.3 uncertain readings go to opus below
EXTRA_OPUS = {(39,'3'),(39,'2'),(38,'2'),(37,'1')}

def is_opus(b, c):
    if (b, c) in EXTRA_OPUS: return True
    return any(lo <= num(c) <= hi for lo, hi in OPUS.get(b, []))

def greek(b, c):
    for name in (c.zfill(2) if c.isdigit() else c, c, c.zfill(3) if c.isdigit() else c):
        p = f'source/book_{b:02d}/chapter_{name}.md'
        if os.path.exists(p):
            s = open(p, encoding='utf-8').read()
            i = s.find('## Greek'); j = s.find('## English Reference')
            g = s[i + 8:j if j > 0 else None].strip()
            return g
    return None

units = []
for f in sorted(glob.glob('Polybius_Histories_Book_[0-9][0-9]_modern_English.md')):
    b = int(f.split('_')[3]); s = open(f, encoding='utf-8').read().replace('\r\n', '\n')
    for blk in re.split(r'^(?=## Book \d+ Chapter )', s, flags=re.M)[1:]:
        h, _, body = blk.partition('\n')
        m = re.match(r'## Book \d+ Chapter (\S+?):', h)
        if not m: continue
        c = m.group(1); g = greek(b, c)
        units.append(dict(book=b, ch=c, heading=h, eng=body.strip(), greek=g, opus=is_opus(b, c)))

def write_batches(tier, items, budget, maxn):
    n = 0; cur = []; size = 0; k = 0; manifest = []
    def flush():
        nonlocal cur, size, k
        if not cur: return
        k += 1; bid = f'{tier}_{k:03d}'
        t = [f'# Batch {bid}\n']
        for u in cur:
            t.append(f"\n## UNIT Book {u['book']} Chapter {u['ch']}\n{u['heading']}\n\n### Greek\n{u['greek'] or '(NO GREEK SOURCE FILE)'}\n\n### English (current)\n{u['eng']}\n")
        open(f'{out}/{bid}.md', 'w', encoding='utf-8').write(''.join(t))
        manifest.append(dict(id=bid, units=[f"{u['book']}.{u['ch']}" for u in cur], chars=size)); cur = []; size = 0
    prev = None
    for u in items:
        sz = len(u['greek'] or '') + len(u['eng'])
        if cur and (u['book'] != prev or size + sz > budget or len(cur) >= maxn): flush()
        cur.append(u); size += sz; prev = u['book']
    flush(); return manifest

opus_items = [u for u in units if u['opus']]
son_items = [u for u in units if not u['opus']]
mo = write_batches('opus', opus_items, 22000, 8)
ms = write_batches('sonnet', son_items, 30000, 12)
json.dump(dict(opus=mo, sonnet=ms), open('work/phase4/manifest.json', 'w'), indent=1)
print('opus chapters', len(opus_items), 'batches', len(mo)); print('sonnet chapters', len(son_items), 'batches', len(ms))
print('no greek:', [f"{u['book']}.{u['ch']}" for u in units if not u['greek']][:40])
print('total chars opus', sum(m['chars'] for m in mo), 'sonnet', sum(m['chars'] for m in ms))
