"""Dev checks (no scored net is touched). usage: dev_check.py TP_ROOT OUT_DIR PART [args]
TP_ROOT = thirdparty/scale-separation (only estimator/lvlib.py and arc_ladder/descale_fac_src.py are loaded).
PART gate     : SL3 with the hook off must equal arc-update's ARC k3f on dev net 9500 (n = 64, L = 8), bit for bit.
PART devlad   : the claim's arms and SL3 on arc-update's dev nets 9500 (n = 32, 64, 128 at L = n/8), scored against their truths.
PART claimB   : rebuild the claim's own cell B (64x16, seeds 7064160 + t, ARC's MLP class), our own MC truth (2^24, two halves),
                LVTV2 scored the claim's way (cross-half, naive MC at N = F / (2 n^2 (L + 1))). The claim reports 1.52e-3, MC/x 2.31.
PART claimI0  : rebuild the claim's cell I net 0 (1024x256, seed 8026560) and run LVTV2: the claim's log gives V_L = 0.0284.
PART time N L : timing of LVTV2 and SL3 on a random net of width N, depth L (seed 99)."""
import json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smlib  # noqa: E402

TP, OUT, PART = sys.argv[1], sys.argv[2], sys.argv[3]
lv = smlib.load_lvlib(os.path.join(TP, 'estimator', 'lvlib.py'))
AU_RUNS = '/home/agent/workspaces/mats/work/arc-update/runs'
os.makedirs(OUT, exist_ok=True)


def save(name, obj):
    json.dump(obj, open(os.path.join(OUT, name), 'w'))


def claim_nets(cell, n, L, T, dev=False):
    from mlp_kprop.mlp import MLP
    old = torch.get_default_dtype()
    torch.set_default_dtype(torch.float64)
    out = []
    for t in range(T):
        sd = (9 if dev else 7) * 10 ** 6 + 1000 * n + 10 * L + t
        torch.manual_seed(sd)
        mlp = MLP(input_dim=n, hidden_dim=n, output_dim=n, num_layers=L + 1)
        out.append(([w.weight.detach().clone() for w in mlp.Ws], sd, list(mlp.init_scale)))
    torch.set_default_dtype(old)
    return out


if PART == 'gate':
    ns = smlib.load_descale_fac(lv, os.path.join(TP, 'arc_ladder', 'descale_fac_src.py'))
    W = smlib.au.weights(9500, 64, 8)
    r = smlib.run_sl3(ns, W, gate=True)
    ref = json.load(open(os.path.join(AU_RUNS, 'lad_n64_L8_s9500_k3f.json')))
    d = float(np.abs(r['mean'] - np.array(ref['mean'])).max())
    print(f'gate SL3(hook off) vs arc-update k3f, net 9500 n=64: max|diff| {d:.3e}; flops {r["flops"]:.4e} vs {ref["flops"]:.4e}')
    save('gate.json', dict(maxdiff=d, flops=r['flops'], ref_flops=ref['flops']))

elif PART == 'devlad':
    ns = smlib.load_descale_fac(lv, os.path.join(TP, 'arc_ladder', 'descale_fac_src.py'))
    rows = []
    for n, L in ((32, 4), (64, 8), (128, 16)):
        W = smlib.au.weights(9500, n, L)
        T = smlib.au.truth_from_moments(dict(np.load(os.path.join(AU_RUNS, f'truth_n{n}_L{L}_s9500.npz'))))
        Y, var = T['mean'][-1], T['var'][-1]
        res = {}
        for arm, mode, rule in (('LVTV2', 'full', 'v2f'), ('LVT', 'full', 'lead'), ('LVTV2f1', 'first', 'v2f'), ('LVT0', 'full', 'zero')):
            r = smlib.run_lv(lv, W, 24, 6.5, mode, rule)
            res[arm] = dict(nmse=smlib.nmse(r['mean'], Y, var), passes=smlib.passes(r['flops'], n, L),
                            passes_fs=smlib.passes(r['flops_flopscope_special'], n, L), V_L=r['Vs'][-1], secs=r['secs'],
                            flags=r['flags'])
        r = smlib.run_sl3(ns, W)
        res['SL3'] = dict(nmse=smlib.nmse(r['mean'], Y, var), passes=smlib.passes(r['flops'], n, L), secs=r['secs'],
                          V_last=r['Vs'][-1] if r['Vs'] else 0.0)
        for v in ('k2', 'k2a', 'k3f', 'k3fa'):
            p = os.path.join(AU_RUNS, f'lad_n{n}_L{L}_s9500_{v}.json')
            if os.path.exists(p):
                d = json.load(open(p))
                res['ARC-' + v] = dict(nmse=smlib.nmse(d['mean'], Y, var), passes=d['passes'])
        rq = json.load(open(os.path.join(AU_RUNS, f'rqmc_n{n}_L{L}_s9500.json')))
        res['RQMC'] = {str(row['N']): float(np.mean(row['nmse'])) for row in rq['rows']}
        for k, v in res.items():
            print(n, L, k, v, flush=True)
        rows.append(dict(n=n, L=L, res=res))
    save('devlad.json', rows)

elif PART == 'claimB':
    n, L, T = 64, 16, 10
    rows = []
    for t, (Wl, sd, isc) in enumerate(claim_nets('B', n, L, T)):
        W = Wl[:L]
        M = smlib.au.mc_moments([w.float() for w in W], 1 << 24, seed=555_000 + t)
        Tr = smlib.au.truth_from_moments(M)
        YA, YB, var = Tr['meanA'][-1], Tr['meanB'][-1], Tr['var'][-1]
        r = smlib.run_lv(lv, W, 24, 6.5, 'full', 'v2f')
        x = smlib.nmse_cross(r['mean'], YA, YB, var)
        Nmc = r['flops'] / (2 * n * n * (L + 1))
        rows.append(dict(t=t, seed=sd, init_scale0=isc[0], nmse=x, flops=r['flops'], mc_over_x=(1 / Nmc) / x, V_L=r['Vs'][-1]))
        print(rows[-1], flush=True)
    xs = np.array([r_['nmse'] for r_ in rows])
    F = np.mean([r_['flops'] for r_ in rows])
    print(f'claim cell B reproduction: LVTV2 mean nMSE {xs.mean():.3e} (claim 1.52e-3); MC/x {(2 * n * n * (L + 1) / F) / xs.mean():.2f} '
          f'(claim 2.31); flops {F:.3e}', flush=True)
    save('claimB.json', rows)

elif PART == 'claimI0':
    n, L = 1024, 256
    (Wl, sd, isc), = claim_nets('I', n, L, 1)
    r = smlib.run_lv(lv, Wl[:L], 24, 6.5, 'full', 'v2f')
    print(f'claim cell I net 0 (seed {sd}): LVTV2 V_L {r["Vs"][-1]:.4f} (claim log 0.0284); flops {r["flops"]:.3e} (claim 1.20e12 mean); '
          f'secs {r["secs"]:.0f}; flags {r["flags"]}', flush=True)
    save('claimI0.json', dict(seed=sd, V_L=r['Vs'][-1], flops=r['flops'], secs=r['secs'], mean=r['mean'].tolist()))

elif PART == 'time':
    n, L = int(sys.argv[4]), int(sys.argv[5])
    W = smlib.au.weights(99, n, L)
    r = smlib.run_lv(lv, W, 24, 6.5, 'full', 'v2f')
    print(f'time LVTV2 n={n} L={L}: {r["secs"]:.1f}s flops {r["flops"]:.3e} passes {smlib.passes(r["flops"], n, L):.0f} '
          f'(flopscope-special {smlib.passes(r["flops_flopscope_special"], n, L):.0f}) ndtr {r["ndtr"]:.2e} exp {r["exp"]:.2e}', flush=True)
    if len(sys.argv) > 6 and sys.argv[6] == 'sl3':
        ns = smlib.load_descale_fac(lv, os.path.join(TP, 'arc_ladder', 'descale_fac_src.py'))
        r = smlib.run_sl3(ns, W)
        print(f'time SL3 n={n} L={L}: {r["secs"]:.1f}s flops {r["flops"]:.3e} passes {smlib.passes(r["flops"], n, L):.0f}', flush=True)
