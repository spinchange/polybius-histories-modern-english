"""Find chapter breaks that cut a sentence and propose moving the unfinished sentence under the next heading.
Detect: chapter N's final paragraph is unterminated (or ends with ' [...]') AND chapter N+1's first paragraph
continues it (starts, after an optional '[...] ', with a lowercase letter / punctuation / '-').
Usage: python p4b_seams.py            -> writes work/phase4b/seams.json (proposals; no book edits)
       python p4b_seams.py --apply    -> applies proposals marked ok in work/phase4b/seam_verdicts.json"""
import re, glob, json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); os.chdir(ROOT)
TERM = '.!?:;”’")]'
def split_chapters(s):
    parts = re.split(r'^(?=## Book \d+ Chapter )', s, flags=re.M)
    return parts[0], parts[1:]
def paras(body):
    return [p for p in re.split(r'\n\s*\n', body.strip('\n')) if p.strip()]
props = []
for f in sorted(glob.glob('Polybius_Histories_Book_[0-9][0-9]_modern_English.md')):
    bk = int(f.split('_')[3])
    s = open(f, encoding='utf-8', newline='').read().replace('\r\n', '\n')
    pre, chs = split_chapters(s)
    info = []
    for blk in chs:
        h, _, body = blk.partition('\n'); m = re.match(r'## Book \d+ Chapter (\S+?):', h)
        info.append((m.group(1) if m else '?', h, paras(body)))
    for i in range(len(info) - 1):
        c1, h1, p1 = info[i]; c2, h2, p2 = info[i + 1]
        if not p1 or not p2: continue
        last = p1[-1].rstrip(); first = p2[0].lstrip()
        core = re.sub(r'\s*\[\.\.\.\]\s*$', '', last).rstrip()
        marker_end = last.endswith('[...]')
        unterminated = (not core) or core[-1] not in TERM or core.endswith('—') or core.endswith('-') or marker_end
        if core and core[-1] in TERM and not marker_end and not core.endswith('[...]'): unterminated = False
        if not unterminated: continue
        rest = re.sub(r'^\[\.\.\.\]\s*', '', first)
        if not rest: continue
        cont = rest[0].islower() or rest[0] in ',;)-—’' or last.endswith('-')
        if not cont: continue
        # unfinished sentence = text after the last sentence boundary in core
        b = None
        for m in re.finditer(r'[.!?][”’")]*\s+(?=[A-Z“‘"(\[])', core): b = m.end()
        partial = core[b:] if b else core
        props.append(dict(book=bk, ch1=c1, ch2=c2, tail_para=last, head_para=first, partial=partial.strip(),
                          whole_para=(b is None), midword=(last.endswith('-') or first.startswith('-'))))
json.dump(props, open('work/phase4b/seams.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
import collections
print('seams', len(props), 'whole-paragraph moves', sum(p['whole_para'] for p in props), 'midword', sum(p['midword'] for p in props))
print(collections.Counter(p['book'] for p in props).most_common(12))
for p in props[:4]: print(p['book'], p['ch1'], '->', p['ch2'], '| partial:', p['partial'][:80], '| next:', p['head_para'][:50])
