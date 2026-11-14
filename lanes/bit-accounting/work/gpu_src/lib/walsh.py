"""Walsh-Fourier and degree statistics for maps between b-bit sign codes (copied from scripts/run_chain.py so that other
scripts can import them; same definitions)."""
import itertools

import numpy as np
import torch
import torch.nn as nn

import smallnets as sn

DEV, DT = sn.DEV, sn.DT


def fwht(f):
    """Normalised Walsh-Hadamard transform along the last axis (length 2^b): fhat(S) = 2^-b sum_x f(x) chi_S(x)."""
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
    return 1.0 - 2.0 * bits


def code_index(c, b):
    bits = (c[..., :b] < 0).long()
    return (bits * (1 << torch.arange(b, device=DEV))).sum(-1)


def walsh_profile(F, b):
    """F (2^b, Kout) in {+-1}: mean over outputs of the Fourier weight by degree, total influence, relevant inputs."""
    fh = fwht(F.T.double())
    deg = torch.tensor([bin(s).count('1') for s in range(2 ** b)], device=DEV)
    W = torch.stack([(fh[:, deg == d] ** 2).sum(1) for d in range(b + 1)], 1)
    I_tot = (W * torch.arange(b + 1, device=DEV)[None, :]).sum(1)
    S = torch.arange(2 ** b, device=DEV)
    inf = torch.stack([(fh[:, ((S >> k) & 1) == 1] ** 2).sum(1) for k in range(b)], 1)
    return W.cpu().numpy(), I_tot.cpu().numpy(), (inf > 0.01).sum(1).cpu().numpy()


def monomials(C, deg):
    b = C.shape[1]
    feats = [torch.ones(C.shape[0], 1, device=DEV)]
    for d in range(1, deg + 1):
        for S in itertools.combinations(range(b), d):
            feats.append(C[:, list(S)].prod(1, keepdim=True))
    return torch.cat(feats, 1)


def ptf_accuracy(C, Y, w, deg, steps=400):
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
        return (acc * wn).sum(0).cpu().numpy()


def cond_entropy(ci, cj, b):
    N = ci.shape[0]
    pi = torch.bincount(ci, minlength=2 ** b).double() / N
    H_i = float(-(pi[pi > 0] * torch.log2(pi[pi > 0])).sum())
    joint = ci * (2 ** b) + cj
    u, cnt = torch.unique(joint, return_counts=True)
    pj = cnt.double() / N
    H_ij = float(-(pj * torch.log2(pj)).sum())
    return H_i, H_ij - H_i


def reachable_majority(ci_codes, cj_codes, b):
    """Reachable input codes (one representative each), their weights, and the data majority of the next code."""
    ci = code_index(ci_codes, b)
    uniq, inv, cnt = torch.unique(ci, return_inverse=True, return_counts=True)
    sums = torch.zeros(len(uniq), b, device=DEV).index_add_(0, inv, cj_codes[:, :b])
    Ymaj = torch.sign(sums + 1e-9)
    first = torch.zeros(len(uniq), dtype=torch.long, device=DEV).scatter_(0, inv, torch.arange(len(inv), device=DEV))
    return ci_codes[first][:, :b], cnt.to(DT), Ymaj


def baseline_maps(b, rng):
    perm = torch.tensor(rng.permutation(2 ** b), device=DEV)
    A = None
    while A is None:
        cand = rng.integers(0, 2, (b, b))
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
        jj = perm[code_index(C, b)]
        return 1.0 - 2.0 * ((jj[:, None] >> torch.arange(b, device=DEV)[None, :]) & 1).to(DT)

    def f_xor(C):
        y = torch.remainder((C < 0).double() @ A.T.double(), 2.0)
        return 1.0 - 2.0 * y.to(DT)

    def f_junta(C):
        bits = (C < 0).long()
        return torch.stack([tables[k][bits[:, J2[k][0]] * 2 + bits[:, J2[k][1]]] for k in range(b)], 1)

    def f_ltf(C):
        return torch.sign(C @ WL + bL + 1e-9)

    return dict(perm=f_perm, xor=f_xor, junta2=f_junta, ltf=f_ltf)


def analyse_map(f, b, Cr, wr):
    F = f(all_codes(b))
    W, I_tot, nrel = walsh_profile(F, b)
    Yr = f(Cr)
    rec = dict(W_by_degree=W.mean(0).tolist(), I_total=float(I_tot.mean()), n_relevant=float(nrel.mean()))
    rec['ptf_acc'] = {str(d): float(ptf_accuracy(Cr, Yr, wr, d).mean()) for d in (1, 2, 3)}
    return rec
