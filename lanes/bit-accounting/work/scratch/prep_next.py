"""Before launching a follow-up VM: finished P1 cells (.json + .pt) -> gpu_src/prior/P1, P1-A results -> prior/P1X,
the given job list reduced to its unfinished jobs, both queue files staged into gpu_src/queue.
usage: prep_next.py <list name: a|b>"""
import os
import shutil
import sys

W = '/home/agent/workspaces/mats/work/bit-accounting'
lst = sys.argv[1]
for sub, pat in (('P1', ('.json', '.pt')), ('P1X', ('.json',))):
    os.makedirs(f'{W}/gpu_src/prior/{sub}', exist_ok=True)
    src = f'{W}/runs/{sub}'
    if not os.path.isdir(src):
        continue
    for f in os.listdir(src):
        if (f.startswith('P_') or f.startswith('X_')) and f.endswith(pat):
            shutil.copy2(f'{src}/{f}', f'{W}/gpu_src/prior/{sub}/{f}')
done = {f[:-5] for f in os.listdir(f'{W}/runs/P1') if f.startswith('P_') and f.endswith('.json')}


def cells(line):
    name, *a = line.split()
    kv = dict(zip(a[::2], a[1::2]))
    n, L = map(int, kv['--configs'].split('x'))
    l, s, k = int(kv['--layers']), kv['--seeds'], kv['--netkind']
    return [f'P_{k}_n{n}_L{L}_s{s}_l{l}_{c}' for c in (['unres'] if l == L else ['local', 'unres'])]


p = f'{W}/gpu_src/queue_lists/jobs_{lst}.txt'
jobs = [ln for ln in open(p).read().splitlines() if ln.strip()]
left = [ln for ln in jobs if not all(c in done for c in cells(ln))]
open(p, 'w').write('\n'.join(left) + '\n')
for q in ('30_p1.sh', '32_p1x.sh'):
    shutil.copy2(f'{W}/gpu_src/staged/{q}', f'{W}/gpu_src/queue/{q}')
print(len(done), 'cells in prior;', len(left), 'unfinished jobs left in list', lst)
