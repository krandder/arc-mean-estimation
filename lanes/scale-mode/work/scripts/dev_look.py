"""Dev-only look at runs_dev outputs (not part of the registered scoring). usage: dev_look.py RUNS_DEV NET_TAG KIND
KIND p2: truth from the Phase 2 public npz; KIND own: truth_<tag>.npz in RUNS_DEV (cross-half)."""
import json, os, sys, glob
import numpy as np
RD, TAG, KIND = sys.argv[1:4]
HF = '/home/agent/workspaces/mats/work/scale-mode/downloads/hf/npz'
if KIND == 'p2':
    d = np.load(os.path.join(HF, f'p2_mlp_{TAG.split("_")[1]}.npz'))
    Y = d['all_layer_means'][-1].astype(float); av = float(d['avg_variance']); n = Y.size; L = d['weights'].shape[0]
    err = lambda e: float(((np.asarray(e) - Y) ** 2).mean() / av)
else:
    t = np.load(os.path.join(RD, f'truth_{TAG}.npz')); N = float(t['N']); h = N / 2
    YA, YB = t['S1A'][-1] / h, t['S1B'][-1] / h; Y = (YA + YB) / 2; var = (t['S2A'][-1] + t['S2B'][-1]) / N - Y ** 2
    n = Y.size; L = int(t['L']); av = float(var.mean())
    err = lambda e: float(((np.asarray(e) - YA) * (np.asarray(e) - YB)).sum() / var.sum())
pf = 2.0 * n * n * L
rows = []
for f in sorted(glob.glob(os.path.join(RD, f'*_{TAG}*.json'))):
    r = json.load(open(f)); b = os.path.basename(f)
    if b.startswith('lv_'):
        for a, x in r['arms'].items(): rows.append((a, err(x['mean']), x['flops'] / pf))
    elif b.startswith('rqmc_'):
        for row in r['rows']:
            es = [err(e) for e in row['est']]; rows.append((f'RQMC N={row["N"]}', float(np.mean(es)), row['N']))
    elif 'mean' in r:
        rows.append((b.split('_')[0] + ('-' + r['variant'] if 'variant' in r else ''), err(r['mean']), r['flops'] / pf))
print(f'{TAG}: n={n} L={L} avgvar={av:.4f}  (raw MSE = nMSE * avgvar)')
for name, e, C in sorted(rows, key=lambda x: x[2]):
    print(f'  {name:16s} nMSE {e:.3e}  raw {e * av:.3e}  passes {C:9.0f}  G_MC {1 / (C * e):7.2f}')
