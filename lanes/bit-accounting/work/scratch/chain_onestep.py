"""What is the lossy part of a chain transition? (main, 00:5xZ). For each saved S2 chain, code size b and transition
i (layer l_i -> l_{i+1}), on held-out inputs (half B of 2^17; majority maps fitted on half A):
  own_i       nMSE of decoding the layer's own code c_i at l_i (through the fixed future);
  own_next    nMSE of decoding the true next code c_{i+1} at l_{i+1};
  bayes_next  nMSE of decoding the Bayes (per-code majority) prediction of c_{i+1} from c_i at l_{i+1};
  T_next      nMSE of decoding the learned transition's prediction T_i(c_i) at l_{i+1}.
Reading: own_next < own_i means the next code carries output-relevant information the current code lacks (the
next encoder sees a state one more layer along); bayes_next >= own_i means the step also loses some of what c_i had
(the two codes' cells do not nest). If the unpredictable bits were output-irrelevant (training noise), bayes_next
would be close to own_next. c_{i+1} is a deterministic function of h_{l_i} (noiseless net), so the unpredictable part
is information about the state that c_i does not contain, never randomness.
-> results/S2_onestep.json"""
import glob
import json
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gpu_src', 'lib'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smallnets as sn  # noqa: E402
from chain_posthoc import Chain, codes_of, idx, BS, K, M  # noqa: E402

torch.set_num_threads(2)
CDIR = os.environ.get('CHAIN_DIR', 'runs/S_chain')
NK = os.environ.get('NETKIND', 'relu')
OUTF = os.environ.get('ONESTEP_OUT', 'results/S2_onestep.json')
out = json.load(open(OUTF)) if os.path.exists(OUTF) else {}
for p in sorted(glob.glob(f'{CDIR}/C_*.pt')):
    tag = os.path.basename(p)[:-3]
    if tag in out:
        continue
    parts = tag.split('_')
    n, L, seed, cls = int(parts[1][1:]), int(parts[2][1:]), int(parts[3][1:]), parts[4]
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    net = sn.Net(seed, n, L, kind=NK)
    g = torch.Generator().manual_seed(123 + seed)
    Hp, Ap = net.sample(65536, set(layers), g)
    frames = [sn.frame(Hp[l]) for l in layers]
    fr_a = sn.frame(Ap)
    ch = Chain(n, layers, cls)
    ch.load_state_dict(torch.load(p, map_location='cpu'), strict=False)
    H, A = net.sample(131072, set(layers), g)
    V = float(A.double().var(0).sum())
    codes = [codes_of(ch, i, H[l], A, frames, fr_a, cls) for i, l in enumerate(layers)]
    half = A.shape[0] // 2
    AB = A[half:]

    def dec_nmse(i, C):
        """nMSE of decoding codes C (M, B, K) at layer i through the fixed future, against AB."""
        with torch.no_grad():
            hh = frames[i]['m'] + ch.dec[i](C) @ frames[i]['S12']
            ah = net.run(hh, layers[i])
            return (((ah - AB) ** 2).sum(-1).mean(-1) / V).tolist()

    ent = {}
    mask = (torch.arange(K)[None, None, :] < torch.tensor(BS).view(M, 1, 1)).float()
    own = [dec_nmse(i, codes[i][:, half:] * mask) for i in range(len(layers))]
    for i in range(len(layers) - 1):
        cB = codes[i][:, half:] * mask
        with torch.no_grad():
            Tpred = torch.where(ch.T[i](cB) > 0, 1.0, -1.0) * mask
        T_next = dec_nmse(i + 1, Tpred)
        bayes = torch.zeros_like(cB)
        for mi, b in enumerate(BS):
            cA = codes[i][mi, :half, :b]
            yA = codes[i + 1][mi, :half, :b]
            ciA, ciB = idx(cA), idx(cB[mi][:, :b])
            s = torch.zeros(2 ** b, b).index_add_(0, ciA, yA)
            cnt = torch.bincount(ciA, minlength=2 ** b)
            tab = torch.where(s >= 0, 1.0, -1.0)
            pred = torch.where((cnt[ciB] > 0)[:, None], tab[ciB], Tpred[mi][:, :b])
            bayes[mi, :, :b] = pred
        bayes_next = dec_nmse(i + 1, bayes)
        for mi, b in enumerate(BS):
            ent.setdefault(str(b), []).append(dict(own_i=own[i][mi], own_next=own[i + 1][mi],
                                                   bayes_next=bayes_next[mi], T_next=T_next[mi]))
    out[tag] = ent
    print(tag, {b: [(round(t['own_i'], 3), round(t['own_next'], 3), round(t['bayes_next'], 3), round(t['T_next'], 3))
                    for t in v] for b, v in ent.items() if b in ('8', '16')}, flush=True)
    json.dump(out, open(OUTF, 'w'))
