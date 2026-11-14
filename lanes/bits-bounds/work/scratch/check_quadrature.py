"""Numerical check (not a registered measurement): is the closure's measured error at large width a quadrature
artifact? Recompute the exact single-Gaussian recursion with q = 128 Gauss-Legendre nodes for Phi2 instead of 48 and
compare |a_48 - a_128|^2 / V with the measured nMSE of runs/closure_n{N}_L{L}_s{SEED}.json.
Usage: python scratch/check_quadrature.py N L SEED -> appends one JSON line to results/quadrature_check.jsonl."""
import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import bb
import closure

ROOT = os.path.join(os.path.dirname(__file__), '..')


def main():
    n, L, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    run = json.load(open(os.path.join(ROOT, 'runs', f'closure_n{n}_L{L}_s{seed}.json')))
    W = bb.make_weights(seed, n, L)
    t0 = time.time()
    a48 = closure.gaussian_recursion(W, q=48)
    a128 = closure.gaussian_recursion(W, q=128)
    out = {'n': n, 'L': L, 'seed': seed, 'V': run['V'], 'nMSE_measured': run['nMSE_closure'],
           'quad_diff_over_V': float(np.sum((a48 - a128) ** 2) / run['V']),
           'rel_norm_diff': float(np.linalg.norm(a48 - a128) / np.linalg.norm(a128)), 'seconds': time.time() - t0}
    with open(os.path.join(ROOT, 'results', 'quadrature_check.jsonl'), 'a') as f:
        f.write(json.dumps(out) + '\n')
    print(json.dumps(out), flush=True)


if __name__ == '__main__':
    main()
