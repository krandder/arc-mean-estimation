"""Numbers for FORMAL v1 (mean-field / leading-order theory; no chain sampling except one-unit integrals).
1. Input regime: angular PR of the input cloud from the double-difference vertex recursion
   D' = kappa'(c) D + zeta,  Var zeta = E[(relu z1 - relu z2)^2 (relu z3 - relu z4)^2] / q^2 for 4 equicorrelated
   Gaussians (corr c, variance 2q); PR(l) = 4 n (1 - c_l)^2 / V_D(l).
2. Stationary relevance curves: closed V_P(t) = 1 - Y(t/T*), Y' = 1 - Y^{3/2}; total T_P(t) from delta' = Q f(delta)/(Q+1)
   started at the fixed point (exact mean-field recursions at finite Q, plus the universal forms).
3. Radius-ratio diffusion: E[y^2 | q] from (5/2)(q^2 m)'' - m' - 2m/q + K q^{-2/3} p = 0, K = 4 x*(1) = 4 * 2.231.
4. Across-net CV of q^{-2/3} and q^{1/3} under the inverse-gamma radius law."""
import math, json, sys
import numpy as np
from scipy import integrate, special
sys.path.insert(0, '/home/agent/workspaces/mats/work/gram-chain/lib')
import gc2

out = {}
# ---------- 1. vertex recursion for the input cloud PR ----------
rng = np.random.default_rng(0)
M = 400000
Zc = rng.standard_normal(M)
Zi = rng.standard_normal((M, 4))


def var_zeta(c):
    # z_a = sqrt(2q)(sqrt(c) Zc + sqrt(1-c) Zi_a), q = 1
    z = math.sqrt(2.0) * (math.sqrt(max(c, 0.0)) * Zc[:, None] + math.sqrt(max(1 - c, 0.0)) * Zi)
    r = np.maximum(z, 0.0)
    return float(np.mean(((r[:, 0] - r[:, 1]) * (r[:, 2] - r[:, 3])) ** 2))


def kprime(c):
    return (math.pi - math.acos(min(max(c, -1), 1))) / math.pi


cs = np.linspace(0, 1, 201)
vz = np.array([var_zeta(c) for c in cs])
res = []
c, VD = 0.0, 4.0
for l in range(1, 513):
    VD = kprime(c) ** 2 * VD + float(np.interp(c, cs, vz))
    c = float(gc2.kappa(c))
    if l in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512):
        res.append(dict(l=l, c=c, VD=VD, PR_over_n=4 * (1 - c) ** 2 / VD, asym_1p5_over_l=1.5 / l))
out['input_cloud_PR_over_n'] = res
meas = {1: 159, 4: 57, 16: 17, 32: 9.6, 64: 6.1, 128: 3.6, 256: 1.9}
print('input cloud angular PR / n (vertex recursion) vs input-bits measured at n = 256:')
for r in res:
    m = meas.get(r['l'])
    print('  l=%4d  PR/n=%.4f  (1.5/l=%.4f)  PR at n=256: %.1f  measured %s' % (
        r['l'], r['PR_over_n'], r['asym_1p5_over_l'], 256 * r['PR_over_n'], m))

# ---------- 2. relevance curves ----------
def closed_curve(Q, tmax):
    d, vals = 0.0, []
    ds = float(gc2.mf_fixed_point(Q)[0])
    for t in range(1, tmax + 1):
        # V_P(t): replicas identical after layer l; t-1 noisy layers then the output layer
        vals.append(1 - float(gc2.f_kernel(d)) / float(gc2.f_kernel(ds)))
        d = (1 + Q * float(gc2.f_kernel(d))) / (Q + 1)
    return ds, vals


def total_curve(Q, tmax):
    ds = float(gc2.mf_fixed_point(Q)[0])
    d, vals = ds, []
    for t in range(1, tmax + 1):
        vals.append(float(gc2.f_kernel(d)) / float(gc2.f_kernel(ds)))
        d = Q * float(gc2.f_kernel(d)) / (Q + 1)
    return vals


Ysol = integrate.solve_ivp(lambda s, y: [1 - max(y[0], 0) ** 1.5], (0, 20), [0.0], dense_output=True, rtol=1e-10, atol=1e-12)
out['relevance'] = {}
for n in (64, 256, 1024):
    Q = 0.5770780 * n
    ds, vp = closed_curve(Q, 8 * n)
    tp = total_curve(Q, 8 * n)
    Tstar = (Q + 1) * ds
    half_v = next(t for t, v in enumerate(vp, 1) if v < 0.5)
    half_t = next(t for t, v in enumerate(tp, 1) if v < 0.5)
    area_v = sum(vp)
    univ = [1 - Ysol.sol(t / Tstar)[0] for t in range(1, 4 * int(Tstar) + 1)]
    out['relevance'][n] = dict(Q=Q, delta_star=ds, Tstar=Tstar, Vp_half_t=half_v, Tp_half_t=half_t, Vp_area=area_v,
                               Vp_area_over_Tstar=area_v / Tstar, Tp_at=[tp[t - 1] for t in (1, 2, 4, 8, 16, 32, 64, 128)],
                               Vp_at=[vp[t - 1] for t in (1, 2, 4, 8, 16, 32, 64, 128)])
    print('n=%d Q=%.1f delta*=%.4f T*=(Q+1)delta*=%.2f; closed V_P: half at t=%d, area %.2f (=%.3f T*); total T_P: half at t=%d' % (
        n, Q, ds, Tstar, half_v, area_v, area_v / Tstar, half_t))
    print('   V_P(t=1,2,4,8,16,32,64,128) =', np.round(out['relevance'][n]['Vp_at'], 3))
    print('   T_P(t=1,2,4,8,16,32,64,128) =', np.round(out['relevance'][n]['Tp_at'], 3))
print('universal closed-relevance area int(1 - Y) ds = 2(1 - pi/(3 sqrt3)) = %.4f' % (2 * (1 - math.pi / (3 * math.sqrt(3)))))

# ---------- 3. radius-ratio diffusion: E[y^2 | q] ----------
# Solve for w(q) = E[y^2|q] with m = w p on a log grid by a stationary relaxation of the 2-D diffusion's second moment:
# simulate the limiting SDE (q, y) directly (Euler, small ds) as a check of the ODE-free route.
K = 4 * gc2.C_K ** (-2.0 / 3.0)
rng = np.random.default_rng(1)
P = 20000
q = 2.0 / (5.0 * rng.exponential(size=P))
y = np.zeros(P)
dt = 2e-3
acc = []
for k in range(int(40 / dt)):
    dW1, dW2 = rng.standard_normal(P) * math.sqrt(dt), rng.standard_normal(P) * math.sqrt(dt)
    y = y - y / q * dt + math.sqrt(K) * q ** (-1 / 3) * dW2
    q = q + dt + math.sqrt(5) * q * dW1
    q = np.maximum(q, 1e-6)
    if k * dt > 20 and k % 50 == 0:
        acc.append((q.copy(), y.copy()))
qq = np.concatenate([a for a, b in acc])
yy = np.concatenate([b for a, b in acc])
bins = [0, 0.3, 0.6, 1.2, 2.5, 5, 10, 1e9]
rows = []
for lo, hi in zip(bins[:-1], bins[1:]):
    m = (qq >= lo) & (qq < hi)
    rows.append(dict(lo=lo, hi=hi, Ey2=float(np.mean(yy[m] ** 2))))
out['ell_diffusion'] = dict(K=K, E_y2=float(np.mean(yy ** 2)), sd_y=float(np.std(yy)), by_q=rows)
print('limiting (q, y = n^(1/3) ell) diffusion, K = %.3f: E y^2 = %.3f, SD(y) = %.3f' % (K, np.mean(yy ** 2), np.std(yy)))
for r in rows:
    print('   q in [%g,%g): E[y^2|q] = %.3f' % (r['lo'], r['hi'], r['Ey2']))

# ---------- 4. across-net CVs under Q/n = 2/(5Z) ----------
cv23 = math.sqrt(special.gamma(7 / 3) / special.gamma(5 / 3) ** 2 - 1)
cv13 = math.sqrt(special.gamma(1 / 3) / special.gamma(2 / 3) ** 2 - 1)
out['cv'] = dict(cv_q_m23=cv23, cv_q_13=cv13)
print('across-net CV of Q^(-2/3) = %.3f, of Q^(1/3) = %.3f (n -> inf, inverse-gamma radius)' % (cv23, cv13))
json.dump(out, open('/home/agent/workspaces/mats/work/gram-chain/results/theory_numbers.json', 'w'), indent=1)
