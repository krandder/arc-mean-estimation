"""Forward-trained comparison codes (bit-accounting S4 style): at layer l, a K-cell code trained directly on the
shared-noise output distortion crn = E|F_l(h_hat, Xi) - F_l(h, Xi)|^2 / V (same future noise Xi for both).
Encoder: MLP(h_l) -> K logits, hard assignment with a straight-through softmax gradient; decoder: K learned cell states
(initialised by k-means of h_l). Evaluated on held-out points: H(c) (Miller-Madow), crn with the learned states and with
the cell means, the noise-averaged distortion (two independent future draws), and I(c; c_L) (Monte Carlo over the
whole future) so the forward codes sit on the same (rate, information) and (rate, crn) planes as the chains' codes.
usage: run_fwd.py --n 16 --L 16 --seed 9100 --sigma 0.1 --KL 64 --layers 14,12,8,4,0 --out runs_gpu/dev
"""
import argparse
import json
import math
import os
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import bb  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--n', type=int, required=True)
ap.add_argument('--L', type=int, required=True)
ap.add_argument('--seed', type=int, required=True)
ap.add_argument('--sigma', type=float, required=True)
ap.add_argument('--KL', type=int, default=64)
ap.add_argument('--layers', required=True)
ap.add_argument('--Ks', default='2,4,8,16,32,64')
ap.add_argument('--steps', type=int, default=3000)
ap.add_argument('--batch', type=int, default=4096)
ap.add_argument('--width', type=int, default=256)
ap.add_argument('--Ntr', type=int, default=1 << 17)
ap.add_argument('--Nte', type=int, default=1 << 15)
ap.add_argument('--Mgt', type=int, default=1024)
ap.add_argument('--device', default='cpu')
ap.add_argument('--threads', type=int, default=4)
ap.add_argument('--out', required=True)
args = ap.parse_args()
torch.set_num_threads(args.threads)
dev = args.device
L = args.L
T0 = time.time()
odir = os.path.join(args.out, f'n{args.n}L{args.L}_s{args.seed}_sig{args.sigma:g}_K{args.KL}')
net = bb.Net(args.seed, args.n, L, args.sigma, dev)
oc = torch.load(os.path.join(odir, 'outcode.pt'), map_location=dev)
out_code = bb.OutCode(oc['C'].to(dev), net)
fpath = os.path.join(odir, 'fwd.json')
res = json.load(open(fpath)) if os.path.exists(fpath) else {}


def xis_for(N, l, g):
    return {k: torch.randn(N, args.n, generator=g, device=dev) for k in range(l + 1, L)}


for l in [int(x) for x in args.layers.split(',')]:
    if str(l) in res:
        continue
    ts = time.time()
    g = bb.make_gen(dev, 'fwd', args.seed, l)
    h_tr = net.sample(args.Ntr, l, g)
    h_te = net.sample(args.Nte, l, g)
    cnt = bb.mc_counts_out(net, l, h_te, out_code, args.Mgt, g)
    Istar = bb.target_stats(cnt)['T']
    x1, x2 = xis_for(args.Nte, l, g), xis_for(args.Nte, l, g)
    a1, a2 = net.run_xi(h_te, l, x1), net.run_xi(h_te, l, x2)
    V = float(a1.double().var(0).sum())
    mu, sd = h_tr.mean(0), h_tr.std(0).clamp_min(1e-6)
    rows = []
    for K in [int(k) for k in args.Ks.split(',')]:
        torch.manual_seed(bb.seed_of('fwd', args.seed, l, K) % (1 << 31))
        C0, _, _ = bb.kmeans(h_tr[: 1 << 15], K, g, restarts=2)
        enc = bb.MLP(args.n, K, args.width, 2).to(dev)
        Hs = torch.nn.Parameter(C0.clone())
        opt = torch.optim.Adam(list(enc.parameters()) + [Hs], lr=1e-3)
        sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=1e-3, total_steps=args.steps, pct_start=0.05)
        with torch.no_grad():                      # warm start: encoder imitates the k-means cells
            pass
        for s in range(args.steps):
            idx = torch.randint(args.Ntr, (args.batch,), generator=g, device=dev)
            hb = h_tr[idx]
            p = torch.softmax(enc((hb - mu) / sd), 1)
            hard = torch.nn.functional.one_hot(p.argmax(1), K).to(p.dtype)
            w = hard + p - p.detach()
            hh = w @ Hs
            xs = xis_for(args.batch, l, g)
            loss = ((net.run_xi(hh, l, xs) - net.run_xi(hb, l, xs)) ** 2).sum(1).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
        with torch.no_grad():
            c_te = enc((h_te - mu) / sd).argmax(1)
            c_tr = enc((h_tr - mu) / sd).argmax(1)
            r = bb.relevance(c_te, cnt, K)
            S = torch.zeros(K, args.n, device=dev).index_add_(0, c_tr, h_tr)
            nk = torch.bincount(c_tr, minlength=K).to(bb.DT)
            hm = S / nk.clamp_min(1)[:, None]
            hm[nk == 0] = Hs.detach()[nk == 0]
            out = {}
            for name, dec in [('learned', Hs.detach()), ('mean', hm)]:
                ah1, ah2 = net.run_xi(dec[c_te], l, x1), net.run_xi(dec[c_te], l, x2)
                out[name] = dict(crn=float(((ah1 - a1) ** 2).sum(1).mean()) / V,
                                 avg=float(((ah1 - a1) * (ah2 - a2)).sum(1).mean()) / V)
        rows.append(dict(K=K, H=r['H'], I_out=r['I'], K_used=r['K_used'], **out))
        print(f"l={l} K={K}: H {r['H']:.3f} I_out {r['I']:.3f} (I* {Istar:.3f}) crn {out['learned']['crn']:.4f} "
              f"(mean dec {out['mean']['crn']:.4f}) avg {out['learned']['avg']:.4f}", flush=True)
    res[str(l)] = dict(I_star=Istar, V=V, rows=rows, sec=time.time() - ts)
    json.dump(res, open(fpath, 'w'), indent=1)
print('done', time.time() - T0)
