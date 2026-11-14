"""Part B: do the compressed coordinates get scrambled from layer to layer? (one net; no code training)

Codes: at each layer l the output-relevant coordinates u_l = Q_l^T Sigma_l^{-1/2} (h_l - m_l) along the active-subspace
basis (lib/lincodes.basis_as; the output PCA at l = L), the first K_l of them, K_l = the channels the layer's linear
analog code opens at capacity C_l (default: the capacity where that code reaches eps = 0.05 on this net, from
runs/lin_<net>_<seed>.json, capped at 256). Binary codes: c_l = sign(u_l) (the most significant bit of each
coordinate). Everything is measured on held-out inputs.

Measured for each layer pair (l, l'):
  real:   R^2 of linear and MLP maps u_l -> u_l' (importance-weighted by lam_l'), and the chain error: decode the predicted
          u_l' at layer l' (linear decoder, other coordinates at their mean) and push through the future; against the
          same decoder applied to the true u_l' (the code's own error).
  binary: bit accuracy (importance-weighted) of LTF (logistic), s-sparse LTF (s = 1, 2, 4, 8, 16, 32) and MLP
          transitions c_l -> c_l'; Walsh statistics of the fitted MLP and LTF transitions on uniform inputs (W^0, W^1,
          noise stability at rho in RHOS, total influence, relevant inputs) and around actual codes (influences, noise
          stability with bit-flip noise).
  baselines at the same (K_l, K_l'): random 3-parities, random K/2-parities, random dense 2-layer threshold nets,
          random dense LTFs, random 4-sparse LTFs (Walsh statistics on uniform inputs).
  avalanche: inputs x, x' with correlation rho_x; fraction of differing code bits and relative coordinate distance at
          every layer.
usage: chain_B.py arc 9100 [eps_rate=0.05] [P_fit=32768] [P_test=8192] -> runs(_dev)/B_<net>_<seed>.json
"""
import json
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import bitlib as bl  # noqa: E402
import lincodes as lc  # noqa: E402

torch.set_num_threads(2)
kind, seed = sys.argv[1], int(sys.argv[2])
eps_rate = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
P_fit = int(sys.argv[4]) if len(sys.argv) > 4 else 32768
P_test = int(sys.argv[5]) if len(sys.argv) > 5 else 8192
net = bl.make_net(kind, seed)
L = net.L
LAYERS = [8, 12, 16, 20, 24, 26, 28, 30, 31, 32] if kind == 'arc' else [8, 32, 64, 128, 192, 255, 256]
PAIRS = [(a, b) for a, b in zip(LAYERS[:-1], LAYERS[1:])] + ([(16, 24), (24, 32), (16, 32), (8, 16)] if kind == 'arc'
                                                             else [(8, 256)])
RHOS = [0.5, 0.8, 0.9, 0.95, 0.99]
outdir = 'runs' if seed < 9000 else 'runs_dev'
t0 = time.time()
rng = np.random.default_rng(71_000 + seed)


def states(X):
    H = {}
    h = X
    for k in range(L + 1):
        if k in LAYERS:
            H[k] = h.copy()
        if k < L:
            h = np.maximum(h @ net.WT64[k], 0.0)
    return H, h


Xf = rng.standard_normal((P_fit, net.n))
Xt = rng.standard_normal((P_test, net.n))
Hf, Af = states(Xf)
Ht, At = states(Xt)
V = float(At.var(0, ddof=1).sum())

# rates: capacity where the layer's linear analog code reaches eps_rate (registered M1 results of this net)
lin = json.load(open(f'{outdir}/lin_{kind}_{seed}.json')) if os.path.exists(f'{outdir}/lin_{kind}_{seed}.json') else None


def cap_for(l):
    if lin is None or str(l) not in lin['layers']:
        return 64.0
    ent = lin['layers'][str(l)]
    best = None
    for b in ['as', 'lin']:
        k = f'{b}_gauss'
        if k in ent:
            cur = ent[k]['curve']
            for c0, c1 in zip(cur[:-1], cur[1:]):
                if c1['nmse'] <= eps_rate < c0['nmse']:
                    f = (math.log(c0['nmse']) - math.log(eps_rate)) / (math.log(c0['nmse']) - math.log(c1['nmse']))
                    v = c0['rate'] + f * (c1['rate'] - c0['rate'])
                    best = v if best is None else min(best, v)
                    break
    return 256.0 if best is None else best


code = {}
for l in LAYERS:
    fr = lc.frame(Hf[l])
    if l < L:
        lam, Q = lc.basis_as(net, l, Hf[l][:4096], fr, q=4, seed=l)
    else:
        lam, Q = lc.basis_lin(Hf[l], Af, fr)
    C = cap_for(l)
    lo, hi = 1e-300, float(lam[0])
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        Ck = np.maximum(0.0, 0.5 * np.log2(np.maximum(lam, 1e-300) / mid))
        lo, hi = (mid, hi) if Ck.sum() > C else (lo, mid)
    Ck = np.maximum(0.0, 0.5 * np.log2(np.maximum(lam, 1e-300) / hi))
    K = int(max(2, min(256, (Ck > 0).sum())))
    Uf = ((Hf[l] - fr['m']) @ fr['Sm12']) @ Q[:, :K]
    Ut = ((Ht[l] - fr['m']) @ fr['Sm12']) @ Q[:, :K]
    code[l] = dict(fr=fr, Q=Q[:, :K], lam=lam[:K], K=K, C=C, Ck=Ck[:K], Uf=Uf, Ut=Ut)
    print(f'layer {l}: C = {C:.1f} bits, K = {K} active coordinates, {time.time() - t0:.0f}s', flush=True)


def decode_out(l, U):
    """Linear decoder of the layer-l coordinates (others at their mean), pushed through the future."""
    c = code[l]
    Hh = c['fr']['m'] + (U @ c['Q'].T) @ c['fr']['S12']
    with torch.no_grad():
        return net.run(torch.tensor(Hh, dtype=torch.float32), l).double().numpy()


def nmse(Ah):
    d = Ah - At
    return float((d * d).sum(1).mean() / V)


def fit_mlp(Xtr, Ytr, Xte, out_kind, steps=1500, width=512, lr=1e-3, seed_=0):
    torch.manual_seed(seed_)
    m = nn.Sequential(nn.Linear(Xtr.shape[1], width), nn.GELU(), nn.Linear(width, width), nn.GELU(),
                      nn.Linear(width, Ytr.shape[1]))
    opt = torch.optim.Adam(m.parameters(), lr=lr)
    Xtr_t = torch.tensor(Xtr, dtype=torch.float32)
    Ytr_t = torch.tensor(Ytr, dtype=torch.float32)
    g = torch.Generator().manual_seed(seed_)
    for s in range(steps):
        idx = torch.randint(0, Xtr.shape[0], (512,), generator=g)
        p = m(Xtr_t[idx])
        if out_kind == 'real':
            loss = ((p - Ytr_t[idx]) ** 2).mean()
        else:
            loss = nn.functional.binary_cross_entropy_with_logits(p, (Ytr_t[idx] > 0).float())
        opt.zero_grad()
        loss.backward()
        opt.step()
        for gr in opt.param_groups:
            gr['lr'] = lr * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * s / steps)))
    m.eval()
    return m


def predict(m, X):
    with torch.no_grad():
        return m(torch.tensor(X, dtype=torch.float32)).double().numpy()


def fit_ltf(Ctr, Ytr, mask=None, steps=1500, lr=0.03):
    """Multi-output logistic regression (one LTF per output bit), optional input mask (s-sparse)."""
    Kin, Kout = Ctr.shape[1], Ytr.shape[1]
    W = torch.zeros(Kin, Kout, requires_grad=True)
    b = torch.zeros(Kout, requires_grad=True)
    opt = torch.optim.Adam([W, b], lr=lr)
    X = torch.tensor(Ctr, dtype=torch.float32)
    Y = (torch.tensor(Ytr, dtype=torch.float32) > 0).float()
    M = None if mask is None else torch.tensor(mask, dtype=torch.float32)
    g = torch.Generator().manual_seed(1)
    for s in range(steps):
        idx = torch.randint(0, X.shape[0], (1024,), generator=g)
        Wm = W if M is None else W * M
        loss = nn.functional.binary_cross_entropy_with_logits(X[idx] @ Wm + b, Y[idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
    Wm = (W if M is None else W * M).detach().double().numpy()
    return Wm, b.detach().double().numpy()


def walsh_stats(f, Kin, P=4096, base=None, rs=0):
    """f: (P, Kin) +-1 -> (P, Kout) +-1. On uniform inputs (base None) or around actual codes (base: (N, Kin) array).
    Returns per-output arrays: W0, W1 (uniform only), stability at RHOS, total influence, number of inputs with
    influence > 0.01."""
    r = np.random.default_rng(rs)
    C = (np.where(r.random((P, Kin)) < 0.5, -1.0, 1.0) if base is None else base[r.integers(0, base.shape[0], P)])
    F = f(C)
    out = {}
    if base is None:
        h = P // 2
        m1, m2 = F[:h].mean(0), F[h:].mean(0)
        out['W0'] = m1 * m2
        g1 = (F[:h].T @ C[:h]) / h
        g2 = (F[h:].T @ C[h:]) / (P - h)
        out['W1'] = (g1 * g2).sum(1)
    stab = {}
    for rho in RHOS:
        flip = r.random(C.shape) < (1 - rho) / 2
        C2 = np.where(flip, -C, C)
        stab[rho] = (F * f(C2)).mean(0)
    out['stab'] = stab
    Pi = min(P, 512)
    infl = np.zeros((F.shape[1], Kin))
    for i in range(Kin):
        C2 = C[:Pi].copy()
        C2[:, i] = -C2[:, i]
        infl[:, i] = (f(C2) != F[:Pi]).mean(0)
    out['I_total'] = infl.sum(1)
    out['n_relevant'] = (infl > 0.01).sum(1)
    return out


def summarize(ws, w=None):
    w = np.ones(len(ws['I_total'])) if w is None else w / w.sum() * len(w)
    s = {k: float(np.average(v, weights=w)) for k, v in ws.items() if k in ('W0', 'W1', 'I_total', 'n_relevant')}
    s['stab'] = {str(k): float(np.average(v, weights=w)) for k, v in ws['stab'].items()}
    if 'W1' in ws:
        s['W_ge2'] = float(np.average(1 - ws['W0'] - ws['W1'], weights=w))
    return s


res = dict(net=kind, seed=seed, V=V, eps_rate=eps_rate, layers={str(l): dict(C=code[l]['C'], K=code[l]['K'],
           lam=code[l]['lam'].tolist()) for l in LAYERS}, pairs={})
for l in LAYERS:
    c = code[l]
    res['layers'][str(l)]['own_nmse_real'] = nmse(decode_out(l, c['Ut']))
    res['layers'][str(l)]['own_nmse_sign'] = nmse(decode_out(l, np.sign(c['Ut']) * math.sqrt(2 / math.pi)))

for (l1, l2) in PAIRS:
    a, b = code[l1], code[l2]
    w = b['lam'] / b['lam'].sum()
    ent = dict(K_in=a['K'], K_out=b['K'])
    # real-valued transitions
    Wl, *_ = np.linalg.lstsq(np.c_[a['Uf'], np.ones(P_fit)], b['Uf'], rcond=None)
    Pl = np.c_[a['Ut'], np.ones(P_test)] @ Wl
    varb = b['Ut'].var(0)
    r2_lin = 1 - ((Pl - b['Ut']) ** 2).mean(0) / varb
    mr = fit_mlp(a['Uf'], b['Uf'], a['Ut'], 'real', seed_=l1 * 100 + l2)
    Pm = predict(mr, a['Ut'])
    r2_mlp = 1 - ((Pm - b['Ut']) ** 2).mean(0) / varb
    ent['R2_lin_w'] = float((w * r2_lin).sum())
    ent['R2_mlp_w'] = float((w * r2_mlp).sum())
    ent['R2_lin_top8'] = r2_lin[:8].tolist()
    ent['R2_mlp_top8'] = r2_mlp[:8].tolist()
    ent['chain_nmse_lin'] = nmse(decode_out(l2, Pl))
    ent['chain_nmse_mlp'] = nmse(decode_out(l2, Pm))
    ent['own_nmse_l2'] = res['layers'][str(l2)]['own_nmse_real']
    # binary transitions
    Cf, Ct = np.sign(a['Uf']), np.sign(a['Ut'])
    Yf, Yt = np.sign(b['Uf']), np.sign(b['Ut'])
    Wd, bd = fit_ltf(Cf, Yf)
    acc_ltf = ((np.sign(Ct @ Wd + bd) == Yt).mean(0))
    ent['acc_ltf_w'] = float((w * acc_ltf).sum())
    sparse = {}
    for s_ in [1, 2, 4, 8, 16, 32]:
        if s_ > a['K']:
            continue
        top = np.argsort(-np.abs(Wd), axis=0)[:s_]
        mask = np.zeros_like(Wd)
        np.put_along_axis(mask, top, 1.0, axis=0)
        Ws, bs = fit_ltf(Cf, Yf, mask=mask)
        sparse[str(s_)] = float((w * (np.sign(Ct @ Ws + bs) == Yt).mean(0)).sum())
    ent['acc_sparse_ltf_w'] = sparse
    mb = fit_mlp(Cf, Yf, Ct, 'bin', seed_=l1 * 100 + l2 + 7)
    acc_mlp = (np.sign(predict(mb, Ct)) == Yt).mean(0)
    ent['acc_mlp_w'] = float((w * acc_mlp).sum())
    ent['acc_majority_w'] = float((w * np.maximum((Yt > 0).mean(0), (Yt < 0).mean(0))).sum())
    # chain error through the binary transition (decode predicted signs at l2)
    ent['chain_nmse_sign_mlp'] = nmse(decode_out(l2, np.sign(predict(mb, Ct)) * math.sqrt(2 / math.pi)))
    ent['own_nmse_sign_l2'] = res['layers'][str(l2)]['own_nmse_sign']
    # Walsh statistics of the fitted transitions
    f_mlp = lambda C_: np.sign(predict(mb, C_) + 1e-12)  # noqa: E731
    f_ltf = lambda C_: np.sign(C_ @ Wd + bd + 1e-12)  # noqa: E731
    ent['walsh_mlp_uniform'] = summarize(walsh_stats(f_mlp, a['K'], rs=1), w)
    ent['walsh_ltf_uniform'] = summarize(walsh_stats(f_ltf, a['K'], rs=2), w)
    ent['walsh_mlp_codes'] = summarize(walsh_stats(f_mlp, a['K'], base=Ct, rs=3), w)
    res['pairs'][f'{l1}-{l2}'] = ent
    print(f'pair {l1}->{l2}: R2 lin {ent["R2_lin_w"]:.3f} mlp {ent["R2_mlp_w"]:.3f} | chain nmse lin '
          f'{ent["chain_nmse_lin"]:.4f} mlp {ent["chain_nmse_mlp"]:.4f} own {ent["own_nmse_l2"]:.4f} | bits: ltf '
          f'{ent["acc_ltf_w"]:.3f} mlp {ent["acc_mlp_w"]:.3f} sparse {sparse} | W1 mlp '
          f'{ent["walsh_mlp_uniform"].get("W1", 0):.3f} I {ent["walsh_mlp_uniform"]["I_total"]:.1f} '
          f'{time.time() - t0:.0f}s', flush=True)

# baselines at a representative size (the pair 24->28 for ARC)
Kin = code[LAYERS[len(LAYERS) // 2]]['K']
Kout = Kin
r = np.random.default_rng(5)
base = {}
S3 = [r.choice(Kin, 3, replace=False) for _ in range(Kout)]
base['parity3'] = lambda C_: np.stack([np.prod(C_[:, s], 1) for s in S3], 1)
SH = [r.choice(Kin, max(1, Kin // 2), replace=False) for _ in range(Kout)]
base['parity_half'] = lambda C_: np.stack([np.prod(C_[:, s], 1) for s in SH], 1)
W1r = r.standard_normal((Kin, 4 * Kin)) / math.sqrt(Kin)
b1r = r.standard_normal(4 * Kin) * 0.5
W2r = r.standard_normal((4 * Kin, Kout)) / math.sqrt(4 * Kin)
base['dense_relu2'] = lambda C_: np.sign(np.maximum(C_ @ W1r + b1r, 0) @ W2r - (np.maximum(C_ @ W1r + b1r, 0) @ W2r).mean(0) + 1e-12)
WL = r.standard_normal((Kin, Kout))
base['ltf_dense'] = lambda C_: np.sign(C_ @ WL + 1e-12)
WS = np.zeros((Kin, Kout))
for j in range(Kout):
    WS[r.choice(Kin, min(4, Kin), replace=False), j] = r.standard_normal(min(4, Kin))
base['ltf_4sparse'] = lambda C_: np.sign(C_ @ WS + 1e-12)
res['baselines'] = dict(K=Kin, stats={k: summarize(walsh_stats(f, Kin, rs=11)) for k, f in base.items()})
for k, v in res['baselines']['stats'].items():
    print('baseline', k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()}, flush=True)

# avalanche: correlated inputs
av = {}
Z = rng.standard_normal((P_test, net.n))
for rho in [0.9, 0.99, 0.999, 0.9999]:
    X2 = rho * Xt + math.sqrt(1 - rho * rho) * Z
    H2, _ = states(X2)
    row = {}
    for l in LAYERS:
        c = code[l]
        U2 = ((H2[l] - c['fr']['m']) @ c['fr']['Sm12']) @ c['Q']
        row[str(l)] = dict(bit_flip_frac=float((np.sign(U2) != np.sign(c['Ut'])).mean()),
                           rel_dist=float(((U2 - c['Ut']) ** 2).sum(1).mean() / (2 * c['Ut'].var(0).sum())))
    av[str(rho)] = row
    print('avalanche rho', rho, {k: round(v['bit_flip_frac'], 4) for k, v in row.items()}, flush=True)
res['avalanche'] = av
with open(f'{outdir}/B_{kind}_{seed}.json', 'w') as f:
    json.dump(res, f)
print('done', f'{time.time() - t0:.0f}s')
