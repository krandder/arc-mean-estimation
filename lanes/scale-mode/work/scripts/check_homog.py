"""EXPLORATORY check: is LVTV2 equivariant under scaling the first layer (the claim's nets use var 1/n there, ours 2/n)?
usage: check_homog.py TP_ROOT"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smlib
lv = smlib.load_lvlib(os.path.join(sys.argv[1], 'estimator', 'lvlib.py'))
for n, L, seed in ((64, 16, 600), (128, 32, 610)):
    W = [w.double() for w in smlib.au.weights(seed, n, L)]
    W2 = [W[0] / math.sqrt(2)] + W[1:]
    a = smlib.run_lv(lv, W, 24, 6.5, 'full', 'v2f'); b = smlib.run_lv(lv, W2, 24, 6.5, 'full', 'v2f')
    print(f'{n}x{L} seed {seed}: max rel |est(W1/sqrt2) * sqrt2 - est(W)| = {np.abs(b["mean"] * math.sqrt(2) - a["mean"]).max() / np.abs(a["mean"]).max():.2e}; '
          f'V_L {a["Vs"][-1]:.6f} vs {b["Vs"][-1]:.6f}', flush=True)
