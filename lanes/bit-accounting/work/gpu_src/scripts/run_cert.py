"""Part S5: convergence certificates for the binary bottlenecks (Kelvin, relayed by main 01:3xZ).
For each (net, layer, class) cell and variant, train 8 sign-bit bottlenecks (b = 1, 2, 3, 4, 6, 8, 12, 16) as in
run_curves.py and certify them with quantiser optimality conditions, on a fit sample (2^16) and an eval sample (2^15):
  model     nMSE of the trained encoder + decoder + real future;
  centroid  the decoder replaced by the per-code mean of the output (fit sample; unseen codes keep the learned
            decoder): the best output any decoder can give for this encoder; drop = model - centroid;
  nn        one Lloyd step: every sample reassigned to the code whose centroid is nearest its output, centroids
            recomputed (an encoder that can compute the output could do this); drop = centroid - nn;
  within    (local and linear classes) the class's encoder fine-tuned for 500 steps to emit the nn-assigned codes,
            then the centroid decoder: the part of the Lloyd gain reachable inside the class; restriction cost =
            within - nn.
Variants: base (width 256, 1500 steps), big (width 512, 3000 steps), and restarts r1, r2 (base settings, other seeds).
Toy known answer (--toy): output space, n = 16, a = table[sign bits of x_1..x_k] with 2^k random entries; the encoder
sees x (local, one ReLU layer) or (x, a) (unres); the decoder predicts a directly. The count for nMSE 0.001 must be k.
usage: run_cert.py --configs 16x16 --seed 5000 --out /root/runs/S_cert   |   run_cert.py --toy 2,4,8 --out ...
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
ap.add_argument('--configs', default='16x16')
ap.add_argument('--seed', type=int, default=5000)
ap.add_argument('--classes', default='local,unres')
ap.add_argument('--variants', default='base,big,deep,r1,r2')
ap.add_argument('--toy', default='')
ap.add_argument('--batch', type=int, default=2048)
ap.add_argument('--out', required=True)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
DEV, DT = sn.DEV, sn.DT
RATES = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0]
VAR = dict(smoke=(64, 20, 0, 3), base=(256, 1500, 0, 3), big=(512, 3000, 0, 3), deep=(512, 3000, 0, 5), r1=(256, 1500, 1, 3),
           r2=(256, 1500, 2, 3))
T0 = time.time()


def code_idx(c):
    """(M, B, K) +-1/0 codes -> (M, B) integer index of the first 16 bits (masked bits are 0 -> treated as +1)."""
    bits = (c[..., :16] < 0).long()
    return (bits * (1 << torch.arange(16, device=DEV))).sum(-1)


def certify(m, enc_in_fit, enc_in_eval, a_fit, a_eval, out_fn_eval, V, cls, train_fn=None):
    """Centroid / nearest-neighbour / within-class tests for the M models of one Bottlenecks group."""
    with torch.no_grad():
        cf = m.code(m.enc(enc_in_fit))            # (M, Bf, K)
        ce = m.code(m.enc(enc_in_eval))
        model_out = out_fn_eval(ce)               # (M, Be, n) decoded and pushed through the future
    res = []
    for mi in range(m.M):
        i_f, i_e = code_idx(cf[mi]), code_idx(ce[mi])
        N = 1 << 16
        s = torch.zeros(N, a_fit.shape[1], device=DEV, dtype=torch.float64).index_add_(0, i_f, a_fit.double())
        cnt = torch.bincount(i_f, minlength=N).double()
        cen = s / cnt.clamp(min=1)[:, None]
        seen = cnt[i_e] > 0
        pred = torch.where(seen[:, None], cen[i_e], model_out[mi].double())
        mod = float(((model_out[mi].double() - a_eval.double()) ** 2).sum(1).mean() / V)
        cent = float(((pred - a_eval.double()) ** 2).sum(1).mean() / V)
        occ = torch.nonzero(cnt > 0).flatten()
        C = cen[occ]                                                    # occupied centroids
        def nn_assign(A):                                               # noqa: E306
            best = torch.empty(A.shape[0], dtype=torch.long, device=DEV)
            for c0 in range(0, A.shape[0], 4096):
                d = torch.cdist(A[c0:c0 + 4096].double(), C)
                best[c0:c0 + 4096] = d.argmin(1)
            return best
        nf, ne = nn_assign(a_fit), nn_assign(a_eval)
        s2 = torch.zeros(len(occ), a_fit.shape[1], device=DEV, dtype=torch.float64).index_add_(0, nf, a_fit.double())
        c2 = torch.bincount(nf, minlength=len(occ)).double()
        cen2 = torch.where((c2 > 0)[:, None], s2 / c2.clamp(min=1)[:, None], C)
        nn = float(((cen2[ne] - a_eval.double()) ** 2).sum(1).mean() / V)
        r = dict(rate=RATES[mi], model=mod, centroid=cent, nn=nn, occupied=int(len(occ)), unseen_eval=float((~seen).float().mean()))
        if train_fn is not None:
            # target codes: the nn-assigned centroid's code pattern (bits of the occupied code index)
            tgt_f = occ[nf]
            r['within'] = train_fn(mi, tgt_f, cen, i_f)
        res.append(r)
    return res


def train_group(models, sample_fn, steps, out_fn, V, seed):
    params = [p for m in models for p in m.parameters()]
    opt = torch.optim.Adam(params, lr=1e-3)
    warm = max(1, steps // 50)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / warm) * (
        0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, steps) / steps))))
    g = torch.Generator(device=DEV).manual_seed(seed)
    for step in range(steps):
        xin, a = sample_fn(args.batch, g)
        loss = 0.0
        for m in models:
            ah = out_fn(m.dec_out(m.code(m.enc(xin), g)))
            loss = loss + (((ah - a) ** 2).sum(-1).mean(-1) / V).sum()
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 10.0)
        opt.step()
        sched.step()


class Group(torch.nn.Module):
    """M sign-bit bottlenecks; encoder input already whitened (and concatenated for unres)."""

    def __init__(self, d_in, n_out, cls, width, h_star, depth=3):
        super().__init__()
        M, K = len(RATES), 16
        self.M, self.K = M, K
        if cls == 'local':
            self.encm = sn.BMLP(M, d_in, K, d_in if d_in <= 64 else 64, 1, act='relu')
        elif cls == 'linear':
            self.encm = sn.BMLP(M, d_in, K, d_in, 0)
        else:
            self.encm = sn.BMLP(M, d_in, K, width, depth)
        self.dec = sn.BMLP(M, K, n_out, width, 3, last_scale=0.0)
        with torch.no_grad():
            self.dec.bs[-1].copy_(h_star.view(1, 1, -1).expand(M, 1, n_out))
        j = torch.arange(K, device=DEV)[None, None, :]
        self.register_buffer('mask', (j < torch.tensor(RATES, device=DEV).view(M, 1, 1)).to(DT))

    def enc(self, x):
        return self.encm(x.unsqueeze(0).expand(self.M, *x.shape))

    def code(self, z, g=None):
        sd = z.detach().std(1, keepdim=True).clamp(min=1e-3)
        t = torch.tanh(z / sd)
        c = t + (torch.where(z > 0, 1.0, -1.0) - t).detach()
        return c * self.mask

    def dec_out(self, c):
        return self.dec(c)


def within_class_fn(m, x_fit, x_eval, a_eval, out_fn_eval, V, cls):
    """Fine-tune a copy of the class encoder to emit the nn-assigned codes, then evaluate with the centroid decoder."""
    import copy

    def fn(mi, tgt_idx, cen, i_f_old):
        if cls == 'unres':
            return None
        enc = copy.deepcopy(m.encm)
        opt = torch.optim.Adam(enc.parameters(), lr=1e-3)
        b = int(RATES[mi])
        tbits = (((tgt_idx[:, None] >> torch.arange(b, device=DEV)[None, :]) & 1) == 0).to(DT)   # 1 = +1
        g = torch.Generator(device=DEV).manual_seed(77 + mi)
        for step in range(500):
            idx = torch.randint(0, x_fit.shape[0], (2048,), generator=g, device=DEV)
            z = enc(x_fit[idx].unsqueeze(0).expand(m.M, 2048, x_fit.shape[1]))[mi][:, :b]
            loss = torch.nn.functional.binary_cross_entropy_with_logits(z, tbits[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
        with torch.no_grad():
            zf = enc(x_fit.unsqueeze(0).expand(m.M, *x_fit.shape))[mi][:, :b]
            ze = enc(x_eval.unsqueeze(0).expand(m.M, *x_eval.shape))[mi][:, :b]
            bits_f = (zf < 0).long()
            bits_e = (ze < 0).long()
            i_f = (bits_f * (1 << torch.arange(b, device=DEV))).sum(1)
            i_e = (bits_e * (1 << torch.arange(b, device=DEV))).sum(1)
            N = 1 << b
            s = torch.zeros(N, a_eval.shape[1], device=DEV, dtype=torch.float64).index_add_(0, i_f, A_FIT[0].double())
            cnt = torch.bincount(i_f, minlength=N).double()
            cen2 = s / cnt.clamp(min=1)[:, None]
            seen = cnt[i_e] > 0
            mean_a = A_FIT[0].double().mean(0)
            pred = torch.where(seen[:, None], cen2[i_e], mean_a[None, :])
            return float(((pred - a_eval.double()) ** 2).sum(1).mean() / V)
    return fn


A_FIT = [None]
results = {}
if args.toy:
    n = 16
    for k in [int(v) for v in args.toy.split(',')]:
        gtab = torch.Generator(device=DEV).manual_seed(900 + k)
        table = torch.randn(2 ** k, n, generator=gtab, device=DEV)

        def sample(P, g, k=k, table=table):
            x = torch.randn(P, n, generator=g, device=DEV)
            idx = ((x[:, :k] < 0).long() * (1 << torch.arange(k, device=DEV))).sum(1)
            return x, table[idx]
        gf = torch.Generator(device=DEV).manual_seed(5)
        xf, af = sample(65536, gf)
        xe, ae = sample(32768, gf)
        V = float(af.double().var(0).sum())
        for cls in ['local', 'unres']:
            for var in ['base']:
                width, steps, r, depth = VAR[var]
                d_in = n if cls == 'local' else 2 * n
                grp = Group(d_in, n, cls, width, af.mean(0), depth)
                inp = (lambda x, a: x) if cls == 'local' else (lambda x, a: torch.cat([x, a], 1))

                def sfn(P, g, inp=inp):
                    x, a = sample(P, g)
                    return inp(x, a), a
                train_group([grp], sfn, steps, lambda h: h, V, 123 + k + r)
                with torch.no_grad():
                    ce = grp.code(grp.enc(inp(xe, ae)))
                    out = grp.dec_out(ce)
                    nm = (((out - ae) ** 2).sum(-1).mean(-1) / V).tolist()
                A_FIT[0] = af
                cert = certify(grp, inp(xf, af), inp(xe, ae), af, ae, lambda c: grp.dec_out(c), V, cls,
                               within_class_fn(grp, inp(xf, af), inp(xe, ae), ae, None, V, cls))
                results[f'toy_k{k}_{cls}'] = dict(k=k, cls=cls, nmse=nm, cert=cert,
                                                  b_0001=sn.crossing(RATES, nm, 0.001), b_001=sn.crossing(RATES, nm, 0.01))
                print(f'toy k={k} {cls}: nMSE by b {[round(v, 4) for v in nm]} -> b(0.001) {results[f"toy_k{k}_{cls}"]["b_0001"]}'
                      f' | {time.time() - T0:.0f}s', flush=True)
                json.dump(results, open(os.path.join(args.out, 'toy.json'), 'w'))
else:
    for cfg in args.configs.split(','):
        n, L = [int(v) for v in cfg.split('x')]
        net = sn.Net(args.seed, n, L)
        layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
        gp = torch.Generator(device=DEV).manual_seed(10_000 + args.seed * 7 + n * 13 + L)
        Hp, Ap = net.sample(65536, set(layers), gp)
        Hp[L] = Ap
        V = float(Ap.double().var(0).sum())
        fr_a = sn.frame(Ap)
        ge = torch.Generator(device=DEV).manual_seed(20_000 + args.seed * 7 + n * 13 + L)
        He, Ae = net.sample(32768, set(layers), ge)
        He[L] = Ae
        A_FIT[0] = Ap
        i_star = int(((Ap - Ap.mean(0)) ** 2).sum(1).argmin())
        for l in layers + [L]:
            fr = sn.frame(Hp[l]) if l < L else fr_a
            h_star = (Hp[l][i_star] - fr['m']) @ fr['Sm12']
            wh = lambda h: (h - fr['m']) @ fr['Sm12']  # noqa: E731
            wa = lambda a: (a - fr_a['m']) @ fr_a['Sm12']  # noqa: E731
            for cls in (args.classes.split(',') if l < L else ['unres']):
                inp = (lambda h, a: wh(h)) if cls in ('local', 'linear') else (lambda h, a: torch.cat([wh(h), wa(a)], 1))
                for var in args.variants.split(','):
                    tag = f'Z_n{n}_L{L}_s{args.seed}_l{l}_{cls}_{var}'
                    path = os.path.join(args.out, tag + '.json')
                    if os.path.exists(path):
                        continue
                    t1 = time.time()
                    width, steps, r, depth = VAR[var]
                    if var == 'deep' and cls != 'unres':
                        continue
                    grp = Group(n if cls != 'unres' else 2 * n, n, cls, width, h_star, depth)
                    out_fn = lambda zh, l=l, fr=fr: net.run(fr['m'] + zh @ fr['S12'], l)  # noqa: E731

                    def sfn(P, g, l=l, inp=inp):
                        Hb, Ab = net.sample(P, {l}, g)
                        hb = Ab if l == L else Hb[l]
                        return inp(hb, Ab), Ab
                    train_group([grp], sfn, steps, out_fn, V, 31_000 + args.seed + l * 7 + r * 1000 + (0 if cls == 'local' else 1))
                    grp.eval()
                    with torch.no_grad():
                        ce = grp.code(grp.enc(inp(He[l], Ae)))
                        nm = (((out_fn(grp.dec_out(ce)) - Ae) ** 2).sum(-1).mean(-1) / V).tolist()
                    cert = certify(grp, inp(Hp[l], Ap), inp(He[l], Ae), Ap, Ae, lambda c: out_fn(grp.dec_out(c)), V, cls,
                                   within_class_fn(grp, inp(Hp[l], Ap), inp(He[l], Ae), Ae, None, V, cls))
                    res = dict(n=n, L=L, seed=args.seed, l=l, cls=cls, variant=var, width=width, steps=steps, V=V,
                               rates=RATES, nmse=nm, cert=cert, seconds=time.time() - t1)
                    json.dump(res, open(path, 'w'))
                    print(f'{tag}: model {[round(c["model"], 3) for c in cert]} | centroid {[round(c["centroid"], 3) for c in cert]}'
                          f' | nn {[round(c["nn"], 3) for c in cert]} | {res["seconds"]:.0f}s total {time.time() - T0:.0f}s', flush=True)
print('ALL DONE', f'{time.time() - T0:.0f}s', flush=True)
