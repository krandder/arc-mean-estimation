"""Cell-by-cell diff of two generated table files (scratch/report_tables.py output): every cell whose median moves by
more than a threshold, and every cell that appears, disappears or changes between a number and 'not reached' / '-'.
usage: table_diff.py <old md> <new md> <out md> [threshold, default 0.05]
"""
import re
import sys

OLD, NEW, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
THR = float(sys.argv[4]) if len(sys.argv) > 4 else 0.05


def parse(path):
    cells, section, header = {}, None, None
    for line in open(path):
        line = line.rstrip('\n')
        if line.startswith('### '):
            section, header = line[4:].split(' (')[0].strip(), None
            continue
        if not line.startswith('|') or set(line) <= set('|-'):
            continue
        parts = [p.strip() for p in line.strip('|').split('|')]
        if header is None:
            header = parts
            continue
        nkey = 2 if header[:2] in (['layer', 'class'], ['family', 'layer'], ['k', 'class']) else 1
        key = (section,) + tuple(parts[:nkey])
        for h, v in zip(header[nkey:], parts[nkey:]):
            cells[key + (h,)] = v
    return cells


def num(v):
    if v is None:
        return None, 'absent'
    if v.startswith('>max'):
        return None, 'not reached'
    m = re.match(r'^([0-9.]+)', v)
    if not m:
        return None, (v or '-')
    return float(m.group(1)), 'value'


old, new = parse(OLD), parse(NEW)
moved, status = [], []
for k in sorted(set(old) | set(new), key=str):
    a, sa = num(old.get(k))
    b, sb = num(new.get(k))
    label = ' / '.join(k)
    if sa == 'value' and sb == 'value':
        if a > 0 and abs(b - a) / a > THR:
            moved.append(f'| {label} | {old[k]} | {new[k]} | {100 * (b - a) / a:+.0f}% |')
    elif sa != sb:
        status.append(f'| {label} | {old.get(k, "absent")} | {new.get(k, "absent")} | {sa} -> {sb} |')
L = [f'Cells whose median moved by more than {int(100 * THR)}% ({len(moved)}):', '',
     '| table / row / column | before | now | change |', '|---|---|---|---|'] + moved + \
    ['', f'Cells that appeared, disappeared, or changed between a number and not reached / - ({len(status)}):', '',
     '| table / row / column | before | now | kind |', '|---|---|---|---|'] + status
open(OUT, 'w').write('\n'.join(L) + '\n')
print(f'{len(moved)} moved, {len(status)} status changes -> {OUT}')
