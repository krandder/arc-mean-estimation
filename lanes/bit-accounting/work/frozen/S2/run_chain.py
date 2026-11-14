"""Part S2, the scrambling test: jointly trained chains of b-bit sign codes on small nets, exact Walsh spectra of the
transitions, and baselines with the same code size.

For a net (n x L, seed), an encoder class ('local' or 'unres', as in run_curves.py) and code sizes b in BS (one model
per b, trained side by side): layers l_0..l_m = {0, L/4, L/2, 3L/4, L-1}; encoders E_i -> c_i = sign(z_i) in {+-1}^b;
decoders D_i -> state at l_i -> fixed future; transitions T_i: {+-1}^b -> {+-1}^b (MLP, sign output, straight-through).
Loss = sum_i [nMSE(D_i(c_i)) + nMSE(D_i(chat_i))] + sum_i [BCE(T_i(c_i), c_{i+1}) + bit-mismatch(T_i(c_i), c_{i+1})],
chat_0 = c_0, chat_{i+1} = sign T_i(chat_i) (the chain run from c_0). Gradients reach every encoder, so the codes adapt
to be predictable (joint training fixes the basis freedom as far as training can).
Analysis per transition T_i (b <= 16): exact Walsh-Fourier spectrum of each output bit over all 2^b inputs (weight by
degree, total influence, relevant inputs); on the reachable codes (a 2^18-input sample): coverage, H(c_i),
H(c_{i+1} | c_i), the data majority map, accuracy of degree-1/2/3 polynomial threshold fits and of the best s-juntas.
Baselines (same b, same reachable codes): random permutation of {+-1}^b, random invertible XOR (GF(2)-linear) map,
random 2-juntas, dense random LTF.
usage: run_chain.py --configs 16x4 --seeds 9100 --classes local,unres --out /root/runs/S_chain
"""
import argparse
import itertools
import json
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import smallnets as sn  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--configs', default='16x4')
ap.add_argument('--seeds', default='9100')
ap.add_argument('--classes', default='local,unres')
ap.add_argument('--bs', default='4,8,12,16')
ap.add_argument('--steps', type=int, default=6000)
ap.add_argument('--batch', type=int, default=1024)
ap.add_argument('--lr', type=float, default=1e-3)
ap.add_argument('--P_eval', type=int, default=32768)
ap.add_argument('--P_reach', type=int, default=262144)
ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--out', required=True)
args = ap.parse_args()
torch.set_num_threads(args.threads)
os.makedirs(args.out, exist_ok=True)
DEV, DT = sn.DEV, sn.DT
BS = [int(b) for b in args.bs.split(',')]
K = max(BS)
M = len(BS)
T0 = time.time()


def ste_sign(z):
    t = torch.tanh(z)
    return t + (torch.sign(z) - t).detach()


class Chain(nn.Module):
    def __init__(self, n, layers, cls, frames, fr_a, h_star_w):
        super().__init__()
        self.layers, self.cls, self.frames, self.fr_a = layers, cls, frames, fr_a
        self.register_buffer('mask', (torch.arange(K, device=DEV)[None, None, :] <
                                      torch.tensor(BS, device=DEV).view(M, 1, 1)).to(DT))
        mk = lambda d_in: (sn.BMLP(M, d_in, K, n, 1, act='relu') if cls == 'local' else  # noqa: E731
                           sn.BMLP(M, d_in, K, 256, 3))
        self.enc = nn.ModuleList([mk(n if cls == 'local' else 2 * n) for _ in layers])
        self.dec = nn.ModuleList([sn.BMLP(M, K, n, 256, 3, last_scale=0.0) for _ in layers])
        for i, l in enumerate(layers):
            with torch.no_grad():
                self.dec[i].bs[-1].copy_(h_star_w[i].view(1, 1, n).expand(M, 1, n))
        self.T = nn.ModuleList([sn.BMLP(M, K, K, 256, 2) for _ in layers[:-1]])

    def code(self, i, h, a):
        fr = self.frames[i]
        x = (h - fr['m']) @ fr['Sm12']
        if self.cls == 'unres':
            x = torch.cat([x, (a - self.fr_a['m']) @ self.fr_a['Sm12']], -1)
        z = self.enc[i](x.unsqueeze(0).expand(M, *x.shape))
        return ste_sign(z) * self.mask

    def decode(self, i, c):
        fr = self.frames[i]
        return fr['m'] + self.dec[i](c) @ fr['S12']

    def trans(self, i, c):
        return self.T[i](c)                              # logits (M, B, K)


def fwht(f):
    """Walsh-Hadamard transform along the last axis (length 2^b), normalised: fhat(S) = 2^-b sum_x f(x) chi_S(x)."""
    f = f.clone()
    N = f.shape[-1]
    hlen = 1
    while hlen < N:
        f = f.view(*f.shape[:-1], N // (2 * hlen), 2, hlen)
        a, b = f[..., 0, :], f[..., 1, :]
        f = torch.stack([a + b, a - b], -2).reshape(*f.shape[:-3], N)
        hlen *= 2
    return f / N


def all_codes(b):
    j = torch.arange(2 ** b, device=DEV)
    bits = ((j[:, None] >> torch.arange(b, device=DEV)[None, :]) & 1).to(DT)
    return 1.0 - 2.0 * bits                              # x_k = (-1)^{bit_k(j)}, matches fwht's ordering


def walsh_profile(F, b):
    """F (2^b, Kout) in {+-1}: per output, Fourier weight by degree, total influence, relevant inputs."""
    fh = fwht(F.T.double())                              # (Kout, 2^b)
    deg = torch.tensor([bin(s).count('1') for s in range(2 ** b)], device=DEV)
    W = torch.stack([(fh[:, deg == d] ** 2).sum(1) for d in range(b + 1)], 1)   # (Kout, b+1)
    I_tot = (W * torch.arange(b + 1, device=DEV)[None, :]).sum(1)
    # influence of input k: sum over S containing k of fhat(S)^2
    S = torch.arange(2 ** b, device=DEV)
    inf = torch.stack([(fh[:, ((S >> k) & 1) == 1] ** 2).sum(1) for k in range(b)], 1)
    return W.cpu().numpy(), I_tot.cpu().numpy(), (inf > 0.01).sum(1).cpu().numpy()


def code_index(c, b):
    bits = (c[..., :b] < 0).long()
    return (bits * (1 << torch.arange(b, device=DEV))).sum(-1)


def monomials(C, deg):
    b = C.shape[1]
    feats = [torch.ones(C.shape[0], 1, device=DEV)]
    for d in range(1, deg + 1):
        for S in itertools.combinations(range(b), d):
            feats.append(C[:, list(S)].prod(1, keepdim=True))
    return torch.cat(feats, 1)


def ptf_accuracy(C, Y, w, deg, steps=400):
    """Weighted accuracy of the best degree-<= deg polynomial threshold fits (logistic regression) of Y (+-1, (N, Kout))
    on inputs C (+-1, (N, b)) with weights w (N,)."""
    X = monomials(C, deg)
    Wt = torch.zeros(X.shape[1], Y.shape[1], device=DEV, requires_grad=True)
    opt = torch.optim.Adam([Wt], lr=0.05)
    tgt = (Y > 0).to(DT)
    wn = (w / w.sum())[:, None]
    for _ in range(steps):
        loss = (nn.functional.binary_cross_entropy_with_logits(X @ Wt, tgt, reduction='none') * wn).sum() / Y.shape[1]
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        acc = (((X @ Wt) > 0).to(DT) == tgt).to(DT)
        return (acc * wn).sum(0).cpu().numpy()            # per output bit


def junta_accuracy(C, Y, w, smax=6):
    """Greedy best s-junta per output bit on the weighted reachable set: lookup table of the majority of Y over the
    2^s patterns of the chosen inputs. Returns (Kout, smax) accuracies."""
    N, b = C.shape
    bits = (C < 0).long()
    out = np.zeros((Y.shape[1], smax))
    wn = w / w.sum()
    for j in range(Y.shape[1]):
        y = (Y[:, j] > 0).long()
        chosen = []
        for s in range(1, smax + 1):
            best, bacc = None, -1.0
            for k in range(b):
                if k in chosen:
                    continue
                idx = torch.zeros(N, dtype=torch.long, device=DEV)
                for t, kk in enumerate(chosen + [k]):
                    idx = idx + (bits[:, kk] << t)
                p1 = torch.zeros(2 ** s, device=DEV).index_add_(0, idx, wn * y)
                p0 = torch.zeros(2 ** s, device=DEV).index_add_(0, idx, wn * (1 - y))
                acc = float(torch.maximum(p0, p1).sum())
                if acc > bacc:
                    best, bacc = k, acc
            chosen.append(best)
            out[j, s - 1] = bacc
    return out


def cond_entropy(ci, cj, b):
    """Plug-in H(c_i), H(c_j | c_i) in bits from paired codes (index tensors)."""
    N = ci.shape[0]
    pi = torch.bincount(ci, minlength=2 ** b).double() / N
    H_i = float(-(pi[pi > 0] * torch.log2(pi[pi > 0])).sum())
    joint = ci * (2 ** b) + cj
    u, cnt = torch.unique(joint, return_counts=True)
    pj = cnt.double() / N
    H_ij = float(-(pj * torch.log2(pj)).sum())
    return H_i, H_ij - H_i


def baseline_maps(b, rng):
    perm = torch.tensor(rng.permutation(2 ** b), device=DEV)
    A = None
    while A is None:
        cand = rng.integers(0, 2, (b, b))
        # invertible over GF(2)?
        Mx = cand.copy()
        r = 0
        for c_ in range(b):
            piv = [i for i in range(r, b) if Mx[i, c_]]
            if not piv:
                continue
            Mx[[r, piv[0]]] = Mx[[piv[0], r]]
            for i in range(b):
                if i != r and Mx[i, c_]:
                    Mx[i] ^= Mx[r]
            r += 1
        if r == b:
            A = torch.tensor(cand, device=DEV)
    J2 = [rng.choice(b, 2, replace=False) for _ in range(b)]
    tables = [torch.tensor(rng.choice([-1.0, 1.0], 4), device=DEV, dtype=DT) for _ in range(b)]
    WL = torch.tensor(rng.standard_normal((b, b)), device=DEV, dtype=DT)
    bL = torch.tensor(rng.standard_normal(b) * 0.3, device=DEV, dtype=DT)

    def f_perm(C):
        j = code_index(C, b)
        jj = perm[j]
        return 1.0 - 2.0 * ((jj[:, None] >> torch.arange(b, device=DEV)[None, :]) & 1).to(DT)

    def f_xor(C):
        bits = (C < 0).long()
        y = (bits @ A.T) % 2
        return 1.0 - 2.0 * y.to(DT)

    def f_junta(C):
        bits = (C < 0).long()
        return torch.stack([tables[k][bits[:, J2[k][0]] * 2 + bits[:, J2[k][1]]] for k in range(b)], 1)

    def f_ltf(C):
        return torch.sign(C @ WL + bL + 1e-9)

    return dict(perm=f_perm, xor=f_xor, junta2=f_junta, ltf=f_ltf)


def analyse_map(f, b, Cr, wr):
    """Walsh profile over all inputs and degree/junta accuracies on the weighted reachable set for a map f."""
    allc = all_codes(b)
    F = f(allc)
    W, I_tot, nrel = walsh_profile(F, b)
    Yr = f(Cr)
    rec = dict(W_by_degree=W.mean(0).tolist(), I_total=float(I_tot.mean()), n_relevant=float(nrel.mean()))
    rec['ptf_acc'] = {str(d): float(ptf_accuracy(Cr, Yr, wr, d).mean()) for d in (1, 2, 3) if b <= 16}
    if b <= 12:
        rec['junta_acc'] = junta_accuracy(Cr, Yr, wr, smax=min(6, b)).mean(0).tolist()
    return rec


for cfg in args.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    for seed in [int(s) for s in args.seeds.split(',')]:
        net = sn.Net(seed, n, L)
        gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
        Hp, Ap = net.sample(65536, set(layers), gp)
        V = float(Ap.double().var(0).sum())
        fr_a = sn.frame(Ap)
        frames = [sn.frame(Hp[l]) for l in layers]
        i_star = int(((Ap - Ap.mean(0)) ** 2).sum(1).argmin())
        h_star_w = [(Hp[l][i_star] - frames[i]['m']) @ frames[i]['Sm12'] for i, l in enumerate(layers)]
        for cls in args.classes.split(','):
            tag = f'C_n{n}_L{L}_s{seed}_{cls}'
            path = os.path.join(args.out, tag + '.json')
            if os.path.exists(path):
                continue
            t1 = time.time()
            ch = Chain(n, layers, cls, frames, fr_a, h_star_w)
            opt = torch.optim.Adam(ch.parameters(), lr=args.lr)
            warm = max(1, args.steps // 50)
            sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / warm) * (
                0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps))))
            gt = torch.Generator(device=DEV).manual_seed(50_000 + seed * 7 + n * 13 + L + (0 if cls == 'local' else 1))
            for step in range(args.steps):
                Hb, Ab = net.sample(args.batch, set(layers), gt)
                cs = [ch.code(i, Hb[l], Ab) for i, l in enumerate(layers)]
                loss = 0.0
                chat = cs[0]
                for i, l in enumerate(layers):
                    rec = net.run(ch.decode(i, cs[i]), l)
                    loss = loss + (((rec - Ab) ** 2).sum(-1).mean(-1) / V).sum()
                    if i > 0:
                        rch = net.run(ch.decode(i, chat), l)
                        loss = loss + (((rch - Ab) ** 2).sum(-1).mean(-1) / V).sum()
                    if i < len(layers) - 1:
                        lg = ch.trans(i, cs[i])
                        tgt = (cs[i + 1].detach() > 0).to(DT)
                        bce = (nn.functional.binary_cross_entropy_with_logits(lg, tgt, reduction='none')
                               * ch.mask).sum((1, 2)) / (ch.mask.sum((1, 2)) * args.batch)
                        mism = (((ste_sign(lg) - cs[i + 1]) ** 2) * ch.mask).sum((1, 2)) / (4 * ch.mask.sum((1, 2)) * args.batch)
                        loss = loss + bce.sum() + mism.sum()
                        chat = ste_sign(ch.trans(i, chat)) * ch.mask
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(ch.parameters(), 10.0)
                opt.step()
                sched.step()
            ch.eval()
            res = dict(n=n, L=L, seed=seed, cls=cls, layers=layers, bs=BS, V=V, train_seconds=time.time() - t1,
                       per_b={})
            with torch.no_grad():
                ge = torch.Generator(device=DEV).manual_seed(60_000 + seed)
                He, Ae = net.sample(args.P_eval, set(layers), ge)
                cs = [ch.code(i, He[l], Ae) for i, l in enumerate(layers)]
                own, chain, agree = [], [], []
                chat = cs[0]
                for i, l in enumerate(layers):
                    own.append((((net.run(ch.decode(i, cs[i]), l) - Ae) ** 2).sum(-1).mean(-1) / V).tolist())
                    chain.append((((net.run(ch.decode(i, chat), l) - Ae) ** 2).sum(-1).mean(-1) / V).tolist())
                    if i < len(layers) - 1:
                        pred = torch.sign(ch.trans(i, cs[i])) * ch.mask
                        agree.append(((pred == cs[i + 1]).to(DT) * ch.mask).sum((1, 2)).div(
                            ch.mask.sum((1, 2)) * args.P_eval).tolist())
                        chat = torch.sign(ch.trans(i, chat)) * ch.mask
                gr = torch.Generator(device=DEV).manual_seed(70_000 + seed)
                Hr, Ar = net.sample(args.P_reach, set(layers), gr)
                cr = [ch.code(i, Hr[l], Ar) for i, l in enumerate(layers)]
            rng = np.random.default_rng(80_000 + seed)
            for mi, b in enumerate(BS):
                ent = dict(own_nmse=[o[mi] for o in own], chain_nmse=[c[mi] for c in chain],
                           bit_agreement=[a[mi] for a in agree], transitions=[])
                for i in range(len(layers) - 1):
                    ci, cj = code_index(cr[i][mi], b), code_index(cr[i + 1][mi], b)
                    H_i, H_ji = cond_entropy(ci, cj, b)
                    uniq, inv, cnt = torch.unique(ci, return_inverse=True, return_counts=True)
                    # data majority map on reachable codes
                    sums = torch.zeros(len(uniq), K, device=DEV).index_add_(0, inv, cr[i + 1][mi])
                    Ymaj = torch.sign(sums[:, :b] + 1e-9)
                    first = torch.zeros(len(uniq), dtype=torch.long, device=DEV).scatter_(0, inv, torch.arange(len(inv), device=DEV))
                    Cr = cr[i][mi][first][:, :b]
                    wr = cnt.to(DT)
                    with torch.no_grad():
                        F = torch.sign(ch.trans(i, torch.cat([all_codes(b), torch.zeros(2 ** b, K - b, device=DEV)], 1)
                                                .unsqueeze(0).expand(M, 2 ** b, K))[mi][:, :b] + 1e-9)
                    W, I_tot, nrel = walsh_profile(F, b)
                    tr = dict(H_in=H_i, H_out_given_in=H_ji, n_reachable=int(len(uniq)), coverage=len(uniq) / 2 ** b,
                              learned_T=dict(W_by_degree=W.mean(0).tolist(), I_total=float(I_tot.mean()),
                                             n_relevant=float(nrel.mean())))
                    with torch.no_grad():
                        Tr = torch.sign(ch.trans(i, torch.cat([Cr, torch.zeros(len(Cr), K - b, device=DEV)], 1)
                                                 .unsqueeze(0).expand(M, len(Cr), K))[mi][:, :b] + 1e-9)
                    tr['T_vs_majority'] = float(((Tr == Ymaj).to(DT) * (wr / wr.sum())[:, None]).sum() / b)
                    tr['majority_ptf_acc'] = {str(d): float(ptf_accuracy(Cr, Ymaj, wr, d).mean()) for d in (1, 2, 3)}
                    if b <= 12:
                        tr['majority_junta_acc'] = junta_accuracy(Cr, Ymaj, wr, smax=min(6, b)).mean(0).tolist()
                    tr['baselines'] = {k: analyse_map(f, b, Cr, wr) for k, f in baseline_maps(b, rng).items()}
                    ent['transitions'].append(tr)
                res['per_b'][str(b)] = ent
            res['seconds'] = time.time() - t1
            with open(path, 'w') as f:
                json.dump(res, f)
            for b in BS:
                e = res['per_b'][str(b)]
                print(f'{tag} b={b}: own ' + ' '.join(f'{v:.3g}' for v in e['own_nmse']) + ' | chain ' +
                      ' '.join(f'{v:.3g}' for v in e['chain_nmse']) + ' | W1 learned ' +
                      ' '.join(f'{t["learned_T"]["W_by_degree"][1]:.2f}' for t in e['transitions']) + ' | ptf1 maj ' +
                      ' '.join(f'{t["majority_ptf_acc"]["1"]:.3f}' for t in e['transitions']) +
                      f' | {res["seconds"]:.0f}s total {time.time() - T0:.0f}s', flush=True)
print('ALL DONE', f'{time.time() - T0:.0f}s', flush=True)
