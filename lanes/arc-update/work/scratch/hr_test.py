"""Fresh-layer sign test of the radius hypotheses behind the asymptotic separation (FORMAL E7; astra r2 eq. 21):
(H_R)         E_W[ E_{Gamma_exact(T_W Q)} |h| - E_{T_W Q} |h| ] >= 0
(H_{R,s,tau}) the same with ARC's K = 2 'simple' update Gamma_s (exact per-unit mean and variance, off-diagonal
              covariance p_i p_j B_ij, variance floor 1e-10)
for Gaussian states Q = N(m_l, C_l) actually reached by ARC's K = 2 'simple' recursion on a 256 x 32 net (layers l in
LAYERS; l = 0 is the input N(0, I)). For each state: R fresh layers W ~ N(0, 2/n), the true push-forward T_W Q sampled
(N_s samples), the two Gaussian updates sampled (N_s samples each); defects rho = E_model|h| - E_true|h| with standard
errors; per-state mean over fresh layers and its SE (the sign test). Not registered (exploratory; reported as such).
usage: hr_test.py SEED R LOG2_NS -> runs/hr_s{SEED}.json"""
import json, math, os, sys, time
import numpy as np
import torch
from scipy.special import ndtr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
sys.path.insert(0, '/home/agent/workspaces/mats/work/bits-bounds/lib')
import au  # noqa: E402
import closure as CL  # noqa: E402

seed, R, lp = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
n, L = 256, 32
LAYERS = [0, 1, 2, 4, 8, 16, 24]
W = au.weights(seed, n, L)
r = au.arc_kprop(W, 2, kind='simple', keep_states=tuple(l for l in LAYERS if l > 0))
states = {0: (np.zeros(n), np.eye(n))}
states.update(r['states'])
gen = torch.Generator().manual_seed(12345 + seed)
rng = np.random.default_rng(777 + seed)
Ns = 1 << lp
TAU = 1e-10


def mean_radius_gauss(m, C, N):
    A, _ = au.psd_sqrt(C)
    z = torch.randn(N, n, generator=gen, dtype=torch.float64)
    h = z @ torch.from_numpy(A.T.copy()) + torch.from_numpy(m)
    rad = h.norm(dim=1).numpy()
    return rad.mean(), rad.std() / math.sqrt(N)


def simple_update(nu, B):
    v = np.maximum(np.diag(B), TAU)
    s = np.sqrt(v); a = nu / s
    p = ndtr(a)
    m1 = nu * p + s * np.exp(-0.5 * a * a) / math.sqrt(2 * math.pi)
    e2 = (nu * nu + v) * p + nu * s * np.exp(-0.5 * a * a) / math.sqrt(2 * math.pi)
    C = np.outer(p, p) * B
    np.fill_diagonal(C, e2 - m1 * m1)
    return m1, C


out = dict(seed=seed, R=R, log2_Ns=lp, states={})
t0 = time.time()
for l in LAYERS:
    m, C = states[l]
    A, clip = au.psd_sqrt(C)
    rows = []
    for k in range(R):
        Wf = rng.standard_normal((n, n)) * math.sqrt(2.0 / n)
        nu = Wf @ m; B = Wf @ C @ Wf.T
        z = torch.randn(Ns, n, generator=gen, dtype=torch.float64) @ torch.from_numpy(A.T.copy()) + torch.from_numpy(m)
        y = torch.relu(z @ torch.from_numpy(Wf.T.copy()))
        rt = y.norm(dim=1).numpy(); r_true, se_true = rt.mean(), rt.std() / math.sqrt(Ns)
        ms, Cs = simple_update(nu, B)
        r_s, se_s = mean_radius_gauss(ms, Cs, Ns)
        mx, Cx = CL.relu_moments(nu, B, 48)
        r_x, se_x = mean_radius_gauss(mx, Cx, Ns)
        rows.append(dict(rho_s=float(r_s - r_true), rho_x=float(r_x - r_true),
                         se_s=float(math.hypot(se_s, se_true)), se_x=float(math.hypot(se_x, se_true)),
                         r_true=float(r_true)))
    rs = np.array([x['rho_s'] for x in rows]); rx = np.array([x['rho_x'] for x in rows])
    res = dict(l=l, clip=clip, mean_rho_s=float(rs.mean()), se_mean_rho_s=float(rs.std(ddof=1) / math.sqrt(R)),
               mean_rho_x=float(rx.mean()), se_mean_rho_x=float(rx.std(ddof=1) / math.sqrt(R)),
               mean_within_se_s=float(np.mean([x['se_s'] for x in rows])),
               mean_r_true=float(np.mean([x['r_true'] for x in rows])), rows=rows)
    out['states'][l] = res
    print(f"l={l:2d} rho_simple {res['mean_rho_s']:+.4e} +- {res['se_mean_rho_s']:.1e}  rho_exact {res['mean_rho_x']:+.4e} "
          f"+- {res['se_mean_rho_x']:.1e}  (within-layer SE {res['mean_within_se_s']:.1e}; radius {res['mean_r_true']:.2f};"
          f" {time.time() - t0:.0f}s)", flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'hr_s{seed}.json'), 'w'))
