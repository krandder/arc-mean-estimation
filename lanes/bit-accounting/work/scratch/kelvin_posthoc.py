"""Held-out scrambling statistics for the S3 (curriculum autoencoder) codes, the same as scratch/chain_posthoc.py:
for each saved arm (runs/S_kelvin/K_*.pt), floor variant, code size b (first b of the 32 nested bits) and transition
between consecutive grid layers: trivial, Bayes (per-code majority, fitted on half A), degree-1/2 threshold maps (held
out), and the relabelled null. -> results/S3_posthoc.json"""
import glob
import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gpu_src', 'lib'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smallnets as sn  # noqa: E402
import chain_posthoc  # noqa: E402
from chain_posthoc import stats, idx  # noqa: E402

chain_posthoc.junta_heldout = lambda *a, **k: np.array([np.nan])   # juntas skipped here (cost)

torch.set_num_threads(2)
K, M = 32, 2


class ArmEnc(nn.Module):
    def __init__(self, n, m):
        super().__init__()
        self.enc = nn.ModuleList([sn.BMLP(M, n, K, 256, 3) for _ in range(m)])


out = json.load(open('results/S3_posthoc.json')) if os.path.exists('results/S3_posthoc.json') else {}
for p in sorted(glob.glob('runs/S_kelvin/K_*.pt')):
    tag = os.path.basename(p)[:-3]
    if tag in out:
        continue
    parts = tag.split('_')
    n, L, seed = int(parts[1][1:]), int(parts[2][1:]), int(parts[3][1:])
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    net = sn.Net(seed, n, L)
    g = torch.Generator().manual_seed(321 + seed)
    Hp, _ = net.sample(65536, set(layers), g)
    frames = [sn.frame(Hp[l]) for l in layers]
    arm = ArmEnc(n, len(layers))
    sd = torch.load(p, map_location='cpu')
    arm.load_state_dict({k: v for k, v in sd.items() if k.startswith('enc.')}, strict=True)
    H, _ = net.sample(131072, set(layers), g)
    codes = []
    with torch.no_grad():
        for i, l in enumerate(layers):
            x = (H[l] - frames[i]['m']) @ frames[i]['Sm12']
            codes.append(torch.where(arm.enc[i](x.unsqueeze(0).expand(M, *x.shape)) > 0, 1.0, -1.0))
    rng = np.random.default_rng(seed)
    ent = {}
    for mi, fl in enumerate([0.0, 0.05]):
        for b in [4, 8, 12, 16]:
            trs = []
            for i in range(len(layers) - 1):
                C, Y = codes[i][mi][:, :b], codes[i + 1][mi][:, :b]
                half = C.shape[0] // 2
                ci = idx(C)
                real = stats(ci[:half], C[:half], Y[:half], ci[half:], C[half:], Y[half:], b, rng)
                u = torch.unique(ci)
                remap = torch.full((2 ** b,), -1, dtype=torch.long)
                remap[u] = u[torch.tensor(rng.permutation(len(u)))]
                cin = remap[ci]
                Cn = 1.0 - 2.0 * ((cin[:, None] >> torch.arange(b)[None, :]) & 1).float()
                null = stats(cin[:half], Cn[:half], Y[:half], cin[half:], Cn[half:], Y[half:], b, rng)
                trs.append(dict(real=real, null=null))
            ent[f'{fl}_{b}'] = trs
    out[tag] = ent
    print(tag, {k: [(round(t['real']['ptf1'], 3), round(t['real']['bayes_bit'], 3), round(t['real']['trivial'], 3),
                     round(t['null']['ptf1'], 3)) for t in v] for k, v in ent.items() if k.endswith('_16')}, flush=True)
    json.dump(out, open('results/S3_posthoc.json', 'w'))
