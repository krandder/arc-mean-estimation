"""Train one nested bottleneck (one model = one whole rate curve) at layer l of a fixed net and evaluate it.

usage: train_bn.py --net arc --seed 4000 --layer 16 --kind bin|gauss --enc local|ahead [--width 1024 --depth 3
       --steps 4000 --batch 512 --lr 1e-3 --K 256 --rmax 256 --fixed_rate R] --out runs/x.json
--layer L (= net depth) with --enc local is the output-space bottleneck (unrestricted reconstruction of a).
--fixed_rate R trains a dedicated single-rate model (rate R every example) for the nested-vs-dedicated check.
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
import bitlib as bl  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--net', default='arc')
ap.add_argument('--seed', type=int, default=9100)
ap.add_argument('--layer', type=int, default=16)
ap.add_argument('--kind', default='bin')
ap.add_argument('--enc', default='local')
ap.add_argument('--width', type=int, default=512)
ap.add_argument('--depth', type=int, default=2)
ap.add_argument('--steps', type=int, default=3000)
ap.add_argument('--batch', type=int, default=256)
ap.add_argument('--lr', type=float, default=1e-3)
ap.add_argument('--K', type=int, default=256)
ap.add_argument('--rmax', type=int, default=256)
ap.add_argument('--fixed_rate', type=float, default=0.0)
ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--P_eval', type=int, default=16384)
ap.add_argument('--P_stats', type=int, default=65536)
ap.add_argument('--grid', default='')
ap.add_argument('--save_model', type=int, default=1)
ap.add_argument('--out', required=True)
args = ap.parse_args()

torch.set_num_threads(args.threads)
t_start = time.time()
net = bl.make_net(args.net, args.seed)
l = args.layer
n = net.n
stats = bl.layer_stats(net, l, args.P_stats, seed=31_337 + args.seed)
V = stats['V']
model = bl.Bottleneck(n, args.K, args.kind, args.enc, args.width, args.depth, stats['h_mean'], stats['h_std'],
                      stats['a_mean'], stats['a_std'], h_star=stats['h_star'])
opt = torch.optim.Adam(model.parameters(), lr=args.lr)
warm = max(1, args.steps // 50)
sched = torch.optim.lr_scheduler.LambdaLR(
    opt, lambda s: min(1.0, (s + 1) / warm) * (0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps))))
bal = bl.RateBalancer(args.rmax)
tseed = 1_000_003 * args.seed + 7_919 * l + (0 if args.kind == 'bin' else 13) + (0 if args.enc == 'local' else 29) \
    + int(args.fixed_rate * 101)
gen = torch.Generator().manual_seed(tseed % (2 ** 62))
log = []
for step in range(args.steps):
    h, a = net.sample(args.batch, l, gen)
    if args.fixed_rate > 0:
        rate = torch.full((args.batch,), args.fixed_rate)
        rate = rate.long() if args.kind == 'bin' else rate.to(bl.DT)
    else:
        rate = bl.sample_rates(args.batch, args.kind, args.rmax, gen)
    hh, Creal = model(h, a, rate, gen)
    ah = net.run(hh, l)
    err = ((ah - a) ** 2).sum(1) / V
    if args.fixed_rate > 0:
        loss = err.mean()
        bi = None
    else:
        w, bi = bal.weights(rate.to(bl.DT))
        loss = (w * err).mean()
    opt.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 10.0)
    opt.step()
    sched.step()
    if bi is not None:
        bal.update(bi, err)
    if step % 200 == 0 or step == args.steps - 1:
        rec = dict(step=step, loss=float(loss.detach()), nmse=float(err.detach().mean()), sec=time.time() - t_start)
        if bi is not None:
            rec['ema'] = [float(x) for x in bal.ema]
        log.append(rec)
        print(json.dumps({k: (v if k != 'ema' else [round(x, 4) for x in v[::4]]) for k, v in rec.items()}), flush=True)

if args.grid:
    rates = [float(x) for x in args.grid.split(',')]
elif args.fixed_rate > 0:
    rates = [args.fixed_rate]
else:
    rates = bl.bin_grid(args.rmax) if args.kind == 'bin' else bl.gauss_grid(args.rmax)
if args.kind == 'bin':
    rates = [int(r) for r in rates]
curve = bl.evaluate(model, net, l, V, rates, args.P_eval, seed=777 + args.seed)
res = dict(args=vars(args), V=V, curve=curve, train_log=log, seconds=time.time() - t_start,
           eta=(model.eta.detach().tolist() if args.kind == 'gauss' else None))
for eps in [0.1, 0.01, 0.001]:
    res[f'b_{eps}'] = bl.crossing(curve, eps)
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
with open(args.out, 'w') as f:
    json.dump(res, f)
if args.save_model:
    torch.save(model.state_dict(), args.out.replace('.json', '.pt'))
print('done', args.out, 'b(eps):', [res[f'b_{e}'] for e in [0.1, 0.01, 0.001]], f'{time.time() - t_start:.0f}s',
      flush=True)
