"""T-LAD: ARC's kprop variants on one net (sigma = 0), final and per-layer means with ARC's FLOP counter.
usage: run_lad.py N L SEED VARIANTS   -> runs/lad_n{N}_L{L}_s{SEED}_{variant}.json"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import au  # noqa: E402

SPEC = dict(k1=(1, False, 'simple'), k2=(2, False, 'simple'), k2a=(2, False, 'augment'), k3=(3, False, 'simple'),
            k3f=(3, True, 'simple'), k3fa=(3, True, 'augment'), k4=(4, False, 'simple'), k4f=(4, True, 'simple'),
            k4fa=(4, True, 'augment'))
n, L, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
W = au.weights(seed, n, L)
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
for v in sys.argv[4].split(','):
    out = os.path.join(RUNS, f'lad_n{n}_L{L}_s{seed}_{v}.json')
    if os.path.exists(out):
        continue
    k, fac, kind = SPEC[v]
    r = au.arc_kprop(W, k, factor=fac, kind=kind)
    json.dump(dict(n=n, L=L, seed=seed, variant=v, k=k, factor=fac, kind=kind, flops=r['flops'], secs=r['secs'],
                   passes=r['flops'] / au.pass_flops(n, L), mean=r['mean'].tolist(),
                   means=[m.tolist() for m in r['means']]), open(out, 'w'))
    print(f'lad n={n} L={L} seed={seed} {v}: flops {r["flops"]:.3e} secs {r["secs"]:.1f}', flush=True)
