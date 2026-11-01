"""Apply confirmed Phase 4 fixes. ACCEPT/REVISE -> edit book files; HUMAN -> report only; REJECT -> ignore.
Usage: python phase4_apply.py [--dry-run]"""
import json, glob, os, re, sys, io, csv, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); os.chdir(ROOT)
dry = '--dry-run' in sys.argv

agg = {x['id']: x for x in json.load(open('work/phase4/aggregate.json', encoding='utf-8'))}
verd = {}
for f in sorted(glob.glob('work/phase4/confirm_out/*.json')):
    for v in json.load(open(f, encoding='utf-8')):
        verd[v['id']] = dict(v, src=os.path.basename(f))
counts = collections.Counter(v['verdict'] for v in verd.values())
print('verdicts', dict(counts), 'of', len(verd), 'ids; aggregate has', len(agg))

applied = []; skipped = []; human = []
by_book = collections.defaultdict(list)
for i, v in verd.items():
    x = agg.get(i)
    if not x: skipped.append((i, 'unknown id')); continue
    if v['verdict'] == 'HUMAN': human.append((x, v)); continue
    if v['verdict'] in ('ACCEPT', 'REVISE'):
        fix = v.get('fix', '')
        if not fix.strip(): skipped.append((i, 'empty fix')); continue
        by_book[int(x['book'])].append((x, v))

def chapter_span(s, c):
    for m in re.finditer(r'^## Book \d+ Chapter (\S+?):.*$', s, flags=re.M):
        if m.group(1) == str(c):
            nxt = re.search(r'^## ', s[m.end():], flags=re.M)
            return m.end(), (m.end() + nxt.start() if nxt else len(s))
    return None

for b, items in sorted(by_book.items()):
    f = f'Polybius_Histories_Book_{b:02d}_modern_English.md'
    raw = open(f, encoding='utf-8', newline='').read()
    crlf = '\r\n' in raw; s = raw.replace('\r\n', '\n')
    for x, v in sorted(items, key=lambda t: t[0]['id']):
        sp = chapter_span(s, x['chapter'])
        if not sp: skipped.append((x['id'], 'chapter not found')); continue
        a, z = sp; region = s[a:z]; q = x['quote']
        if region.count(q) != 1: skipped.append((x['id'], f'quote matches {region.count(q)}x (conflict)')); continue
        s = s[:a] + region.replace(q, v['fix'], 1) + s[z:]
        applied.append(dict(id=x['id'], book=b, chapter=x['chapter'], verdict=v['verdict'], old=q, new=v['fix']))
    if not dry:
        out = s.replace('\n', '\r\n') if crlf else s
        open(f, 'w', encoding='utf-8', newline='').write(out)

os.makedirs('work/reports', exist_ok=True)
with open('work/reports/phase4_applied.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['id', 'book', 'chapter', 'verdict', 'old', 'new']); w.writeheader(); w.writerows(applied)
with open('work/reports/phase4_human.md', 'w', encoding='utf-8') as fh:
    fh.write('# Phase 4 — items needing the translator/editor (NOT applied)\n\n')
    for x, v in sorted(human, key=lambda t: (int(t[0]['book']), t[0]['chapter'])):
        fh.write(f"## {x['book']}.{x['chapter']} ({x['id']})\n- current: {x['quote']}\n- problem: {x['problem']}\n- proposed: {v.get('fix','')}\n- reason: {v.get('reason','')}\n\n")
with open('work/reports/phase4_unapplied.txt', 'w', encoding='utf-8') as fh:
    for i, why in skipped: fh.write(f'{i}\t{why}\n')
print('applied', len(applied), 'human', len(human), 'skipped', len(skipped), '(dry-run)' if dry else '')
for i, why in skipped[:20]: print('  skip', i, why)
