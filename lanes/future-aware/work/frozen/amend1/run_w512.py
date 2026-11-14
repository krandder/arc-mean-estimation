"""Part 2 (width extension): on one net at n = 512, L = 64 (or any width), compute (1) the Monte Carlo truth (two
halves, 2^LOG2T paths) if missing, (2) scrambled-Sobol RQMC replicates (8 per size), (3) ARC k2 'simple', k3f
('simple', factorised) and the D1 projected-k3 variants (lib/fa_kprop.py, unchanged), writing
runs/truth_n{N}_L{L}_s{SEED}.npz, runs/rqmc_n{N}_L{L}_s{SEED}.json and runs/k3p_n{N}_L{L}_s{SEED}.json.
usage: run_w512.py N L SEED [--log2T 22] [--rqmc 8,10,12,14] [--variants none,futmf2_128,...]"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import fa, fa2, fa_kprop as FK  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--log2T', type=int, default=22); ap.add_argument('--rqmc', default='8,10,12,14')
ap.add_argument('--variants', default='none,futmf2_128,futmf2_64,futmf2_16,pca128,pca64,pca16')
ap.add_argument('--steps', default='truth,rqmc,k3p')
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
RUNS = fa2.FA_RUNS
steps = args.steps.split(',')
t0 = time.time()
W = fa.au.weights(seed, n, L)
tp = os.path.join(RUNS, f'truth_n{n}_L{L}_s{seed}.npz')
if 'truth' in steps and not os.path.exists(tp):
    M = fa.au.mc_moments(W, 1 << args.log2T, seed=777_000 + seed)
    np.savez(tp, S1A=M['S1A'], S1B=M['S1B'], S2A=M['S2A'], S2B=M['S2B'], N=M['N'], n=n, L=L, seed=seed,
             secs=time.time() - t0)
    print(f'truth n={n} L={L} s={seed} 2^{args.log2T} paths ({time.time() - t0:.0f}s)', flush=True)
net = fa2.load_net(n, L, seed)
Y, V = net['Y'], net['V']
PASS = 2.0 * n * n * L
if 'rqmc' in steps:
    ms = [int(m) for m in args.rqmc.split(',')]
    rows = []
    for m in ms:
        reps = fa.au.rqmc(W, m, 8, seed=seed * 10 + m)
        e = [float(((r - Y) ** 2).sum() / V) for r in reps]
        rows.append(dict(m=m, N=1 << m, nmse=e, mean_nmse=float(np.mean(e)), mc_nmse=1.0 / (1 << m)))
        print(f'rqmc n={n} m={m}: {np.mean(e):.3e} (MC {1.0 / (1 << m):.3e}) ({time.time() - t0:.0f}s)', flush=True)
    json.dump(dict(n=n, L=L, seed=seed, V=V, R=8, rows=rows, truth=net['truth_path']),
              open(os.path.join(RUNS, f'rqmc_n{n}_L{L}_s{seed}.json'), 'w'))
if 'k3p' in steps:
    out = os.path.join(RUNS, f'k3p_n{n}_L{L}_s{seed}.json')
    res = dict(n=n, L=L, seed=seed, V=V, variants={}, part=2)
    probs, k2run = FK.k2_gate_probs(W)
    Rmf = FK.mf_relevance(W, probs)
    res['k2'] = dict(nmse=float(((k2run['mean'] - Y) ** 2).sum() / V), passes=k2run['flops'] / PASS)
    mf_cost = (k2run['flops'] + L * 2.0 * n ** 3) / PASS
    print(f'n={n} L={L} s={seed} k2: nMSE {res["k2"]["nmse"]:.3e} passes {res["k2"]["passes"]:.0f}', flush=True)
    for v in args.variants.split(','):
        if v == 'none':
            kind, k = 'none', 0
        else:
            for kd in ('futmf2', 'futv', 'pca'):
                if v.startswith(kd):
                    kind, k = kd, int(v[len(kd):].lstrip('_'))
                    break
        r = FK.arc_k3_proj(W, kind=kind, k=k, Jmf=None, Rmf=Rmf, seed=seed, factor=True)
        passes = (r['flops'] + r['hook_flops'] + r['backward_flops']) / PASS + (mf_cost if kind == 'futmf2' else 0.0)
        res['variants'][v] = dict(kind=kind, k=k, nmse=float(((r['mean'] - Y) ** 2).sum() / V), passes=passes,
                                  arc_passes=r['flops'] / PASS, secs=r['secs'])
        print(f'n={n} L={L} s={seed} {v}: nMSE {res["variants"][v]["nmse"]:.3e} passes {passes:.0f} ({r["secs"]:.0f}s)',
              flush=True)
        json.dump(res, open(out, 'w'))
print('done', f'{time.time() - t0:.0f}s', flush=True)
