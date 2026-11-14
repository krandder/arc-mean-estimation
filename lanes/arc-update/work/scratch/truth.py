"""Monte Carlo truth for a fresh net: per-layer sums in two independent halves.
usage: truth.py N L SEED LOG2_PATHS   -> runs/truth_n{N}_L{L}_s{SEED}.npz"""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import au  # noqa: E402

n, L, seed, lp = (int(a) for a in sys.argv[1:5])
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'truth_n{n}_L{L}_s{seed}.npz')
if os.path.exists(out):
    sys.exit(0)
W = au.weights(seed, n, L)
t0 = time.time()
M = au.mc_moments(W, 1 << lp, seed=777_000 + seed)
np.savez(out, S1A=M['S1A'], S1B=M['S1B'], S2A=M['S2A'], S2B=M['S2B'], N=M['N'], n=n, L=L, seed=seed,
         secs=time.time() - t0)
print(f'truth n={n} L={L} seed={seed} N=2^{lp} secs {time.time() - t0:.0f}', flush=True)
