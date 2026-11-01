"""Build verification batches for proposed seam moves, and apply verified ones.
  python p4b_seam_apply.py --batches   -> work/phase4b/seam_in/s_NN.md (for a model sanity check)
  python p4b_seam_apply.py --apply [--dry-run] -> applies work/phase4b/seam_verdicts.json (OK / FIX) and logs moves"""
import re, json, os, sys, io, csv, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); os.chdir(ROOT)
props = json.load(open('work/phase4b/seams.json', encoding='utf-8'))
def key(p): return f"{p['book']}:{p['ch1']}>{p['ch2']}"
def joined(p):
    partial = re.sub(r'\s*\[\.\.\.\]\s*$', '', p['partial']).rstrip()
    rest = re.sub(r'^\[\.\.\.\]\s*', '', p['head_para'].lstrip())
    sep = '' if (partial.endswith('-') or rest.startswith('-')) else ' '
    return (partial.rstrip('-') if partial.endswith('-') and rest.startswith('-') else partial) + sep + rest.lstrip('-') if False else partial + sep + rest
def new_tail(p):
    last = p['tail_para']; core = re.sub(r'\s*\[\.\.\.\]\s*$', '', last).rstrip()
    if p['whole_para']: return None
    return core[:len(core) - len(p['partial'])].rstrip()
if '--batches' in sys.argv:
    os.makedirs('work/phase4b/seam_in', exist_ok=True)
    for f in glob.glob('work/phase4b/seam_in/*.md'): os.remove(f)
    per = 18
    for k in range(0, len(props), per):
        o = [f'# Seam batch s_{k//per+1:02d}\n']
        for p in props[k:k+per]:
            nt = new_tail(p)
            o.append(f"\n## SEAM {key(p)}\n- BEFORE end of ch {p['ch1']}: …{p['tail_para'][-260:]}\n- BEFORE start of ch {p['ch2']}: {p['head_para'][:260]}…\n"
                     f"- MOVED text (the unfinished sentence): {p['partial']}\n- AFTER start of ch {p['ch2']}: {joined(p)[:420]}…\n"
                     f"- AFTER end of ch {p['ch1']}: …{(nt if nt is not None else '(paragraph removed; ch ends at the previous paragraph)')[-200:]}\n")
        open(f'work/phase4b/seam_in/s_{k//per+1:02d}.md', 'w', encoding='utf-8').write(''.join(o))
    print('batches', (len(props) + per - 1) // per)
if '--apply' in sys.argv:
    dry = '--dry-run' in sys.argv
    verd = {}
    for f in glob.glob('work/phase4b/seam_out/*.json'):
        for v in json.load(open(f, encoding='utf-8')): verd[v['key']] = v
    byfile = {}
    for p in props: byfile.setdefault(p['book'], []).append(p)
    log = []; skipped = []
    for bk, ps in sorted(byfile.items()):
        fn = f'Polybius_Histories_Book_{bk:02d}_modern_English.md'
        raw = open(fn, encoding='utf-8', newline='').read(); crlf = '\r\n' in raw; s = raw.replace('\r\n', '\n')
        for p in ps:
            v = verd.get(key(p))
            if not v or v['verdict'] not in ('OK', 'FIX'): skipped.append((key(p), (v or {}).get('verdict', 'no verdict'), (v or {}).get('note', ''))); continue
            head_new = joined(p) if v['verdict'] == 'OK' else v['new_head_para']
            if s.count(p['tail_para']) != 1 or s.count(p['head_para']) != 1: skipped.append((key(p), 'text not unique/changed', '')); continue
            nt = new_tail(p)
            # replace head paragraph first (it comes later in the file), then tail
            s = s.replace(p['head_para'], head_new, 1)
            if nt is None:
                s = re.sub(r'\n*' + re.escape(p['tail_para']) + r'\n*(?=## Book)', '\n\n', s, count=1)
            else:
                s = s.replace(p['tail_para'], nt, 1)
            log.append(dict(key=key(p), moved=p['partial'], midword=p['midword'], verdict=v['verdict']))
        if not dry: open(fn, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
    with open('work/reports/p4b_seam_moves.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['key', 'moved', 'midword', 'verdict']); w.writeheader(); w.writerows(log)
    with open('work/reports/p4b_seam_skipped.txt', 'w', encoding='utf-8') as fh:
        for x in skipped: fh.write('\t'.join(map(str, x)) + '\n')
    print('moved', len(log), 'skipped', len(skipped), '(dry)' if dry else '')
