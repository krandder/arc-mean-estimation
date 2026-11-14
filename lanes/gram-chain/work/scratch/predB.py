"""Mean-field predictions for PREREG Part B, averaged over the stationary radius law as ratios of means (the estimands
are ratios of annealed means). Radius held fixed along each curve (adiabatic). Output layer: f(delta) = 1 - kappa(1-delta)
is E[1 - cos] of the output pair given the hidden angle (kernel level)."""
import sys, json, math
sys.path.insert(0, '/home/agent/workspaces/mats/work/gram-chain/lib')
import numpy as np
import gc2

rng = np.random.default_rng(99)
out = {}
for n in (16, 64, 256, 1024):
    Q = gc2.sample_Q_stationary(n, 4000, rng)
    ds = gc2.mf_fixed_point(Q)
    fstar = gc2.f_kernel(ds)
    den = fstar.mean()
    tmax = 4 * n
    dcl = np.zeros_like(Q)  # closed: replicas identical, independent noise afterwards
    dto = ds.copy()  # total: from the fixed point, shared noise afterwards
    Vp, Tp = [], []
    for t in range(1, tmax + 1):
        Vp.append(1 - gc2.f_kernel(dcl).mean() / den)
        Tp.append(gc2.f_kernel(dto).mean() / den)
        dcl = (1 + Q * gc2.f_kernel(dcl)) / (Q + 1)
        dto = Q * gc2.f_kernel(dto) / (Q + 1)
    Vp, Tp = np.array(Vp), np.array(Tp)
    Qmed = np.median(Q)
    Tstar = (Qmed + 1) * float(gc2.mf_fixed_point(Qmed)[0])
    half_v = int(np.argmax(Vp < 0.5)) + 1
    half_t = int(np.argmax(Tp < 0.5)) + 1
    t4 = int(round(4 * Tstar))
    # perturbation survival (hidden direction), shared noise, eps -> delta_0 = 1 - 1/sqrt(1 + eps^2)
    surv = {}
    for eps in (1e-3, 1e-2, 0.1, 0.3):
        d0 = 1 - 1 / math.sqrt(1 + eps * eps)
        d = np.full_like(Q, d0)
        s = []
        for t in range(0, 2 * n + 1):
            s.append(float(d.mean() / d0))
            d = Q * gc2.f_kernel(d) / (Q + 1)
        surv[eps] = s
    out[n] = dict(Tstar_med=Tstar, Vp_half=half_v, Vp_area=float(Vp.sum()), Tp_half=half_t, t4=t4, Tp_at_4Tstar=float(Tp[t4 - 1]),
                  Vp=[float(Vp[t - 1]) for t in (1, 2, 4, 8, 16, 32, 64)], Tp=[float(Tp[t - 1]) for t in (1, 2, 4, 8, 16, 32, 64)],
                  surv={str(k): v for k, v in surv.items()})
    print('n=%d T*_med=%.2f  V_P half %d area %.2f | T_P half %d, T_P(4T*=%d) = %.4f' % (n, Tstar, half_v, Vp.sum(), half_t, t4, Tp[t4 - 1]))
    print('   V_P(1,2,4,8,16,32,64) =', np.round(out[n]['Vp'], 3), ' T_P =', np.round(out[n]['Tp'], 3))
    for eps in (1e-3, 0.1, 0.3):
        s = surv[eps]
        print('   survival eps=%g at t = 4, 16, 64, n/4: %s' % (eps, [round(s[t], 4) for t in (4, 16, min(64, 2 * n), n // 4)]))
json.dump(out, open('/home/agent/workspaces/mats/work/gram-chain/results/predB_meanfield.json', 'w'), indent=1)
