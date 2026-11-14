"""Part S6: does joint (vector) quantisation close the binary-vs-channel gap? (Kelvin's correction, relayed 01:4xZ)
For each small net: an explicit codebook of 2^b output vectors (k-means, k-means++ start, 40 Lloyd iterations on 2^16
fit outputs), b = 1..12; nMSE on 2^15 held-out outputs:
  free     reconstructions are the centroids (output-space VQ: an upper bound on the output's b-bit optimum);
  medoid   each centroid replaced by the nearest actual fit output, so every reconstruction is reachable from every
           layer (decode to that sample's state at layer l): an achievable b-bit scheme for the unrestricted class at
           every layer, scored with the forward-propagated distortion;
  H        entropy of the index on the held-out set (the entropy-coded rate of the same quantiser).
b_VQ(eps) is compared with the channel count C(eps) (Gaussian bound over Cov a and the learned/linear channel codes).
usage: run_vq.py --configs 16x4,32x8,16x16,32x32 --seeds 5000,5001,5002 --out /root/runs/S_vq
"""
import argparse
import json
import math
import os
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import smallnets as sn  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--configs', default='16x16')
ap.add_argument('--seeds', default='5000')
ap.add_argument('--bmax', type=int, default=12)
ap.add_argument('--iters', type=int, default=40)
ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--tag', default='')
ap.add_argument('--out', required=True)
args = ap.parse_args()
torch.set_num_threads(args.threads)
os.makedirs(args.out, exist_ok=True)
DEV = sn.DEV
T0 = time.time()


def assign(X, C, chunk=None):
    chunk = chunk or max(64, int(2e8 / (8 * C.shape[0])))       # keep each distance block under ~200 MB
    out = torch.empty(X.shape[0], dtype=torch.long, device=DEV)
    for c0 in range(0, X.shape[0], chunk):
        out[c0:c0 + chunk] = torch.cdist(X[c0:c0 + chunk], C).argmin(1)
    return out


def kmeans(X, k, iters, g):
    # k-means++ start
    idx = [int(torch.randint(0, X.shape[0], (1,), generator=g, device=DEV))]
    d2 = ((X - X[idx[0]]) ** 2).sum(1)
    for _ in range(1, k):
        p = d2 / d2.sum()
        j = int(torch.multinomial(p, 1, generator=g))
        idx.append(j)
        d2 = torch.minimum(d2, ((X - X[j]) ** 2).sum(1))
    C = X[idx].clone()
    for _ in range(iters):
        a = assign(X, C)
        s = torch.zeros_like(C).index_add_(0, a, X)
        cnt = torch.bincount(a, minlength=k).to(X.dtype)
        C = torch.where((cnt > 0)[:, None], s / cnt.clamp(min=1)[:, None], C)
    return C


res = {}
for cfg in args.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    for seed in [int(s) for s in args.seeds.split(',')]:
        net = sn.Net(seed, n, L)
        gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
        _, Af = net.sample(65536, set(), gp)
        ge = torch.Generator(device=DEV).manual_seed(20_000 + seed * 7 + n * 13 + L)
        _, Ae = net.sample(32768, set(), ge)
        Af, Ae = Af.double(), Ae.double()
        V = float(Ae.var(0).sum())
        g = torch.Generator(device=DEV).manual_seed(1234 + seed)
        ent = dict(V=V, b=[], free=[], medoid=[], H=[])
        for b in range(1, args.bmax + 1):
            C = kmeans(Af, 2 ** b, args.iters, g)
            ae = assign(Ae, C)
            free = float(((Ae - C[ae]) ** 2).sum(1).mean() / V)
            med_idx = assign(C, Af)                     # nearest actual output to each centroid
            Cm = Af[med_idx]
            am = assign(Ae, Cm)
            med = float(((Ae - Cm[am]) ** 2).sum(1).mean() / V)
            p = torch.bincount(ae, minlength=2 ** b).double() / Ae.shape[0]
            H = float(-(p[p > 0] * torch.log2(p[p > 0])).sum())
            ent['b'].append(b)
            ent['free'].append(free)
            ent['medoid'].append(med)
            ent['H'].append(H)
        for name in ['free', 'medoid']:
            ent[f'cross_{name}'] = {str(e): sn.crossing(ent['b'], ent[name], e) for e in [0.1, 0.01]}
        res[f'n{n}_L{L}_s{seed}'] = ent
        print(f'{cfg} s{seed}: free {[round(v, 4) for v in ent["free"]]} | b_VQ(0.1) {ent["cross_free"]["0.1"]} '
              f'b_VQ(0.01) {ent["cross_free"]["0.01"]} | medoid(0.1) {ent["cross_medoid"]["0.1"]} | {time.time() - T0:.0f}s',
              flush=True)
        json.dump(res, open(os.path.join(args.out, f'vq{args.tag}.json'), 'w'))
print('ALL DONE', flush=True)
