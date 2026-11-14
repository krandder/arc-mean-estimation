"""scale-mode lane runner: one job per call; outputs are estimates, costs and truths only (scoring is score.py).
usage: run_cell.py TP_ROOT RUNS JOB NET [args]
NET: au:SEED:N:L   (our weight stream, au.weights(SEED, N, L): W_l iid N(0, 2/n), z = W h)
     p2:ID         (WhestBench Phase 2 public 'mini' MLP ID, from downloads/hf/npz/p2_mlp_ID.npz; 1e9-sample truth)
     claim:CELL:N:L:T  (the claim's own net T of a cell, rebuilt with ARC's MLP class and the seeds of its nets.py)
JOB truth LOG2N         MC truth in two independent halves (au.mc_moments, float32 forward, float64 sums)
    lv                  the claim's estimator: LVTV2 (rule v2f, Gamma s_k), LVT (old rule), LVTV2f1 (first-order s_k), LVT0 (V = 0);
                        R = 24, b = 6.5 (the claim's frozen numerics)
    sl3                 SL3: ARC factored K3 SIMPLE + the claim's factored de-scaling hook with the exact Gamma law
    arc VARIANTS        ARC mlp_kprop variants (k1, k2, k2a, k3f, k3fa) through arc-update's wrapper
    cov                 the starter kit's covariance-propagation ('gain') baseline
    rqmc MLIST R        scrambled-Sobol RQMC, R replicates at each N = 2^m (estimates saved, scored later)"""
import json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smlib  # noqa: E402

TP, RUNS, JOB, NET = sys.argv[1:5]
ARGS = sys.argv[5:]
HF_NPZ = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'downloads', 'hf', 'npz')
os.makedirs(RUNS, exist_ok=True)


def get_net(net):
    """Returns (W list of (out, in) float64 tensors, n, L, tag)."""
    p = net.split(':')
    if p[0] == 'au':
        seed, n, L = int(p[1]), int(p[2]), int(p[3])
        return [w.double() for w in smlib.au.weights(seed, n, L)], n, L, f'au{seed}_n{n}_L{L}'
    if p[0] == 'p2':
        d = np.load(os.path.join(HF_NPZ, f'p2_mlp_{int(p[1]):02d}.npz'))
        Wd = d['weights']
        W = [torch.from_numpy(np.ascontiguousarray(Wd[l].T).astype(np.float64)) for l in range(Wd.shape[0])]
        return W, Wd.shape[1], Wd.shape[0], f'p2_{int(p[1]):02d}'
    if p[0] == 'claim':
        from mlp_kprop.mlp import MLP
        cell, n, L, t = p[1], int(p[2]), int(p[3]), int(p[4])
        sd = (9 if cell.startswith('dev') else 7) * 10 ** 6 + 1000 * n + 10 * L + t
        old = torch.get_default_dtype()
        torch.set_default_dtype(torch.float64)
        torch.manual_seed(sd)
        mlp = MLP(input_dim=n, hidden_dim=n, output_dim=n, num_layers=L + 1)
        torch.set_default_dtype(old)
        return [mlp.Ws[l].weight.detach().clone() for l in range(L)], n, L, f'claim{cell}{t}_n{n}_L{L}'
    raise ValueError(net)


W, n, L, tag = get_net(NET)
out_base = os.path.join(RUNS, f'{JOB}_{tag}')
t0 = time.time()

if JOB == 'truth':
    lg = int(ARGS[0])
    out = out_base + '.npz'
    if not os.path.exists(out):
        M = smlib.au.mc_moments([w.float() for w in W], 1 << lg, seed=880_000 + sum(map(ord, tag)) * 101)
        np.savez(out, S1A=M['S1A'], S1B=M['S1B'], S2A=M['S2A'], S2B=M['S2B'], N=M['N'], n=n, L=L, net=NET, secs=time.time() - t0)
    print(f'truth {NET} 2^{lg} {time.time() - t0:.0f}s', flush=True)

elif JOB == 'lv':
    out = out_base + '.json'
    lv = smlib.load_lvlib(os.path.join(TP, 'estimator', 'lvlib.py'))
    res = dict(net=NET, n=n, L=L, arms={})
    for arm, mode, rule in (('LVTV2', 'full', 'v2f'), ('LVT', 'full', 'lead'), ('LVTV2f1', 'first', 'v2f'), ('LVT0', 'full', 'zero')):
        r = smlib.run_lv(lv, W, 24, 6.5, mode, rule)
        r['mean'] = r['mean'].tolist()
        res['arms'][arm] = r
        print(f'lv {NET} {arm}: V_L {r["Vs"][-1]:.4f} flops {r["flops"]:.3e} passes {smlib.passes(r["flops"], n, L):.0f} '
              f'{r["secs"]:.1f}s flags {r["flags"]}', flush=True)
    json.dump(res, open(out, 'w'))

elif JOB == 'sl3':
    out = out_base + '.json'
    lv = smlib.load_lvlib(os.path.join(TP, 'estimator', 'lvlib.py'))
    ns = smlib.load_descale_fac(lv, os.path.join(TP, 'arc_ladder', 'descale_fac_src.py'))
    r = smlib.run_sl3(ns, W)
    r['mean'] = r['mean'].tolist()
    json.dump(dict(net=NET, n=n, L=L, **r), open(out, 'w'))
    print(f'sl3 {NET}: flops {r["flops"]:.3e} passes {smlib.passes(r["flops"], n, L):.0f} {r["secs"]:.1f}s', flush=True)

elif JOB == 'arc':
    for v in ARGS[0].split(','):
        out = out_base + f'_{v}.json'
        if os.path.exists(out):
            continue
        r = smlib.run_arc([w.double() for w in W], v)
        json.dump(dict(net=NET, n=n, L=L, variant=v, mean=np.asarray(r['mean']).tolist(), flops=r['flops'], secs=r['secs']),
                  open(out, 'w'))
        print(f'arc {NET} {v}: flops {r["flops"]:.3e} passes {smlib.passes(r["flops"], n, L):.0f} {r["secs"]:.1f}s', flush=True)

elif JOB == 'cov':
    out = out_base + '.json'
    r = smlib.run_covprop_gain(W)
    r['mean'] = r['mean'].tolist()
    json.dump(dict(net=NET, n=n, L=L, **r), open(out, 'w'))
    print(f'cov {NET}: flops {r["flops"]:.3e} passes {smlib.passes(r["flops"], n, L):.0f} {r["secs"]:.1f}s', flush=True)

elif JOB == 'rqmc':
    out = out_base + '.json'
    ms = [int(a) for a in ARGS[0].split(',')]
    R = int(ARGS[1])
    res = dict(net=NET, n=n, L=L, R=R, rows=[])
    Wf = [w.float() for w in W]
    for m in ms:
        reps = smlib.au.rqmc(Wf, m, R, seed=sum(map(ord, tag)) * 10 + m)
        res['rows'].append(dict(m=m, N=1 << m, est=reps.tolist()))
        print(f'rqmc {NET} m={m} {time.time() - t0:.0f}s', flush=True)
    json.dump(res, open(out, 'w'))
else:
    raise ValueError(JOB)
