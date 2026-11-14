"""Dev timing (not scored): ARC kprop variants and forward passes at small sizes and 256 x 32 on dev weights.
usage: dev_timing.py N L SEED VARIANTS"""
import json, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import au  # noqa: E402

n, L, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
variants = sys.argv[4].split(',')
SPEC = dict(k1=(1, False, 'simple'), k2=(2, False, 'simple'), k2a=(2, False, 'augment'), k3=(3, False, 'simple'),
            k3f=(3, True, 'simple'), k3fa=(3, True, 'augment'), k4=(4, False, 'simple'), k4f=(4, True, 'simple'),
            k4fa=(4, True, 'augment'))
W = au.weights(seed, n, L)
t0 = time.time()
x = torch.randn(1 << 14, n)
h = au.forward(W, x)
tf = time.time() - t0
print(f'forward 16384 paths: {tf:.2f}s ({(1 << 14) * au.pass_flops(n, L) / tf / 1e9:.1f} GFLOP/s)', flush=True)
for v in variants:
    k, fac, kind = SPEC[v]
    r = au.arc_kprop(W, k, factor=fac, kind=kind)
    print(f'{v}: flops {r["flops"]:.3e} ({r["flops"] / au.pass_flops(n, L):.0f} passes) secs {r["secs"]:.1f}', flush=True)
