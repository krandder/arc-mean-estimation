"""Tests for lib/au.py. Run: nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python tests/test_au.py"""
import math, os, sys
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import au  # noqa: E402

ok = True


def check(name, cond, info=''):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + name + (' | ' + info if info else ''), flush=True)


# 1. one layer: E relu(w . x) = |w| / sqrt(2 pi) exactly
W = au.weights(9001, 16, 1)
exact = (W[0].norm(dim=1) / math.sqrt(2 * math.pi)).numpy()
M = au.mc_moments(W, 1 << 18, seed=1)
T = au.truth_from_moments(M)
se = np.sqrt(T['var'][0] / T['N'])
z = np.abs(T['mean'][0] - exact) / se
check('mc one-layer mean within 4.5 SE', z.max() < 4.5, f'max z {z.max():.2f}')
for k, kind in ((2, 'simple'), (2, 'augment'), (3, 'simple')):
    r = au.arc_kprop(W, k, factor=False, kind=kind)
    check(f'kprop K={k} {kind} exact at L=1', np.abs(r['mean'] - exact).max() < 1e-9,
          f'max err {np.abs(r["mean"] - exact).max():.2e}, flops {r["flops"]:.2e}')

# 2. gauss_push at the input layer with the true input law reproduces the MC truth (same distribution)
W = au.weights(9002, 16, 4)
M = au.mc_moments(W, 1 << 18, seed=2)
T = au.truth_from_moments(M)
g, clip, gA, gB = au.gauss_push(W, np.zeros(16), np.eye(16), 0, 1 << 18, seed=3)
se = np.sqrt(2 * T['var'][-1] / T['N'])
z = np.abs(g - T['mean'][-1]) / se
check('gauss_push(l=0, N(0,I)) matches MC truth within 4.5 SE', z.max() < 4.5 and clip < 1e-12,
      f'max z {z.max():.2f}, clip {clip:.1e}')

# 3. K = 2 state extraction: the layer-L mean equals the last state's mean; the covariance is symmetric
r = au.arc_kprop(W, 2, kind='simple', keep_states=(1, 2, 4))
m4, S4 = r['states'][4]
check('K=2 state mean equals final mean', np.allclose(m4, r['mean']))
check('K=2 state covariance symmetric', np.allclose(S4, S4.T, atol=1e-12))
# the last nonlinear step of K=2 is the exact Gaussian relu mean of the layer-3 state (CHECK-1 for K = 2)
m3, S3 = r['states'][2] if False else (None, None)
r3 = au.arc_kprop(W, 2, kind='simple', keep_states=(3,))
m3, S3 = r3['states'][3]
w = W[3].numpy()
mu = w @ m3; sd = np.sqrt(np.einsum('ij,jk,ik->i', w, S3, w))
from scipy.special import ndtr
gm = mu * ndtr(mu / sd) + sd * np.exp(-0.5 * (mu / sd) ** 2) / math.sqrt(2 * math.pi)
check('CHECK-1 (K=2): last step = exact Gaussian relu mean of the layer-(L-1) state',
      np.abs(gm - r['mean']).max() < 1e-9, f'max diff {np.abs(gm - r["mean"]).max():.2e}')

# 4. k3 statistics: Gaussian cloud (kappa_3 = 0) and planted rank-r cloud
rng = np.random.default_rng(5)
n, N = 64, 1 << 14
X = rng.standard_normal((N, n))
s = au.k3_flat_stats(X, np.zeros(n))
scale = n ** 1.5 / (N / 4)  # rough noise scale of the U-statistic
check('Gaussian cloud: ||kappa_3||^2 consistent with 0', abs(s['fro2']) < 5 * scale,
      f'fro2 {s["fro2"]:.3e}, noise scale {scale:.2e}')
r_pl = 4
U = np.linalg.qr(rng.standard_normal((n, r_pl)))[0]
c = 2.0
E = (rng.chisquare(1, size=(N, r_pl)) - 1) / math.sqrt(2)
Xp = rng.standard_normal((N, n)) + c * E @ U.T
s = au.k3_flat_stats(Xp, np.zeros(n))
kexp = r_pl * c ** 6 * (8 / 2 ** 1.5) ** 2
check('planted rank-4: participation ratio near 4', 3.0 < s['pr'] < 5.5, f'pr {s["pr"]:.2f}')
check('planted rank-4: top-4 flattening capture > 0.9', s['topk_flat'][4] > 0.9, f'{s["topk_flat"][4]:.3f}')
check('planted rank-4: top-4 multilinear capture > 0.85', s['capk'][4] > 0.85, f'{s["capk"][4]:.3f}')
check('planted rank-4: ||kappa_3||^2 matches the closed form within 15%', abs(s['fro2'] / kexp - 1) < 0.15,
      f'{s["fro2"]:.1f} vs {kexp:.1f}')

# 5. RQMC unbiased against the MC truth (n = 8, L = 4)
W = au.weights(9003, 8, 4)
M = au.mc_moments(W, 1 << 20, seed=4)
T = au.truth_from_moments(M)
reps = au.rqmc(W, 10, 16, seed=7)
est = reps.mean(0)
se = np.sqrt(reps.var(0, ddof=1) / reps.shape[0] + T['var'][-1] / T['N'])
z = np.abs(est - T['mean'][-1]) / np.maximum(se, 1e-300)
check('RQMC replicate mean matches MC truth within 4.5 SE', z.max() < 4.5, f'max z {z.max():.2f}')

print('ALL PASS' if ok else 'SOME FAILED')
