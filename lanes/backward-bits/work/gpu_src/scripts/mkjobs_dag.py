"""Jobs JSON (with dependencies) for gpu_src/scripts/sched.py: the registered scored2 commands (same lines as
queue/scored2_*.txt), ids per net and kind, deps: truth after the net's four chains; gauss and conv after its chain K;
fwd after nothing (needs only the output code). Priority: long chains first, then post jobs as they become ready.
usage: mkjobs_dag.py <out-json>"""
import json
import re
import sys

base = '/home/agent/workspaces/mats/work/backward-bits/gpu_src/queue/'
PFX = sys.argv[2] if len(sys.argv) > 2 else 'scored2'
jobs = []


def net_of(cmd):
    n = re.search(r'--n (\d+)', cmd).group(1)
    L = re.search(r'--L (\d+)', cmd).group(1)
    s = re.search(r'--seed (\d+)', cmd).group(1)
    return f'n{n}L{L}s{s}'


for line in open(base + PFX + '_chains.txt').read().splitlines():
    if line.strip():
        ch = re.search(r'--chain (\w+)', line).group(1)
        jobs.append(dict(id=f'{net_of(line)}_chain{ch}', cmd=line, deps=[]))
post = []
for fn, kind in [(PFX + '_post.txt', 'truth'), (PFX + '_extra.txt', None), (PFX + '_conv.txt', 'conv')]:
    for line in open(base + fn).read().splitlines():
        if not line.strip():
            continue
        net = net_of(line)
        k = kind or ('gauss' if 'run_gauss' in line else 'fwd')
        deps = {'truth': [f'{net}_chain{c}' for c in ('K', 'R', 'P', 'PR')], 'gauss': [f'{net}_chainK'],
                'conv': [f'{net}_chainK'], 'fwd': []}[k]
        post.append(dict(id=f'{net}_{k}', cmd=line, deps=deps))
order = {'truth': 0, 'gauss': 1, 'fwd': 2, 'conv': 3}
post.sort(key=lambda j: (order[j['id'].split('_')[-1]], -int(re.search(r'L(\d+)s', j['id']).group(1))))
json.dump(jobs + post, open(sys.argv[1], 'w'), indent=1)
print(len(jobs), 'chain jobs,', len(post), 'post jobs')
