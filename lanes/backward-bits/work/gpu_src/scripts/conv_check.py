"""Estimator convergence for a saved chain: at the given layers, with the chain's own codes c_l and c_{l+1} fixed,
recompute T_l = I(h_l; c_{l+1}), H(c_l) and I(c_l; c_{l+1}) on fresh points for several (N, M); and the truth
I(h_l; c_L) for several M. Chains with the next-code target (K, R) only.
usage: conv_check.py --n 16 --L 16 --seed 9100 --sigma 0.1 --KL 64 --chain K --layers 14,8,0 --out runs_gpu/dev
"""
import argparse
import json
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
ap.add_argument('--chain', default='K')
ap.add_argument('--layers', required=True)
ap.add_argument('--Ns', default='32768,65536,131072')
ap.add_argument('--Ms', default='256,1024,4096')
ap.add_argument('--device', default='cpu')
ap.add_argument('--out', required=True)
args = ap.parse_args()
dev = args.device
L = args.L
odir = os.path.join(args.out, f'n{args.n}L{args.L}_s{args.seed}_sig{args.sigma:g}_K{args.KL}')
cdir = os.path.join(odir, 'chain' + args.chain)
net = bb.Net(args.seed, args.n, L, args.sigma, dev)
oc = torch.load(os.path.join(odir, 'outcode.pt'), map_location=dev)
out_code = bb.OutCode(oc['C'].to(dev), net)


def load(l):
    if l == L - 1:
        return out_code
    return bb.load_code(lambda k: os.path.join(cdir, f'code_l{k}.pt'), l, L, net, out_code, dev)


res = {}
for l in [int(x) for x in args.layers.split(',')]:
    code, nxt = load(l), load(l + 1)
    rows = []
    for N in [int(x) for x in args.Ns.split(',')]:
        for M in [int(x) for x in args.Ms.split(',')]:
            t0 = time.time()
            g = bb.make_gen(dev, 'conv', args.seed, l, N, M)
            h = net.sample(N, l, g)
            cnt = bb.mc_counts_next(net, l, h, nxt, M, g)
            st = bb.target_stats(cnt)
            r = bb.relevance(code.assign(h), cnt, code.K)
            cnt_o = bb.mc_counts_out(net, l, h, out_code, M, g)
            so = bb.target_stats(cnt_o)
            ro = bb.relevance(code.assign(h), cnt_o, code.K)
            rows.append(dict(N=N, M=M, T=st['T'], T_gr=st['T_gr'], se=st['se'], H=r['H'], I=r['I'],
                             I_plugin=r['I_plugin'], I_star=so['T'], I_star_gr=so['T_gr'], I_out=ro['I'],
                             sec=time.time() - t0))
            print(f"l={l} N={N} M={M}: T {st['T']:.4f} (gr {st['T_gr']:.4f}, se {st['se']:.4f}) H {r['H']:.4f} "
                  f"I {r['I']:.4f} | I* {so['T']:.4f} (gr {so['T_gr']:.4f}) I_out {ro['I']:.4f}", flush=True)
    res[str(l)] = rows
json.dump(res, open(os.path.join(cdir, 'conv_check.json'), 'w'), indent=1)
