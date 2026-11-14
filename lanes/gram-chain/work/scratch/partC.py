"""Part C (PREREG Part C): per-net (quenched) quantities on real nets, to compare with the chain's annealed moments.
Model S, sigma = 1, nets = st.W_layer(seed, n, l) (layers <= 0 the past, output a = relu(W_1 h_0)).
Per net: M independent noise replicas from h = 0 at layer -B (B = 8n burn-in) to layer 0.
  - radius: Qbar = median_i |h_0|^2/n; direction cloud of u = h_0/|h_0|: trC = unbiased sample variance trace;
    trC2 = U-statistic over disjoint replica pairs x_k = u_{2k} - u_{2k+1}: mean_{k != k'} (x_k.x_k')^2 / 4;
    per-net PR = trC^2/trC2; same for the output direction a/|a|.
  - closed relevance V_P(t; W), t in TG: copy 64 replicas' states at layer 1 - t, rerun layers 2-t..0 with fresh noise,
    output; V_P = 1 - mean|ua - ua'|^2 / (2 Var(ua | W)).
  - total relevance T_P(t; W): 32 disjoint pairs of independent replicas at layer 1 - t, rerun both with the SAME
    fresh noise; T_P = mean|ua_i' - ua_j'|^2 / (2 Var(ua | W)).
usage: partC.py n seed0 nnets [--M M]"""
import sys, os, math, json, time, argparse
sys.path.insert(0, '/home/agent/workspaces/mats/work/stationary/lib')
import numpy as np
import st

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int)
ap.add_argument('seed0', type=int)
ap.add_argument('nnets', type=int)
ap.add_argument('--M', type=int, default=256)
a = ap.parse_args()
n, M = a.n, a.M
B = 8 * n
TG = [t for t in (1, 2, 4, 8, 16, 32, 64) if t <= max(8, n // 2)]
OUT = '/home/agent/workspaces/mats/work/gram-chain/runs/C_n%d_s%d_%d.json' % (n, a.seed0, a.nnets)
t0 = time.time()


def dirs(h):
    r = np.linalg.norm(h, axis=1, keepdims=True)
    return h / np.maximum(r, 1e-300), r[:, 0]


def cloud_stats(u):
    m = u.shape[0]
    trC = float(np.sum(np.var(u, axis=0, ddof=1)))
    x = u[0:m - 1:2] - u[1:m:2]
    K = x.shape[0]
    Gx = x @ x.T
    off = Gx[~np.eye(K, dtype=bool)]
    trC2 = float(np.mean(off ** 2) / 4.0)
    return trC, trC2


nets = []
for k in range(a.nnets):
    seed = a.seed0 + k
    Wf = st.WCache(seed, n, max_bytes=300e6)
    rng = np.random.default_rng([31337, n, seed])
    h = np.zeros((M, n))
    saved = {}
    for l in range(-B + 1, 1):
        W = Wf(l)
        h = np.maximum(h @ W.T, 0.0) + rng.standard_normal((M, n))
        for t in TG:
            if l == 1 - t:
                saved[t] = h.copy()
    W1 = Wf(1)
    aout = np.maximum(h @ W1.T, 0.0)
    u, r = dirs(h)
    ua, ra = dirs(aout)
    trC_u, trC2_u = cloud_stats(u)
    trC_a, trC2_a = cloud_stats(ua)
    var_a = trC_a  # Var(ua | W) = tr Cov(ua)
    rec = dict(seed=seed, Qbar=float(np.median(r ** 2) / n), Q_sd_log=float(np.std(np.log(r ** 2))),
               trC_u=trC_u, trC2_u=trC2_u, PR_u=trC_u ** 2 / trC2_u, trC_a=trC_a, trC2_a=trC2_a, PR_a=trC_a ** 2 / trC2_a,
               logQa_var=float(np.var(2 * np.log(np.maximum(ra, 1e-300)), ddof=1)))
    VP, TP = {}, {}
    for t in TG:
        hs = saved[t]
        # closed: copies of 64 replicas, fresh independent noise for layers 2-t..0
        hc = hs[:64].copy()
        for l in range(2 - t, 1):
            hc = np.maximum(hc @ Wf(l).T, 0.0) + rng.standard_normal(hc.shape)
        uc, _ = dirs(np.maximum(hc @ W1.T, 0.0))
        VP[t] = float(1 - np.mean(np.sum((ua[:64] - uc) ** 2, 1)) / (2 * var_a))
        # total: 32 disjoint pairs of independent replicas, rerun with shared fresh noise
        hp = hs[:64].copy()
        for l in range(2 - t, 1):
            xi = rng.standard_normal((32, n))
            hp = np.maximum(hp @ Wf(l).T, 0.0) + np.repeat(xi, 2, axis=0)
        up, _ = dirs(np.maximum(hp @ W1.T, 0.0))
        TP[t] = float(np.mean(np.sum((up[0::2] - up[1::2]) ** 2, 1)) / (2 * var_a))
    rec['V_P'] = VP
    rec['T_P'] = TP
    nets.append(rec)
    print(json.dumps({k2: (round(v, 4) if isinstance(v, float) else v) for k2, v in rec.items() if k2 not in ('V_P', 'T_P')}),
          'VP', {t: round(v, 3) for t, v in VP.items()}, '%.0fs' % (time.time() - t0), flush=True)
json.dump(dict(n=n, M=M, B=B, TG=TG, nets=nets, sec=time.time() - t0), open(OUT, 'w'), indent=1)
