"""Rate curves for small nets: for each net (n x L, seed), layer l in {0, L/4, L/2, 3L/4, L-1} and the output space,
encoder class in {local, linear, unres}: train 10 binary and 10 Gaussian-channel bottlenecks (one per rate) side by side
and evaluate nMSE and the output-mean error on held-out inputs.

usage: run_curves.py --configs 16x4,16x16 --seeds 9100,5000 --out /root/runs/S_curves [--steps 6000 --batch 1024]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import smallnets as sn  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--configs', default='16x4')
ap.add_argument('--seeds', default='9100')
ap.add_argument('--classes', default='local,linear,unres')
ap.add_argument('--rates', default='1,2,3,4,6,8,12,16,24,32')
ap.add_argument('--steps', type=int, default=6000)
ap.add_argument('--batch', type=int, default=1024)
ap.add_argument('--lr', type=float, default=1e-3)
ap.add_argument('--P_pilot', type=int, default=65536)
ap.add_argument('--P_eval', type=int, default=32768)
ap.add_argument('--width', type=int, default=256)
ap.add_argument('--depth', type=int, default=3)
ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--out', required=True)
args = ap.parse_args()
torch.set_num_threads(args.threads)
if sn.DEV == 'cuda':
    torch.backends.cuda.matmul.allow_tf32 = False   # keep float32 accuracy for the low-distortion end
os.makedirs(args.out, exist_ok=True)
rates = [float(r) for r in args.rates.split(',')]
EPS = [0.1, 0.01, 0.001]
T0 = time.time()


def layer_grid(L):
    return sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))


for cfg in args.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    for seed in [int(s) for s in args.seeds.split(',')]:
        net = sn.Net(seed, n, L)
        layers = layer_grid(L)
        gp = torch.Generator(device=sn.DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
        Hp, Ap = net.sample(args.P_pilot, set(layers), gp)
        Hp[L] = Ap
        V = float(Ap.double().var(0).sum())
        Ea2 = float((Ap.double() ** 2).sum(1).mean())
        fr_a = sn.frame(Ap)
        ge = torch.Generator(device=sn.DEV).manual_seed(20_000 + seed * 7 + n * 13 + L)
        He, Ae = net.sample(args.P_eval, set(layers), ge)
        He[L] = Ae
        Ve = float(Ae.double().var(0).sum())
        i_star = int(((Ap - Ap.mean(0)) ** 2).sum(1).argmin())
        for l in layers + [L]:
            fr = sn.frame(Hp[l]) if l < L else fr_a
            h_star_w = (Hp[l][i_star] - fr['m']) @ fr['Sm12']
            classes = args.classes.split(',') if l < L else ['unres']
            for cls in classes:
                tag = f'S_n{n}_L{L}_s{seed}_l{l}_{cls}'
                path = os.path.join(args.out, tag + '.json')
                if os.path.exists(path):
                    continue
                t1 = time.time()
                models = [sn.Bottlenecks(n, kind, cls, rates, fr, fr_a, h_star_w, width=args.width, depth=args.depth)
                          for kind in ('bin', 'gauss')]
                params = [p for m in models for p in m.parameters()]
                opt = torch.optim.Adam(params, lr=args.lr)
                warm = max(1, args.steps // 50)
                sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / warm) * (
                    0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps))))
                gt = torch.Generator(device=sn.DEV).manual_seed(30_000 + seed * 7 + n * 13 + L * 101 + l * 3
                                                               + {'local': 0, 'linear': 1, 'unres': 2}[cls])
                log = []
                for step in range(args.steps):
                    Hb, Ab = net.sample(args.batch, {l}, gt)
                    hb = Ab if l == L else Hb[l]
                    loss = 0.0
                    errs = []
                    for m in models:
                        ah = net.run(m(hb, Ab, gt), l)
                        err = ((ah - Ab) ** 2).sum(-1).mean(-1) / V
                        errs.append(err.detach())
                        loss = loss + err.sum()
                    opt.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(params, 10.0)
                    opt.step()
                    sched.step()
                    if step % 1000 == 0 or step == args.steps - 1:
                        log.append(dict(step=step, bin=errs[0].tolist(), gauss=errs[1].tolist()))
                # evaluation
                res = dict(n=n, L=L, seed=seed, l=l, cls=cls, V=V, V_eval=Ve, Ea2=Ea2, rank=fr['rank'],
                           cloud_evals=fr['evals'][:n].tolist(), rates=rates, train_log=log, curves={})
                gev = torch.Generator(device=sn.DEV).manual_seed(40_000 + seed)
                for m in models:
                    m.eval()
                    with torch.no_grad():
                        sq, dsum, d2 = [], 0.0, 0.0
                        D = []
                        for c0 in range(0, args.P_eval, 8192):
                            hb = He[l][c0:c0 + 8192]
                            ab = Ae[c0:c0 + 8192]
                            ah = net.run(m(hb, ab, gev), l)
                            d = (ah - ab).double()                     # (M, B, n)
                            sq.append((d * d).sum(-1))
                            D.append(d)
                        sq = torch.cat(sq, 1) / Ve                     # (M, P)
                        D = torch.cat(D, 1)
                        md = D.mean(1)
                        mean_err = (md * md).sum(-1) / Ve
                        floor = D.var(1).sum(-1) / args.P_eval / Ve
                        caps = m.capacities().tolist()
                    cur = dict(rate=rates, cap=caps, nmse=sq.mean(1).tolist(),
                               se=(sq.std(1) / math.sqrt(args.P_eval)).tolist(), mean_err=mean_err.tolist(),
                               mean_floor=floor.tolist())
                    cur['cross'] = {str(e): sn.crossing(rates, cur['nmse'], e) for e in EPS}
                    res['curves'][m.kind] = cur
                res['seconds'] = time.time() - t1
                with open(path, 'w') as f:
                    json.dump(res, f)
                cb, cg = res['curves']['bin'], res['curves']['gauss']
                print(f'{tag}: {res["seconds"]:.0f}s | bin nmse ' + ' '.join(f'{v:.3g}' for v in cb['nmse']) +
                      f' | gauss nmse ' + ' '.join(f'{v:.3g}' for v in cg['nmse']) +
                      f' | b(eps) {cb["cross"]} C(eps) {cg["cross"]} | total {time.time() - T0:.0f}s', flush=True)
print('ALL DONE', f'{time.time() - T0:.0f}s', flush=True)
