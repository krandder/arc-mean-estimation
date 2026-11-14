"""Sampler baselines on one net: scrambled-Sobol RQMC replicates at N = 2^m points, R replicates each.
usage: run_rqmc.py N L SEED TRUTH(path|s0|s0.001) M_LIST R  -> runs/rqmc_n{N}_L{L}_s{SEED}.json
nMSE per replicate against the truth; plain MC is 1/N exactly (not simulated)."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import au  # noqa: E402

n, L, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
tk = sys.argv[4]
ms = [int(a) for a in sys.argv[5].split(',')]
R = int(sys.argv[6])
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'rqmc_n{n}_L{L}_s{seed}.json')
W = au.weights(seed, n, L)
if tk in ('s0', 's0.001'):
    d = np.load(os.path.join(au.ARC_NOISY, 'truth', f'truth_{n}_{L}_{tk}_seed{seed}.npz'))
    N_t = float(d['N']); Y = d['S1'][-1] / N_t; var = d['S2'][-1] / N_t - Y ** 2
else:
    T = au.truth_from_moments(dict(np.load(tk)))
    N_t = float(T['N']); Y = T['mean'][-1]; var = T['var'][-1]
V = float(var.sum())
res = dict(n=n, L=L, seed=seed, truth=tk, N_truth=N_t, V=V, R=R, rows=[])
t0 = time.time()
for m in ms:
    reps = au.rqmc(W, m, R, seed=seed * 10 + m)
    e = [float(((r - Y) ** 2).sum() / V) for r in reps]
    res['rows'].append(dict(m=m, N=1 << m, nmse=e, mean_nmse=float(np.mean(e)), mc_nmse=1.0 / (1 << m)))
    print(f'rqmc n={n} L={L} seed={seed} m={m}: mean nMSE {np.mean(e):.3e} (MC {1.0 / (1 << m):.3e}) '
          f'gain {1.0 / (1 << m) / np.mean(e):.2f} ({time.time() - t0:.0f}s)', flush=True)
json.dump(res, open(out, 'w'))
