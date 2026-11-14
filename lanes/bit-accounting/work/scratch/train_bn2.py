"""Train one nested local bottleneck (Bottleneck2: starts at the linear transform code, residual MLPs on top) at layer l
of a fixed net, evaluate the whole rate curve, and evaluate the linear code it started from on the same inputs.

usage: train_bn2.py --net arc --seed 4000 --layer 16 --kind gauss|bin|fsq --basis as|lin [--width 512 --depth 2
       --steps 3000 --batch 256 --lr 3e-4 --K 256] --out runs/x.json
--layer L is the output-space bottleneck (future = identity, basis = output PCA).
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
import lincodes as lc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--net', default='arc')
ap.add_argument('--seed', type=int, default=9100)
ap.add_argument('--layer', type=int, default=16)
ap.add_argument('--kind', default='gauss')
ap.add_argument('--basis', default='as')
ap.add_argument('--width', type=int, default=512)
ap.add_argument('--depth', type=int, default=2)
ap.add_argument('--steps', type=int, default=3000)
ap.add_argument('--batch', type=int, default=256)
ap.add_argument('--lr', type=float, default=3e-4)
ap.add_argument('--lin_mult', type=float, default=0.03)
ap.add_argument('--K', type=int, default=0)
ap.add_argument('--rmax', type=int, default=256)
ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--P_fit', type=int, default=16384)
ap.add_argument('--P_eval', type=int, default=8192)
ap.add_argument('--save_model', type=int, default=1)
ap.add_argument('--out', required=True)
args = ap.parse_args()

torch.set_num_threads(args.threads)
t_start = time.time()
net = bl.make_net(args.net, args.seed)
l = args.layer
n = net.n
K = args.K if args.K > 0 else (n if args.kind != 'bin' else max(n, 64 if n < 64 else n))
# frame and basis from a fit sample (float64)
rng = np.random.default_rng(91_000 + args.seed)
x = rng.standard_normal((args.P_fit, n))
h = x
H = None
for k in range(net.L):
    if k == l:
        H = h.copy()
    h = np.maximum(h @ net.WT64[k], 0.0)
A = h
if l == net.L:
    H = A.copy()
fr = lc.frame(H)
if args.basis == 'as' and l < net.L:
    lam, Q = lc.basis_as(net, l, H[:4096], fr, q=4, seed=l)
else:
    lam, Q = lc.basis_lin(H, A, fr)
V = float(A.var(0, ddof=1).sum())
t_basis = time.time() - t_start
print(f'basis {args.basis} ready {t_basis:.0f}s, V_fit {V:.4f}, lam[:4] {lam[:4]}', flush=True)

model = bl.Bottleneck2(n, K, args.kind, args.width, args.depth, fr['m'], fr['S12'], fr['Sm12'], Q, lam)
lin_params = [model.enc_lin, model.dec_lin]
other = [p for nm, p in model.named_parameters() if nm not in ('enc_lin', 'dec_lin')]
opt = torch.optim.Adam([dict(params=lin_params, lr=args.lr * args.lin_mult), dict(params=other, lr=args.lr)])
warm = max(1, args.steps // 50)
sched = torch.optim.lr_scheduler.LambdaLR(
    opt, lambda s: min(1.0, (s + 1) / warm) * (0.03 + 0.97 * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps))))
rmax = args.rmax if args.kind != 'bin' else min(args.rmax, K)
bal = bl.RateBalancer(rmax)
tseed = 1_000_003 * args.seed + 7_919 * l + {'bin': 0, 'gauss': 13, 'fsq': 17}[args.kind]
gen = torch.Generator().manual_seed(tseed % (2 ** 62))


def sample_rates(B):
    u = torch.rand(B, generator=gen, dtype=torch.float64)
    r = torch.exp(u * math.log(rmax + 1.0))
    if args.kind == 'gauss':
        return r.clamp(1.0, rmax).to(bl.DT)
    return torch.floor(r).long().clamp(1, rmax)


# evaluation set and the starting point (step 0 = the linear code inside the model)
egen = torch.Generator().manual_seed(777 + args.seed)
rates = bl.gauss_grid(rmax) if args.kind == 'gauss' else [r for r in bl.bin_grid(256) if r <= rmax]
curve0 = bl.evaluate(model, net, l, V, rates, args.P_eval, seed=777 + args.seed)
print('step-0 (linear code) curve:', [(c['rate'], round(c['nmse'], 4)) for c in curve0[::4]], flush=True)
log = []
for step in range(args.steps):
    hb, ab = net.sample(args.batch, l, gen)
    rate = sample_rates(args.batch)
    hh, Creal = model(hb, ab, rate, gen)
    ah = net.run(hh, l)
    err = ((ah - ab) ** 2).sum(1) / V
    w, bi = bal.weights(rate.to(bl.DT))
    loss = (w * err).mean()
    opt.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 10.0)
    opt.step()
    sched.step()
    bal.update(bi, err)
    if step % 250 == 0 or step == args.steps - 1:
        rec = dict(step=step, loss=float(loss.detach()), nmse=float(err.detach().mean()), sec=time.time() - t_start,
                   ema=[float(v) for v in bal.ema])
        log.append(rec)
        print(json.dumps(dict(step=step, loss=round(rec['loss'], 4), sec=round(rec['sec']),
                              ema=[round(v, 4) for v in rec['ema'][::4]])), flush=True)
curve = bl.evaluate(model, net, l, V, rates, args.P_eval, seed=777 + args.seed)
res = dict(args=vars(args), V=V, K=K, curve=curve, curve_linear_start=curve0, train_log=log,
           seconds=time.time() - t_start, lam=np.asarray(lam[:K]).tolist(),
           eta=(model.eta.detach().tolist() if args.kind == 'gauss' else None))
for eps in [0.1, 0.01, 0.001]:
    res[f'b_{eps}'] = bl.crossing(curve, eps)
    res[f'b0_{eps}'] = bl.crossing(curve0, eps)
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
with open(args.out, 'w') as f:
    json.dump(res, f)
if args.save_model:
    torch.save(model.state_dict(), args.out.replace('.json', '.pt'))
print('done', args.out, 'learned b(eps):', [res[f'b_{e}'] for e in [0.1, 0.01, 0.001]], 'linear start:',
      [res[f'b0_{e}'] for e in [0.1, 0.01, 0.001]], f'{time.time() - t_start:.0f}s', flush=True)
