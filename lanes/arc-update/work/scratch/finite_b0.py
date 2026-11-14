"""Finite-width radius weight b_0^{(n,t)} = K(0)/K(1), K(rho) = E_future <g_t(u), g_t(v)> for unit u, v with u.v = rho
(the future g_t = t fresh He-ReLU layers; A2's expansion K(rho) = sum_d b_d rho^d with b_d >= 0). Exploratory
NUMERICAL measurement (not registered): F random futures, P orthogonal pairs per future, all depths t <= T from one
stack (a t-layer prefix of a random stack is a random t-layer future). Standard errors over futures.
usage: finite_b0.py N T F P SEED -> results/finite_b0_n{N}.json"""
import json, os, sys, time
import numpy as np
import torch

torch.set_num_threads(1)
n, T, F, P, seed = (int(a) for a in sys.argv[1:6])
gen = torch.Generator().manual_seed(seed)
t0 = time.time()
num = np.zeros((F, T)); den = np.zeros((F, T))
for f in range(F):
    x = torch.randn(2 * P, n, generator=gen, dtype=torch.float64)
    u, v = x[:P], x[P:]
    u = u / u.norm(dim=1, keepdim=True)
    v = v - (v * u).sum(1, keepdim=True) * u
    v = v / v.norm(dim=1, keepdim=True)
    h = torch.cat([u, v]).float()
    for t in range(T):
        W = torch.randn(n, n, generator=gen) * (2.0 / n) ** 0.5
        h = torch.relu(h @ W.T)
        hu, hv = h[:P].double(), h[P:].double()
        num[f, t] = (hu * hv).sum(1).mean().item()
        den[f, t] = 0.5 * ((hu * hu).sum(1).mean().item() + (hv * hv).sum(1).mean().item())
out = {}
for t in range(T):
    b0 = num[:, t].mean() / den[:, t].mean()
    # delta-method SE over futures
    a, b = num[:, t], den[:, t]
    g = a / b.mean() - a.mean() * b / b.mean() ** 2
    out[t + 1] = dict(b0=float(b0), se=float(g.std(ddof=1) / np.sqrt(F)))
res = dict(n=n, T=T, F=F, P=P, seed=seed, secs=time.time() - t0, b0=out)
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results'), exist_ok=True)
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', f'finite_b0_n{n}.json'),
               'w'), indent=1)
for t in (1, 2, 4, 8, 16, 24, 28, 30, 31):
    if t <= T:
        print(f"n={n} t={t}: b0 {out[t]['b0']:.4f} +- {out[t]['se']:.4f}")
print(f'{time.time() - t0:.0f}s')
