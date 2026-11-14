"""Post-hoc decoder certificate for unrestricted codes (C1/C8 follow-up): reload a saved base model (all nets and
restarts of one layer), and at a few lambdas compare, on held-out inputs, the plain layer-l decoder, the output-space
head (free reconstruction from the code) and the preimage refinement toward the head's output with more effort
(Adam, up to `steps`, cosine lr; checkpoints reported). The refinement target is the head's output, never the true
output, so this is a decoder of the code (no leakage). The rate is the trained prior's held-out rate at that lambda.
usage: refine_posthoc.py --family arc --seeds 4000,4001,4002,4003 --restarts 2 --layer 0 --pt <file> --out <dir>
"""
import argparse
import json
import math
import os
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vrlib as vr  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--family', default='arc')
ap.add_argument('--seeds', default='4000')
ap.add_argument('--restarts', type=int, default=2)
ap.add_argument('--layer', type=int, required=True)
ap.add_argument('--cls', default='unres')
ap.add_argument('--pt', required=True)
ap.add_argument('--t_list', default='-5,-4,-3,-2')
ap.add_argument('--steps', type=int, default=1000)
ap.add_argument('--checkpoints', default='150,400,1000')
ap.add_argument('--P', type=int, default=4096)
ap.add_argument('--out', required=True)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
seeds = [int(s) for s in args.seeds.split(',')]
R, l = args.restarts, args.layer
saved = torch.load(args.pt, map_location=vr.DEV)
sa = saved['args']
K = sa['K'] or {'arc': 256, 'nd': 16}[args.family]
W = sa['width'] or {'arc': 1024, 'nd': 256}[args.family]
Ws_list = []
for s in seeds:
    Ws, act = vr.family_weights(args.family, s)
    Ws_list.append(Ws)
L = len(Ws_list[0])
bnet = vr.BNet(Ws_list, act)
stats = [vr.pilot_stats(Ws, act, l, P=65536, seed=10_000 + s) for s, Ws in zip(seeds, Ws_list)]
M = len(seeds) * R
init = vr.build_init(stats, Ws_list, l, args.cls, K, R, mode=(sa.get('init') or None))
model = vr.VRCode(M, args.cls, bnet.n, K, W, sa['depth'], (sa['tmin'], sa['tmax']), init,
                  lin_src=('y' if init['mode'] == 'refu' else 'xa'))
model.load_state_dict(saved['state'])
model.eval()
fr = vr.Frames(stats, l, L, R)
torch.backends.cuda.matmul.allow_tf32 = False
x = torch.stack([vr.heldout_x(s, args.P, bnet.n) for s in seeds]).unsqueeze(1).expand(len(seeds), R, args.P, bnet.n)
x = x.reshape(M, args.P, bnet.n)
with torch.no_grad():
    h = x if l == 0 else bnet.run(x, 0, l)
    a = bnet.run(h, l)
V = fr.V.view(M, 1)
cps = [int(c) for c in args.checkpoints.split(',')]
res = dict(family=args.family, seeds=seeds, restarts=R, layer=l, cls=args.cls, pt=os.path.basename(args.pt), P=args.P,
           steps=args.steps, points=[])
for ti, tv in enumerate([float(v) for v in args.t_list.split(',')]):
    T0 = time.time()
    gen = torch.Generator(device=vr.DEV).manual_seed(4242 + ti)
    with torch.no_grad():
        t = torch.full((M, 1), tv, device=vr.DEV)
        yhat, rate, ex = model(fr.white(h).view(M, 1, args.P, -1), fr.pca_a(a).view(M, 1, args.P, -1), t, gen)
        yhat = yhat.view(M, args.P, -1)
        ahd = torch.relu(fr.from_pca_a(ex['xa_head'].view(M, args.P, -1)))
        plain = ((bnet.run(fr.unwhite(yhat), l) - a) ** 2).sum(-1) / V
        head = ((ahd - a) ** 2).sum(-1) / V
    y = yhat.clone().requires_grad_(True)
    opt = torch.optim.Adam([y], lr=3e-2)
    curve = {}
    for s in range(1, args.steps + 1):
        for pg in opt.param_groups:
            pg['lr'] = 1e-4 + (3e-2 - 1e-4) * 0.5 * (1 + math.cos(math.pi * (s - 1) / args.steps))
        loss = ((bnet.run(fr.unwhite(y), l) - ahd) ** 2).sum()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if s in cps or s == args.steps:
            with torch.no_grad():
                dref = ((bnet.run(fr.unwhite(y), l) - a) ** 2).sum(-1) / V
                curve[s] = dref.mean(1).tolist()
    res['points'].append(dict(t=tv, rate=rate.view(M, -1).mean(1).tolist(), nmse_plain=plain.mean(1).tolist(),
                              nmse_head=head.mean(1).tolist(), nmse_refined=curve, seconds=time.time() - T0))
    print(f't {tv}: rate {rate.mean():.1f} plain {plain.mean():.4g} head {head.mean():.4g} refined '
          + ' '.join(f'{k}:{sum(v) / len(v):.4g}' for k, v in curve.items()) + f' ({time.time() - T0:.0f}s)', flush=True)
json.dump(res, open(os.path.join(args.out, f'REFINE_{args.family}_l{l}_{args.cls}_{os.path.basename(args.pt)}.json'), 'w'))
