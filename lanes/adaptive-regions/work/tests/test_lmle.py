"""Known-answer tests T1-T5 of SPEC-learned-experts.md section 6 for lib/lmle.py.
Run: nice -n 19 python tests/test_lmle.py. Both fusion modes are tested: 'gpoe' (the spec: product over every
route x expert pair) and 'mix' (mixture of a component's parts within a route, gPoE across routes)."""
import math, os, sys
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import lmle  # noqa: E402

torch.set_num_threads(2)
results = {}


def check(name, cond, info=''):
    results[name] = bool(cond)
    print(('PASS ' if cond else 'FAIL ') + name + ('  ' + info if info else ''))


rng = np.random.RandomState(0)
DT = lmle.DT

# ---------------- T1: linear net (no ReLU), K = 1, routes s = 1, 2: exact mean and covariance at every layer
n, L = 6, 3
Ws = [rng.standard_normal((n, n)) / math.sqrt(n) for _ in range(L)]
X = rng.standard_normal((20000, n))
H = [X]
for W in Ws:
    H.append(H[-1] @ W.T)
model = lmle.LMLE(L, n, 1, n, skips=(1, 2))
for key, bank in model.banks.items():
    l, s = map(int, key.split('_'))
    bank.init_em(H[l], H[l + s], reg=1e-10)
m0 = torch.as_tensor(rng.standard_normal(n), dtype=DT); S0 = torch.eye(n, dtype=DT) * 0.5
eps = {l: lmle.std_draws(256, n, 10 + l) for l in range(L + 1)}
for mode in ('gpoe', 'mix', 'tgpoe', 'poe'):
    with torch.no_grad():
        out, _ = model.propagate(m0, S0, eps, mode=mode, split_on=False)
    m_ex, S_ex = m0.numpy(), S0.numpy()
    worst_m = worst_S = 0.0
    for t in range(1, L + 1):
        m_ex = Ws[t - 1] @ m_ex; S_ex = Ws[t - 1] @ S_ex @ Ws[t - 1].T
        worst_m = max(worst_m, float(np.abs(out[t - 1][0].numpy() - m_ex).max()))
        worst_S = max(worst_S, float(np.abs(out[t - 1][1].numpy() - S_ex).max()))
    check(f'T1 linear net exact mean, {mode}', worst_m < 1e-6, f'{worst_m:.1e}')
    check(f'T1 linear net exact covariance, {mode}', worst_S < 1e-6, f'{worst_S:.1e}')

# ---------------- T2: one ReLU layer, n = 4, 16 planted experts with gates aligned to the 4 unit hyperplanes
n = 4
W = rng.standard_normal((n, n))
C = np.linalg.inv(W.T @ W)                      # W C W^T = I
alpha = 300.0
patterns = [np.array([(p >> k) & 1 for k in range(n)]) for p in range(1 << n)]
model = lmle.LMLE(1, n, 1 << n, n, skips=(1,))
bank = model.banks['0_1']
with torch.no_grad():
    bank.logpi.zero_()
    s_vec = [2 * p - 1 for p in patterns]
    bank.mu.copy_(torch.as_tensor(np.stack([alpha * C @ (W.T @ sv) for sv in s_vec])))
    Pg = np.linalg.cholesky(np.linalg.inv(C))
    bank.Lg.copy_(torch.as_tensor(np.stack([Pg] * len(patterns))))
    Aex = np.stack([np.diag(p) @ W for p in patterns])
    base = Aex.mean(0)
    Us, Vs = [], []
    for A in Aex:
        u_, s_, vt_ = np.linalg.svd(A - base)
        Us.append(u_ * s_); Vs.append(vt_.T)
    bank.B.copy_(torch.as_tensor(base)); bank.U.copy_(torch.as_tensor(np.stack(Us))); bank.V.copy_(torch.as_tensor(np.stack(Vs)))
    bank.b.zero_(); bank.Lr.copy_(torch.eye(n, dtype=DT).repeat(len(patterns), 1, 1) * 1e-4)
exact = np.linalg.norm(W, axis=1) / math.sqrt(2 * math.pi)
eps = {0: lmle.std_draws(1 << 20, n, 3)}
for mode, split in (('gpoe', 0.2), ('mix', 0.2), ('tgpoe', 0.2), ('poe', 0.2), ('gpoe', 0.01)):
    with torch.no_grad():
        out, st = model.propagate(torch.zeros(n, dtype=DT), torch.eye(n, dtype=DT), eps, mode=mode, split=split, K_pop=64)
    err = float(np.abs(out[0][0].numpy() - exact).max())
    check(f'T2 rectified mean within 1e-3, {mode}, split threshold {split}', err < 1e-3, f'max error {err:.2e}; splits {st["n_split"]}')

# ---------------- T3: K = 1, one layer: the population mean equals the linear regression estimator
n = 5
W = rng.standard_normal((n, n))
X = rng.standard_normal((20000, n)); V = np.maximum(X @ W.T, 0)
model = lmle.LMLE(1, n, 1, n, skips=(1,))
model.banks['0_1'].init_em(X, V, reg=1e-10)
Bls, *_ = np.linalg.lstsq(np.c_[X, np.ones(len(X))], V, rcond=None)
eps = {0: lmle.std_draws(256, n, 4)}
mq = rng.standard_normal(n) * 0.3
for mode in ('gpoe', 'mix', 'tgpoe', 'poe'):
    with torch.no_grad():
        out, _ = model.propagate(torch.as_tensor(mq, dtype=DT), torch.eye(n, dtype=DT) * 0.7, eps, mode=mode, split_on=False)
    reg = np.r_[mq, 1.0] @ Bls
    err = float(np.abs(out[0][0].numpy() - reg).max())
    check(f'T3 K=1 equals the regression estimator, {mode}', err < 1e-6, f'{err:.1e}')

# ---------------- T4: tiny populations -> the pointwise prediction at the centre
n, L = 6, 3
Ws = [rng.standard_normal((n, n)) * math.sqrt(2 / n) for _ in range(L)]
X = rng.standard_normal((20000, n)); H = [X]
for W in Ws:
    H.append(np.maximum(H[-1] @ W.T, 0))
model = lmle.LMLE(L, n, 4, n, skips=(1, 2))
for key, bank in model.banks.items():
    l, s = map(int, key.split('_'))
    bank.init_em(H[l], H[l + s], seed=1)
eps = {l: lmle.std_draws(256, n, 20 + l) for l in range(L + 1)}
xs = rng.standard_normal((5, n))
for mode in ('gpoe', 'mix', 'tgpoe', 'poe'):
    worst = 0.0
    with torch.no_grad():
        pc = model.point_chain(torch.as_tensor(xs, dtype=DT), mode=mode)[0][L].numpy()
        for i in range(len(xs)):
            out, _ = model.propagate(torch.as_tensor(xs[i], dtype=DT), torch.eye(n, dtype=DT) * 1e-10, eps, mode=mode,
                                     split_on=False)
            worst = max(worst, float(np.abs(out[-1][0].numpy() - pc[i]).max() / (np.abs(pc[i]).max() + 1e-12)))
    check(f'T4 tiny populations -> pointwise prediction, {mode}', worst < 1e-4, f'relative {worst:.1e}')

# ---------------- T5: planted 2-piece linear map is recovered by the EM warm start
n = 4
A1, A2 = rng.standard_normal((n, n)), rng.standard_normal((n, n))
b1, b2 = rng.standard_normal(n), rng.standard_normal(n)
X = rng.standard_normal((40000, n))
side = X[:, 0] > 0
V = np.where(side[:, None], X @ A1.T + b1, X @ A2.T + b2) + 0.01 * rng.standard_normal((40000, n))
bank = lmle.Bank(n, n, 2, n).init_em(X, V, seed=0)
with torch.no_grad():
    Ahat = bank.A().numpy(); bhat = bank.b.numpy()
e_direct = max(np.abs(Ahat[0] - A1).max(), np.abs(Ahat[1] - A2).max(), np.abs(bhat[0] - b1).max(), np.abs(bhat[1] - b2).max())
e_swap = max(np.abs(Ahat[1] - A1).max(), np.abs(Ahat[0] - A2).max(), np.abs(bhat[1] - b1).max(), np.abs(bhat[0] - b2).max())
err = min(e_direct, e_swap)
check('T5 planted 2-piece linear map recovered (max abs coefficient error < 0.05)', err < 0.05, f'{err:.3f}')

print('ALL PASS' if all(results.values()) else 'FAILED: ' + ', '.join(k for k, v in results.items() if not v))
import sys
sys.exit(0 if all(results.values()) else 1)   # review fix (astra #17): failures fail the process
