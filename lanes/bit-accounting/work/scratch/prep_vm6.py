"""Before launching VM 6: copy finished P1 cells into gpu_src/prior/P1 (restored and skipped on the VM), put the
unfinished jobs of VM 4's list at the front of jobs_b, and stage the P1 queue script into gpu_src/queue."""
import os
import shutil

W = '/home/agent/workspaces/mats/work/bit-accounting'
os.makedirs(f'{W}/gpu_src/prior/P1', exist_ok=True)
done = set()
for f in os.listdir(f'{W}/runs/P1'):
    if f.startswith('P_') and f.endswith('.json'):
        shutil.copy2(f'{W}/runs/P1/{f}', f'{W}/gpu_src/prior/P1/{f}')
        done.add(f[:-5])


def cells(line):
    name, *a = line.split()
    kv = dict(zip(a[::2], a[1::2]))
    n, L = map(int, kv['--configs'].split('x'))
    l, s, k = int(kv['--layers']), kv['--seeds'], kv['--netkind']
    return [f'P_{k}_n{n}_L{L}_s{s}_l{l}_{c}' for c in (['unres'] if l == L else ['local', 'unres'])]


left = [ln for ln in open(f'{W}/gpu_src/queue_lists/jobs_vm4.txt').read().splitlines()
        if ln.strip() and not all(c in done for c in cells(ln))]
b = [ln for ln in open(f'{W}/gpu_src/queue_lists/jobs_b.txt').read().splitlines() if ln.strip()]
b = left + [ln for ln in b if ln not in left]
open(f'{W}/gpu_src/queue_lists/jobs_b.txt', 'w').write('\n'.join(b) + '\n')
shutil.copy2(f'{W}/gpu_src/staged/30_p1.sh', f'{W}/gpu_src/queue/30_p1.sh')
print(len(done), 'cells copied to prior;', len(left), 'VM-4 jobs moved to the front of jobs_b;', len(b), 'jobs in b')
