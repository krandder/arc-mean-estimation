"""Job lists for phase 1 (run_vr.py), one line per job: name and arguments. One job = one (net, layer) = the local and
unres cells of that layer, or the output cell. Lists: vm4 (relu 16x16 and 32x32 seed 5000), a (relu 16x16, 32x32
seeds 5001-5002 and 32x8 seed 5002), b (controls, 16x4 seeds 5000-5002, 32x8 seeds 5000-5001).
Within a list, jobs are ordered by priority (registered order), the deepest (most expensive) layers first."""
import os

OUT = '/home/agent/workspaces/mats/work/bit-accounting/gpu_src/queue_lists'
os.makedirs(OUT, exist_ok=True)


def jobs(kind, n, L, seed):
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    out = []
    for l in layers + [L]:
        name = f'{kind}_{n}x{L}_s{seed}_{"out" if l == L else "l" + str(l)}'
        out.append(f'{name} --configs {n}x{L} --seeds {seed} --layers {l} --netkind {kind}')
    return out


lists = {
    'vm4': jobs('relu', 16, 16, 5000) + jobs('relu', 32, 32, 5000),
    'a': (jobs('relu', 16, 16, 5001) + jobs('relu', 32, 32, 5001) + jobs('relu', 16, 16, 5002)
          + jobs('relu', 32, 32, 5002) + jobs('relu', 32, 8, 5002)),
    'b': (jobs('tanh4', 16, 16, 5000) + jobs('feistel', 16, 16, 5000) + jobs('linear', 16, 16, 5000)
          + jobs('relu', 16, 4, 5000) + jobs('relu', 32, 8, 5000) + jobs('relu', 16, 4, 5001)
          + jobs('relu', 32, 8, 5001) + jobs('relu', 16, 4, 5002)),
}
for k, v in lists.items():
    open(f'{OUT}/jobs_{k}.txt', 'w').write('\n'.join(v) + '\n')
    print(k, len(v), 'jobs')
