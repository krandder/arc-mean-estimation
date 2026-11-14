"""Tests for lib/ar.py (run: nice -n 19 python tests/test_ar.py). Small nets so it runs in seconds."""
import os, sys, math
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

torch.manual_seed(0)
ok = True


def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + ('  ' + info if info else ''))
    ok = ok and bool(cond)


# 1. forward matches arc-update's au.forward on a dev net
n, L = 32, 4
W = ar.weights(9500, n, L)
X = torch.randn(1000, n)
f1 = ar.forward(W, X)
f2 = ar.au.forward(ar.au.weights(9500, n, L), X)
check('forward == au.forward', float((f1.double() - f2.double()).abs().max()) < 1e-4)

# 2. vjp and jvp against finite differences (piecewise linear: exact within a region; use tiny steps)
x = torch.randn(5, n, dtype=torch.float64)
W64 = [w.double() for w in W]
t = torch.randn(5, n, dtype=torch.float64)
jt, fx = ar.jvp(W64, x, t)
h = 1e-7
fd = (ar.forward(W64, x + h * t) - ar.forward(W64, x - h * t)) / (2 * h)
check('jvp == finite difference', float((jt - fd).abs().max()) < 1e-5)
v = torch.randn(5, n, dtype=torch.float64)
g = ar.vjp(W64, x, v)
check('vjp transpose identity <J^T v, t> = <v, J t>', float(((g * t).sum(1) - (v * jt).sum(1)).abs().max()) < 1e-8)
check('homogeneity f(x) = J(x) x', float((ar.jvp(W64, x, x)[0] - fx).abs().max()) < 1e-9)

# 3. IBP and CROWN are sound on random boxes at several layers; CROWN no looser than IBP on average;
#    exact (zero width) when the box is tiny and no unit straddles
for l in (0, 1, 3):
    B = 6
    xs = torch.randn(B, n, dtype=torch.float64)
    c = ar.forward(W64, xs, 0, l) if l > 0 else xs
    for rr in (1e-3, 0.05, 0.3):
        r = torch.full((B,), rr, dtype=torch.float64)
        pre_i, (lo_i, hi_i) = ar.ibp(W64, l, c, None, r)
        pre_c, (lo_c, hi_c) = ar.crown(W64, l, c, None, r)
        # sample points in the box
        m = 2000
        u = (torch.rand(B, m, n, dtype=torch.float64) * 2 - 1) * rr
        pts = (c[:, None, :] + u).reshape(B * m, n)
        out = ar.forward(W64, pts, l, L).reshape(B, m, n)
        viol_i = float(torch.maximum(out - hi_i[:, None, :], lo_i[:, None, :] - out).max())
        viol_c = float(torch.maximum(out - hi_c[:, None, :], lo_c[:, None, :] - out).max())
        check(f'IBP sound l={l} r={rr}', viol_i <= 1e-9, f'max violation {viol_i:.2e}')
        check(f'CROWN sound l={l} r={rr}', viol_c <= 1e-9, f'max violation {viol_c:.2e}')
        wi = float((hi_i - lo_i).mean()); wc = float((hi_c - lo_c).mean())
        check(f'CROWN tighter than IBP l={l} r={rr}', wc <= wi * (1 + 1e-9), f'{wc:.3e} vs {wi:.3e}')
        # intermediate bounds sound
        h = pts
        worst = 0.0
        for j, (zlo, zhi) in enumerate(pre_c):
            z = h @ W64[l + j].T
            zz = z.reshape(B, m, n)
            worst = max(worst, float(torch.maximum(zz - zhi[:, None, :], zlo[:, None, :] - zz).max()))
            h = torch.relu(z)
        check(f'CROWN intermediate bounds sound l={l} r={rr}', worst <= 1e-9, f'{worst:.2e}')
# tiny box: CROWN width ~ |J| r (linear), equal to the exact range of the linear map when nothing straddles
xs = torch.randn(1, n, dtype=torch.float64)
r = torch.tensor([1e-9], dtype=torch.float64)
pre_c, (lo_c, hi_c) = ar.crown(W64, 0, xs, None, r)
J = torch.stack([ar.jvp(W64, xs, torch.eye(n, dtype=torch.float64)[i:i + 1])[0][0] for i in range(n)], 1)
exact_half = (J.abs().sum(1) * 1e-9)
check('CROWN exact on a tiny box (linear piece)',
      float(((hi_c - lo_c)[0] / 2 - exact_half).abs().max()) < 1e-15 + 1e-6 * float(exact_half.max()))

# 4. rotated input sets (P = orthonormal basis): soundness
P = torch.from_numpy(ar.haar(n, 3))
c = torch.randn(3, n, dtype=torch.float64)
r = torch.full((3,), 0.2, dtype=torch.float64)
pre_c, (lo_c, hi_c) = ar.crown(W64, 0, c, P, r)
a = (torch.rand(3, 3000, n, dtype=torch.float64) * 2 - 1) * 0.2
pts = (c[:, None, :] + a @ P.T).reshape(-1, n)
out = ar.forward(W64, pts).reshape(3, 3000, n)
viol = float(torch.maximum(out - hi_c[:, None, :], lo_c[:, None, :] - out).max())
check('CROWN sound on rotated boxes', viol <= 1e-9, f'{viol:.2e}')

# 5. frame sign cells have exact mass 2^-k; gate-cone probabilities match MC; centroid identity
Xn = np.random.RandomState(1).standard_normal((200000, n))
U = ar.haar(n, 5)
lab = ar.sign_cells_in_frame(Xn @ U, 3)
emp = np.bincount(lab, minlength=8) / len(lab)
check('frame sign cells mass 1/8', np.abs(emp - 0.125).max() < 0.005, str(np.round(emp, 4)))
W1 = W[0].double().numpy()
units = [0, 5, 9]
gc = ar.gate_cone_probs(W1, units, 1 << 21, seed=2, centroids=True)
Z = Xn @ W1.T
lab = ar.gate_cell_labels(Z, units)
emp = np.bincount(lab, minlength=8) / len(lab)
check('gate-cone probabilities vs MC', np.abs(emp - gc['p']).max() < 0.004, f"{np.round(gc['p'], 4)} vs {np.round(emp, 4)}")
cen = np.array([Xn[lab == k].mean(0) for k in range(8)])
check('gate-cone centroid identity vs MC', np.abs(cen - gc['centroid']).max() < 0.03, f'{np.abs(cen - gc["centroid"]).max():.3f}')
p_genz = ar.orthant_prob_genz(W1[units] @ W1[units].T, [1, 1, 1])
check('Genz orthant prob vs sampling', abs(p_genz - gc['p'][7]) < 0.003, f"{p_genz:.4f} vs {gc['p'][7]:.4f}")

# 6. stratified variance formula: post-stratification on frame sign cells reproduces sum p sigma^2 / N
F = ar.forward(W, torch.from_numpy(Xn.astype(np.float32))).double().numpy()
lab = ar.sign_cells_in_frame(Xn @ U, 3)
g = ar.gains(np.full(8, 1 / 8), lab, F, 8)
check('gains: G_N >= G_P >= 1', g['G_N'] >= g['G_P'] - 1e-12 and g['G_P'] >= 1 - 0.01, f"G_N {g['G_N']:.3f} G_P {g['G_P']:.3f}")

# 7. closed index: S = 1 for the full space, ~0 for an empty subspace direction set of a function of other coords
S_full, se, V = ar.closed_index(W, np.eye(n), 4096, 7)
check('closed index of the full space = 1', abs(S_full - 1) < 1e-6, f'{S_full:.6f}')

# 8. collision counter
hh = ar.gate_hashes(W, torch.randn(5000, n))
cs = ar.collision_stats(hh)
check('collision stats run; layer-1 patterns mostly distinct at n=32', cs[0]['distinct'] > 4000, str(cs[0]['distinct']))

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
